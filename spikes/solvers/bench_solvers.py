# THROWAWAY SPIKE: not engine code. Purpose: indicative timing, memory and determinism of free MILP/CP solvers on synthetic DK NBA Classic and Showdown lineup problems.
"""
One solver, one contest type, one task per process. Prints a single JSON object on stdout.

  python bench_solvers.py --solver highs --contest classic --task seq150 --seed 7
  python bench_solvers.py --solver cpsat --contest showdown --task rand --n 5000 --seed 7 --procs 4

Solvers:
  highs          highspy, one persistent model; overlap cuts via addRow, perturbed projections via changeColsCost
  highs_rebuild  highspy, fresh model built for every solve (same formulation)
  pulp_cbc       PuLP 2.4 + bundled cbc.exe (CBC 2.9.0), subprocess per solve (how pydfs-lineup-optimizer runs)
  ortools_cbc    OR-Tools pywraplp CBC backend, in-process
  cpsat          OR-Tools CP-SAT, num_workers=1 (objective scaled x100 to integers)
  cpsat_mt       OR-Tools CP-SAT, num_workers=8
  scip           PySCIPOpt (SCIP 10), freeTransform + modify between solves
  glpk           swiglpk (GLPK 5.0), persistent problem, glp_intopt with presolve

Tasks:
  single   build + solve one max-projection lineup
  seq150   150 lineups: solve, then add "share at most K players with this lineup" cut, repeat
  rand     N independent solves, each with projections perturbed by a seeded normal draw

Every returned lineup is validated by solver-independent code (slots, salary, games/teams, distinct players),
and the objective is recomputed from the projection vector.
"""
import argparse
import hashlib
import json
import os
import sys
import threading
import time

import numpy as np
import psutil

CAP = 50000
GAP = 0.0  # relative MIP gap, set from --gap
CLASSIC_SLOTS = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]


# ----------------------------------------------------------------------------- pools
def slot_ok(positions, slot):
    if slot == "UTIL":
        return True
    if slot == "G":
        return "PG" in positions or "SG" in positions
    if slot == "F":
        return "SF" in positions or "PF" in positions
    return slot in positions


