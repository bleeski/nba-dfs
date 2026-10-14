# THROWAWAY SPIKE: not engine code. Purpose: measure what this laptop can do on one synthetic NBA night (joint stat simulation, field model, per-scenario thresholds, candidates, coverage selection, late-news re-run) to set runtime and memory budgets, and numerically test whether goal 1 (top-1% per contest) and goal 2 (no washout) conflict.
"""
Synthetic data only. Nothing here is engine code and nothing should import it.

  python night_spike.py --games 8 --showdowns 3 --S 30000 --workers 8 --late-news --belief-err 1 --tag night8
  python night_spike.py --games 8 --showdowns 3 --S 30000 --workers 8 --belief-err 0 --tag night8
  python night_spike.py --games 8 --showdowns 3 --S 30000 --workers 8 --belief-err 1 --berr-scale 2 --tag night8
  python night_spike.py --games 2 --showdowns 2 --S 30000 --workers 8 --late-news --belief-err 1 --tag night2
  python night_spike.py --games 8 --showdowns 3 --S 30000 --workers 8 --edge-sd 0.10 --edge-sel mix --skip-simtiming --tag edge8
  python night_spike.py --games 8 --showdowns 3 --S 10000 --workers 8 --edge-sd 0.10 --edge-sel one --skip-simtiming --tag edge8

S scenarios are split into selection set A (S/2) and validation set V (S/2); an independent test set B (S) is used only for reporting.
Writes out/<stamp>_<tag>_be<flag>_S<S>.json (rewritten after every step) and a matching .txt console log.
The weighted-greedy lambda sweep (class Selector) is kept for reference but no longer called; selection is greedy + swap_search.
"""
import argparse
import datetime as dt
import heapq
import itertools
import json
import math
import os
import sys
import threading
import time

import numpy as np
import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "out")
CAP = 50000
PG, SG, SF, PF, C = 1, 2, 4, 8, 16
SLOT_MASKS = {"PG": PG, "SG": SG, "SF": SF, "PF": PF, "C": C, "G": PG | SG, "F": SF | PF, "UTIL": 31}
CLASSIC_SLOTS = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]
POS_NAMES = [(PG, "PG"), (SG, "SG"), (SF, "SF"), (PF, "PF"), (C, "C")]
STATS = ["TPM", "TWO", "FTM", "REB", "AST", "STL", "BLK", "TOV"]
NB_SHAPE = {"TPM": 10.0, "TWO": 20.0, "FTM": 12.0, "REB": 15.0, "AST": 10.0, "STL": 5.0, "BLK": 3.0, "TOV": 8.0}
GRID = np.geomspace(0.45, 1e-5, 72)  # exceedance levels for the stored tail of F_{c,s}
EPS_LIST = [0.0, 0.02, 0.05, 0.10, 0.20]


def pos_str(mask):
    return "/".join(n for b, n in POS_NAMES if mask & b)


# ============================================================================ instrumentation
class MemSampler(threading.Thread):
    """Samples RSS of this process plus all child processes (pool workers) every 50 ms."""

    def __init__(self):
        super().__init__(daemon=True)
        self.me = psutil.Process()
        self.peak_total = 0
        self.peak_self = 0
        self.peak_children = 0
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            try:
                own = self.me.memory_info().rss
                ch = 0
                for c in self.me.children(recursive=True):
                    try:
                        ch += c.memory_info().rss
                    except Exception:
                        pass
                self.peak_self = max(self.peak_self, own)
                self.peak_children = max(self.peak_children, ch)
                self.peak_total = max(self.peak_total, own + ch)
            except Exception:
                pass
            time.sleep(0.05)


