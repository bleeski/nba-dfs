# THROWAWAY SPIKE: not engine code. Purpose: turn night_spike.py JSON outputs into the tables quoted in docs/research/R9-night-benchmark.md, so no number is hand-copied.
"""python summarize_night.py label=path.json [label=path.json ...]  -> writes out/<stamp>_night_summary.txt
Expected labels: 8g_be1_S30k 8g_be1_S10k 8g_be0_S30k 2g_be1_S30k 2g_be0_S30k 8g_be1x2_S30k"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
runs = {}
for arg in sys.argv[1:]:
    k, v = arg.split("=", 1)
    runs[k] = (os.path.basename(v), json.load(open(v, encoding="utf-8")))
out = []
P = out.append


def pct(x, d=2):
    return "n/a" if x is None else f"{100 * x:.{d}f}%"


P("sources: " + "; ".join(f"{k} = {v[0]}" for k, v in runs.items()))
for k, (f, D) in runs.items():
    lb = D["meta"]["load_before"]
    P(f"{k}: load_before system_cpu={lb['system_cpu_pct']}% avail_gb={lb['avail_gb']} busy_other_python={[o for o in lb['other_python'] if o['cpu_pct'] > 1]}; "
      f"workers={D['meta']['args']['workers']}; belief={D['results']['night'].get('belief_err')}; total_wall_s={D.get('total_wall_s')}; first_full_build_s={D.get('first_full_build_s')}; memory={D.get('memory')}")
P("")

# ---------------- timing
if "8g_be1_S10k" in runs and "8g_be1_S30k" in runs:
    D10, D30 = runs["8g_be1_S10k"][1], runs["8g_be1_S30k"][1]
    P("## Timing table, 8-game night with belief layer (wall seconds, average cores busy)")
    P("| Step | S=10,000 | S=30,000 |")
    P("|---|---|---|")
    steps = list(D30["steps"].keys())
    for k in D10["steps"]:
        if k not in steps:
            steps.append(k)
    for k in steps:
        a = D10["steps"].get(k)
        b = D30["steps"].get(k)
        fa = f"{a['wall_s']:.1f} s ({a['avg_cores_busy']:.1f})" if a else "-"
        fb = f"{b['wall_s']:.1f} s ({b['avg_cores_busy']:.1f})" if b else "-"
        P(f"| {k} | {fa} | {fb} |")
    P(f"| first full build (production steps) | {D10['first_full_build_s']} s | {D30['first_full_build_s']} s |")
    P(f"production steps: {D30.get('first_full_build_steps')}")
    for nm, D in (("S10k", D10), ("S30k", D30)):
        ln = D["results"].get("late_news")
        if ln:
            P(f"late news {nm}: total {ln['total_compute_s']} s; dropped {ln['classic_candidates_dropped']} added {ln['classic_candidates_added']}; affected {ln['affected_contests']}; "
              f"swaps {ln['swaps']} pw_V_after {ln['pw_V_after']}; beneficiary proj {ln['proj_change']}")
            P("   " + "; ".join(f"{k}: {v['wall_s']} s" for k, v in ln["steps"].items()))
    P(f"sim timing by S (full night, one process): {D30['results'].get('sim_timing_s_by_S')}")
for k in ("8g_be0_S30k", "2g_be1_S30k"):
    if k in runs:
        D = runs[k][1]
        P(f"{k}: first full build {D['first_full_build_s']} s; thresholds {D['steps'].get('thresholds_AV_classic', {}).get('wall_s')} + {D['steps'].get('thresholds_AV_showdown', {}).get('wall_s')} s; "
          f"late news {D['results'].get('late_news', {}).get('total_compute_s')} s")
P("")

# ---------------- sanity and field (main run)
main = runs.get("8g_be1_S30k") or next(iter(runs.values()))
r = main[1]["results"]
for lab in ("8g_be1_S30k", "8g_be0_S30k"):
    if lab not in runs:
        continue
    ss = runs[lab][1]["results"]["sim_sanity"]
    P(f"## Sim sanity ({lab}, set A)")
    for k in ("star", "role_player", "questionable_q0", "beneficiary_all", "beneficiary_when_q0_active", "beneficiary_when_q0_out", "top_big"):
        v = ss[k]
        P(f"{k}: {v['pos']} {v['tier']} base_min {v['base_min']} mean {v['mean']} sd {v['sd']} p01 {v['p01']} p50 {v['p50']} p99 {v['p99']} DD {v['dd_rate']} TD {v['td_rate']}")
    P(f"corr teammates rotation {ss['corr_teammates_rotation_mean']} starters {ss['corr_teammates_starters_mean']} opponents {ss['corr_opponents_rotation_mean']} q0-beneficiary {ss['corr_q0_vs_beneficiary']} OT {ss['ot_rate_overall']} maxTD {ss['max_td_rate_any_player']}")
    for g in ss["games"]:
        P(f"game {g['game']}: total line {g['line_total']} sim mean {g['sim_mean_total']} over-rate {g['over_rate_vs_line']} | spread {g['line_spread']} sim margin {g['sim_mean_margin']} sd {g['sim_sd_margin']} | OT {g['ot_rate']} |drawn margin|>15 {g['blowout_rate_drawn_margin_gt15']}")
    P("")
P("## Field (main run)")
fc = r["field_classic"]
P(f"classic: {json.dumps({k: v for k, v in fc.items() if k != 'implied_ownership_150max_top15'})}")
P("classic implied ownership top 15 (150-max mix): " + "; ".join(f"{d['player']} {d['pos']} ${d['salary']} proj {d['proj']} own {d['own_pct']}% (SE150 {d['own_pct_SE150']}%)" for d in fc["implied_ownership_150max_top15"]))
for g, v in r["field_showdown"].items():
    P(f"showdown game {g}: legal {v['n_legal']} enum_s {v['enumerate_s']} pool_unique {v['pool_unique']} opt_unique {v['opt_unique']} share_of_20max_field_in_lineups_with>=2_copies {v['share_of_20max_field_in_lineups_with_ge2_expected_copies']}")
    P(f"   top expected copies 20max: {[d['expected_copies'] for d in v['top10_expected_dups_20max']]}; SE50: {[d['expected_copies_SE50'] for d in v['top10_expected_dups_20max'][:5]]}")
    P(f"   CPT own top5 {v['cpt_own_top5']}; UTIL own top8 {v['util_own_top8']}")
P(f"candidates classic: {r['cand_classic']}; bitsets V MB {r.get('bitsets_V_mb')}")
P(f"thresholds A: {json.dumps(r['thresholds_A_summary'])}")
P("")

# ---------------- washout by entry profile, with and without belief layer
P("## P(W) at eps 0 (greedy, pure goal 1), held-out B")
P("| run | " + " | ".join(["profile entries", "P(W) hit", "SE", "washout scen", "upper95 if 0", "P(W) binomial", "P(W) on V"]) + " |")
P("|---|---|---|---|---|---|---|---|")
for k, (f, D) in runs.items():
    for pk, v in D["results"]["washout_by_profile_eps0"].items():
        P(f"| {k} | {v['entries']} | {pct(v['pw_B_hit'], 3)} | {pct(v['pw_B_se'], 3)} | {v['washout_scen_count_B']} | {pct(v['pw_B_upper95'], 3) if v['pw_B_upper95'] else '-'} | {pct(v['pw_B_binom'], 3)} | {pct(v['pw_V_hit'], 3)} |")
for k, (f, D) in runs.items():
    pr = D["results"]["washout_by_profile_eps0"]
    P(f"{k} caps: " + "; ".join(f"{pk}: {v['caps']}" for pk, v in pr.items()))
    small = min(pr, key=lambda x: pr[x]["entries"])
    P(f"{k} per-contest no-cash at {small}: {pr[small]['per_contest_nocash_B']}")
    spec = sorted(pr, key=lambda x: pr[x]["entries"])[2]
    P(f"{k} per-contest no-cash at {spec}: {pr[spec]['per_contest_nocash_B']}")
P("")


def frontier_block(lab, label):
    if lab not in runs:
        return
    rr = runs[lab][1]["results"]
    t = rr[f"{label}_frontier_B"]
    names = list(next(iter(t.values()))["g1_ratio_B"].keys())
    P(f"## Frontier {lab} [{label}]")
    P("| Portfolio | swaps | secs | P(W) V | P(W) B | SE | washout scen B | diff vs eps0 (paired SE) | P(W) binomial | mean G1 loss | max G1 loss | " + " | ".join(names) + " |")
    P("|---|---|---|---|---|---|---|---|---|---|---|" + "---|" * len(names))
    for k, v in t.items():
        P(f"| {k} | {v['swaps']} | {v['secs']} | {pct(v['pw_V'], 3)} | {pct(v['pw_B'], 3)} | {pct(v['pw_B_se'], 3)} | {v['washout_scen_count_B']} | {100 * v['pw_diff_vs_eps0']:+.3f} pp ({100 * v['pw_diff_vs_eps0_se']:.3f}) | {pct(v['pw_B_binom'], 3)} | "
          f"{v['mean_g1_loss_pct_B']:.1f}% | {v['max_g1_loss_pct_B']:.1f}% | " + " | ".join(f"{v['g1_ratio_B'][n]:.3f} +/- {v['g1_ratio_B_paired_se'][n]:.3f}" for n in names) + " |")
    P("shape (overlap within 150-max / across classic contests / SD SE vs 20max; distinct classic lineups of classic entries; share of entries exposed by game):")
    for k, v in t.items():
        s = v["shape"]
        P(f"  {k}: {s['overlap_within_150max']} / {s['overlap_across_classic_contests']} / {s['overlap_sd_SE_vs_20max_same_game']}; distinct {s['distinct_classic_lineups']} of {s['classic_entries']}; "
          f"exposure {s['share_entries_exposed_by_game']}; classic entries with >=3 from game0 {s['share_classic_entries_ge3_from_game0']}")
    P(f"price of insurance (vs eps 0): {json.dumps(rr[f'{label}_price_of_insurance_B'])}")
    P("estimators (greedy portfolio, held-out): G1 quantile-threshold vs binomial; cash quantile vs binomial; scenario agreement")
    for n, d in rr[f"{label}_estimators_greedy_B"].items():
        P(f"  {n}: n={d['entries']} G1 {pct(d['g1_quantile_hit'])} vs {pct(d['g1_binomial'])}; cash {pct(d['cash_quantile_hit'], 1)} vs {pct(d['cash_binomial'], 1)}; agree {d['scenario_agreement']}")
    P("")


for lab in runs:
    frontier_block(lab, "spec")
    frontier_block(lab, "small")
for lab, (f, D) in runs.items():
    rr = D["results"]
    P(f"## Counterfactual clusters {lab}: {json.dumps(rr.get('counterfactual_clusters'))}")
    P(f"## Duplication-adjusted vs raw {lab}")
    for n, d in rr["duplication_adjusted_vs_raw_B"].items():
        P(f"  {n}: n={d['entries']} same {d['same_lineups']} jaccard {d['jaccard']}; mean copies raw {d['mean_expected_copies_raw']} dup {d['mean_expected_copies_dup']}; max copies raw {d['max_expected_copies_raw']} dup {d['max_expected_copies_dup']}; "
          f"G1 raw-port raw {d['raw_port_g1_raw']} adj {d['raw_port_g1_dupadj']} | dup-port raw {d['dup_port_g1_raw']} adj {d['dup_port_g1_dupadj']}; share cand q>0 {d['share_candidates_with_q_gt0']} min f {d['min_share_factor_candidates']}")
    P(f"swap eps05 from greedy (production setting) {lab}: {rr.get('swap_eps05_from_greedy')}")
    P("")

stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
dst = os.path.join(HERE, "out", f"{stamp}_night_summary.txt")
open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
print("WROTE", dst)
