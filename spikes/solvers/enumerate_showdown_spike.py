# THROWAWAY SPIKE: not engine code. Purpose: count and time full enumeration of legal DK NBA Showdown lineups on the synthetic 22-player pool (is a solver needed at all for Showdown?).
import datetime as dt, importlib.util, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bench", os.path.join(HERE, "bench_solvers.py")); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
pl = B.make_showdown_pool()
n = len(pl)
sal = np.array([p["salary"] for p in pl]); team = np.array([p["team"] for p in pl]); proj = np.array([p["proj"] for p in pl])
P = B.build_showdown(pl); cptproj = {P.col_player[j]: P.c[j] for j in range(len(P.c)) if P.col_role[j] == "CPT"}  # same rounding as the solver model
t0 = time.perf_counter()
U = np.array(list(itertools.combinations(range(n), 5)), dtype=np.int16)  # all 5-player UTIL sets
usal = sal[U].sum(1); uproj = proj[U].sum(1); uteam = team[U].sum(1)
rows = []
for c in range(n):
    mask = ~(U == c).any(1)
    tot = usal[mask] + 1.5 * sal[c]
    tm = uteam[mask] + team[c]
    ok = (tot <= 50000) & (tm > 0) & (tm < 6)
    rows.append(int(ok.sum()))
    if c == 0:
        pass
t_enum = time.perf_counter() - t0
# best by projection via enumeration, compare with solver optimum from bench (266.99)
best = -1
for c in range(n):
    mask = ~(U == c).any(1)
    tot = usal[mask] + 1.5 * sal[c]; tm = uteam[mask] + team[c]
    ok = (tot <= 50000) & (tm > 0) & (tm < 6)
    v = (uproj[mask] + cptproj[c])[ok]
    if v.size: best = max(best, float(v.max()))
out = dict(players=n, util_sets=len(U), legal_lineups=sum(rows), legal_per_captain_min=min(rows), legal_per_captain_max=max(rows),
           enumerate_and_filter_s=round(t_enum, 3), best_projection_by_enumeration=round(best, 2), solver_optimum_from_bench=266.99)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
path = os.path.join(HERE, "out", f"{stamp}_enumerate_showdown.json")
json.dump(out, open(path, "w"), indent=1); print(json.dumps(out)); print("WROTE", path)
