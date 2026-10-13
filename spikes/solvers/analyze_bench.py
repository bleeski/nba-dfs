# THROWAWAY SPIKE: not engine code. Purpose: summarize a run_bench.py raw .jsonl into a table, determinism checks and cross-solver objective agreement.
"""python analyze_bench.py out/<stamp>_bench_raw.jsonl  -> writes out/<stamp>_bench_summary.txt"""
import json
import sys
from collections import defaultdict

import numpy as np

raw = sys.argv[1]
rows = [json.loads(l) for l in open(raw, encoding="utf-8") if l.strip()]
meta = rows[0]
runs = [r for r in rows[1:] if "solver" in r]
errs = [r for r in rows[1:] if "error" in r]
out = []
out.append(f"source: {raw}")
out.append(f"meta: {json.dumps({k: meta[k] for k in meta if k != 'meta'})}")
out.append("TIMINGS ARE INDICATIVE: other agents were running on this laptop. load_before = cpu% / available GB at run start.")
out.append("")
hdr = f"{'ph':2} {'solver':13} {'contest':8} {'task':6} {'form':11} {'gm':>2} {'n':>5} {'pr':>2} {'rep':>3} {'valid':>5} {'uniq':>5} {'total_s':>8} {'med_ms':>7} {'p95_ms':>7} {'max_ms':>8} {'peakMB':>6} {'childMB':>7} {'objsum':>11} {'hash':16} {'ovl':>3} {'load':>10}"
out.append(hdr)
for r in runs:
    load = r.get("load_before", {})
    out.append(f"{r['phase']:2} {r['solver']:13} {r['contest']:8} {r['task']:6} {r.get('form',''):11} {r.get('games',''):>2} {r['n_requested']:>5} {r['procs']:>2} {r.get('rep',0):>3} "
               f"{r['n_valid']:>5} {str(r.get('unique_lineups','')):>5} {r['total_s']:>8} {r['solve_ms_median']:>7} {r['solve_ms_p95']:>7} {r['solve_ms_max']:>8} "
               f"{r['peak_wset_self_mb']:>6} {r['peak_sampled_children_mb']:>7} {r['obj_sum']:>11} {r['lineup_set_sha256']:16} {str(r.get('max_pairwise_overlap','')):>3} "
               f"{str(load.get('cpu_pct',''))+'/'+str(load.get('avail_gb','')):>10}")
    if r.get("n_problems"):
        out.append(f"   PROBLEMS: {r['problems']}")
for e in errs:
    out.append(f"ERROR {e.get('phase')} {e.get('error','')[:300]}")

out.append("")
out.append("DETERMINISM (same config, same seed, run twice: identical ordered lineup list?)")
groups = defaultdict(list)
for r in runs:
    groups[(r["phase"], r["solver"], r["contest"], r["task"], r.get("form"), r["n_requested"], r["procs"], r.get("games"))].append(r)
for k, g in groups.items():
    if len(g) > 1:
        hs = {x["lineup_set_sha256"] for x in g}
        out.append(f"  {k}: runs={len(g)} identical={len(hs) == 1} hashes={sorted(hs)}")

out.append("")
out.append("CROSS-SOLVER OBJECTIVE AGREEMENT (per-solve optimal objective vs glpk, same task/contest/n/form/games)")
ref = {}
for r in runs:
    if r["solver"] == "glpk" and r.get("rep", 0) == 0:
        ref[(r["contest"], r["task"], r.get("form"), r["n_requested"], r.get("games"))] = r
for r in runs:
    key = (r["contest"], r["task"], r.get("form"), r["n_requested"], r.get("games"))
    if r["solver"] == "glpk" or key not in ref or r.get("rep", 0) != 0:
        continue
    a = [x for x in ref[key]["objs"]]
    b = [x for x in r["objs"]]
    m = min(len(a), len(b))
    if m == 0:
        continue
    d = np.abs(np.array(a[:m], dtype=float) - np.array(b[:m], dtype=float))
    first_div = int(np.argmax(d > 1e-6)) if (d > 1e-6).any() else None
    same_lineups = r["lineup_set_sha256"] == ref[key]["lineup_set_sha256"]
    out.append(f"  {r['phase']} {r['solver']:13} {key}: compared={m} max_abs_diff={d.max():.4f} first_diverging_index={first_div} identical_lineups={same_lineups}")

txt = "\n".join(out)
dst = raw.replace("_raw.jsonl", "_summary.txt")
open(dst, "w", encoding="utf-8").write(txt + "\n")
print(txt)
print("WROTE", dst)
