# THROWAWAY SPIKE: not engine code. Purpose: does Showdown enumeration still work with fuller rosters (26 to 34 players), and what does scoring every legal lineup against 10,000 scenarios cost?
"""
  python enumerate_showdown_scale_spike.py --extra 0 2 4 6 --S 10000
Starts from the 22-player synthetic Showdown pool in bench_solvers.py and appends `extra` low-salary,
low-projection bench players PER TEAM (so 22, 26, 30, 34 players). For each pool size:
  - enumerate every legal lineup (1 CPT + 5 UTIL, cap $50,000, both teams), time it, count it
  - score ALL legal lineups against S scenarios in lineup chunks (matrix multiply), counting for each lineup how often
    it beats a per-scenario line; record time and peak memory
"""
import argparse
import datetime as dt
import importlib.util
import itertools
import json
import os
import time

import numpy as np
import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bench", os.path.join(HERE, "bench_solvers.py"))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


def pool(extra, seed=2026):
    pl = [dict(p) for p in B.make_showdown_pool()]
    rng = np.random.default_rng(seed + 50)
    pid = len(pl)
    for team in (0, 1):
        for _ in range(extra):
            sal = int(rng.integers(10, 21)) * 100  # $1,000 to $2,000
            proj = round(max(0.0, rng.normal(3.0, 2.0)), 2)
            pl.append(dict(id=pid, team=team, salary=sal, proj=proj, sd=round(0.30 * proj + 1.5, 2)))
            pid += 1
    return pl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", type=int, nargs="+", default=[0, 2, 4, 6])
    ap.add_argument("--S", type=int, default=10000)
    ap.add_argument("--chunk", type=int, default=10000)
    a = ap.parse_args()
    proc = psutil.Process()
    out = []
    for extra in a.extra:
        pl = pool(extra)
        n = len(pl)
        sal = np.array([p["salary"] for p in pl]); team = np.array([p["team"] for p in pl])
        t0 = time.perf_counter()
        U = np.array(list(itertools.combinations(range(n), 5)), dtype=np.int16)
        usal = sal[U].sum(1); uteam = team[U].sum(1)
        caps, utils = [], []
        for c in range(n):
            m = ~(U == c).any(1)
            tot = usal[m] + 1.5 * sal[c]; tm = uteam[m] + team[c]
            ok = (tot <= 50000) & (tm > 0) & (tm < 6)
            caps.append(np.full(int(ok.sum()), c, dtype=np.int16)); utils.append(U[m][ok])
        CAPS = np.concatenate(caps); UTILS = np.concatenate(utils)
        t_enum = time.perf_counter() - t0

        # scenarios for these players (independent normal, floored at 0; cost is what matters here)
        rng = np.random.default_rng(7)
        proj = np.array([p["proj"] for p in pl], dtype=np.float32); sd = np.array([p["sd"] for p in pl], dtype=np.float32)
        X = np.maximum(0.0, proj + sd * rng.standard_normal((a.S, n)).astype(np.float32))
        # per-scenario line: 95th percentile of a random 20,000-lineup sample, a stand-in for a field cut line
        samp = rng.choice(len(CAPS), size=min(20000, len(CAPS)), replace=False)
        def weights(idx):
            W = np.zeros((n, len(idx)), dtype=np.float32)
            cols = np.arange(len(idx))
            W[CAPS[idx], cols] = 1.5
            for k in range(5):
                W[UTILS[idx, k], cols] += 1.0
            return W
        line = np.quantile(X @ weights(samp), 0.95, axis=1).astype(np.float32)
        t1 = time.perf_counter()
        hits = np.empty(len(CAPS), dtype=np.int32)
        for s0 in range(0, len(CAPS), a.chunk):
            idx = np.arange(s0, min(s0 + a.chunk, len(CAPS)))
            CS = X @ weights(idx)  # S x chunk
            hits[idx] = (CS >= line[:, None]).sum(0)
        t_score = time.perf_counter() - t1
        rec = dict(players=n, legal_lineups=int(len(CAPS)), enumerate_s=round(t_enum, 3), S=a.S,
                   score_all_lineups_s=round(t_score, 2), lineup_scenario_pairs_per_s=round(len(CAPS) * a.S / t_score / 1e9, 2),
                   lineups_hitting_line_at_least_once=int((hits > 0).sum()),
                   peak_wset_mb=round(getattr(proc.memory_info(), "peak_wset", 0) / 2**20, 1))
        print(json.dumps(rec), flush=True)
        out.append(rec)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    path = os.path.join(HERE, "out", f"{stamp}_enumerate_showdown_scale.json")
    json.dump(dict(note="lineup_scenario_pairs_per_s is in billions; scoring = matrix multiply in lineup chunks", runs=out), open(path, "w"), indent=1)
    print("WROTE", path)


if __name__ == "__main__":
    main()
