# ADR-029: Settlement v2: one tie split, joint ranks in every field, realized outcomes for Goal 2, an exact top tail, greedy as a labeled heuristic

**Status:** Accepted. **Date:** 2026-10-14. **Supersedes in part:** ADR-024 (the Definition bullet's tie formula, the Computation bullet's additive approximation, the Selection bullet's diminishing-returns claim), ADR-025 (the Settlement bullet, for how Goal 2 is computed), ADR-007 (the 63% guarantee statement). The goals themselves are unchanged. **Source:** ADJUDICATION-R2 entries R2-2, R2-3, R2-4, R2-5 (A-R2-I-02, A-R2-I-03, A-R2-I-05, B-R2-I-01, B-R2-I-05, B-R2-I-06, X-R2-01); advisor consultation 3. **Changelog:** 2026-10-14 (R2-33, the owner's real files): Showdown candidates are enumerated over a measured subset of the pool and Showdown fields are sampled by popularity, because a real 41-player pool has 13.6 million legal lineups (see the last Decision bullet). 2026-10-14 created.

## Context

Round 2 found four defects in how the v4 settlement turned simulated scores into the owner's two money goals, each verified by a small script (ADJUDICATION-R2 V-R2-1 to V-R2-4b):

1. The tie formula divided twice: "the average of `W(r+j)` for `j = 0..D`, divided by `1 + D`" pays $40 where DraftKings pays $80 on a two-way tie over $100 and $60.
2. Goal 2 thresholded expected winnings: with a 10% chance of $100 on $10 of fees, the expected $10 clears the $2.50 threshold, so the model reports no drawdown on a night that has a 90% chance of one.
3. For fields of 10,000 or more, selection ranked each of our entries against the field alone (the "additive" approximation), which pays two first prizes for one and removes any penalty for near-copies.
4. The field was summarized by a 400-point quantile grid (about four intervals across the whole top 1%, and float16 storage that merges legitimate Showdown totals), and the settlement could not see lineup identity, while Goal 1 in a 35,000-entry contest is mostly first-place money.

Checking a fifth claim found a sixth problem: the design said the joint objective keeps diminishing returns, so greedy selection carries a 63% guarantee. A brute-force test over all subsets of five entries in 3,000 random contests found 16,700 violations in 480,000 checks; diminishing returns hold only when the payout curve, extended by its drop to zero after the last top-1% place, is convex, which in practice means contests that pay first place only (fields under 200). The round 1 claim rested on V16, which was about a different objective (the best of our entries per scenario).

## Options considered

1. **Patch the formulas only.** Fixes 1 and 2; leaves the additive double count and the coarse field.
2. **Full joint simulation of every opponent.** Exact but costs a field draw of up to 35,000 lineups per scenario per contest.
3. **Expected joint settlement for Goal 1, one portfolio-independent realized outcome per scenario for Goal 2 and every probability, a field interface with exact scores and a fitted tail, and greedy labeled as a heuristic.**

## Decision

Option 3. The contract is `docs/build/CONTRACTS.md` sections 7 to 10.

- **One tie split.** A tie group occupying ranks `r` to `r + t - 1` (opponent copies, other equal-score opponents, and our own tied entries) pays each member `sum(W(j)) / t` over those ranks. Goal 1 uses `W_top1(j) = W(j)` for `j <= k` and 0 beyond, so a tie straddling place `k` credits only the top-1% places' money. Payouts conserve the paid pool and top-1% allocations conserve the top-1% pool.
- **Joint ranks in every field size.** An entry's rank counts opponents above it and our own entries above it. The additive approximation and the `exact_max_field` threshold are deleted. Expected prizes per entry stay exact by linearity of expectation, so this costs one sort per scenario.
- **Expected and realized outputs.** Goal 1 uses expected dollars (lower noise). Goal 2 and every probability (at least one top-1% finish, recovering the fees, a meaningful prize, literal washout) use one realized joint outcome per scenario. The realization is independent of the portfolio being settled: opponent counts are drawn top-down on the score lattice with each bin keyed by (run seed, scenario set, scenario, contest, bin), and copies are keyed by `lineup_hash`, so two portfolios that differ by one entry see the same field. This keeps the insurance search's paired comparisons valid (advisor consultation 3).
- **Field interface.** The field exposes `p_above` and `p_equal` per scenario on exact eighth-point scores: a bulk grid for display and screening, the exact weighted top of the field sample, and a fitted upper tail above the sample's resolution (C08 chooses the family; default an exponential excess). Scores are float32 or integer eighths, never float16, never rounded to two decimals. Settlement takes lineup hashes so copy rates attach to the right lineup; copies are counted once. If the tail fit is not ready, first-place numbers are labeled "tail unfitted" and the Baseline still ships. Acceptance: first-place probability within a factor of 1.5 of a ten-times-larger sample on a synthetic field.
- **Greedy as a labeled heuristic.** Per-contest selection stays greedy on Goal 1, with exact incremental updates (after adding an entry, recompute gains only in scenarios where that entry has top-1% value). The 1-1/e bound is claimed only for contests with `k = 1`; elsewhere the result is "best found (heuristic)". Lazy upper bounds, valid only with diminishing returns, are a labeled fallback if the runtime test misses.

- **Showdown at real pool sizes (R2-33).** Our Showdown candidates are every legal lineup over a subset of the pool (active players above a projected-minutes floor, capped at the highest projected, default 22, measured in C09), labeled "searched over N of M players". The Showdown field is sampled by public popularity with rejection for the cap and the both-teams rule, never pruned or enumerated, so our subset cannot shape the field's thresholds or copy rates.

## Consequences

- **Results:** both goals now equal the money DraftKings would pay under the model; near-copy portfolios no longer look better than they are; Goal 2 can no longer hide a likely drawdown behind an average; first-place money in large fields stops resting on a handful of sampled opponents.
- **Cost:** about one second of draws per contest per scenario set; about 70 MB of tail storage per large contest at the selection set size; C09 measures greedy's runtime.
- **Workload:** none.
- **Tests that pin it:** the new tiny fixtures in CONTRACTS section 14 (`tiny_tie_100_60`, `tiny_tie_across_k`, `tiny_joint_vs_additive`, `tiny_goal2_binary`, `tiny_same_score_diff_hash`, `tiny_eighth_apart`, `tiny_crn_swap`, `tiny_conservation`).