def make_classic_pool(seed=2026, games=6):
    """10 players per team, 2 teams per game (default 6 games = 120 players). Salaries $3,000 to $11,500 in $100 steps, multi-position eligibility."""
    rng = np.random.default_rng(seed)
    template = [("PG",), ("PG", "SG"), ("SG",), ("SG", "SF"), ("SF",), ("SF", "PF"), ("PF",), ("PF", "C"), ("C",)]
    tiers = ["star", "high", "mid", "mid", "low", "bench", "bench", "bench", "bench", "bench"]
    ranges = {"star": (9000, 11500), "high": (7000, 9000), "mid": (5000, 7000), "low": (4000, 5000), "bench": (3000, 4200)}
    players = []
    pid = 0
    for team in range(2 * games):
        pos_list = list(template) + [template[rng.integers(len(template))]]
        tier_list = list(tiers)
        rng.shuffle(tier_list)
        for pos, tier in zip(pos_list, tier_list):
            lo, hi = ranges[tier]
            sal = int(rng.integers(lo // 100, hi // 100 + 1)) * 100
            if tier == "bench":
                value = max(0.3, rng.normal(4.0, 1.4))
            else:
                value = max(2.5, rng.normal(5.0, 0.6))
            proj = round(sal / 1000.0 * value, 2)
            sd = round(0.30 * proj + 1.5, 2)
            players.append(dict(id=pid, pos=pos, team=team, game=team // 2, salary=sal, proj=proj, sd=sd))
            pid += 1
    return players


def make_showdown_pool(seed=2026):
    """22 players, 2 teams of 11. UTIL salary $1,000 to $12,000; CPT row = 1.5x salary and 1.5x points."""
    rng = np.random.default_rng(seed + 1)
    tiers = ["star", "high", "mid", "mid", "low", "low", "low", "bench", "bench", "bench", "bench"]
    ranges = {"star": (10000, 12000), "high": (8000, 10000), "mid": (5000, 8000), "low": (3000, 5000), "bench": (1000, 3000)}
    players = []
    pid = 0
    for team in range(2):
        for tier in tiers:
            lo, hi = ranges[tier]
            sal = int(rng.integers(lo // 100, hi // 100 + 1)) * 100
            if tier == "bench":
                value = max(0.0, rng.normal(2.5, 1.5))
            else:
                value = max(2.5, rng.normal(5.1, 0.6))
            proj = round(sal / 1000.0 * value, 2)
            sd = round(0.30 * proj + 1.5, 2)
            players.append(dict(id=pid, team=team, salary=sal, proj=proj, sd=sd))
            pid += 1
    return players


# ----------------------------------------------------------------------------- generic binary program
class Problem:
    """max c.x subject to lo <= A_r x <= hi for each row, x binary. Rows stored sparse."""

    def __init__(self):
        self.c = []
        self.col_player = []
        self.col_role = []  # slot name (classic) or 'CPT'/'UTIL' (showdown)
        self.rows = []  # (idx list, coef list, lo, hi)  lo/hi may be None for -inf/+inf


def hall_rows(players, cols_of_player):
    """Hall's theorem rows: for every subset S of the 7 non-UTIL slots, at least |S| chosen players must be
    eligible for some slot in S. With these rows a valid slot assignment always exists (UTIL takes anyone).
    Duplicate and dominated rows are dropped."""
    from itertools import combinations
    slots7 = [s for s in CLASSIC_SLOTS if s != "UTIL"]
    best = {}
    for r in range(1, 8):
        for S in combinations(slots7, r):
            nb = frozenset(p["id"] for p in players if any(slot_ok(p["pos"], s) for s in S))
            best[nb] = max(best.get(nb, 0), len(S))
    items = sorted(best.items(), key=lambda kv: (len(kv[0]), -kv[1]))
    kept = []
    for nb, need in items:
        # row (nb, need) is implied by a kept row (nb2, need2) with nb2 subset of nb and need2 >= need
        if any(nb2 <= nb and need2 >= need for nb2, need2 in kept):
            continue
        kept.append((nb, need))
    rows = []
    for nb, need in kept:
        idx = sorted(cols_of_player[pid][0] for pid in nb)
        rows.append((idx, [1.0] * len(idx), float(need), None))
    return rows


def build_classic(players, form="hall"):
    """form='slot': one binary per (player, eligible slot) (symmetric, slow to prove optimal).
    form='hall': one binary per player plus Hall rows (no slot symmetry); slots assigned afterwards."""
    P = Problem()
    cols_of_player = {p["id"]: [] for p in players}
    if form == "slot":
        cols_of_slot = {s: [] for s in CLASSIC_SLOTS}
        for p in players:
            for s in CLASSIC_SLOTS:
                if slot_ok(p["pos"], s):
                    j = len(P.c)
                    P.c.append(p["proj"])
                    P.col_player.append(p["id"])
                    P.col_role.append(s)
                    cols_of_player[p["id"]].append(j)
                    cols_of_slot[s].append(j)
        for s in CLASSIC_SLOTS:  # each slot filled exactly once
            P.rows.append((cols_of_slot[s], [1.0] * len(cols_of_slot[s]), 1.0, 1.0))
        for p in players:  # each player at most once
            idx = cols_of_player[p["id"]]
            P.rows.append((idx, [1.0] * len(idx), None, 1.0))
    else:
        for p in players:
            j = len(P.c)
            P.c.append(p["proj"])
            P.col_player.append(p["id"])
            P.col_role.append("Y")
            cols_of_player[p["id"]].append(j)
        P.rows.append((list(range(len(P.c))), [1.0] * len(P.c), 8.0, 8.0))
        P.rows.extend(hall_rows(players, cols_of_player))
    sal = {p["id"]: p["salary"] for p in players}
    P.rows.append((list(range(len(P.c))), [float(sal[P.col_player[j]]) for j in range(len(P.c))], None, float(CAP)))
    games = sorted({p["game"] for p in players})
    for g in games:  # at most 7 of 8 from one game  <=>  players from at least 2 games
        idx = [j for j in range(len(P.c)) if players[P.col_player[j]]["game"] == g]
        P.rows.append((idx, [1.0] * len(idx), None, 7.0))
    P.cols_of_player = cols_of_player
    P.kind = "classic"
    P.form = form
    P.size = 8
    return P


def assign_slots(players, pids):
    """bipartite matching players -> slots by augmenting paths; returns dict slot->pid or None"""
    match = {}  # slot -> pid

    def try_assign(pid, seen):
        for s in CLASSIC_SLOTS:
            if slot_ok(players[pid]["pos"], s) and s not in seen:
                seen.add(s)
                if s not in match or try_assign(match[s], seen):
                    match[s] = pid
                    return True
        return False

    for pid in pids:
        if not try_assign(pid, set()):
            return None
    return match


def build_showdown(players):
    P = Problem()
    cols_of_player = {p["id"]: [] for p in players}
    cpt, utl = [], []
    for p in players:
        for role, mult in (("CPT", 1.5), ("UTIL", 1.0)):
            j = len(P.c)
            P.c.append(round(p["proj"] * mult, 2))  # 2 decimals so CP-SAT x100 scaling is exact
            P.col_player.append(p["id"])
            P.col_role.append(role)
            cols_of_player[p["id"]].append(j)
            (cpt if role == "CPT" else utl).append(j)
    P.rows.append((cpt, [1.0] * len(cpt), 1.0, 1.0))
    P.rows.append((utl, [1.0] * len(utl), 5.0, 5.0))
    for p in players:
        idx = cols_of_player[p["id"]]
        P.rows.append((idx, [1.0, 1.0], None, 1.0))
    coef = [float(players[P.col_player[j]]["salary"] * (1.5 if P.col_role[j] == "CPT" else 1.0)) for j in range(len(P.c))]
    P.rows.append((list(range(len(P.c))), coef, None, float(CAP)))
    for t in (0, 1):  # both teams represented
        idx = [j for j in range(len(P.c)) if players[P.col_player[j]]["team"] == t]
        P.rows.append((idx, [1.0] * len(idx), 1.0, None))
    P.cols_of_player = cols_of_player
    P.kind = "showdown"
    P.size = 6
    return P


def col_obj(P, players, proj_vec):
    """objective vector for a per-player projection vector"""
    out = np.empty(len(P.c))
    for j in range(len(P.c)):
        m = 1.5 if P.col_role[j] == "CPT" else 1.0
        out[j] = round(proj_vec[P.col_player[j]] * m, 2)
    return out


# ----------------------------------------------------------------------------- validation
def validate(P, players, sel):
    """Returns (ok, key, reason). key identifies the lineup by players (and CPT for showdown)."""
    pids = [P.col_player[j] for j in sel]
    roles = [P.col_role[j] for j in sel]
    if len(sel) != P.size:
        return False, None, f"size {len(sel)}"
    if len(set(pids)) != P.size:
        return False, None, "duplicate player"
    if P.kind == "classic" and P.form == "hall":
        m = assign_slots(players, pids)
        if m is None or len(m) != 8:
            return False, None, "no valid slot assignment"
        roles = [None] * len(pids)
        for slot, pid in m.items():
            roles[pids.index(pid)] = slot
    if P.kind == "classic":
        if sorted(roles) != sorted(CLASSIC_SLOTS):
            return False, None, f"slots {roles}"
        for pid, r in zip(pids, roles):
            if not slot_ok(players[pid]["pos"], r):
                return False, None, f"ineligible {pid}->{r}"
        sal = sum(players[pid]["salary"] for pid in pids)
        if sal > CAP:
            return False, None, f"salary {sal}"
        if len({players[pid]["game"] for pid in pids}) < 2:
            return False, None, "one game"
        return True, tuple(sorted(pids)), ""
    else:
        if roles.count("CPT") != 1:
            return False, None, "cpt count"
        sal = sum(players[pid]["salary"] * (1.5 if r == "CPT" else 1.0) for pid, r in zip(pids, roles))
        if sal > CAP:
            return False, None, f"salary {sal}"
        if len({players[pid]["team"] for pid in pids}) < 2:
            return False, None, "one team"
        cptid = pids[roles.index("CPT")]
        return True, (cptid, tuple(sorted(p for p, r in zip(pids, roles) if r != "CPT"))), ""


def overlap_cut(P, key, K):
    """share at most K players (by player identity, any slot/role) with the lineup `key`"""
    pids = key if P.kind == "classic" else (key[0],) + tuple(key[1])
    idx = []
    for pid in pids:
        idx.extend(P.cols_of_player[pid])
    return idx, [1.0] * len(idx), None, float(K)


# ----------------------------------------------------------------------------- solver adapters
class HighsAdapter:
    TUNED = {"mip_heuristic_effort": 0.0, "mip_heuristic_run_rins": False, "mip_heuristic_run_rens": False,
             "mip_heuristic_run_root_reduced_cost": False}

    def __init__(self, P, seed, threads=1, rebuild=False, tuned=False):
        import highspy
        self.hp = highspy
        self.P, self.seed, self.threads, self.rebuild, self.tuned = P, seed, threads, rebuild, tuned
        self.extra_rows = []
        self.c = np.array(P.c, dtype=np.float64)
        self._build()

    def _build(self):
        hp = self.hp
        h = hp.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("random_seed", int(self.seed))
        h.setOptionValue("threads", int(self.threads))
        h.setOptionValue("mip_rel_gap", float(GAP))
        if self.tuned:
            for k, v in self.TUNED.items():
                h.setOptionValue(k, v)
        n = len(self.c)
        h.addCols(n, self.c, np.zeros(n), np.ones(n), 0, np.zeros(n, dtype=np.int32),
                  np.array([], dtype=np.int32), np.array([], dtype=np.float64))
        h.changeColsIntegrality(n, np.arange(n, dtype=np.int32), np.array([hp.HighsVarType.kInteger] * n))
        for r in self.P.rows + self.extra_rows:
            self._add_row(h, r)
        h.changeObjectiveSense(hp.ObjSense.kMaximize)
        self.h = h

    def _add_row(self, h, r):
        idx, coef, lo, hi = r
        inf = self.hp.kHighsInf
        h.addRow(-inf if lo is None else lo, inf if hi is None else hi, len(idx),
                 np.array(idx, dtype=np.int32), np.array(coef, dtype=np.float64))

    def add_row(self, r):
        self.extra_rows.append(r)
        if not self.rebuild:
            self._add_row(self.h, r)

    def set_obj(self, c):
        self.c = np.asarray(c, dtype=np.float64)
        if not self.rebuild:
            n = len(self.c)
            self.h.changeColsCost(n, np.arange(n, dtype=np.int32), self.c)

    def solve(self):
        if self.rebuild:
            self._build()
        self.h.run()
        st = self.h.getModelStatus()
        if st != self.hp.HighsModelStatus.kOptimal:
            return None, None
        x = np.array(self.h.getSolution().col_value)
        return list(np.where(x > 0.5)[0]), self.h.getInfo().objective_function_value


class PulpCbcAdapter:
    def __init__(self, P, seed, threads=1):
        import pulp
        self.pulp = pulp
        self.P, self.seed = P, seed
        self.prob = pulp.LpProblem("lineup", pulp.LpMaximize)
        self.x = [pulp.LpVariable(f"x{j}", cat="Binary") for j in range(len(P.c))]
        self.prob += pulp.lpSum(P.c[j] * self.x[j] for j in range(len(P.c)))
        for r in P.rows:
            self.add_row(r)
        self.cmd = pulp.PULP_CBC_CMD(msg=False, gapRel=(GAP if GAP > 0 else None), options=[f"randomCbcSeed {int(seed) + 1}"])

    def add_row(self, r):
        idx, coef, lo, hi = r
        e = self.pulp.lpSum(coef[k] * self.x[idx[k]] for k in range(len(idx)))
        if lo is not None and hi is not None and lo == hi:
            self.prob += e == lo
        else:
            if lo is not None:
                self.prob += e >= lo
            if hi is not None:
                self.prob += e <= hi

    def set_obj(self, c):
        self.prob.setObjective(self.pulp.lpSum(float(c[j]) * self.x[j] for j in range(len(c))))

    def solve(self):
        self.prob.solve(self.cmd)
        if self.pulp.LpStatus[self.prob.status] != "Optimal":
            return None, None
        sel = [j for j, v in enumerate(self.x) if (v.varValue or 0) > 0.5]
        return sel, self.pulp.value(self.prob.objective)


class OrtoolsCbcAdapter:
    def __init__(self, P, seed, threads=1):
        from ortools.linear_solver import pywraplp
        self.lp = pywraplp
        self.s = pywraplp.Solver.CreateSolver("CBC")
        self.s.SetNumThreads(int(threads))
        inf = self.s.infinity()
        self.inf = inf
        self.x = [self.s.BoolVar(f"x{j}") for j in range(len(P.c))]
        for r in P.rows:
            self.add_row(r)
        self.obj = self.s.Objective()
        for j, cj in enumerate(P.c):
            self.obj.SetCoefficient(self.x[j], cj)
        self.obj.SetMaximization()
        self.params = pywraplp.MPSolverParameters()
        self.params.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, float(GAP))

    def add_row(self, r):
        idx, coef, lo, hi = r
        ct = self.s.RowConstraint(-self.inf if lo is None else lo, self.inf if hi is None else hi, "")
        for k in range(len(idx)):
            ct.SetCoefficient(self.x[idx[k]], coef[k])

    def set_obj(self, c):
        for j in range(len(c)):
            self.obj.SetCoefficient(self.x[j], float(c[j]))

    def solve(self):
        st = self.s.Solve(self.params)
        if st != self.lp.Solver.OPTIMAL:
            return None, None
        sel = [j for j, v in enumerate(self.x) if v.solution_value() > 0.5]
        return sel, self.obj.Value()


class CpSatAdapter:
    SCALE = 100

    def __init__(self, P, seed, threads=1):
        from ortools.sat.python import cp_model
        self.cp = cp_model
        self.m = cp_model.CpModel()
        self.x = [self.m.new_bool_var(f"x{j}") for j in range(len(P.c))]
        for r in P.rows:
            self.add_row(r)
        self.set_obj(P.c)
        self.solver = cp_model.CpSolver()
        self.solver.parameters.num_workers = int(threads)
        self.solver.parameters.random_seed = int(seed)
        if GAP > 0:
            self.solver.parameters.relative_gap_limit = float(GAP)

    def add_row(self, r):
        idx, coef, lo, hi = r
        ints = [int(round(v)) for v in coef]
        assert all(abs(a - b) < 1e-9 for a, b in zip(ints, coef)), "CP-SAT needs integer row coefficients"
        e = self.cp.LinearExpr.weighted_sum([self.x[i] for i in idx], ints)
        self.m.add_linear_constraint(e, -(2 ** 40) if lo is None else int(lo), 2 ** 40 if hi is None else int(hi))

    def set_obj(self, c):
        self.cint = [int(round(float(v) * self.SCALE)) for v in c]
        self.m.clear_objective()
        self.m.maximize(self.cp.LinearExpr.weighted_sum(self.x, self.cint))

    def solve(self):
        st = self.solver.solve(self.m)
        if st != self.cp.OPTIMAL:
            return None, None
        sel = [j for j, v in enumerate(self.x) if self.solver.boolean_value(v)]
        return sel, self.solver.objective_value / self.SCALE


class ScipAdapter:
    def __init__(self, P, seed, threads=1):
        import pyscipopt
        self.ps = pyscipopt
        self.m = pyscipopt.Model()
        self.m.hideOutput()
        self.m.setParam("randomization/randomseedshift", int(seed))
        self.m.setParam("limits/gap", float(GAP))
        self.x = [self.m.addVar(vtype="B", name=f"x{j}") for j in range(len(P.c))]
        for r in P.rows:
            self._add(r)
        self.m.setObjective(pyscipopt.quicksum(P.c[j] * self.x[j] for j in range(len(P.c))), "maximize")
        self.solved = False

    def _add(self, r):
        idx, coef, lo, hi = r
        e = self.ps.quicksum(coef[k] * self.x[idx[k]] for k in range(len(idx)))
        if lo is not None and hi is not None and lo == hi:
            self.m.addCons(e == lo)
        else:
            if lo is not None:
                self.m.addCons(e >= lo)
            if hi is not None:
                self.m.addCons(e <= hi)

    def add_row(self, r):
        if self.solved:
            self.m.freeTransform()
            self.solved = False
        self._add(r)

    def set_obj(self, c):
        if self.solved:
            self.m.freeTransform()
            self.solved = False
        self.m.setObjective(self.ps.quicksum(float(c[j]) * self.x[j] for j in range(len(c))), "maximize")

    def solve(self):
        if self.solved:
            self.m.freeTransform()
        self.m.optimize()
        self.solved = True
        if self.m.getStatus() != "optimal":
            return None, None
        sol = self.m.getBestSol()
        sel = [j for j, v in enumerate(self.x) if self.m.getSolVal(sol, v) > 0.5]
        return sel, self.m.getObjVal()


class GlpkAdapter:
    def __init__(self, P, seed, threads=1):
        import swiglpk as g
        self.g = g
        g.glp_term_out(g.GLP_OFF)
        self.lp = g.glp_create_prob()
        g.glp_set_obj_dir(self.lp, g.GLP_MAX)
        n = len(P.c)
        self.n = n
        g.glp_add_cols(self.lp, n)
        for j in range(n):
            g.glp_set_col_kind(self.lp, j + 1, g.GLP_BV)
            g.glp_set_obj_coef(self.lp, j + 1, float(P.c[j]))
        for r in P.rows:
            self.add_row(r)
        self.parm = g.glp_iocp()
        g.glp_init_iocp(self.parm)
        self.parm.presolve = g.GLP_ON
        self.parm.msg_lev = g.GLP_MSG_OFF
        self.parm.mip_gap = float(GAP)

    def add_row(self, r):
        g = self.g
        idx, coef, lo, hi = r
        i = g.glp_add_rows(self.lp, 1)
        if lo is not None and hi is not None:
            t = g.GLP_FX if lo == hi else g.GLP_DB
        elif lo is not None:
            t = g.GLP_LO
        else:
            t = g.GLP_UP
        g.glp_set_row_bnds(self.lp, i, t, 0.0 if lo is None else lo, 0.0 if hi is None else hi)
        ia = g.intArray(len(idx) + 1)
        va = g.doubleArray(len(idx) + 1)
        for k in range(len(idx)):
            ia[k + 1] = int(idx[k]) + 1
            va[k + 1] = float(coef[k])
        g.glp_set_mat_row(self.lp, i, len(idx), ia, va)

    def set_obj(self, c):
        for j in range(len(c)):
            self.g.glp_set_obj_coef(self.lp, j + 1, float(c[j]))

    def solve(self):
        g = self.g
        ret = g.glp_intopt(self.lp, self.parm)
        if ret != 0 or g.glp_mip_status(self.lp) != g.GLP_OPT:
            return None, None
        sel = [j for j in range(self.n) if g.glp_mip_col_val(self.lp, j + 1) > 0.5]
        return sel, g.glp_mip_obj_val(self.lp)


IMPORTS = {"highs": "highspy", "highs_tuned": "highspy", "highs_rebuild": "highspy", "pulp_cbc": "pulp", "ortools_cbc": "ortools.linear_solver.pywraplp",
           "cpsat": "ortools.sat.python.cp_model", "cpsat_mt": "ortools.sat.python.cp_model", "scip": "pyscipopt", "glpk": "swiglpk"}


def make_adapter(name, P, seed):
    if name == "highs":
        return HighsAdapter(P, seed, threads=1)
    if name == "highs_tuned":
        return HighsAdapter(P, seed, threads=1, tuned=True)
    if name == "highs_rebuild":
        return HighsAdapter(P, seed, threads=1, rebuild=True)
    if name == "pulp_cbc":
        return PulpCbcAdapter(P, seed)
    if name == "ortools_cbc":
        return OrtoolsCbcAdapter(P, seed)
    if name == "cpsat":
        return CpSatAdapter(P, seed, threads=1)
    if name == "cpsat_mt":
        return CpSatAdapter(P, seed, threads=8)
    if name == "scip":
        return ScipAdapter(P, seed)
    if name == "glpk":
        return GlpkAdapter(P, seed)
    raise ValueError(name)


# ----------------------------------------------------------------------------- memory sampler
class MemSampler(threading.Thread):
    """Samples RSS of this process plus all descendants (catches cbc.exe children and pool workers)."""

    def __init__(self, interval=0.02):
        super().__init__(daemon=True)
        self.interval = interval
        self.peak_total = 0
        self.peak_children = 0
        self.stop_flag = False
        self.me = psutil.Process()

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
                self.peak_children = max(self.peak_children, ch)
                self.peak_total = max(self.peak_total, own + ch)
            except Exception:
                pass
            time.sleep(self.interval)


# ----------------------------------------------------------------------------- tasks
def perturbed(players, seed, k):
    rng = np.random.default_rng([int(seed), int(k)])
    proj = np.array([p["proj"] for p in players])
    sd = np.array([p["sd"] for p in players])
    return np.round(np.maximum(0.0, proj + sd * rng.standard_normal(len(players))), 2)


def rand_chunk(args):
    """worker for --procs > 1 (also used inline for procs == 1)"""
    solver, contest, seed, ks, form, gap, games = args
    global GAP
    GAP = gap
    players = make_classic_pool(games=games) if contest == "classic" else make_showdown_pool()
    P = build_classic(players, form) if contest == "classic" else build_showdown(players)
    ad = make_adapter(solver, P, seed)
    out = []
    for k in ks:
        c = col_obj(P, players, perturbed(players, seed, k))
        ad.set_obj(c)
        t0 = time.perf_counter()
        sel, obj = ad.solve()
        dt = time.perf_counter() - t0
        if sel is None:
            out.append((k, None, None, dt, "infeasible"))
            continue
        ok, key, why = validate(P, players, sel)
        recomputed = float(sum(c[j] for j in sel))
        out.append((k, key if ok else None, recomputed, dt, "" if ok and abs(recomputed - obj) < 1e-4 else f"{why} obj {obj} vs {recomputed}"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", required=True)
    ap.add_argument("--contest", choices=["classic", "showdown"], required=True)
    ap.add_argument("--task", choices=["single", "seq150", "rand"], required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--procs", type=int, default=1)
    ap.add_argument("--overlap", type=int, default=None, help="max shared players with any prior lineup (seq150)")
    ap.add_argument("--games", type=int, default=6, help="classic slate size in games (10 players per team)")
    ap.add_argument("--form", choices=["hall", "slot"], default="hall", help="classic formulation")
    ap.add_argument("--gap", type=float, default=0.0, help="relative MIP gap (0 = prove optimal)")
    a = ap.parse_args()
    global GAP
    GAP = a.gap

    sampler = MemSampler()
    sampler.start()
    import importlib
    t_imp = time.perf_counter()
    importlib.import_module(IMPORTS[a.solver])
    import_s = time.perf_counter() - t_imp
    t_start = time.perf_counter()
    players = make_classic_pool(games=a.games) if a.contest == "classic" else make_showdown_pool()
    P = build_classic(players, a.form) if a.contest == "classic" else build_showdown(players)
    res = dict(solver=a.solver, contest=a.contest, task=a.task, seed=a.seed, procs=a.procs, gap=a.gap, form=(a.form if a.contest == "classic" else "player-role"),
               n_players=len(players), n_cols=len(P.c), n_rows=len(P.rows), import_s=round(import_s, 3))
    objs, keys, times, problems = [], [], [], []

    if a.task in ("single", "seq150"):
        K = a.overlap if a.overlap is not None else (6 if a.contest == "classic" else 4)
        n = 1 if a.task == "single" else a.n
        res["overlap_K"] = K
        t0 = time.perf_counter()
        ad = make_adapter(a.solver, P, a.seed)
        res["build_s"] = round(time.perf_counter() - t0, 4)
        for i in range(n):
            t1 = time.perf_counter()
            sel, obj = ad.solve()
            times.append(time.perf_counter() - t1)
            if os.environ.get("BENCH_VERBOSE"):
                print(f"solve {i} {times[-1]*1000:.1f} ms obj {obj}", file=sys.stderr, flush=True)
            if sel is None:
                problems.append(f"lineup {i}: no optimal solution")
                break
            ok, key, why = validate(P, players, sel)
            recomputed = float(sum(P.c[j] for j in sel))
            if not ok or abs(recomputed - obj) > 1e-4:
                problems.append(f"lineup {i}: {why} obj {obj} vs {recomputed}")
                break
            objs.append(round(recomputed, 4))
            keys.append(key)
            if a.task == "seq150":
                ad.add_row(overlap_cut(P, key, K))
    else:
        ks = list(range(a.n))
        if a.procs == 1:
            chunks_out = [rand_chunk((a.solver, a.contest, a.seed, ks, a.form, a.gap, a.games))]
        else:
            import multiprocessing as mp
            parts = [ks[i::a.procs] for i in range(a.procs)]
            with mp.get_context("spawn").Pool(a.procs) as pool:
                chunks_out = pool.map(rand_chunk, [(a.solver, a.contest, a.seed, p, a.form, a.gap, a.games) for p in parts])
        rows = sorted([r for ch in chunks_out for r in ch], key=lambda r: r[0])
        for k, key, obj, dt, why in rows:
            times.append(dt)
            if why:
                problems.append(f"draw {k}: {why}")
            keys.append(key)
            objs.append(None if obj is None else round(obj, 4))
        res["unique_lineups"] = len({k for k in keys if k is not None})

    total = time.perf_counter() - t_start
    sampler.stop_flag = True
    sampler.join(timeout=1)
    mi = psutil.Process().memory_info()
    keystr = json.dumps([list(k) if not isinstance(k, tuple) or a.contest == "classic" else [k[0], list(k[1])] for k in keys])
    t_ms = np.array(times) * 1000 if times else np.array([0.0])
    res.update(
        n_requested=(1 if a.task == "single" else a.n),
        n_valid=sum(1 for k in keys if k is not None),
        problems=problems[:10],
        n_problems=len(problems),
        total_s=round(total, 3),
        solve_ms_median=round(float(np.median(t_ms)), 2),
        solve_ms_p95=round(float(np.percentile(t_ms, 95)), 2),
        solve_ms_max=round(float(t_ms.max()), 2),
        solve_ms_sum_s=round(float(t_ms.sum()) / 1000, 3),
        peak_wset_self_mb=round(getattr(mi, "peak_wset", mi.rss) / 2**20, 1),
        peak_sampled_total_mb=round(sampler.peak_total / 2**20, 1),
        peak_sampled_children_mb=round(sampler.peak_children / 2**20, 1),
        lineup_set_sha256=hashlib.sha256(keystr.encode()).hexdigest()[:16],
        obj_first=objs[:3],
        obj_sum=round(float(sum(o for o in objs if o is not None)), 3),
        objs=objs,
    )
    if a.task == "seq150" and keys:
        # max pairwise overlap actually achieved (by player id)
        sets = [set(k) if a.contest == "classic" else {k[0], *k[1]} for k in keys]
        mx = 0
        for i in range(len(sets)):
            for j in range(i):
                mx = max(mx, len(sets[i] & sets[j]))
        res["max_pairwise_overlap"] = mx
    print(json.dumps(res))


if __name__ == "__main__":
    main()
