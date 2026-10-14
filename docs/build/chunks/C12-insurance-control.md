# C12: Insurance control

**State:** Optimizer (milestone M4). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C09. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the `insurance` capability flag (created off by C01) is the one switch; this chunk enables and rehearses it, and `[insurance] enabled` is gone from the settings. 2026-10-14 (ADJUDICATION-R2): `P(SD)` comes from realized outcomes (`prize_draw`) and the per-contest Goal 1 constraint from expected outputs (`top1_exp`); the paired comparisons rely on the portfolio-independent realized field (R2-2, ADR-029, CONTRACTS section 9 common-random-numbers test); both swap orderings (largest drawdown reduction first; drawdown reduction per expected top-1% dollar given up first) are computed on saved nights and the better kept as the frozen default (R2-24); reading list adds ADR-029; usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Make Goal 2 something the engine acts on, not only reports. The insurance control takes the Goal 1 portfolios from C09 and searches single-lineup swaps that lower the probability of a severe-drawdown night, accepting a swap only when every contest keeps its top-1% prize equity inside a budget measured with the exact paired margin from ADR-025. The spike's margin was wrong (the unpaired error of the level, which froze almost every contest), so the corrected formula is pinned here by a test. It opens M4 because its three nightly variants feed the hunch test (C13 scores them, C15 gives the verdict).

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 7 (sizes and determinism only), 9, 10 (`Portfolio`, `NightPortfolio`, `search_quality`), 12 (`Brief`), 15 (`[goal2]`, `[insurance]`, `[scenarios]`).
2. `docs/ARCHITECTURE.md` section 2 "The control: the insurance budget", "How the goals trade off, and the hunch test", "How each goal is estimated, and how precise it is".
3. `docs/adr/ADR-025-goal-2-severe-drawdown-and-insurance-control.md` in full; `docs/adr/ADR-029-settlement-v2-single-tie-split-joint-ranks-realized-outcomes.md` (the "Expected and realized outputs" bullet only).
4. `docs/review/ADJUDICATION.md` entries 8 and 9 only, plus items V1 and V2 in its "Verification log" (why the spike's margin is wrong).
5. `docs/research/R9-night-benchmark.md`: its correction note only.

## Scope

**Build:**

- `select/insurance.py`: `insure(night_portfolio, pools, settle_fn, sets, settings) -> (NightPortfolio, InsuranceResult)`. Start from each contest's best portfolio `E*_c`. Run condition: at least `insurance.min_sd_scenarios` (default 50) severe-drawdown scenarios in the validation set; otherwise the brief says "Goal 2 is too rare to trade tonight". Search single-lineup swaps in any contest. A swap is accepted only if it lowers `P(SD)` on the validation set and every contest satisfies `Delta_c - 2 x SE_paired(Delta_c) >= -epsilon x G1_c(E*_c)`, where `Delta_c = G1_c(E_c) - G1_c(E*_c)` is cumulative from `E*_c` (never measured against the previous swap) and `SE_paired` is the paired standard error: the standard error of the per-scenario differences between the two portfolios' top-1% prize values. Stop when a pass accepts nothing or at `insurance.max_swaps` (setting, default 200); the design expects about a second.
- Which outputs each side uses (CONTRACTS section 9; ADR-029): `P(SD)` is computed from realized outcomes (`prize_draw`, through `night_goal2`), never from expected dollars; the per-contest Goal 1 constraint uses expected outputs (`top1_exp`), so `G1_c` and the per-scenario differences behind `SE_paired` are `top1_exp` values. Both portfolios in a comparison are settled on the same scenarios, and the realized field does not depend on which portfolio is settled (the CONTRACTS section 9 common-random-numbers test), so the paired standard error and the change in `P(SD)` measure the swap rather than a re-drawn field.
- Swap ordering (ADJUDICATION-R2 R2-24): within the same constraint, the search can try swaps in two orders: the largest drawdown reduction first, or the largest drawdown reduction per expected top-1% dollar given up first. Compute both on the saved nights (Oct 15 and Oct 16, and any real night already saved) and keep the better as the frozen default `insurance.swap_order` (setting, `"reduction"` or `"reduction_per_dollar"`; starting value `"reduction"` until the comparison runs): better means the lower `P(SD)` after the search measured on the reporting set (not the validation set the search optimizes on, whose noise it can exploit), averaged over those nights, with ties broken by the smaller total top-1% equity given up. Both results and the choice are recorded in PROGRESS.md; the setting does not change again without a C19 challenger.
- No pre-freeze. After the search, a contest in which no candidate swap satisfied the constraint is labeled `frozen`, and the brief names it.
- Roll-back as a label: each contest is re-checked on the reporting set and flagged when more than two paired standard errors below its guarantee. If `insurance.rollback_apply` (setting, default true) reverts it, every reported number is recomputed on a fresh 30,000-scenario reporting draw (about 3 minutes, only then) and the manifest records `reporting_draw = "fresh"`.
- Three variants every night, even when the `insurance` capability is off: epsilon 0%, epsilon 20%, and the lowest-drawdown portfolio (the same search without the Goal 1 constraint), written to `runs/<run_id>/insurance/variants.json` for C13's flashback.
- `dfs night` runs the control when the `insurance` capability is enabled (C01 creates it off in `capabilities.toml` with the other seven; this chunk enables and rehearses it with `dfs rehearsed insurance`); `Portfolio.search_quality.insurance` becomes `"best found"` or `"not run"`.
- `dfs insure [--run <run_id>]`: re-runs the search on a saved night run and prints the trace (accepted swaps, `P(SD)` before and after, per-contest `Delta_c` and `SE_paired`, frozen contests, the roll-back check) without exporting.
- Brief lines: `P(SD)` before and after, swaps accepted, frozen contests, the roll-back flag, and the wording "a model-based target under stated assumptions". `insurance.epsilon = 0.02` is the starting value, re-measured on the first real nights.

**Out of scope:** scoring the variants against real standings (C13), the hunch verdict (C15), the field-strength sensitivity range (C16), any change to settlement or Goal 2 arithmetic (C08).

## Contracts

- **Consumes:** `NightPortfolio`, `Portfolio`, `CandidatePool` (C09); `settle` with its `top1_exp` and `prize_draw` outputs, `night_goal2`, `Goal2` (C08); `ScenarioSet` validation and reporting (C07); `Brief`, `RunManifest` (C09, C03).
- **Produces:** `InsuranceResult(ran, reason, p_sd_before, p_sd_after, swaps_accepted, contests: {contest_id: {g1_star, g1_final, delta, se_paired, frozen, rollback_flag}}, reporting_draw: "original"|"fresh", swap_order: "reduction"|"reduction_per_dollar")` and `InsuranceVariants(variants: {"eps_0"|"eps_20"|"min_sd": {lineups, p_sd, g1_by_contest}})`, both added to CONTRACTS.md section 10 in the same commit; `insurance.swap_order` added to section 15 `[insurance]`; the `insurance` capability flag; `dfs insure`.

## Definition of done

- The known-case test: a fixture with hand-computed per-scenario values for `E_c` and `E*_c` where the paired formula accepts the swap and the unpaired level formula (the spike's) rejects it; the test asserts `Delta_c`, `SE_paired` and the decision equal the hand values, and that the unpaired rule gives the opposite decision on the same case.
- Cumulative test: two swaps in one contest that each pass alone but fail together; the second is rejected.
- Outputs test: on `fixtures/tiny/tiny_goal2_binary.json`, `P(SD)` before the search is 0.9, computed from `prize_draw` (thresholding expected dollars would give 0); the constraint reads `top1_exp`, and a static test shows the search never thresholds an expected value.
- Paired comparison on the same field: on `fixtures/tiny/tiny_crn_swap.json`, a one-entry swap leaves every unchanged entry's realized outcome the same apart from the swapped entry's push, so the change in `P(SD)` comes only from the swap.
- Swap ordering test: both orderings run on the saved Oct 16 night and produce their own trace; the chosen default, both reporting-set `P(SD)` results and the top-1% equity given up are recorded in PROGRESS.md and in `insurance.swap_order`; `InsuranceResult.swap_order` names the ordering used.
- Run condition: 49 severe-drawdown scenarios means no search and the brief line; 50 runs it.
- Frozen label: a contest whose every candidate fails is labeled `frozen` and named in the brief.
- Roll-back: a forced reporting-set miss triggers the fresh draw; the seed differs and `reporting_draw == "fresh"`.
- Epsilon 0 returns the C09 portfolio with Goal 2 used only for ties; the three variants are written on a run with the `insurance` capability off.
- Determinism: the same inputs twice give the same accepted swaps and files.
- Timing on the saved Oct 16 night recorded in PROGRESS.md: the search (about a second expected) and the fresh draw (about 3 minutes).

## What I check

On the saved Oct 16 files, after a `dfs night` run:

```bash
uv run dfs insure
```

Expected: a short trace ending in a summary like "P(SD) 14% before, 11% after; 6 swaps accepted; frozen: none; roll-back: not flagged". Every contest's Goal 1 should show at or above 98% of its best with the paired error beside it, and the last line should say the budget is a model-based target. Then enable the `insurance` capability, run `uv run dfs night`, and confirm the brief shows the same block.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the constraint function, the paired standard error, the known-case and cumulative tests (commit). Checkpoint 2: the search, the run condition, frozen labels, the three variants, both swap orderings on the saved nights and the frozen default (commit). Checkpoint 3: the roll-back check with the fresh draw, the brief block, `dfs insure`, the capability flag (commit).

## Usage budget

About 25% of a five-hour window and 4% of a weekly window (estimates until measured). If the session passes 40% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The validation set rarely holds 50 severe-drawdown scenarios at low volume.** The control does not act and the brief says so; PROGRESS.md logs how often.
- **The search still exploits validation-set noise.** The margin exists for this; if the reporting-set check flags contests on most nights, raise `insurance.se_multiplier` (setting, default 2) and note it.
- **The fresh reporting draw blows the night's time.** It runs only when a roll-back is applied; if that is frequent, the cause is upstream noise; meanwhile the brief shows the original numbers labeled "roll-back applied, not recomputed".
- **Epsilon 2% is the wrong price.** It is a setting, re-measured on the first real nights; C15 shows the 0% and 20% variants beside it.
