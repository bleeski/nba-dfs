# THROWAWAY SPIKE: not engine code. Purpose: run the bench_solvers.py matrix one process at a time and write raw + summary output.
"""
  python run_bench.py [--phases A,B,C,D,E,F] [--tag name]
Writes out/YYYYMMDD-HHMM_<tag>_raw.jsonl (one JSON object per run, appended as runs finish)
and   out/YYYYMMDD-HHMM_<tag>_summary.txt (table) at the end.
Timings are INDICATIVE: other agents share this laptop. Machine load is recorded around every run.
"""
import argparse
import datetime as dt
import json
import os
import platform
import subprocess
import sys
import time

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ALL = ["highs", "highs_tuned", "pulp_cbc", "ortools_cbc", "cpsat", "cpsat_mt", "scip", "glpk"]


def runs_for(phase):
    R = []
    if phase == "A":  # formulation effect: slot-assignment binaries vs player binaries + Hall rows, 20 sequential lineups
        for s in ["highs", "glpk", "cpsat", "ortools_cbc", "scip", "pulp_cbc"]:
            for f in ["slot", "hall"]:
                R.append(dict(solver=s, contest="classic", task="seq150", n=20, form=f))
    if phase == "B":  # one max-projection lineup
        for s in ALL:
            R.append(dict(solver=s, contest="classic", task="single", form="hall"))
            R.append(dict(solver=s, contest="classic", task="single", form="slot"))
            R.append(dict(solver=s, contest="showdown", task="single"))
    if phase == "C":  # 150 lineups with max-overlap cuts, repeated for determinism
        for s in ALL + ["highs_rebuild"]:
            for c in ["classic", "showdown"]:
                if s == "highs_rebuild" and c == "classic":
                    continue
                reps = 1 if (c == "classic" and s in ("highs", "pulp_cbc")) else 2
                for rep in range(reps):
                    R.append(dict(solver=s, contest=c, task="seq150", n=150, form="hall", rep=rep))
    if phase == "D":  # 500 perturbed-projection solves, repeated for determinism
        for s in ALL:
            for c in ["classic", "showdown"]:
                reps = 1 if s == "pulp_cbc" else 2
                for rep in range(reps):
                    R.append(dict(solver=s, contest=c, task="rand", n=500, form="hall", rep=rep))
    if phase == "E":  # the full 5,000-candidate job
        for s in ["glpk", "ortools_cbc", "highs_tuned", "cpsat", "scip"]:
            R.append(dict(solver=s, contest="classic", task="rand", n=5000, form="hall", procs=1))
        for s in ["glpk", "highs_tuned", "cpsat", "ortools_cbc"]:
            R.append(dict(solver=s, contest="classic", task="rand", n=5000, form="hall", procs=4))
        for s in ["glpk", "ortools_cbc", "highs_tuned", "cpsat"]:
            R.append(dict(solver=s, contest="showdown", task="rand", n=5000, procs=1))
    if phase == "F":  # bigger slate: 12 games, 240 players (trimmed: seq150 only for the three fastest sequential solvers)
        for s in ["glpk", "ortools_cbc", "cpsat"]:
            R.append(dict(solver=s, contest="classic", task="seq150", n=150, form="hall", games=12))
        for s in ["glpk", "highs_tuned", "ortools_cbc", "cpsat", "scip"]:
            R.append(dict(solver=s, contest="classic", task="rand", n=500, form="hall", games=12))
    return R


def load():
    vm = psutil.virtual_memory()
    return dict(cpu_pct=psutil.cpu_percent(interval=0.5), avail_gb=round(vm.available / 2**30, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phases", default="A,B,C,D,E,F")
    ap.add_argument("--tag", default="bench")
    ap.add_argument("--timeout", type=int, default=1500)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    raw = os.path.join(HERE, "out", f"{stamp}_{a.tag}_raw.jsonl")
    with open(raw, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(meta=True, started=stamp, python=sys.version, platform=platform.platform(),
                                cpu_count=psutil.cpu_count(), ram_gb=round(psutil.virtual_memory().total / 2**30, 1),
                                load=load(), phases=a.phases)) + "\n")
    for ph in a.phases.split(","):
        for r in runs_for(ph):
            cmd = [PY, "-W", "ignore", os.path.join(HERE, "bench_solvers.py"), "--solver", r["solver"], "--contest", r["contest"],
                   "--task", r["task"], "--seed", "7"]
            if "n" in r:
                cmd += ["--n", str(r["n"])]
            if "form" in r:
                cmd += ["--form", r["form"]]
            if "procs" in r:
                cmd += ["--procs", str(r["procs"])]
            if "games" in r:
                cmd += ["--games", str(r["games"])]
            before = load()
            t0 = time.time()
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=HERE)
                out = p.stdout.strip().splitlines()
                res = json.loads(out[-1]) if out else dict(error=p.stderr[-2000:])
            except subprocess.TimeoutExpired:
                res = dict(error=f"timeout after {a.timeout}s")
            res.update(phase=ph, rep=r.get("rep", 0), wall_s=round(time.time() - t0, 2), load_before=before, load_after=load(),
                       games=r.get("games", 6 if r["contest"] == "classic" else 1))
            with open(raw, "a", encoding="utf-8") as f:
                f.write(json.dumps(res) + "\n")
            print(ph, r["solver"], r["contest"], r["task"], r.get("n"), r.get("form"), r.get("procs", 1), "->",
                  res.get("total_s"), "s", res.get("error", ""), flush=True)
    print("RAW", raw)


if __name__ == "__main__":
    main()