class Recorder:
    def __init__(self, path_json, path_txt, meta):
        self.path_json, self.path_txt = path_json, path_txt
        self.data = dict(meta=meta, steps={}, results={})
        self.txt = open(path_txt, "w", encoding="utf-8")
        self.workers = []  # psutil.Process of every pool worker ever started (for CPU accounting)
        self.cpu_cache = {}  # pid -> last seen cpu seconds (dead workers keep their last value)
        self.me = psutil.Process()

    def log(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        self.txt.write(s + "\n")
        self.txt.flush()

    def _cpu(self):
        t = self.me.cpu_times()
        tot = t.user + t.system
        for w in self.workers:
            try:
                c = w.cpu_times()
                self.cpu_cache[w.pid] = c.user + c.system
            except Exception:
                pass
            tot += self.cpu_cache.get(w.pid, 0.0)
        return tot

    def step(self, name):
        rec = self

        class _S:
            def __enter__(self_):
                self_.t0 = time.perf_counter()
                self_.c0 = rec._cpu()
                return self_

            def __exit__(self_, *exc):
                wall = time.perf_counter() - self_.t0
                cpu = rec._cpu() - self_.c0
                rec.data["steps"][name] = dict(wall_s=round(wall, 3), cpu_s=round(cpu, 2), avg_cores_busy=round(cpu / max(wall, 1e-9), 2),
                                               rss_mb_after=round(rec.me.memory_info().rss / 2**20, 1))
                rec.log(f"[step] {name}: {wall:.2f} s wall, {cpu:.1f} s cpu, {cpu / max(wall, 1e-9):.2f} cores busy")
                rec.flush()
                return False
        return _S()

    def put(self, key, val):
        self.data["results"][key] = val
        self.flush()

    def flush(self):
        with open(self.path_json, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1, default=_json_default)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    return str(o)


def system_load(seconds=3.0):
    """System CPU % over a window, plus other python processes and their CPU %."""
    me = os.getpid()
    procs = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if "python" in (p.info["name"] or "").lower() and p.info["pid"] != me:
                p.cpu_percent(None)
                procs.append(p)
        except Exception:
            pass
    tot = psutil.cpu_percent(interval=seconds)
    others = []
    for p in procs:
        try:
            c = p.cpu_percent(None)
            others.append(dict(pid=p.pid, cpu_pct=round(c, 1), cmd=" ".join(p.info["cmdline"] or [])[-120:]))
        except Exception:
            pass
    vm = psutil.virtual_memory()
    return dict(system_cpu_pct=tot, avail_gb=round(vm.available / 2**30, 2), other_python=sorted(others, key=lambda d: -d["cpu_pct"])[:8])


# ============================================================================ synthetic night
RATES = {  # per 36 minutes: PTS, 3PM, REB, AST, STL, BLK, TOV
    ("star", "guard"): (29, 3.2, 5.5, 8.0, 1.3, 0.4, 3.4), ("star", "wing"): (28, 2.8, 7.0, 5.0, 1.3, 0.7, 3.0),
    ("star", "forward"): (26, 1.8, 9.5, 4.5, 1.1, 1.0, 2.9), ("star", "center"): (25, 0.9, 12.5, 4.5, 1.0, 1.7, 3.0),
    ("starter", "guard"): (18, 2.6, 4.5, 5.5, 1.2, 0.4, 2.1), ("starter", "wing"): (16, 2.3, 6.0, 3.0, 1.1, 0.6, 1.6),
    ("starter", "forward"): (15, 1.4, 8.5, 2.6, 0.9, 0.8, 1.6), ("starter", "center"): (15, 0.4, 11.5, 2.6, 0.8, 1.6, 1.8),
    ("bench", "guard"): (16, 2.2, 4.0, 4.5, 1.1, 0.3, 2.0), ("bench", "wing"): (14, 2.0, 5.5, 2.5, 1.0, 0.5, 1.5),
    ("bench", "forward"): (13, 1.2, 7.5, 2.0, 0.9, 0.7, 1.4), ("bench", "center"): (13, 0.3, 10.5, 2.0, 0.8, 1.4, 1.6),
}


def cls_of(mask):
    if mask & C:
        return "center"
    if mask == PF:
        return "forward"
    if mask & SF:
        return "wing"
    return "guard"


def make_night(n_games, seed):
    rng = np.random.default_rng(seed)
    games = []
    for g in range(n_games):
        games.append(dict(id=g, spread=float(np.round(rng.normal(0, 5.5) * 2) / 2), total=float(np.round(rng.uniform(216, 238) * 2) / 2)))
    st_opts = [[PG, PG | SG], [SG, SG | SF, PG | SG], [SF, SF | PF, SG | SF], [PF, SF | PF, PF | C], [C, PF | C]]
    bn_opts = [[PG, PG | SG, SG], [SG | SF, SF], [SF | PF, PF], [C, PF | C], [PG, SG]]
    allpos = [PG, SG, SF, PF, C, PG | SG, SG | SF, SF | PF, PF | C]
    P = []
    team_players = []
    for t in range(2 * n_games):
        g = t // 2
        G = games[g]
        imp = G["total"] / 2 + (G["spread"] / 2 if t % 2 == 0 else -G["spread"] / 2)
        star = int(rng.integers(5))
        costar = int(rng.integers(5)) if rng.random() < 0.35 else -1
        roster = []
        for k in range(5):
            mask = int(rng.choice(st_opts[k]))
            tier = "star" if k == star else ("costar" if k == costar else "starter")
            m = 35 + rng.normal(0, 1) if tier == "star" else (33 + rng.normal(0, 1) if tier == "costar" else rng.uniform(28, 33.5))
            roster.append(dict(mask=mask, tier=tier, min=m, role="starter"))
        for k, bm in enumerate([24, 21, 17, 13, 9]):
            mask = int(rng.choice(bn_opts[k]))
            roster.append(dict(mask=mask, tier="bench", min=bm + rng.normal(0, 1.5), role="bench"))
        for bm in (4.0, 2.0, 0.7):
            roster.append(dict(mask=int(rng.choice(allpos)), tier="deep", min=bm, role="deep"))
        tot = sum(r["min"] for r in roster)
        for r in roster:
            r["min"] *= 240.0 / tot
        # per-36 rates with player-level variety
        for r in roster:
            cl = cls_of(r["mask"])
            r["cls"] = cl
            if r["tier"] == "costar":
                base = np.mean([RATES[("star", cl)], RATES[("starter", cl)]], axis=0)
            elif r["tier"] == "deep":
                base = np.array(RATES[("bench", cl)]) * 0.85
            else:
                base = np.array(RATES[(r["tier"], cl)], dtype=float)
            pts, tpm, reb, ast, stl, blk, tov = base
            ms = math.exp(rng.normal(0, 0.12))
            pts *= ms
            tpm *= ms * math.exp(rng.normal(0, 0.15))
            reb *= math.exp(rng.normal(0, 0.12))
            ast *= math.exp(rng.normal(0, 0.15))
            stl *= math.exp(rng.normal(0, 0.15))
            blk *= math.exp(rng.normal(0, 0.15))
            tov *= ms ** 0.7
            ftm = (0.20 if cl in ("forward", "center") else 0.18) * pts
            two = max(0.5, (pts - 3 * tpm - ftm) / 2)
            r["rates"] = np.array([tpm, two, ftm, reb, ast, stl, blk, tov])
        # scale scoring so expected team points match the implied team total
        exp_pts = sum((3 * r["rates"][0] + 2 * r["rates"][1] + r["rates"][2]) / 36 * r["min"] for r in roster)
        sc = imp / exp_pts
        for r in roster:
            r["rates"][[0, 1, 2]] *= sc
            r["rates"][4] *= sc ** 0.8
        ids = []
        for r in roster:
            r.update(team=t, game=g, id=len(P))
            ids.append(len(P))
            P.append(r)
        team_players.append(np.array(ids))
    n = len(P)
    arr = dict(
        pos=np.array([p["mask"] for p in P], dtype=np.int64), team=np.array([p["team"] for p in P]), game=np.array([p["game"] for p in P]),
        base_min=np.array([p["min"] for p in P]), rates=np.array([p["rates"] for p in P]),
        starter=np.array([p["role"] == "starter" for p in P]), deep=np.array([p["role"] == "deep" for p in P]),
        cls=np.array([p["cls"] for p in P]), tier=np.array([p["tier"] for p in P]))
    pts36 = 3 * arr["rates"][:, 0] + 2 * arr["rates"][:, 1] + arr["rates"][:, 2]
    arr["use_w"] = pts36 * arr["base_min"]
    arr["reb_w"] = arr["rates"][:, 3] * arr["base_min"]
    arr["ast_w"] = arr["rates"][:, 4] * arr["base_min"]
    # questionable starters with a named beneficiary
    q_games = [g for g in (0, 1, 4, 6) if g < n_games]
    quest = []
    for g in q_games:
        t = 2 * g
        ids = team_players[t]
        if g == 0:
            q = int(ids[np.argmax([1 if P[i]["tier"] == "star" else 0 for i in ids])])
        else:
            cand = [i for i in ids if P[i]["role"] == "starter" and P[i]["tier"] == "starter"]
            q = int(max(cand, key=lambda i: P[i]["min"]))
        bench = [i for i in ids if P[i]["role"] == "bench"]
        same = [i for i in bench if P[i]["cls"] == P[q]["cls"]] or bench
        b = int(max(same, key=lambda i: P[i]["min"]))
        quest.append(dict(player=q, beneficiary=b, p_active=0.5, game=g, team=t))
    return dict(games=games, n_games=n_games, players=P, n=n, team_players=team_players, arr=arr, quest=quest,
                game_players=[np.concatenate([team_players[2 * g], team_players[2 * g + 1]]) for g in range(n_games)])


# ============================================================================ stat-level joint simulator
SIMP = dict(pace_sd=0.045, env_sd=0.065, margin_sd=12.0, team_eps_sd=3.0, g_shape=40.0, min_cv=0.08, min_sd0=1.0, ee_rate=0.015,
            share_shape={"TPM": 15.0, "TWO": 40.0, "FTM": 15.0, "REB": 30.0, "AST": 25.0}, nb_shape={"STL": 8.0, "BLK": 5.0, "TOV": 8.0})


def _alloc(rng, n_tot, w):
    """Dirichlet-multinomial style allocation of a team count to players (zero-sum within team)."""
    p = w / np.maximum(w.sum(1, keepdims=True), 1e-12)
    p[:, -1] = np.clip(1.0 - p[:, :-1].sum(1), 0.0, 1.0)
    return rng.multinomial(n_tot, p)


def sim_game(night, g, S, seed, force_out=(), force_in=()):
    """Simulate one game for S scenarios (R3 section 4 structure, simplified). Draw order never depends on
    force flags, so re-simulating one game with news keeps common random numbers for everything else."""
    A = night["arr"]
    G = night["games"][g]
    sp = SIMP
    rng = np.random.default_rng([seed, 7919, g])
    pace = np.exp(rng.normal(0, sp["pace_sd"], S) - sp["pace_sd"] ** 2 / 2)
    env = np.exp(rng.normal(0, sp["env_sd"], S) - sp["env_sd"] ** 2 / 2)
    margin = rng.normal(G["spread"], sp["margin_sd"], S)
    u_ot, u_ot2 = rng.random(S), rng.random(S)
    n_ot = np.where((np.abs(margin) < 1.25) & (u_ot < 0.55), 1 + (u_ot2 < 0.12), 0).astype(np.float64)
    total_reg = G["total"] * pace * env
    Pt = [(total_reg + margin) / 2, (total_reg - margin) / 2]
    imp = [G["total"] / 2 + G["spread"] / 2, G["total"] / 2 - G["spread"] / 2]
    eff_rel = [Pt[i] / (imp[i] * pace) for i in (0, 1)]
    excess = np.clip(np.abs(margin) - 15, 0, 15) * (n_ot == 0)
    res = dict(cols=[], X=[], team_pts=np.zeros((S, 2), np.float32), n_ot=n_ot, margin=margin, act={}, dd={}, td={})
    for side in (0, 1):
        t = 2 * g + side
        idx = night["team_players"][t]
        n = len(idx)
        bm = A["base_min"][idx]
        starter = A["starter"][idx]
        deep = A["deep"][idx]
        sd_m = np.where(deep, 2.5, sp["min_cv"] * bm + sp["min_sd0"])
        mins = np.clip(bm[None, :] + sd_m[None, :] * rng.standard_normal((S, n)), 0, 44)
        ee = (rng.random((S, n)) < sp["ee_rate"]) & ~deep[None, :]
        ee_f = rng.uniform(0.1, 0.6, (S, n))
        mins = np.where(ee, mins * ee_f, mins)
        active = np.ones((S, n), bool)
        sc_boost = np.ones((S, n))
        ast_boost = np.ones((S, n))
        tmult = np.ones(S)
        for q in night["quest"]:
            if q["team"] != t:
                continue
            uq = rng.random(S)
            act_q = uq < q["p_active"]
            if q["player"] in force_out:
                act_q[:] = False
            if q["player"] in force_in:
                act_q[:] = True
            qi = int(np.nonzero(idx == q["player"])[0][0])
            bi = int(np.nonzero(idx == q["beneficiary"])[0][0])
            out = ~act_q
            mins[out, qi] = 0.0
            active[out, qi] = False
            mins[out, bi] += 0.5 * bm[qi]
            others = np.array([j for j in range(n) if j not in (qi, bi) and not deep[j]])
            w = bm[others] * np.where(A["cls"][idx[others]] == A["cls"][idx[qi]], 2.0, 1.0)
            mins[np.ix_(out, others)] += 0.5 * bm[qi] * (w / w.sum())[None, :]
            sc_boost[out, bi] *= 1.12
            ast_boost[out, bi] *= 1.08
            sc_boost[np.ix_(out, others)] *= 1.04
            if A["tier"][q["player"]] == "star":  # team scores a little less without its star (line assumes 50/50)
                tmult = np.where(out, 0.9875, 1.0125)
            res["act"][q["player"]] = act_q
        # blowout trim: starters lose minutes, deep bench gets garbage time
        mins[:, starter] *= (1 - 0.013 * excess)[:, None]
        mins[:, deep] += 0.35 * excess[:, None]
        mins *= active
        # reconcile to 240 (+25 per overtime)
        target = 240.0 + 25.0 * n_ot
        D = target - mins.sum(1)
        bench_flag = (~starter).astype(float)
        w_pos = mins * (1 + 1.5 * bench_flag[None, :] * (excess > 0)[:, None]) * (1 + (n_ot > 0)[:, None] * 0.03 * mins)
        w = np.where(D[:, None] > 0, w_pos, mins)
        w = w / np.maximum(w.sum(1, keepdims=True), 1e-9)
        mins = np.clip(mins + D[:, None] * w, 0, (48 + 5 * n_ot)[:, None]) * active
        # team scoring from the game draw (spread, total, pace, OT); players split it (zero-sum within team)
        Pt_eff = Pt[side] * (target / 240.0) * tmult
        gf = rng.gamma(sp["g_shape"], 1 / sp["g_shape"], (S, n))  # per-player "big night" factor shared across stats
        r = A["rates"][idx] / 36.0
        bw = mins * gf
        lamT = r[None, :, 0] * bw * sc_boost
        lam2 = r[None, :, 1] * bw * sc_boost
        lamF = r[None, :, 2] * bw * sc_boost
        sT, s2, sF = lamT.sum(1), lam2.sum(1), lamF.sum(1)
        kappa = Pt_eff / np.maximum(3 * sT + 2 * s2 + sF, 1e-9)
        n3 = rng.poisson(kappa * sT * rng.gamma(40.0, 1 / 40.0, S))
        nF = rng.poisson(kappa * sF * rng.gamma(30.0, 1 / 30.0, S))
        eps_t = rng.normal(0, sp["team_eps_sd"], S)
        n2 = np.maximum(0, np.rint((Pt_eff + eps_t - 3 * n3 - nF) / 2)).astype(np.int64)
        sh = sp["share_shape"]
        TPM = _alloc(rng, n3, lamT * rng.gamma(sh["TPM"], 1 / sh["TPM"], (S, n)))
        TWO = _alloc(rng, n2, lam2 * rng.gamma(sh["TWO"], 1 / sh["TWO"], (S, n)))
        FTM = _alloc(rng, nF, lamF * rng.gamma(sh["FTM"], 1 / sh["FTM"], (S, n)))
        rebm = pace * np.clip(2 - eff_rel[1 - side], 0.2, None) ** 0.5 * np.clip(2 - eff_rel[side], 0.2, None) ** 0.25
        lamR = r[None, :, 3] * bw
        nR = rng.poisson(lamR.sum(1) * rebm * (target / 240.0) * rng.gamma(30.0, 1 / 30.0, S))
        REB = _alloc(rng, nR, lamR * rng.gamma(sh["REB"], 1 / sh["REB"], (S, n)))
        lamA = r[None, :, 4] * bw * ast_boost
        fgm = n3 + n2
        p_ast = np.clip(lamA.sum(1) * (Pt_eff / imp[side]) / np.maximum(kappa * (sT + s2), 1e-9), 0.3, 0.8)
        nA = rng.binomial(fgm, p_ast)
        AST = _alloc(rng, nA, lamA * rng.gamma(sh["AST"], 1 / sh["AST"], (S, n)))
        nb = sp["nb_shape"]
        STL = rng.poisson(r[None, :, 5] * mins * pace[:, None] * gf * rng.gamma(nb["STL"], 1 / nb["STL"], (S, n)))
        BLK = rng.poisson(r[None, :, 6] * mins * pace[:, None] * gf * rng.gamma(nb["BLK"], 1 / nb["BLK"], (S, n)))
        TOV = rng.poisson(r[None, :, 7] * mins * pace[:, None] * np.sqrt(gf * sc_boost) * rng.gamma(nb["TOV"], 1 / nb["TOV"], (S, n)))
        PTS = 3 * TPM + 2 * TWO + FTM
        dk = PTS + 0.5 * TPM + 1.25 * REB + 1.5 * AST + 2 * STL + 2 * BLK - 0.5 * TOV
        cats = (PTS >= 10).astype(np.int8) + (REB >= 10) + (AST >= 10) + (BLK >= 10) + (STL >= 10)
        dk = dk + 1.5 * (cats >= 2) + 3.0 * (cats >= 3)
        res["cols"].append(idx)
        res["X"].append(dk.astype(np.float32))
        res["team_pts"][:, side] = PTS.sum(1)
        for j, pid in enumerate(idx):
            res["dd"][int(pid)] = float((cats[:, j] >= 2).mean())
            res["td"][int(pid)] = float((cats[:, j] >= 3).mean())
    res["cols"] = np.concatenate(res["cols"])
    res["X"] = np.concatenate(res["X"], axis=1)
    be = night.get("berr")
    if be:  # belief-error layer: our projections are wrong, drawn per scenario from its own stream (BET sizes)
        rng_e = np.random.default_rng([seed, 31337, g])
        ts = be["team_sd"]
        tm = np.exp(rng_e.normal(0, ts, (S, 2)) - ts ** 2 / 2)
        A_ = night["arr"]
        psd = np.where(A_["starter"][res["cols"]], be["starter_sd"], be["bench_sd"])
        pm = np.exp(rng_e.normal(0, 1, (S, len(res["cols"]))) * psd[None, :] - psd[None, :] ** 2 / 2)
        side = (A_["team"][res["cols"]] % 2)
        res["X"] = (res["X"] * tm[:, side] * pm).astype(np.float32)
    ed = night.get("edge")
    if ed:  # edge uncertainty: truth = public + w (engine - public), w ~ Beta(a, b) ONCE per scenario, shared by every player and contest
        if ed.get("w_fixed") is not None:
            wv = np.full(S, float(ed["w_fixed"]))
        else:
            wv = np.random.default_rng([seed, 777]).beta(ed["a"], ed["b"], S)
        dcol = ed["d"][res["cols"]]
        res["X"] = (res["X"] * (1 + wv[:, None] * (dcol[None, :] - 1))).astype(np.float32)
    return res


def sim_night(night, S, seed, force_out=()):
    X = np.zeros((S, night["n"]), np.float32)
    team_pts = np.zeros((S, 2 * night["n_games"]), np.float32)
    n_ot = np.zeros((S, night["n_games"]))
    margin = np.zeros((S, night["n_games"]))
    act, dd, td = {}, {}, {}
    for g in range(night["n_games"]):
        r = sim_game(night, g, S, seed, force_out=force_out)
        X[:, r["cols"]] = r["X"]
        team_pts[:, 2 * g:2 * g + 2] = r["team_pts"]
        n_ot[:, g] = r["n_ot"]
        margin[:, g] = r["margin"]
        act.update(r["act"])
        dd.update(r["dd"])
        td.update(r["td"])
    own = {}
    be = night.get("berr")
    if be:  # one field-ownership shock per slate per scenario (log-scale, per player), shared by every contest on the slate
        rng_o = np.random.default_rng([seed, 4242])
        own["classic"] = rng_o.normal(0, be["own_sd"], (S, night["n"])).astype(np.float32)
        for g in range(night["n_games"]):
            own[f"sd{g}"] = rng_o.normal(0, be["own_sd"], (S, len(night["game_players"][g]))).astype(np.float32)
    return dict(X=X, team_pts=team_pts, n_ot=n_ot, margin=margin, act=act, dd=dd, td=td, seed=seed, S=S, own=own)


def replace_game(sim, night, g, force_out=()):
    r = sim_game(night, g, sim["S"], sim["seed"], force_out=force_out)
    sim["X"][:, r["cols"]] = r["X"]
    sim["team_pts"][:, 2 * g:2 * g + 2] = r["team_pts"]
    sim["n_ot"][:, g] = r["n_ot"]
    sim["margin"][:, g] = r["margin"]
    sim["act"].update(r["act"])


def sim_diagnostics(night, sim, proj):
    A = night["arr"]
    X = sim["X"]
    P = night["players"]
    out = {}
    games = []
    for g, G in enumerate(night["games"]):
        tot = sim["team_pts"][:, 2 * g] + sim["team_pts"][:, 2 * g + 1]
        mar = sim["team_pts"][:, 2 * g] - sim["team_pts"][:, 2 * g + 1]
        games.append(dict(game=g, line_total=G["total"], sim_mean_total=round(float(tot.mean()), 1), sim_median_total=round(float(np.median(tot)), 1),
                          over_rate_vs_line=round(float((tot > G["total"]).mean()), 3), line_spread=G["spread"],
                          sim_mean_margin=round(float(mar.mean()), 2), sim_sd_margin=round(float(mar.std()), 2),
                          ot_rate=round(float((sim["n_ot"][:, g] > 0).mean()), 4), blowout_rate_drawn_margin_gt15=round(float((np.abs(sim["margin"][:, g]) > 15).mean()), 3)))
    out["games"] = games
    out["ot_rate_overall"] = round(float((sim["n_ot"] > 0).mean()), 4)

    def desc(i, mask=None):
        x = X[:, i] if mask is None else X[mask, i]
        return dict(player=int(i), pos=pos_str(int(A["pos"][i])), tier=str(A["tier"][i]), base_min=round(float(A["base_min"][i]), 1),
                    n=int(len(x)), mean=round(float(x.mean()), 2), sd=round(float(x.std()), 2), p01=round(float(np.percentile(x, 1)), 1),
                    p50=round(float(np.percentile(x, 50)), 1), p99=round(float(np.percentile(x, 99)), 1), dd_rate=round(sim["dd"][int(i)], 4),
                    td_rate=round(sim["td"][int(i)], 4))
    star = int(np.argmax(proj))
    starters = np.nonzero(A["starter"] & (A["tier"] == "starter"))[0]
    role = int(starters[np.argmin(np.abs(proj[starters] - 25))])
    q0 = night["quest"][0]
    act = sim["act"][q0["player"]]
    out["star"] = desc(star)
    out["role_player"] = desc(role)
    out["questionable_q0"] = desc(q0["player"])
    out["beneficiary_all"] = desc(q0["beneficiary"])
    out["beneficiary_when_q0_active"] = desc(q0["beneficiary"], act)
    out["beneficiary_when_q0_out"] = desc(q0["beneficiary"], ~act)
    centers = np.nonzero((A["cls"] == "center") & A["starter"])[0]
    big = int(centers[np.argmax(proj[centers])])
    out["top_big"] = desc(big)
    # correlations among rotation players (base minutes >= 15)
    same, opp, ss = [], [], []
    for g in range(night["n_games"]):
        ids = night["game_players"][g]
        rot = [i for i in ids if A["base_min"][i] >= 15 and i not in [q["player"] for q in night["quest"]]]
        Cm = np.corrcoef(X[:, rot].T)
        for a in range(len(rot)):
            for b in range(a + 1, len(rot)):
                i, j = rot[a], rot[b]
                if A["team"][i] == A["team"][j]:
                    same.append(Cm[a, b])
                    if A["starter"][i] and A["starter"][j]:
                        ss.append(Cm[a, b])
                else:
                    opp.append(Cm[a, b])
    out["corr_teammates_rotation_mean"] = round(float(np.mean(same)), 4)
    out["corr_teammates_starters_mean"] = round(float(np.mean(ss)), 4)
    out["corr_opponents_rotation_mean"] = round(float(np.mean(opp)), 4)
    out["corr_q0_vs_beneficiary"] = round(float(np.corrcoef(X[:, q0["player"]], X[:, q0["beneficiary"]])[0, 1]), 4)
    out["max_td_rate_any_player"] = round(max(sim["td"].values()), 4)
    return out


# ============================================================================ MILP (GLPK via swiglpk, Hall formulation)
def hall_requirements():
    """Hall's theorem rows for the 7 non-UTIL Classic slots, keyed by the union of eligible position bits."""
    seven = [SLOT_MASKS[s] for s in CLASSIC_SLOTS if s != "UTIL"]
    need = {}
    for r in range(1, 8):
        for comb in itertools.combinations(range(7), r):
            u = 0
            for i in comb:
                u |= seven[i]
            need[u] = max(need.get(u, 0), r)
    items = sorted(need.items(), key=lambda kv: (bin(kv[0]).count("1"), -kv[1]))
    kept = []
    for u, nd in items:
        if any((u2 & ~u) == 0 and n2 >= nd for u2, n2 in kept):
            continue
        kept.append((u, nd))
    return kept


_WK = {}


def _worker_init(pos, salary, game, n_games):
    import swiglpk as g
    g.glp_term_out(g.GLP_OFF)
    n = len(pos)
    lp = g.glp_create_prob()
    g.glp_set_obj_dir(lp, g.GLP_MAX)
    g.glp_add_cols(lp, n)
    for j in range(n):
        g.glp_set_col_kind(lp, j + 1, g.GLP_BV)

    def add_row(idx, coef, lo, hi):
        idx = list(idx)
        i = g.glp_add_rows(lp, 1)
        if lo is not None and hi is not None:
            t = g.GLP_FX if lo == hi else g.GLP_DB
        elif lo is not None:
            t = g.GLP_LO
        else:
            t = g.GLP_UP
        g.glp_set_row_bnds(lp, i, t, 0.0 if lo is None else float(lo), 0.0 if hi is None else float(hi))
        ia = g.intArray(len(idx) + 1)
        va = g.doubleArray(len(idx) + 1)
        for k, (j, v) in enumerate(zip(idx, coef)):
            ia[k + 1] = int(j) + 1
            va[k + 1] = float(v)
        g.glp_set_mat_row(lp, i, len(idx), ia, va)
    add_row(range(n), [1.0] * n, 8, 8)
    for u, nd in hall_requirements():
        idx = [j for j in range(n) if pos[j] & u]
        add_row(idx, [1.0] * len(idx), nd, None)
    add_row(range(n), [float(s) for s in salary], None, CAP)
    for gm in range(n_games):
        idx = [j for j in range(n) if game[j] == gm]
        add_row(idx, [1.0] * len(idx), None, 7)
    parm = g.glp_iocp()
    g.glp_init_iocp(parm)
    parm.presolve = g.GLP_ON
    parm.msg_lev = g.GLP_MSG_OFF
    _WK.update(g=g, lp=lp, parm=parm, n=n)


def _solve_batch(objs):
    g, lp, parm, n = _WK["g"], _WK["lp"], _WK["parm"], _WK["n"]
    out, times = [], []
    for row in objs:
        t0 = time.perf_counter()
        for j in range(n):
            g.glp_set_obj_coef(lp, j + 1, float(row[j]))
        ret = g.glp_intopt(lp, parm)
        if ret != 0 or g.glp_mip_status(lp) != g.GLP_OPT:
            out.append(None)
        else:
            out.append(tuple(j for j in range(n) if g.glp_mip_col_val(lp, j + 1) > 0.5))
        times.append(time.perf_counter() - t0)
    return out, times


class SolverPool:
    def __init__(self, night, salary, workers, rec):
        import multiprocessing as mp
        for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
            os.environ[k] = "1"  # children only; this process already initialized its BLAS
        A = night["arr"]
        ctx = mp.get_context("spawn")
        self.pool = ctx.Pool(workers, initializer=_worker_init, initargs=(A["pos"].tolist(), [int(s) for s in salary], A["game"].tolist(), night["n_games"]))
        self.pool.map(_solve_batch, [[] for _ in range(workers)])  # force worker start-up
        self.procs = [psutil.Process(p.pid) for p in self.pool._pool]
        rec.workers.extend(self.procs)
        rec._cpu()
        self.rec = rec

    def solve(self, objs, batch=40):
        chunks = [objs[i:i + batch] for i in range(0, len(objs), batch)]
        res = self.pool.map(_solve_batch, chunks)
        lineups, times = [], []
        for l, t in res:
            lineups.extend(l)
            times.extend(t)
        return lineups, np.array(times)

    def worker_rss_mb(self):
        tot = 0
        for p in self.procs:
            try:
                tot += p.memory_info().rss
            except Exception:
                pass
        return round(tot / 2**20, 1)

    def close(self):
        self.rec._cpu()  # cache final worker cpu times
        self.pool.terminate()
        self.pool.join()


def assign_slots(pos, pids):
    match = {}

    def try_assign(pid, seen):
        for s in CLASSIC_SLOTS:
            if (pos[pid] & SLOT_MASKS[s]) and s not in seen:
                seen.add(s)
                if s not in match or try_assign(match[s], seen):
                    match[s] = pid
                    return True
        return False
    for pid in pids:
        if not try_assign(pid, set()):
            return None
    return match


def validate_classic(night, salary, L):
    A = night["arr"]
    if L is None or len(L) != 8 or len(set(L)) != 8:
        return False
    if salary[list(L)].sum() > CAP:
        return False
    gm = A["game"][list(L)]
    if np.bincount(gm, minlength=night["n_games"]).max() > 7:
        return False
    m = assign_slots(A["pos"], list(L))
    return m is not None and len(m) == 8


# ============================================================================ field model
def own_weights_classic(proj, sal):
    value = proj / (sal / 1000.0)
    w = np.exp(1.3 * (value - 4.8)) * (proj / 25.0)
    return np.where(proj >= 4, w, 1e-4)


def classic_sampler(night, proj, sal, n_target, rng, floor=48000, own_mult=None):
    A = night["arr"]
    P = night["n"]
    w = own_weights_classic(proj, sal)
    if own_mult is not None:
        w = w * own_mult
    elig = {s: ((A["pos"] & SLOT_MASKS[s]) != 0) for s in CLASSIC_SLOTS}
    out = []
    tries = 0
    B = 40000
    while sum(len(o) for o in out) < n_target:
        used = np.zeros((B, P), bool)
        picks = np.zeros((B, 8), np.int64)
        for k, s in enumerate(CLASSIC_SLOTS):
            W = np.where(used, 0.0, (w * elig[s])[None, :])
            cum = np.cumsum(W, axis=1)
            r = rng.random(B) * cum[:, -1]
            pick = (cum < r[:, None]).sum(1)
            pick = np.minimum(pick, P - 1)
            picks[:, k] = pick
            used[np.arange(B), pick] = True
        tries += B
        tot = sal[picks].sum(1)
        gm = A["game"][picks]
        ok = (tot >= floor) & (tot <= CAP) & ~(gm == gm[:, :1]).all(1)
        out.append(np.sort(picks[ok], axis=1))
    L = np.concatenate(out)[:n_target]
    return L, tries


def unique_counts(rows):
    """rows: (n, k) int array -> unique rows (u, k), counts (u,)"""
    u, c = np.unique(rows, axis=0, return_counts=True)
    return u, c


def sd_enumerate(sal_sd, team01):
    n = len(sal_sd)
    combos = np.array(list(itertools.combinations(range(n - 1), 5)), dtype=np.int16)
    rows = []
    for c in range(n):
        others = np.array([j for j in range(n) if j != c], dtype=np.int16)
        U = others[combos]
        s = 1.5 * sal_sd[c] + sal_sd[U].sum(1)
        tm = team01[c] + team01[U].sum(1)
        ok = (s <= CAP) & (tm >= 1) & (tm <= 5)
        rows.append(np.column_stack([np.full(int(ok.sum()), c, dtype=np.int16), U[ok]]))
    L = np.vstack(rows)
    return L  # (n_legal, 6): col 0 = captain, cols 1..5 = sorted UTILs (local indices)


def sd_incidence(L, n):
    M = np.zeros((len(L), n), np.float32)
    r = np.arange(len(L))
    M[r, L[:, 0]] = 1.5
    for k in range(1, 6):
        M[r, L[:, k]] = 1.0
    return M


def sd_mean_sd(L, mu, cov, chunk=200000):
    n = len(mu)
    mean = np.empty(len(L), np.float32)
    sd = np.empty(len(L), np.float32)
    for i in range(0, len(L), chunk):
        M = sd_incidence(L[i:i + chunk], n)
        mean[i:i + chunk] = M @ mu.astype(np.float32)
        sd[i:i + chunk] = np.sqrt(np.maximum(((M @ cov.astype(np.float32)) * M).sum(1), 0))
    return mean, sd


SD_OWN = dict(val_k=0.6, pj_pow=0.7, cpt_pow=1.0)  # casual Showdown ownership temperature (BET, tuned to ~85% unique entries at N=1,200)


def field_showdown(night, g, proj, sal_sd, rng, n_cas=50000, n_opt=2000, floor=46000, own_mult=None):
    cols = night["game_players"][g]
    team01 = (night["arr"]["team"][cols] % 2).astype(np.int16)
    t0 = time.perf_counter()
    L = sd_enumerate(sal_sd[cols], team01)
    t_enum = time.perf_counter() - t0
    pj = proj[cols]
    ss = sal_sd[cols]
    val = pj / (ss / 1000.0)
    uw = np.where(pj >= 3, np.exp(SD_OWN["val_k"] * (val - 4.0)) * (pj / 20.0) ** SD_OWN["pj_pow"], 1e-4)
    if own_mult is not None:
        uw = uw * own_mult[cols]
    cw = uw * np.maximum(pj / 30.0, 1e-3) ** SD_OWN["cpt_pow"]
    lw = np.log(cw)[L[:, 0]] + np.log(uw)[L[:, 1:]].sum(1)
    salL = 1.5 * ss[L[:, 0]] + ss[L[:, 1:]].sum(1)
    lw = np.where(salL >= floor, lw, -np.inf)
    p = np.exp(lw - lw.max())
    p /= p.sum()
    draws = rng.choice(len(L), size=n_cas, p=p)
    cnt_cas = np.bincount(draws, minlength=len(L))
    # optimizer-like: argmax over legal lineups under noisy projections (restricted to top 60k by mean, exact for these draws)
    meanL = (1.5 * pj[L[:, 0]] + pj[L[:, 1:]].sum(1)).astype(np.float32)
    top = np.argsort(-meanL)[:60000]
    Mtop = sd_incidence(L[top], len(cols))
    noisy = np.maximum(0, pj[None, :] * (1 + 0.15 * rng.standard_normal((n_opt, len(cols))))).astype(np.float32)
    if own_mult is not None:
        noisy = noisy * (own_mult[cols][None, :] > 0.5)
    winners = []
    for i in range(0, n_opt, 250):
        sc = Mtop @ noisy[i:i + 250].T
        winners.append(top[np.argmax(sc, axis=0)])
    winners = np.concatenate(winners)
    cnt_opt = np.bincount(winners, minlength=len(L))
    ids = np.nonzero((cnt_cas > 0) | (cnt_opt > 0))[0]
    assert len(ids) < 65536
    return dict(L_all=L, ids=ids, lineups=L[ids], cnt_opt=cnt_opt[ids], cnt_cas=cnt_cas[ids], n_opt=n_opt, n_cas=n_cas,
                n_legal=len(L), t_enum=t_enum, cols=cols, meanL=meanL)


def contest_weights(pool, wopt):
    return wopt * pool["cnt_opt"] / pool["n_opt"] + (1 - wopt) * pool["cnt_cas"] / pool["n_cas"]


# ============================================================================ thresholds (chunked, field never held whole)
def thresholds(Xs, cols, pool_inc, cnt_opt, cnt_cas, wopts, levels, chunk, own_delta=None):
    """For each contest (mixture weight wopts[c], exceedance levels[c]) return the field score at each level per scenario.
    The field is a two-component mixture (optimizer-like, casual) with per-lineup counts, so one sort and two integer
    cumulative sums per chunk serve every contest; each contest then needs only a vectorized bisection.
    Exceedance e: field weight scoring at or above the returned score is >= e (first crossing from the top)."""
    S = Xs.shape[0]
    n_pool = pool_inc.shape[0]
    assert n_pool < 65536, n_pool
    incT = np.ascontiguousarray(pool_inc.T)
    idx_arr = np.arange(n_pool, dtype=np.uint32)
    cO = np.asarray(cnt_opt, np.int32)
    cC = np.asarray(cnt_cas, np.int32)
    n_opt, n_cas = int(cO.sum()), int(cC.sum())
    outs = [np.empty((S, len(lv)), np.float32) for lv in levels]
    maxq = 0
    n_it = int(math.ceil(math.log2(n_pool))) + 1
    inc01T = (incT > 0).astype(np.float32) if own_delta is not None else None
    for s0 in range(0, S, chunk):
        s1 = min(S, s0 + chunk)
        r = s1 - s0
        sc = Xs[s0:s1][:, cols] @ incT
        np.maximum(sc, 0, out=sc)
        smax = float(sc.max())
        scale = 100.0 if smax * 100 < 65000 else math.floor(65000 / smax)  # 0.01-point keys unless a score tops 650
        q = np.rint(sc * scale).astype(np.uint32)
        del sc
        mq = int(q.max())
        maxq = max(maxq, smax)
        assert mq < 65536, f"score overflow {smax}"
        q <<= 16
        q |= idx_arr[None, :]
        q.sort(axis=1)
        q = q[:, ::-1]
        idx_sorted = (q & 0xFFFF).astype(np.int32)
        sc_sorted = (q >> 16).astype(np.float32) / scale
        del q
        if own_delta is None:
            CO = np.cumsum(cO[idx_sorted], axis=1, dtype=np.int32)
            CC = np.cumsum(cC[idx_sorted], axis=1, dtype=np.int32)
            ZO = np.full((r, 1), float(n_opt))
            ZC = np.full((r, 1), float(n_cas))
        else:  # this scenario's ownership shock reweights every field lineup by exp(sum of its players' shocks)
            lm = own_delta[s0:s1] @ inc01T
            lm -= lm.max(1, keepdims=True)
            np.exp(lm, out=lm)
            ms = np.take_along_axis(lm, idx_sorted, axis=1)
            del lm
            CO = np.cumsum(ms * cO[idx_sorted], axis=1, dtype=np.float32)
            CC = np.cumsum(ms * cC[idx_sorted], axis=1, dtype=np.float32)
            del ms
            ZO = CO[:, -1:].copy()
            ZC = CC[:, -1:].copy()
        del idx_sorted
        for ci, (wopt, lv) in enumerate(zip(wopts, levels)):
            a_, b_ = wopt / ZO, (1 - wopt) / ZC
            tgt = np.broadcast_to(np.asarray(lv, np.float64)[None, :], (r, len(lv)))
            lo = np.zeros((r, len(lv)), np.int64)
            hi = np.full((r, len(lv)), n_pool - 1, np.int64)
            for _ in range(n_it):
                mid = (lo + hi) // 2
                val = a_ * np.take_along_axis(CO, mid, axis=1) + b_ * np.take_along_axis(CC, mid, axis=1)
                ge = val >= tgt - 1e-12
                hi = np.where(ge, mid, hi)
                lo = np.where(ge, lo, np.minimum(mid + 1, n_pool - 1))
            outs[ci][s0:s1] = np.take_along_axis(sc_sorted, hi, axis=1)
        del CO, CC, sc_sorted
    return outs, round(maxq, 2)


# ============================================================================ hit bitsets and greedy coverage
def hit_bits(Xs, cols, cand_inc, T_list, chunk=2048):
    S = Xs.shape[0]
    K = cand_inc.shape[0]
    nbytes = ((S + 63) // 64) * 8
    H = [np.zeros((K, nbytes), np.uint8) for _ in T_list]
    incT = np.ascontiguousarray(cand_inc.T)
    for s0 in range(0, S, chunk):
        s1 = min(S, s0 + chunk)
        sc = Xs[s0:s1][:, cols] @ incT
        for h, T in zip(H, T_list):
            pb = np.packbits(sc >= T[s0:s1, None], axis=0, bitorder="little")
            h[:, s0 // 8: s0 // 8 + pb.shape[0]] = pb.T
    return [h.view(np.uint64) for h in H]


def popc(a):
    return np.bitwise_count(a).sum(axis=-1, dtype=np.int64)


def bits_to_bool(words, S):
    return np.unpackbits(words.view(np.uint8), bitorder="little")[:S].astype(bool)


def bool_to_words(b):
    S = len(b)
    nbytes = ((S + 63) // 64) * 8
    out = np.zeros(nbytes, np.uint8)
    pb = np.packbits(b, bitorder="little")
    out[:len(pb)] = pb
    return out.view(np.uint64)


def greedy_single(H1, n, mask=None, allowed=None):
    K, W = H1.shape
    allowed = np.arange(K) if allowed is None else np.asarray(allowed)
    Hm = H1[allowed] if mask is None else (H1[allowed] & mask)
    gains = popc(Hm)
    cov = np.zeros(W, np.uint64)
    chosen = []
    heap = list(zip((-gains).tolist(), range(len(allowed))))
    heapq.heapify(heap)
    while len(chosen) < n and heap:
        _, i = heapq.heappop(heap)
        gnow = int(popc(Hm[i] & ~cov))
        if not heap or gnow >= -heap[0][0]:
            chosen.append(i)
            cov |= Hm[i]
        else:
            heapq.heappush(heap, (-gnow, i))
    return [int(allowed[i]) for i in chosen], int(popc(cov))


def greedy_weighted(H1, f, n, S):
    """Greedy for sum over scenarios of max over chosen hitting lineups of f[L] (duplication-adjusted goal 1).
    f[L] = E[1/(1+D_L)], D_L ~ Binomial(N', q_L). Facility-location style objective, still submodular."""
    K, W = H1.shape
    unc = bool_to_words(np.ones(S, bool))
    levels = []  # (value, words of scenarios whose current best value == value)
    chosen = []
    for _ in range(n):
        gain = f * popc(H1 & unc)
        for v, m in levels:
            gain += np.maximum(f - v, 0) * popc(H1 & m)
        if chosen:
            gain[chosen] = -1
        j = int(np.argmax(gain))
        hj = H1[j]
        moved = hj & unc
        unc = unc & ~hj
        new = []
        for v, m in levels:
            if v < f[j]:
                moved |= m & hj
                m = m & ~hj
            new.append((v, m))
        new.append((float(f[j]), moved))
        levels = new
        chosen.append(j)
    value = sum(v * int(popc(m)) for v, m in levels) / S
    return chosen, value


def swap_search(H1, HC, start, g1star, eps, S, max_swaps=400, margin_k=0.0):
    """Best-improvement local search: accept the single lineup swap (any contest) that most lowers washout on this
    scenario set while every contest keeps G1_c >= (1 - eps) * G1*_c (counts on the same set). Stops when none helps."""
    nC = len(start)
    port = [list(p) for p in start]
    c1, cc = {}, {}

    def b1(c, L):
        if (c, L) not in c1:
            c1[(c, L)] = bits_to_bool(H1[c][L], S)
        return c1[(c, L)]

    def bc(c, L):
        if (c, L) not in cc:
            cc[(c, L)] = bits_to_bool(HC[c][L], S)
        return cc[(c, L)]
    cnt1 = [np.zeros(S, np.int16) for _ in range(nC)]
    cntW = np.zeros(S, np.int16)
    for c in range(nC):
        for L in port[c]:
            cnt1[c] += b1(c, L)
            cntW += bc(c, L)
    def se_rel(c):  # relative Monte Carlo SE of G1* on this scenario set
        p_ = max(g1star[c], 1) / S
        return math.sqrt(p_ * (1 - p_) / S) / p_
    thr = [0 if eps >= 1 else math.ceil((1 - eps + margin_k * se_rel(c)) * g1star[c] - 1e-9) for c in range(nC)]
    curW = int((cntW > 0).sum())
    swaps = 0
    while swaps < max_swaps:
        best_gain, best = 0, None
        for c in range(nC):
            used = np.zeros(H1[c].shape[0], bool)
            used[port[c]] = True
            for pos, e in enumerate(port[c]):
                covWm = bool_to_words((cntW - bc(c, e)) > 0)
                gain = popc(HC[c] | covWm) - curW
                gain[used] = -1
                if gain.max() <= best_gain:
                    continue
                cand = np.nonzero(gain > best_gain)[0]
                cov1m = bool_to_words((cnt1[c] - b1(c, e)) > 0)
                newG1 = popc(H1[c][cand] | cov1m)
                ok = newG1 >= thr[c]
                if not ok.any():
                    continue
                cand, g_, n1 = cand[ok], gain[cand[ok]], newG1[ok]
                j = np.lexsort((n1, g_))[-1]
                best_gain, best = int(g_[j]), (c, pos, int(cand[j]))
        if best is None:
            break
        c, pos, L = best
        e = port[c][pos]
        cnt1[c] += b1(c, L).astype(np.int16) - b1(c, e).astype(np.int16)
        cntW += bc(c, L).astype(np.int16) - bc(c, e).astype(np.int16)
        port[c][pos] = L
        curW = int((cntW > 0).sum())
        swaps += 1
    g1 = np.array([int((cnt1[c] > 0).sum()) for c in range(nC)], float)
    return port, dict(swaps=swaps, pw=(S - curW) / S, g1_cnt=g1, ratio=g1 / np.maximum(np.asarray(g1star, float), 1))


class Selector:
    """Holds per-contest hit bitsets on the selection scenario set and runs the goal-1 / washout greedy."""

    def __init__(self, contests, H1, HC, S):
        self.contests = contests
        self.H1, self.HC = H1, HC
        self.S = S
        self.W = H1[0].shape[1]
        self.cnt1 = [popc(h) for h in H1]
        self.cntc = [popc(h) for h in HC]
        self.nC = len(contests)
        self.singles = [i for i, c in enumerate(contests) if c["n"] == 1]
        self.g1star_cnt = None

    def g1star(self):
        res = []
        for ci, c in enumerate(self.contests):
            ch, cov = greedy_single(self.H1[ci], c["n"])
            res.append((ch, cov))
        self.g1star_cnt = np.array([max(1, r[1]) for r in res], dtype=float)
        return res

    def joint(self, lam, mu=None, batch=64):
        S = self.S
        mu = np.ones(self.nC) if mu is None else mu
        a = mu / self.g1star_cnt
        b = lam / S  # objective: sum_c G1_c/G1*_c + lam * (1 - W), (1 - W) = covered scenarios / S
        tbs = [1e-9 * (self.cnt1[ci] + self.cntc[ci]) / S for ci in range(self.nC)]
        heap = []
        for ci in range(self.nC):
            g = a[ci] * self.cnt1[ci] + b * self.cntc[ci] + tbs[ci]
            heap.extend(zip((-g).tolist(), [ci] * len(g), range(len(g))))
        heapq.heapify(heap)
        cov1 = [np.zeros(self.W, np.uint64) for _ in range(self.nC)]
        covW = np.zeros(self.W, np.uint64)
        cap = [c["n"] for c in self.contests]
        chosen = [[] for _ in range(self.nC)]
        chosen_set = [set() for _ in range(self.nC)]
        need = sum(cap)
        picks = 0
        evals = 0
        bsize = batch
        while picks < need and heap:
            bt = []
            while heap and len(bt) < bsize:
                _, ci, i = heapq.heappop(heap)
                if len(chosen[ci]) >= cap[ci] or i in chosen_set[ci]:
                    continue
                bt.append((ci, i))
            if not bt:
                break
            ex = np.empty(len(bt))
            byc = {}
            for k, (ci, i) in enumerate(bt):
                byc.setdefault(ci, []).append(k)
            for ci, ks in byc.items():
                rows = np.array([bt[k][1] for k in ks])
                g1 = popc(self.H1[ci][rows] & ~cov1[ci])
                gc = popc(self.HC[ci][rows] & ~covW)
                ex[ks] = a[ci] * g1 + b * gc + tbs[ci][rows]
            evals += len(bt)
            j = int(np.argmax(ex))
            nxt = -heap[0][0] if heap else -np.inf
            if ex[j] >= nxt:
                ci, i = bt[j]
                chosen[ci].append(i)
                chosen_set[ci].add(i)
                cov1[ci] |= self.H1[ci][i]
                covW |= self.HC[ci][i]
                picks += 1
                bsize = batch
                for k, (cj, ij) in enumerate(bt):
                    if k != j:
                        heapq.heappush(heap, (-ex[k], cj, ij))
            else:
                bsize = min(bsize * 2, 8192)  # many stale bounds at once (e.g. washout term just collapsed): widen the batch
                for k, (cj, ij) in enumerate(bt):
                    heapq.heappush(heap, (-ex[k], cj, ij))
        return chosen, evals

    def refine_singles(self, port, eps, passes=2):
        """Exact step for n=1 contests: among lineups with G1 >= (1-eps) G1*, pick the one covering the most
        still-uncovered washout scenarios given every other entry (tie-break: higher G1)."""
        port = [list(p) for p in port]
        for _ in range(passes):
            for ci in self.singles:
                covO = np.zeros(self.W, np.uint64)
                for cj in range(self.nC):
                    if cj != ci and port[cj]:
                        covO |= np.bitwise_or.reduce(self.HC[cj][port[cj]], axis=0)
                thr = math.ceil((1 - eps) * self.g1star_cnt[ci] - 1e-9)
                elig = np.nonzero(self.cnt1[ci] >= thr)[0]
                if len(elig) == 0:
                    continue
                gc = popc(self.HC[ci][elig] & ~covO)
                best = elig[np.lexsort((self.cnt1[ci][elig], gc))[-1]]
                port[ci] = [int(best)]
        return port

    def stats(self, port):
        covW = np.zeros(self.W, np.uint64)
        g1 = []
        for ci in range(self.nC):
            if port[ci]:
                g1.append(int(popc(np.bitwise_or.reduce(self.H1[ci][port[ci]], axis=0))))
                covW |= np.bitwise_or.reduce(self.HC[ci][port[ci]], axis=0)
            else:
                g1.append(0)
        g1 = np.array(g1, float)
        return dict(ratio=g1 / self.g1star_cnt, g1=g1 / self.S, pw=(self.S - int(popc(covW))) / self.S)


# ============================================================================ evaluation helpers
def exceed_from_grid(grid, x):
    """Interpolated exceedance P(opponent >= x) from stored tail quantiles (grid[s, j] = score at exceedance GRID[j])."""
    L = len(GRID)
    j = (grid <= x[:, None]).sum(1) - 1
    e = np.empty(len(x))
    lo = j < 0
    hi = j >= L - 1
    mid = ~lo & ~hi
    jm = j[mid]
    rows = np.nonzero(mid)[0]
    q0 = grid[rows, jm]
    q1 = grid[rows, jm + 1]
    le0, le1 = np.log(GRID[jm]), np.log(GRID[jm + 1])
    f = np.where(q1 > q0, (x[mid] - q0) / np.maximum(q1 - q0, 1e-9), 0.0)
    e[mid] = np.exp(le0 + f * (le1 - le0))
    e[lo] = GRID[0]
    rh = np.nonzero(hi)[0]
    e[hi] = np.where(x[hi] > grid[rh, -1] + 0.005, 0.0, GRID[-1])
    return e


# ============================================================================ main pipeline
def build_contests(n_sd):
    cs = [dict(name="C_SE150", slate="classic", N=150, n=1, wopt=0.35), dict(name="C_SE2000", slate="classic", N=2000, n=1, wopt=0.30),
          dict(name="C_3max500", slate="classic", N=500, n=3, wopt=0.35), dict(name="C_20max3000", slate="classic", N=3000, n=20, wopt=0.40),
          dict(name="C_150max8000", slate="classic", N=8000, n=60, wopt=0.45)]
    for g in range(n_sd):
        cs.append(dict(name=f"SD{g}_SE50", slate=f"sd{g}", N=50, n=1, wopt=0.30))
        cs.append(dict(name=f"SD{g}_20max1200", slate=f"sd{g}", N=1200, n=10, wopt=0.35))
    for c in cs:
        c["k"] = max(1, int(math.floor(0.01 * c["N"])))
        c["m"] = int(round(0.22 * c["N"]))
        c["Nopp"] = c["N"] - c["n"]
        c["e1"] = (c["k"] - 1.0 / 3.0) / c["Nopp"]
        c["ec"] = (c["m"] - 1.0 / 3.0) / c["Nopp"]
    return cs


def caps_for_total(contests, T):
    """Entry caps that scale the multi-entry contests to reach about T entries in total (single-entry stay 1)."""
    maxn = {c["name"]: (1 if c["n"] == 1 else (150 if "150max" in c["name"] else (20 if "20max" in c["name"] else 3))) for c in contests}
    best = None
    for f in np.arange(0.0, 4.001, 0.01):
        caps = {}
        for c in contests:
            nm = c["name"]
            if c["n"] == 1:
                caps[nm] = 1
                continue
            lo = 2 if nm in ("C_150max8000", "C_20max3000") else 1
            caps[nm] = int(min(maxn[nm], max(lo, round(c["n"] * f))))
        tot = sum(caps.values())
        if best is None or abs(tot - T) < abs(best[1] - T):
            best = (caps, tot, round(float(f), 2))
    return best


def share_factor(q, n_opp):
    """E[1/(1+D)] for D ~ Binomial(n_opp, q): (1 - (1-q)^(n_opp+1)) / ((n_opp+1) q); equals 1 when q = 0."""
    q = np.asarray(q, float)
    out = np.ones_like(q)
    m = q > 1e-15
    n1 = n_opp + 1
    out[m] = -np.expm1(n1 * np.log1p(-q[m])) / (n1 * q[m])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=8)
    ap.add_argument("--showdowns", type=int, default=3)
    ap.add_argument("--S", type=int, default=10000, help="selection set A = S/2, validation set V = S/2, held-out test set B = S")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20261020)
    ap.add_argument("--tag", default="night")
    ap.add_argument("--belief-err", type=int, default=1)
    ap.add_argument("--berr-scale", type=float, default=1.0, help="multiplies every belief-error sd (sensitivity runs)")
    ap.add_argument("--edge-sd", type=float, default=0.0, help="engine-vs-public disagreement: our_mean = public_mean x lognormal(0, edge_sd); 0 = off")
    ap.add_argument("--edge-sel", default="mix", choices=["mix", "one"], help="selection sets A and V drawn with w ~ Beta(2,3) (mix) or w = 1 (one, overconfident engine)")
    ap.add_argument("--late-news", action="store_true")
    ap.add_argument("--n-so", type=int, default=3200, help="Classic scenario-optimal solves")
    ap.add_argument("--n-mv", type=int, default=1300, help="Classic mean/ownership-penalty solves")
    ap.add_argument("--sd-keep", type=int, default=20000)
    ap.add_argument("--max-swaps", type=int, default=400)
    ap.add_argument("--skip-simtiming", action="store_true")
    a = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    os.makedirs(OUTDIR, exist_ok=True)
    base = os.path.join(OUTDIR, f"{stamp}_{a.tag}_be{a.belief_err if a.berr_scale == 1 else f'{a.belief_err}x{a.berr_scale:g}'}" + (f"_edge{a.edge_sd:g}{a.edge_sel}" if a.edge_sd > 0 else "") + f"_S{a.S}")
    load0 = system_load(3.0)
    meta = dict(stamp=stamp, args=vars(a), python=sys.version, numpy=np.__version__, cpu_count=psutil.cpu_count(), cpu_count_physical=psutil.cpu_count(logical=False),
                ram_gb=round(psutil.virtual_memory().total / 2**30, 1), load_before=load0, simp=SIMP, sd_own=SD_OWN,
                note="synthetic data; THROWAWAY SPIKE; numbers are a BET until real slates")
    rec = Recorder(base + ".json", base + ".txt", meta)
    rec.log(f"night spike {a.tag} S={a.S} games={a.games} showdowns={a.showdowns} workers={a.workers} belief_err={a.belief_err}")
    rec.log("load before:", json.dumps(load0))
    mem = MemSampler()
    mem.start()
    T_START = time.perf_counter()
    S = a.S
    SA = S // 2
    SV = S - SA
    SB = S
    rng = np.random.default_rng(a.seed + 1)

    # ---------------------------------------------------------------- night, pilot projections, salaries
    with rec.step("setup_pool_pilot_projections"):
        night = make_night(a.games, a.seed)
        if a.belief_err:
            k_ = a.berr_scale
            night["berr"] = dict(team_sd=0.08 * k_, starter_sd=0.12 * k_, bench_sd=0.18 * k_, own_sd=0.25 * k_)
        if a.edge_sd > 0:
            rng_d = np.random.default_rng(a.seed + 999)
            night["edge"] = dict(d=np.exp(rng_d.normal(0, a.edge_sd, night["n"])), a=2.0, b=3.0, w_fixed=None)
        ed_keep = night.get("edge")
        night["edge"] = None  # pilot = public view (what DK prices and the field see)
        pilot = sim_night(night, 6000, a.seed + 77)
        night["edge"] = ed_keep
        proj = pilot["X"].mean(0).astype(np.float64)
        proj_eng = proj * ed_keep["d"] if ed_keep else proj  # engine view: public x our private deviations
        sal = np.clip(np.round((proj * 200 + rng.normal(0, 350, night["n"])) / 100) * 100, 3000, 11500)
        sal_sd = np.clip(np.round((proj * 250 + rng.normal(0, 450, night["n"])) / 100) * 100, 1000, 16000)
        covs = {g: np.cov(pilot["X"][:, night["game_players"][g]].T) for g in range(a.showdowns)}
    A = night["arr"]
    contests = build_contests(a.showdowns)
    names = [c["name"] for c in contests]
    if night.get("edge") is not None:
        dd = night["edge"]["d"]
        rec.put("edge_layer", dict(edge_sd=a.edge_sd, selection_sets=a.edge_sel, w_dist="Beta(2,3)", d_min=round(float(dd.min()), 3), d_max=round(float(dd.max()), 3),
                                   d_sd_log=round(float(np.log(dd).std()), 4), corr_proj_eng_vs_pub=round(float(np.corrcoef(proj, proj_eng)[0, 1]), 4)))
    rec.put("night", dict(games=night["games"], n_players=night["n"], belief_err=night.get("berr"),
                          quest=[dict(q, player_proj=round(proj[q["player"]], 2), beneficiary_proj=round(proj[q["beneficiary"]], 2)) for q in night["quest"]],
                          contests=contests, total_entries=sum(c["n"] for c in contests), S_A=SA, S_V=SV, S_B=SB,
                          players=[dict(id=i, team=int(A["team"][i]), game=int(A["game"][i]), pos=pos_str(int(A["pos"][i])), tier=str(A["tier"][i]),
                                        base_min=round(float(A["base_min"][i]), 1), proj=round(float(proj[i]), 2), salary=int(sal[i]), salary_sd=int(sal_sd[i]))
                                   for i in range(night["n"])]))

    # ---------------------------------------------------------------- simulate selection set A and validation set V
    if night.get("edge") is not None and a.edge_sel == "one":
        night["edge"]["w_fixed"] = 1.0  # overconfident engine: its own scenarios assume its view is the truth
    with rec.step("sim_A_V"):
        simA = sim_night(night, SA, a.seed)
        simV = sim_night(night, SV, a.seed + 500)
    if night.get("edge") is not None:
        night["edge"]["w_fixed"] = None  # the test set B always draws w ~ Beta(2, 3)
    XA, XV = simA["X"], simV["X"]
    diag = sim_diagnostics(night, simA, proj)
    rec.put("sim_sanity", diag)
    rec.log("sim sanity:", json.dumps({k: diag[k] for k in ("star", "role_player", "beneficiary_when_q0_active", "beneficiary_when_q0_out", "top_big")}))
    rec.log("corr teammates/opponents:", diag["corr_teammates_rotation_mean"], diag["corr_opponents_rotation_mean"], "OT", diag["ot_rate_overall"])
    simt = {}
    for s_ in (() if a.skip_simtiming else (10000, 30000)):
        t0 = time.perf_counter()
        _tmp = sim_night(night, s_, a.seed + 5)
        simt[s_] = round(time.perf_counter() - t0, 2)
        del _tmp
    rec.put("sim_timing_s_by_S", simt)
    rec.log("sim timing", simt)

    # ---------------------------------------------------------------- field
    with rec.step("pool_spawn"):
        solver = SolverPool(night, sal, a.workers, rec)
    with rec.step("field_classic_milp"):
        z = rng.standard_normal((2000, night["n"]))
        objs = np.maximum(0, proj[None, :] * (1 + 0.15 * z))
        opt_l, opt_t = solver.solve(objs)
    bad = sum(1 for L in opt_l if not validate_classic(night, sal, L))
    with rec.step("field_classic_sampler"):
        cas_L, cas_tries = classic_sampler(night, proj, sal, 20000, rng)

    def make_cpool(opt_l_, cas_L_):
        opt_arr = np.array([L for L in opt_l_ if L is not None])
        u_all, inv = np.unique(np.vstack([opt_arr, cas_L_]), axis=0, return_inverse=True)
        inv = inv.ravel()
        cp = dict(lineups=u_all, cnt_opt=np.bincount(inv[:len(opt_arr)], minlength=len(u_all)), cnt_cas=np.bincount(inv[len(opt_arr):], minlength=len(u_all)),
                  n_opt=len(opt_arr), n_cas=len(cas_L_))
        inc = np.zeros((len(u_all), night["n"]), np.float32)
        for k in range(8):
            inc[np.arange(len(u_all)), u_all[:, k]] = 1.0
        return cp, inc
    cpool, cpool_inc = make_cpool(opt_l, cas_L)
    own = {}
    for c in contests:
        if c["slate"] == "classic":
            c["w"] = contest_weights(cpool, c["wopt"])
            own[c["name"]] = (c["w"][:, None] * cpool_inc).sum(0) * 100
    own_pct = own["C_150max8000"]
    top_own = np.argsort(-own_pct)[:15]
    rec.put("field_classic", dict(milp_solves=len(opt_l), milp_invalid_or_failed=bad, milp_wall_s=rec.data["steps"]["field_classic_milp"]["wall_s"],
                                  milp_solve_ms_median=round(float(np.median(opt_t)) * 1000, 2), milp_solve_ms_p95=round(float(np.percentile(opt_t, 95)) * 1000, 2),
                                  opt_unique=int((cpool["cnt_opt"] > 0).sum()), sampler_tries=cas_tries, sampler_accept_rate=round(len(cas_L) / cas_tries, 4),
                                  cas_unique=int((cpool["cnt_cas"] > 0).sum()), pool_unique=len(cpool["lineups"]),
                                  implied_ownership_150max_top15=[dict(player=int(i), pos=pos_str(int(A["pos"][i])), proj=round(proj[i], 1), salary=int(sal[i]),
                                                                       own_pct=round(float(own_pct[i]), 1), own_pct_SE150=round(float(own["C_SE150"][i]), 1)) for i in top_own],
                                  ownership_sum_pct=round(float(own_pct.sum()), 1)))
    rec.log(f"classic field: {len(opt_l)} MILP ({bad} bad) median {np.median(opt_t) * 1000:.1f} ms; sampler accept {len(cas_L) / cas_tries:.3f}; pool unique {len(cpool['lineups'])}")
    sd_pools = {}
    with rec.step("field_showdown"):
        for g in range(a.showdowns):
            sd_pools[g] = field_showdown(night, g, proj, sal_sd, rng)
    sd_field_rep = {}

    def sd_weights(g):
        fp = sd_pools[g]
        fp["inc"] = sd_incidence(fp["lineups"], len(fp["cols"]))
        for c in contests:
            if c["slate"] == f"sd{g}":
                c["w"] = contest_weights(fp, c["wopt"])
    for g in range(a.showdowns):
        sd_weights(g)
        fp = sd_pools[g]
        cols = fp["cols"]
        c_big = [c for c in contests if c["slate"] == f"sd{g}" and c["n"] > 1][0]
        c_se = [c for c in contests if c["slate"] == f"sd{g}" and c["n"] == 1][0]
        dup_big = c_big["Nopp"] * c_big["w"]
        o = np.argsort(-dup_big)[:10]
        cpt_own = np.zeros(len(cols))
        util_own = np.zeros(len(cols))
        np.add.at(cpt_own, fp["lineups"][:, 0], c_big["w"])
        for k in range(1, 6):
            np.add.at(util_own, fp["lineups"][:, k], c_big["w"])
        sd_field_rep[g] = dict(n_legal=fp["n_legal"], enumerate_s=round(fp["t_enum"], 3), pool_unique=len(fp["ids"]), opt_unique=int((fp["cnt_opt"] > 0).sum()),
                               cas_unique=int((fp["cnt_cas"] > 0).sum()),
                               top10_expected_dups_20max=[dict(cpt=int(cols[fp["lineups"][i, 0]]), utils=[int(cols[u]) for u in fp["lineups"][i, 1:]], expected_copies=round(float(dup_big[i]), 2),
                                                               expected_copies_SE50=round(float(c_se["Nopp"] * c_se["w"][i]), 3)) for i in o],
                               share_of_20max_field_in_lineups_with_ge2_expected_copies=round(float(c_big["w"][dup_big >= 2].sum()), 3),
                               cpt_own_top5=[dict(player=int(cols[i]), pct=round(float(cpt_own[i] * 100), 1)) for i in np.argsort(-cpt_own)[:5]],
                               util_own_top8=[dict(player=int(cols[i]), pct=round(float(util_own[i] * 100), 1)) for i in np.argsort(-util_own)[:8]])
    rec.put("field_showdown", sd_field_rep)

    # ---------------------------------------------------------------- thresholds (chunked; ownership shock per slate per scenario when belief layer on)
    def compute_thresholds(simx, which=None):
        Xs = simx["X"]
        res = {}
        cl = [c for c in contests if c["slate"] == "classic" and (which is None or c["name"] in which)]
        if cl:
            outs, mx = thresholds(Xs, np.arange(night["n"]), cpool_inc, cpool["cnt_opt"], cpool["cnt_cas"], [c["wopt"] for c in cl],
                                  [np.concatenate([[c["e1"], c["ec"]], GRID]) for c in cl], chunk=512, own_delta=simx["own"].get("classic"))
            for c, o in zip(cl, outs):
                res[c["name"]] = dict(T1=o[:, 0].copy(), Tc=o[:, 1].copy(), grid=o[:, 2:].copy(), max_field_score=mx)
        for g in range(a.showdowns):
            sl = [c for c in contests if c["slate"] == f"sd{g}" and (which is None or c["name"] in which)]
            if not sl:
                continue
            fp = sd_pools[g]
            outs, mx = thresholds(Xs, fp["cols"], fp["inc"], fp["cnt_opt"], fp["cnt_cas"], [c["wopt"] for c in sl],
                                  [np.concatenate([[c["e1"], c["ec"]], GRID]) for c in sl], chunk=512, own_delta=simx["own"].get(f"sd{g}"))
            for c, o in zip(sl, outs):
                res[c["name"]] = dict(T1=o[:, 0].copy(), Tc=o[:, 1].copy(), grid=o[:, 2:].copy(), max_field_score=mx)
        return res
    cl_names = {c["name"] for c in contests if c["slate"] == "classic"}
    sd_names = {c["name"] for c in contests if c["slate"] != "classic"}
    with rec.step("thresholds_AV_classic"):
        thrA = compute_thresholds(simA, cl_names)
        thrV = compute_thresholds(simV, cl_names)
    with rec.step("thresholds_AV_showdown"):
        thrA.update(compute_thresholds(simA, sd_names))
        thrV.update(compute_thresholds(simV, sd_names))
    rec.put("thresholds_A_summary", {k: dict(T1_mean=round(float(v["T1"].mean()), 1), T1_p10=round(float(np.percentile(v["T1"], 10)), 1), T1_p90=round(float(np.percentile(v["T1"], 90)), 1),
                                             Tc_mean=round(float(v["Tc"].mean()), 1), Tc_p10=round(float(np.percentile(v["Tc"], 10)), 1), Tc_p90=round(float(np.percentile(v["Tc"], 90)), 1),
                                             max_field_score=v["max_field_score"]) for k, v in thrA.items()})

    # ---------------------------------------------------------------- candidates
    alphas = [0.0, 0.05, 0.1, 0.2, 0.3]
    sigs = [0.03, 0.08, 0.15]
    with rec.step("cand_classic_milp"):
        src = rng.choice(SA, size=min(a.n_so, SA), replace=False)
        objs_so = XA[src].astype(np.float64)
        zz = rng.standard_normal((a.n_mv, night["n"]))
        objs_mv = np.array([proj_eng * (1 + sigs[(i // 5) % 3] * zz[i]) - alphas[i % 5] * own_pct for i in range(a.n_mv)])
        lin, ct = solver.solve(np.vstack([objs_so, objs_mv]))
    srcs = list(src) + [-1 - (i % 5) for i in range(a.n_mv)]
    cand = {}
    bad_c = 0
    for L, s_ in zip(lin, srcs):
        if not validate_classic(night, sal, L):
            bad_c += 1
            continue
        if L not in cand:
            cand[L] = int(s_)
    cl_lineups = np.array(list(cand.keys()))
    cl_src = np.array(list(cand.values()))
    with rec.step("pool_close"):
        worker_rss = solver.worker_rss_mb()
        solver.close()
    rec.put("cand_classic", dict(solves=len(lin), invalid=bad_c, unique=len(cl_lineups), from_scenarios=int((cl_src >= 0).sum()), from_mean_variants=int((cl_src < 0).sum()),
                                 solve_ms_median=round(float(np.median(ct)) * 1000, 2), solve_ms_p95=round(float(np.percentile(ct, 95)) * 1000, 2), worker_rss_total_mb=worker_rss))
    rec.log(f"classic candidates: {len(lin)} solves -> {len(cl_lineups)} unique, invalid {bad_c}; worker RSS {worker_rss} MB")

    def make_cl_inc(L_):
        inc = np.zeros((len(L_), night["n"]), np.float32)
        for k in range(8):
            inc[np.arange(len(L_)), L_[:, k]] = 1.0
        return inc
    cl_inc = make_cl_inc(cl_lineups)
    sd_cand = {}

    def screen_sd(g, mu, cov, ban_local=None):
        fp = sd_pools[g]
        meanL, sdL = sd_mean_sd(fp["L_all"], mu, cov)
        if ban_local is not None:
            meanL = np.where((fp["L_all"] == ban_local).any(1), -1e9, meanL)
        chosen, seen = [], set()
        per = int(a.sd_keep * 0.4)
        for arr_ in (np.argsort(-(meanL + 2.5 * sdL))[:per], np.argsort(-(meanL + 0.5 * sdL))[:per], np.argsort(-(meanL + 1.5 * sdL))):
            for i in arr_:
                if len(chosen) >= a.sd_keep:
                    break
                if i not in seen:
                    seen.add(i)
                    chosen.append(i)
        ids = np.array(chosen)
        sd_cand[g] = dict(lineups=fp["L_all"][ids], inc=sd_incidence(fp["L_all"][ids], len(fp["cols"])), cols=fp["cols"], legal_ids=ids)
    with rec.step("cand_showdown_screen"):
        for g in range(a.showdowns):
            screen_sd(g, proj_eng[sd_pools[g]["cols"]], covs[g])

    # duplication factor f_L = E[1/(1+D_L)] per contest and candidate (D_L from the contest's field weights)
    def dup_factors():
        fac = {}
        cl_index = {tuple(int(x) for x in r_): i for i, r_ in enumerate(cpool["lineups"])}
        cl_pos = np.array([cl_index.get(tuple(int(x) for x in L), -1) for L in cl_lineups])
        for c in contests:
            if c["slate"] == "classic":
                q = np.where(cl_pos >= 0, c["w"][np.maximum(cl_pos, 0)], 0.0)
            else:
                g = int(c["slate"][2:])
                ids_pool = sd_pools[g]["ids"]
                ids_c = sd_cand[g]["legal_ids"]
                pos = np.clip(np.searchsorted(ids_pool, ids_c), 0, len(ids_pool) - 1)
                q = np.where(ids_pool[pos] == ids_c, c["w"][pos], 0.0)
            fac[c["name"]] = dict(q=q, f=share_factor(q, c["Nopp"]))
        return fac
    dupf = dup_factors()

    # ---------------------------------------------------------------- hit bitsets
    def build_bits(Xs, thr, which=None, only_t1=False):
        H1, HC = {}, {}
        cl = [c for c in contests if c["slate"] == "classic" and (which is None or c["name"] in which)]
        if cl:
            Ts = [thr[c["name"]]["T1"] for c in cl] + ([] if only_t1 else [thr[c["name"]]["Tc"] for c in cl])
            hs = hit_bits(Xs, np.arange(night["n"]), cl_inc, Ts)
            for i, c in enumerate(cl):
                H1[c["name"]] = hs[i]
                if not only_t1:
                    HC[c["name"]] = hs[len(cl) + i]
        for g in range(a.showdowns):
            sl = [c for c in contests if c["slate"] == f"sd{g}" and (which is None or c["name"] in which)]
            if not sl:
                continue
            Ts = [thr[c["name"]]["T1"] for c in sl] + ([] if only_t1 else [thr[c["name"]]["Tc"] for c in sl])
            hs = hit_bits(Xs, sd_cand[g]["cols"], sd_cand[g]["inc"], Ts, chunk=1024)
            for i, c in enumerate(sl):
                H1[c["name"]] = hs[i]
                if not only_t1:
                    HC[c["name"]] = hs[len(sl) + i]
        return H1, HC

    # entry profiles: 25, 50, specified, 200 entries
    spec_total = sum(c["n"] for c in contests)
    profiles = {}
    for T in (25, 50, spec_total, 200):
        caps, tot, f = caps_for_total(contests, T)
        if T == spec_total:
            caps, tot, f = {c["name"]: c["n"] for c in contests}, spec_total, 1.0
        profiles[f"n{tot}"] = dict(caps=caps, total=tot, f=f)
    spec_key = f"n{spec_total}"
    small_key = min(profiles, key=lambda k: profiles[k]["total"])
    maxcap = {n_: max(p["caps"][n_] for p in profiles.values()) for n_ in names}
    rec.put("profiles", profiles)
    rec.log("profiles:", {k: v["total"] for k, v in profiles.items()})

    with rec.step("bitsets_A"):
        H1A, _ = build_bits(XA, thrA, only_t1=True)
    order = {}
    with rec.step("select_greedy_A"):
        for c in contests:
            order[c["name"]], _ = greedy_single(H1A[c["name"]], maxcap[c["name"]])
    # counterfactual "one thesis everywhere" on A (spec and smallest profile)

    def over_mask(simx, g):
        tot = simx["team_pts"][:, 2 * g] + simx["team_pts"][:, 2 * g + 1]
        line = night["games"][g]["total"]
        rate = float((tot > line).mean())
        thr_ = line if abs(rate - 0.5) < 0.05 else float(np.median(tot))
        return tot > thr_, dict(game=g, line=line, over_rate_vs_line=round(rate, 3), cutoff_used=round(thr_, 1))
    m0, info0 = over_mask(simA, 0)
    mall = m0.copy()
    infos = [info0]
    for g in range(1, a.showdowns):
        mg, ig = over_mask(simA, g)
        mall &= mg
        infos.append(ig)
    theses = {"game0_over": m0, f"games0-{a.showdowns - 1}_all_over": mall}
    cf_ports = {}
    with rec.step("counterfactual_select"):
        for pk in (spec_key, small_key):
            for tname, msk in theses.items():
                mw = bool_to_words(msk)
                port = []
                for c in contests:
                    n_ = profiles[pk]["caps"][c["name"]]
                    allowed = None
                    if c["slate"] == "classic":
                        allowed = np.nonzero((cl_src >= 0) & np.isin(cl_src, np.nonzero(msk)[0]))[0]
                        if len(allowed) < n_:
                            allowed = None
                    ch, _ = greedy_single(H1A[c["name"]], n_, mask=mw, allowed=allowed)
                    port.append(ch)
                cf_ports[(pk, tname)] = port
    rec.put("counterfactual_clusters", dict(defs=infos, share_game0_over=round(float(m0.mean()), 3), share_all_over=round(float(mall.mean()), 3)))
    # duplication-adjusted goal 1 on A for every contest (spec entries)
    dup_ports = {}
    with rec.step("dup_adjusted_greedy"):
        for c in contests:
            if c["slate"] == "classic":  # exact duplicates are negligible in Classic (checked below via q), keep the raw greedy
                dup_ports[c["name"]] = list(order[c["name"]][:c["n"]])
            else:
                dup_ports[c["name"]], _ = greedy_weighted(H1A[c["name"]], dupf[c["name"]]["f"], c["n"], SA)
    del H1A

    with rec.step("bitsets_V"):
        H1d, HCd = build_bits(XV, thrV)
    rec.put("bitsets_V_mb", round((sum(h.nbytes for h in H1d.values()) + sum(h.nbytes for h in HCd.values())) / 2**20, 1))

    def start_port(caps):
        return [list(order[n_][:caps[n_]]) for n_ in names]

    def g1_counts(port, H1):
        return np.array([int(popc(np.bitwise_or.reduce(H1[n_][port[ci]], axis=0))) if port[ci] else 0 for ci, n_ in enumerate(names)], float)

    def run_frontier(pk, step_prefix, margin_k=0.0):
        caps = profiles[pk]["caps"]
        H1l = [H1d[n_] for n_ in names]
        HCl = [HCd[n_] for n_ in names]
        start = start_port(caps)
        g1star = g1_counts(start, H1d)
        _, st0 = swap_search(H1l, HCl, start, g1star, 0.0, SV, max_swaps=0)
        res = {"greedy": (start, dict(st0, secs=0.0))}
        port = start
        for eps in EPS_LIST + [1.0]:
            t0 = time.perf_counter()
            port, st = swap_search(H1l, HCl, port, g1star, eps, SV, max_swaps=a.max_swaps, margin_k=margin_k)
            st["secs"] = round(time.perf_counter() - t0, 2)
            res[f"eps_{eps:.2f}"] = (port, st)
            rec.log(f"[{pk}] eps {eps:.2f}: swaps {st['swaps']} pw_V {st['pw']:.5f} min ratio_V {st['ratio'].min():.4f} ({st['secs']} s)")
        return res, g1star

    with rec.step("select_swap_eps05_from_greedy"):  # the production setting (default insurance budget 5%) from the greedy start
        caps = profiles[spec_key]["caps"]
        start = start_port(caps)
        g1s_ = g1_counts(start, H1d)
        _, st05 = swap_search([H1d[n_] for n_ in names], [HCd[n_] for n_ in names], start, g1s_, 0.05, SV, max_swaps=a.max_swaps)
    rec.put("swap_eps05_from_greedy", dict(swaps=st05["swaps"], pw_V=st05["pw"], min_ratio_V=float(st05["ratio"].min())))
    with rec.step("select_swap_frontier_spec"):
        F_spec, g1s_spec = run_frontier(spec_key, "")
    with rec.step("select_swap_frontier_small"):
        F_small, g1s_small = run_frontier(small_key, "small_")
    with rec.step("select_swap_frontier_margin2"):  # safety margin: enforce epsilon minus 2 SE on V
        F_spec_m2, _ = run_frontier(spec_key, "", margin_k=2.0)
        F_small_m2, _ = run_frontier(small_key, "small_", margin_k=2.0)

    # ---------------------------------------------------------------- held-out test set B (spike only)
    with rec.step("evalB_sim"):
        simB = sim_night(night, SB, a.seed + 1000)
    XB = simB["X"]
    with rec.step("evalB_thresholds"):
        thrB = compute_thresholds(simB)
    from scipy.stats import binom

    def prof_of(caps):
        return [dict(c, n=int(caps[c["name"]]), Nopp=c["N"] - int(caps[c["name"]])) for c in contests]

    def lineup_scores(Xs, c, rows):
        if c["slate"] == "classic":
            return Xs @ cl_inc[rows].T
        g = int(c["slate"][2:])
        return Xs[:, sd_cand[g]["cols"]] @ sd_cand[g]["inc"][rows].T

    def evaluate(prof, port, Xs, thr, want_binom=True):
        Sx = Xs.shape[0]
        nocash_hit = np.ones(Sx, bool)
        nocash_bin = np.ones(Sx)
        per = {}
        for ci, c in enumerate(prof):
            rows = np.array(port[ci])
            sc = lineup_scores(Xs, c, rows)
            Bc = sc.max(1)
            t = thr[c["name"]]
            h1 = Bc >= t["T1"]
            hc = Bc >= t["Tc"]
            nocash_hit &= ~hc
            fL = dupf[c["name"]]["f"][rows]
            dup_val = np.where(sc >= t["T1"][:, None], fL[None, :], 0.0).max(1)
            d = dict(g1_hit=float(h1.mean()), cash_hit=float(hc.mean()), h1=h1, g1_dup=float(dup_val.mean()),
                     entry_cash=(sc >= t["Tc"][:, None]).mean(0).tolist())
            if want_binom:
                e = exceed_from_grid(t["grid"], Bc)
                p1 = binom.cdf(c["k"] - 1, c["Nopp"], e)
                pnc = 1 - binom.cdf(c["m"] - 1, c["Nopp"], e)
                nocash_bin *= pnc
                d.update(g1_binom=float(p1.mean()), cash_binom=float(1 - pnc.mean()), agree_scen=float(((p1 > 0.5) == h1).mean()))
            per[c["name"]] = d
        return dict(per=per, pw_hit=float(nocash_hit.mean()), pw_binom=float(nocash_bin.mean()) if want_binom else None, wash_vec=nocash_hit)

    def port_shape(prof, port):
        cl_sets = {c["name"]: [set(int(x) for x in cl_lineups[i]) for i in port[ci]] for ci, c in enumerate(prof) if c["slate"] == "classic"}
        big = cl_sets["C_150max8000"]
        within = [len(big[i] & big[j]) for i in range(len(big)) for j in range(i + 1, len(big))]
        across = []
        nm = list(cl_sets)
        for x in range(len(nm)):
            for y in range(x + 1, len(nm)):
                for s1_ in cl_sets[nm[x]]:
                    for s2_ in cl_sets[nm[y]]:
                        across.append(len(s1_ & s2_))
        sd_across = []
        for g in range(a.showdowns):
            sl = [ci for ci, c in enumerate(prof) if c["slate"] == f"sd{g}"]
            sets_ = [[set(int(sd_cand[g]["cols"][u]) for u in sd_cand[g]["lineups"][i]) for i in port[ci]] for ci in sl]
            for s1_ in sets_[0]:
                for s2_ in sets_[1]:
                    sd_across.append(len(s1_ & s2_))
        expo = np.zeros(a.games)
        n_ent = 0
        for ci, c in enumerate(prof):
            for i in port[ci]:
                n_ent += 1
                gs = set(int(x) for x in A["game"][cl_lineups[i]]) if c["slate"] == "classic" else {int(c["slate"][2:])}
                for gg in gs:
                    expo[gg] += 1
        cl_ent = [i for ci, c in enumerate(prof) if c["slate"] == "classic" for i in port[ci]]
        return dict(overlap_within_150max=round(float(np.mean(within)), 3) if within else None, overlap_across_classic_contests=round(float(np.mean(across)), 3) if across else None,
                    overlap_sd_SE_vs_20max_same_game=round(float(np.mean(sd_across)), 3) if sd_across else None,
                    share_entries_exposed_by_game=[round(float(x / n_ent), 3) for x in expo], entries=n_ent,
                    share_classic_entries_ge3_from_game0=round(float(np.mean([np.sum(A["game"][cl_lineups[i]] == 0) >= 3 for i in cl_ent])), 3),
                    distinct_classic_lineups=len({tuple(cl_lineups[i]) for i in cl_ent}), classic_entries=len(cl_ent))

    def se_p(p, n):
        return math.sqrt(max(p * (1 - p), 0) / n)

    with rec.step("evalB_score_portfolios"):
        # (1) washout at eps 0 (greedy, pure goal 1) by entry profile
        prof_tab = {}
        for pk, pr in profiles.items():
            prof = prof_of(pr["caps"])
            port = start_port(pr["caps"])
            ev = evaluate(prof, port, XB, thrB)
            evv = evaluate(prof, port, XV, thrV, want_binom=False)
            cnt = int(ev["wash_vec"].sum())
            prof_tab[pk] = dict(entries=pr["total"], caps=pr["caps"], pw_B_hit=round(ev["pw_hit"], 6), pw_B_se=round(se_p(ev["pw_hit"], SB), 6), washout_scen_count_B=cnt,
                                pw_B_upper95=round(3.0 / SB, 6) if cnt == 0 else None, pw_B_binom=round(ev["pw_binom"], 6), pw_V_hit=round(evv["pw_hit"], 6),
                                per_contest_nocash_B={n_: round(1 - ev["per"][n_]["cash_hit"], 4) for n_ in names},
                                per_contest_g1_B={n_: round(ev["per"][n_]["g1_hit"], 5) for n_ in names},
                                per_entry_cash_mean_B=round(float(np.mean([x for n_ in names for x in ev["per"][n_]["entry_cash"]])), 4),
                                per_entry_cash_single_entry_B=round(float(np.mean([x for c in prof if c["n"] == 1 for x in ev["per"][c["name"]]["entry_cash"]])), 4),
                                per_entry_cash_by_contest_B={n_: round(float(np.mean(ev["per"][n_]["entry_cash"])), 4) for n_ in names})
        rec.put("washout_by_profile_eps0", prof_tab)
        rec.log("washout by profile (greedy, pure goal 1):", json.dumps({k: (v["entries"], v["pw_B_hit"], v["washout_scen_count_B"], v["pw_B_binom"]) for k, v in prof_tab.items()}))

        # (2) swap-search frontiers
        def frontier_table(pk, F, label):
            prof = prof_of(profiles[pk]["caps"])
            ports = {k: v[0] for k, v in F.items()}
            for (pk2, tname), p in cf_ports.items():
                if pk2 == pk:
                    ports[f"one_thesis_{tname}"] = p
            evB = {k: evaluate(prof, p, XB, thrB) for k, p in ports.items()}
            ref = evB["greedy"]
            ref0 = evB["eps_0.00"]
            tab = {}
            for k, ev in evB.items():
                ratios = np.array([ev["per"][n_]["g1_hit"] / max(ref["per"][n_]["g1_hit"], 1e-12) for n_ in names])
                dw0 = ev["wash_vec"].astype(float) - ref0["wash_vec"].astype(float)
                dwg = ev["wash_vec"].astype(float) - ref["wash_vec"].astype(float)
                stV = F[k][1] if k in F else None
                tab[k] = dict(pw_B=round(ev["pw_hit"], 6), pw_B_se=round(se_p(ev["pw_hit"], SB), 6), pw_B_binom=round(ev["pw_binom"], 6), washout_scen_count_B=int(ev["wash_vec"].sum()),
                              pw_diff_vs_eps0=round(float(dw0.mean()), 6), pw_diff_vs_eps0_se=round(float(dw0.std(ddof=1) / math.sqrt(SB)), 6),
                              pw_diff_vs_greedy=round(float(dwg.mean()), 6), pw_diff_vs_greedy_se=round(float(dwg.std(ddof=1) / math.sqrt(SB)), 6),
                              pw_V=None if stV is None else round(stV["pw"], 6), min_ratio_V=None if stV is None else round(float(stV["ratio"].min()), 4),
                              swaps=None if stV is None else stV["swaps"], secs=None if stV is None else stV["secs"],
                              g1_ratio_B={n_: round(r_, 4) for n_, r_ in zip(names, ratios)},
                              g1_ratio_B_paired_se={n_: round(float((ev["per"][n_]["h1"].astype(float) - ref["per"][n_]["h1"]).std(ddof=1) / math.sqrt(SB) / max(ref["per"][n_]["g1_hit"], 1e-12)), 4) for n_ in names},
                              g1_B={n_: round(ev["per"][n_]["g1_hit"], 5) for n_ in names},
                              mean_g1_loss_pct_B=round(float((1 - ratios).mean() * 100), 3), max_g1_loss_pct_B=round(float((1 - ratios).max() * 100), 3),
                              shape=port_shape(prof, ports[k]))
            pw0 = tab["eps_0.00"]["pw_B"]
            price = {}
            for e in (0.02, 0.05, 0.10, 0.20, 1.0):
                if f"eps_{e:.2f}" not in tab:
                    continue
                k = f"eps_{e:.2f}"
                red = (pw0 - tab[k]["pw_B"]) / pw0 * 100 if pw0 > 0 else None
                loss = tab[k]["mean_g1_loss_pct_B"] - tab["eps_0.00"]["mean_g1_loss_pct_B"]
                price[k] = dict(rel_washout_reduction_vs_eps0_pct=None if red is None else round(red, 2), mean_g1_given_up_vs_eps0_pct=round(loss, 3),
                                reduction_per_1pct_budget=None if (red is None or e >= 1) else round(red / (e * 100), 2),
                                reduction_per_1pct_realized_loss=(round(red / loss, 2) if (red is not None and loss > 0.05) else None),
                                pw_diff=tab[k]["pw_diff_vs_eps0"], pw_diff_se=tab[k]["pw_diff_vs_eps0_se"])
            est = {}
            for n_ in names:
                d = ref["per"][n_]
                est[n_] = dict(entries=next(c["n"] for c in prof if c["name"] == n_), g1_quantile_hit=round(d["g1_hit"], 5), g1_binomial=round(d["g1_binom"], 5),
                               cash_quantile_hit=round(d["cash_hit"], 4), cash_binomial=round(d["cash_binom"], 4), scenario_agreement=round(d["agree_scen"], 4))
            rec.put(f"{label}_frontier_B", tab)
            rec.put(f"{label}_price_of_insurance_B", price)
            rec.put(f"{label}_estimators_greedy_B", est)
            rec.log(f"[{label}] frontier B (pw, se, count, mean loss %, max loss %, swaps):",
                    json.dumps({k: (v["pw_B"], v["pw_B_se"], v["washout_scen_count_B"], v["mean_g1_loss_pct_B"], v["max_g1_loss_pct_B"], v["swaps"]) for k, v in tab.items()}))
            rec.log(f"[{label}] price:", json.dumps(price))
        frontier_table(spec_key, F_spec, "spec")
        frontier_table(small_key, F_small, "small")
        frontier_table(spec_key, F_spec_m2, "spec_margin2")
        frontier_table(small_key, F_small_m2, "small_margin2")

        # (3) duplication-adjusted goal 1 vs raw (spec entries)
        dup_rep = {}
        prof = prof_of(profiles[spec_key]["caps"])
        raw_port = start_port(profiles[spec_key]["caps"])
        dport = [dup_ports[n_] for n_ in names]
        evr = evaluate(prof, raw_port, XB, thrB, want_binom=False)
        evd = evaluate(prof, dport, XB, thrB, want_binom=False)
        for ci, c in enumerate(prof):
            n_ = c["name"]
            q = dupf[n_]["q"]
            rset, dset = set(raw_port[ci]), set(dport[ci])
            dup_rep[n_] = dict(entries=c["n"], same_lineups=len(rset & dset), jaccard=round(len(rset & dset) / max(1, len(rset | dset)), 3),
                               mean_expected_copies_raw=round(float(c["Nopp"] * q[list(rset)].mean()), 3), mean_expected_copies_dup=round(float(c["Nopp"] * q[list(dset)].mean()), 3),
                               max_expected_copies_raw=round(float(c["Nopp"] * q[list(rset)].max()), 3), max_expected_copies_dup=round(float(c["Nopp"] * q[list(dset)].max()), 3),
                               raw_port_g1_raw=round(evr["per"][n_]["g1_hit"], 5), raw_port_g1_dupadj=round(evr["per"][n_]["g1_dup"], 5),
                               dup_port_g1_raw=round(evd["per"][n_]["g1_hit"], 5), dup_port_g1_dupadj=round(evd["per"][n_]["g1_dup"], 5),
                               share_candidates_with_q_gt0=round(float((q > 0).mean()), 4), min_share_factor_candidates=round(float(dupf[n_]["f"].min()), 4))
        rec.put("duplication_adjusted_vs_raw_B", dup_rep)
        rec.log("dup:", json.dumps({k: (v["same_lineups"], v["entries"], v["mean_expected_copies_raw"], v["mean_expected_copies_dup"], v["raw_port_g1_dupadj"], v["dup_port_g1_dupadj"]) for k, v in dup_rep.items()}))
    del thrB, XB, simB

    # ---------------------------------------------------------------- late news (one questionable starter ruled OUT 30 minutes before tip)
    if a.late_news:
        q0 = night["quest"][0]
        qp = q0["player"]
        g0 = q0["game"]
        rec.log(f"LATE NEWS: player {qp} (game {g0}) OUT; beneficiary {q0['beneficiary']}")
        load_ln = system_load(1.0)
        t_ln = time.perf_counter()
        with rec.step("late_resim_game"):
            replace_game(simA, night, g0, force_out={qp})
            replace_game(simV, night, g0, force_out={qp})
            pil = sim_game(night, g0, 6000, a.seed + 77, force_out={qp})
            proj2 = proj.copy()
            proj2[pil["cols"]] = pil["X"].mean(0)
            cov2 = np.cov(pil["X"].T) if g0 < a.showdowns else None
        XA, XV = simA["X"], simV["X"]
        own_mult = np.ones(night["n"])
        own_mult[qp] = 0.02  # a few stale field lineups still hold him
        with rec.step("late_pool_spawn"):
            solver = SolverPool(night, sal, a.workers, rec)
        with rec.step("late_field_classic"):
            z = rng.standard_normal((2000, night["n"]))
            objs = np.maximum(0, proj2[None, :] * (1 + 0.15 * z))
            objs[:, qp] = -1000.0
            opt_l2, _ = solver.solve(objs)
            cas2, _ = classic_sampler(night, proj2, sal, 20000, rng, own_mult=own_mult)
            cpool, cpool_inc = make_cpool(opt_l2, cas2)
            for c in contests:
                if c["slate"] == "classic":
                    c["w"] = contest_weights(cpool, c["wopt"])
            own_pct2 = (contests[4]["w"][:, None] * cpool_inc).sum(0) * 100
        affected = set(cl_names)
        if g0 < a.showdowns:
            with rec.step("late_field_showdown"):
                sd_pools[g0] = field_showdown(night, g0, proj2, sal_sd, rng, own_mult=own_mult)
                sd_weights(g0)
            affected |= {c["name"] for c in contests if c["slate"] == f"sd{g0}"}
        with rec.step("late_thresholds_AV"):
            thrA.update(compute_thresholds(simA, affected))
            thrV.update(compute_thresholds(simV, affected))
        with rec.step("late_cand_classic"):
            keep = ~(cl_lineups == qp).any(1)
            n_drop = int((~keep).sum())
            src2 = rng.choice(SA, size=max(800, n_drop), replace=False)
            zz = rng.standard_normal((300, night["n"]))
            objs_mv2 = np.array([proj2 * (1 + sigs[(i // 5) % 3] * zz[i]) - alphas[i % 5] * own_pct2 for i in range(300)])
            allo = np.vstack([XA[src2].astype(np.float64), objs_mv2])
            allo[:, qp] = -1000.0
            lin2, _ = solver.solve(allo)
            old = {tuple(int(x) for x in L): int(s_) for L, s_ in zip(cl_lineups[keep], cl_src[keep])}
            added = 0
            for L, s_ in zip(lin2, list(src2) + [-1] * 300):
                if validate_classic(night, sal, L) and L not in old:
                    old[L] = int(s_)
                    added += 1
            cl_lineups = np.array(list(old.keys()))
            cl_src = np.array(list(old.values()))
            cl_inc = make_cl_inc(cl_lineups)
        with rec.step("late_pool_close"):
            solver.close()
        if g0 < a.showdowns:
            with rec.step("late_cand_showdown"):
                screen_sd(g0, proj2[sd_pools[g0]["cols"]], cov2, ban_local=int(np.nonzero(sd_pools[g0]["cols"] == qp)[0][0]))
        with rec.step("late_bitsets_A_greedy"):
            H1a, _ = build_bits(XA, thrA, which=affected, only_t1=True)
            for c in contests:
                if c["name"] in affected:
                    order[c["name"]], _ = greedy_single(H1a[c["name"]], c["n"])
            del H1a
        with rec.step("late_bitsets_V"):
            for n_ in affected:
                H1d.pop(n_, None)
                HCd.pop(n_, None)
            H1n, HCn = build_bits(XV, thrV, which=affected)
            H1d.update(H1n)
            HCd.update(HCn)
            del H1n, HCn
        with rec.step("late_reselect_swap_eps05"):
            caps = {c["name"]: c["n"] for c in contests}
            start = start_port(caps)
            g1s_ = g1_counts(start, H1d)
            _, stL = swap_search([H1d[n_] for n_ in names], [HCd[n_] for n_ in names], start, g1s_, 0.05, SV, max_swaps=a.max_swaps)
        total_ln = time.perf_counter() - t_ln
        ln_steps = {k: v for k, v in rec.data["steps"].items() if k.startswith("late_")}
        rec.put("late_news", dict(player=qp, game=g0, beneficiary=q0["beneficiary"], affected_contests=sorted(affected), classic_candidates_dropped=n_drop,
                                  classic_candidates_added=added, classic_candidates_after=len(cl_lineups), total_compute_s=round(total_ln, 2), steps=ln_steps,
                                  swaps=stL["swaps"], pw_V_after=round(stL["pw"], 6), load_at_start=load_ln,
                                  proj_change=dict(beneficiary_before=round(proj[q0["beneficiary"]], 2), beneficiary_after=round(proj2[q0["beneficiary"]], 2))))
        rec.log(f"LATE NEWS total compute {total_ln:.1f} s")

    # ---------------------------------------------------------------- summary
    mem.stop_flag = True
    time.sleep(0.1)
    pi = psutil.Process().memory_info()
    rec.data["memory"] = dict(peak_self_wset_mb=round(getattr(pi, "peak_wset", 0) / 2**20, 1), sampled_peak_self_mb=round(mem.peak_self / 2**20, 1),
                              sampled_peak_children_mb=round(mem.peak_children / 2**20, 1), sampled_peak_total_mb=round(mem.peak_total / 2**20, 1),
                              note="total = this process + pool workers, sampled every 50 ms")
    rec.data["total_wall_s"] = round(time.perf_counter() - T_START, 1)
    prod_steps = ["setup_pool_pilot_projections", "sim_A_V", "pool_spawn", "field_classic_milp", "field_classic_sampler", "field_showdown", "thresholds_AV_classic",
                  "thresholds_AV_showdown", "cand_classic_milp", "pool_close", "cand_showdown_screen", "bitsets_A", "select_greedy_A", "bitsets_V", "select_swap_eps05_from_greedy"]
    rec.data["first_full_build_s"] = round(sum(rec.data["steps"][k]["wall_s"] for k in prod_steps if k in rec.data["steps"]), 1)
    rec.data["first_full_build_steps"] = prod_steps
    rec.data["load_after"] = system_load(2.0)
    rec.flush()
    rec.log("memory:", json.dumps(rec.data["memory"]))
    rec.log("first full build (s):", rec.data["first_full_build_s"], "total wall:", rec.data["total_wall_s"])
    rec.log("WROTE", rec.path_json)


if __name__ == "__main__":
    main()
