# THROWAWAY SPIKE: not engine code. Purpose: indicative cost of scenario-based portfolio selection (field cut lines, hit matrices, greedy max-coverage) on synthetic data.
"""
Pipeline sketch on a synthetic 6-game Classic slate (same pool as bench_solvers.py):
  1. S joint player-outcome scenarios (game factor + team factor + individual noise, clipped at 0)
  2. candidate pool: K lineups from GLPK solves on perturbed projections (each solve = one scenario-like draw)
  3. synthetic opponent field: ownership-weighted slot sampling with salary and 2-game rules, N entries with duplicates
  4. per scenario: field top-1% line and min-cash line (streamed in scenario chunks, field scores never stored whole)
  5. hit matrices H1[j, s] = candidate j beats top-1% line in scenario s; HC[j, s] = beats cash line
  6. greedy max-coverage selection of M entries under three objectives, report P(at least one top-1%) and P(no cash)
Numbers are synthetic and only show computational cost and the shape of the trade-off, not real edge.
"""
import argparse
import datetime as dt
import importlib.util
import json
import os
import time

import numpy as np
import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bench", os.path.join(HERE, "bench_solvers.py"))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


def scenarios(players, S, seed):
    rng = np.random.default_rng(seed)
    proj = np.array([p["proj"] for p in players], dtype=np.float32)
    sd = np.array([p["sd"] for p in players], dtype=np.float32)
    game = np.array([p["game"] for p in players])
    team = np.array([p["team"] for p in players])
    g = rng.standard_normal((S, game.max() + 1)).astype(np.float32)
    t = rng.standard_normal((S, team.max() + 1)).astype(np.float32)
    e = rng.standard_normal((S, len(players))).astype(np.float32)
    # shared game environment (+), small team factor, individual noise; variance sums to 1
    z = np.sqrt(0.12) * g[:, game] + np.sqrt(0.03) * t[:, team] + np.sqrt(0.85) * e
    return np.maximum(0.0, proj + sd * z)


