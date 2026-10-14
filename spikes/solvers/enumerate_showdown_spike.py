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

# ---- part 2: reproduce the 150-lineup overlap sequence (at most 4 shared players) by enumeration instead of a solver
t1 = time.perf_counter()
caps, utils, projs = [], [], []
for c in range(n):
    mask = ~(U == c).any(1)
    tot = usal[mask] + 1.5 * sal[c]; tm = uteam[mask] + team[c]
    ok = (tot <= 50000) & (tm > 0) & (tm < 6)
    Uc = U[mask][ok]
    caps.append(np.full(len(Uc), c, dtype=np.int16)); utils.append(Uc); projs.append(uproj[mask][ok] + cptproj[c])
CAPS = np.concatenate(caps); UTILS = np.concatenate(utils); PROJ = np.round(np.concatenate(projs), 2)
members = np.zeros((len(CAPS), n), dtype=bool)
members[np.arange(len(CAPS)), CAPS] = True
for k in range(5):
    members[np.arange(len(CAPS)), UTILS[:, k]] = True
order = np.argsort(-PROJ, kind="stable")
allowed = np.ones(len(CAPS), dtype=bool)
picked = []
for it in range(150):
    cand = order[allowed[order]]
    if len(cand) == 0:
        break
    j = cand[0]
    picked.append(int(j))
    shared = members[:, members[j]].sum(1)  # players shared with the new pick
    allowed &= shared <= 4
t_seq = time.perf_counter() - t1
obj_sum = round(float(PROJ[picked].sum()), 2)
out2 = dict(seq150_by_enumeration_s=round(t_seq, 3), picked=len(picked), obj_sum=obj_sum, solver_seq150_obj_sum_from_bench=36226.67,
            first_obj=float(PROJ[picked[0]]), last_obj=float(PROJ[picked[-1]]))
path2 = os.path.join(HERE, "out", f"{stamp}_enumerate_showdown_seq150.json")
json.dump(out2, open(path2, "w"), indent=1); print(json.dumps(out2)); print("WROTE", path2)