def field(players, N, seed, floor_pts, own_temp=1.0):
    """ownership-weighted slot sampling; ownership proxy = softmax(value) mixed with projection"""
    rng = np.random.default_rng(seed)
    proj = np.array([p["proj"] for p in players])
    sal = np.array([p["salary"] for p in players])
    w = np.exp((proj / sal * 1000 - 4.5) * 1.2 / own_temp) * (proj / proj.mean())
    elig = {s: np.array([B.slot_ok(p["pos"], s) for p in players]) for s in B.CLASSIC_SLOTS}
    game = np.array([p["game"] for p in players])
    out = []
    tries = 0
    while len(out) < N:
        tries += 1
        chosen = []
        used = np.zeros(len(players), bool)
        for s in B.CLASSIC_SLOTS:
            ww = w * elig[s] * ~used
            i = rng.choice(len(players), p=ww / ww.sum())
            chosen.append(i)
            used[i] = True
        tot = sal[chosen].sum()
        if 47500 <= tot <= 50000 and len(set(game[chosen])) >= 2 and proj[chosen].sum() >= floor_pts:
            out.append(tuple(sorted(chosen)))
    return out, tries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--S", type=int, default=10000)
    ap.add_argument("--K", type=int, default=5000)
    ap.add_argument("--N", type=int, default=20000)
    ap.add_argument("--M", type=int, default=150)
    ap.add_argument("--cash_frac", type=float, default=0.20)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--tag", default="portfolio_select_spike")
    ap.add_argument("--field_floor", type=float, default=0.85, help="field lineups must project at least this share of the optimal projection")
    a = ap.parse_args()
    proc = psutil.Process()
    T = {}
    players = B.make_classic_pool()
    P = B.build_classic(players, "hall")

    t = time.perf_counter()
    X = scenarios(players, a.S, a.seed)  # S x n_players float32
    T["scenarios_s"] = time.perf_counter() - t

    t = time.perf_counter()
    ad = B.GlpkAdapter(P, a.seed)
    cand = []
    for k in range(a.K):
        ad.set_obj(B.col_obj(P, players, B.perturbed(players, a.seed, k)))
        sel, _ = ad.solve()
        ok, key, _ = B.validate(P, players, sel)
        cand.append(key)
    uniq = sorted(set(cand))
    T["candidates_s"] = time.perf_counter() - t

    t = time.perf_counter()
    ad0 = B.GlpkAdapter(P, a.seed)
    _, opt = ad0.solve()
    fl, tries = field(players, a.N, a.seed + 1, a.field_floor * opt)
    T["field_s"] = time.perf_counter() - t
    fu, fcount = np.unique(np.array(fl), axis=0, return_counts=True)  # unique field lineups + dup counts
    field_dup = {tuple(r): int(c) for r, c in zip(fu, fcount)}

    # per-scenario cut lines, streamed over scenario chunks; only unique field lineups scored, weighted by counts
    t = time.perf_counter()
    k1 = int(np.ceil(0.01 * a.N))
    kc = int(np.ceil(a.cash_frac * a.N))
    line1 = np.empty(a.S, np.float32)
    linec = np.empty(a.S, np.float32)
    order_w = fcount
    chunk = 250
    for s0 in range(0, a.S, chunk):
        Xs = X[s0:s0 + chunk]
        F = Xs[:, fu].sum(axis=2)  # chunk x unique_field
        for r in range(F.shape[0]):
            o = np.argsort(-F[r])
            cw = np.cumsum(order_w[o])
            line1[s0 + r] = F[r, o[np.searchsorted(cw, k1)]]
            linec[s0 + r] = F[r, o[np.searchsorted(cw, kc)]]
    T["cutlines_s"] = time.perf_counter() - t

    t = time.perf_counter()
    U = np.array(uniq)
    CS = X[:, U].sum(axis=2)  # S x K_unique float32
    H1 = (CS > line1[:, None]).T.copy()  # K x S bool (strict: a tie at the line is treated as a miss here)
    HC = (CS > linec[:, None]).T.copy()
    T["hits_s"] = time.perf_counter() - t

    def greedy(score_fn, M):
        chosen = []
        cov1 = np.zeros(a.S, bool)
        covc = np.zeros(a.S, bool)
        for _ in range(M):
            g = score_fn(cov1, covc)
            if chosen:
                g[chosen] = -1e18
            j = int(np.argmax(g))
            chosen.append(j)
            cov1 |= H1[j]
            covc |= HC[j]
        return chosen, cov1.mean(), 1 - covc.mean()

    t = time.perf_counter()
    res = {}
    res["greedy_top1"] = greedy(lambda c1, cc: H1[:, ~c1].sum(1).astype(float), a.M)
    res["greedy_cash"] = greedy(lambda c1, cc: HC[:, ~cc].sum(1).astype(float), a.M)
    # lexicographic-ish blend: top-1% coverage gain plus a weight on newly covered no-cash scenarios
    res["greedy_blend_w0.5"] = greedy(lambda c1, cc: H1[:, ~c1].sum(1) + 0.5 * HC[:, ~cc].sum(1).astype(float), a.M)
    proj = np.array([p["proj"] for p in players])
    topproj = np.argsort(-proj[U].sum(1))[: a.M]
    res["top_projection"] = (list(topproj), H1[topproj].any(0).mean(), 1 - HC[topproj].any(0).mean())
    T["greedy_3x_s"] = time.perf_counter() - t

    out = dict(
        S=a.S, K_solves=a.K, field_floor=a.field_floor, K_unique=len(uniq), N_field=a.N, field_unique=len(fu), field_tries=tries,
        field_max_dup=int(fcount.max()), M=a.M, cash_frac=a.cash_frac,
        timings_s={k: round(v, 2) for k, v in T.items()},
        peak_wset_mb=round(getattr(proc.memory_info(), "peak_wset", 0) / 2**20, 1),
        arrays_mb=dict(scenarios=round(X.nbytes / 2**20, 1), cand_scores=round(CS.nbytes / 2**20, 1),
                       H1_bool=round(H1.nbytes / 2**20, 1), H1_bitpacked=round(np.packbits(H1, axis=1).nbytes / 2**20, 2)),
        results={k: dict(P_at_least_one_top1=round(float(v[1]), 4), P_no_cash=round(float(v[2]), 4),
                         mean_field_dups_of_chosen=round(float(np.mean([field_dup.get(tuple(U[j]), 0) for j in v[0]])), 3))
                 for k, v in res.items()},
        single_best_lineup_P_top1=round(float(H1.mean(1).max()), 4),
        note="synthetic data; shows cost and trade-off shape only",
    )
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    path = os.path.join(HERE, "out", f"{stamp}_{a.tag}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE", path)


if __name__ == "__main__":
    main()
