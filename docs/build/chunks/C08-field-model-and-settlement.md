# C08: Field model and settlement

**State:** Baseline. **Size:** L (one session, about 2.5 to 3 hours, three checkpoints). **Depends on:** C04b, C07. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the tiny tests compare every settlement fixture to its hand values to 1e-9 and check `tiny_crn_swap`'s property (the infeasible-cap and same-team cases belong to C09 and C10); `lineup_hash` comes from C01, and the reading list adds CONTRACTS section 10. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): `p_top1_any` states its one exception: a single entry uses the exact binomial (CONTRACTS section 9). 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): Showdown fields are sampled by popularity with rejection for the cap and both teams, not enumerated (a real 41-player pool has 13.6 million legal lineups); the public formula may use DraftKings' `AvgPointsPerGame`; the runtime test uses the real Oct 14 DEN@LAC pool. 2026-10-14 (ADJUDICATION-R2): the settlement follows ADR-029: one tie split with top-1% attribution at the cutoff (R2-3); joint ranks in every field size, no additive mode (R2-5); expected outputs for Goal 1 and one portfolio-independent realized outcome per scenario for Goal 2 and every probability (R2-2); the field exposes `p_above` and `p_equal` on exact eighth-point scores with an exact top tail and a fitted upper tail, never float16 (R2-4); settlement takes lineup hashes; a labeled salary-use prior for casual Showdown entrants (R2-23); depends on C04b for payout facts; usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Build the opponents and the money. The field model simulates each contest's opponents from a public view that never sees our private model, reads ownership and copy rates off it, and scores it in every scenario, keeping the top of the field exact because first-place money dominates Goal 1 in large contests. The settlement turns scores into dollars exactly as DraftKings pays: each of our entries' rank among the field and our other entries, the payout at that rank, ties split once, and from that Goal 1 (top-1% prize equity, from expected dollars) and Goal 2 (severe-drawdown probability, from realized dollars). Selection (C09) needs both.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 3.2 (as consumed), 7 (as consumed, including the precision rule), 8, 9, 10 (`lineup_hash`), 14 (`fixtures/tiny/`), 15 (`[settle]`, `[public_view]`, `[field]`, `[goal2]`).
2. `docs/adr/ADR-029-settlement-v2-single-tie-split-joint-ranks-realized-outcomes.md` in full.
3. `docs/ARCHITECTURE.md` section 2 "The settlement: from scores to dollars", "Goal 1", "Goal 2" (skip the insurance subsection); section 5 in full.
4. `docs/adr/ADR-024-goal-1-as-top-1pct-prize-equity.md` (the Copy rates and Payout facts bullets; the others are superseded by ADR-029), `docs/adr/ADR-008-field-model-from-a-public-view.md` (Decision section).
5. `docs/research/R2-optimization-methods.md` section 5.2 (Haugh and Singal's opponent model and tie splitting) and `docs/research/R9-night-benchmark.md` "Field" and "Lines" subsections for the mechanics to regression-check (read its correction note first).
6. `docs/review/ADJUDICATION.md` entries 5, 6, 9 only, and `docs/review/ADJUDICATION-R2.md` entries R2-2 to R2-5.

## Scope

**Build:**

- `field/public_view.py`: `build_public_view(slate, lines, facts_public, dff_file)`: Daily Fantasy Fuel CSV parser (the download the owner may make in a browser; its format from `spikes/data/out/downloads/projection_pages/`) and the deterministic public formula when the file is absent or empty (salary-implied value, market-implied team share, trailing DraftKings points per minute, weights in settings); DraftKings' `AvgPointsPerGame` may serve as the formula's trailing-points input (it is public, CONTRACTS 2.1); public facts applied; **a static test proves this module never imports the engine's `ProjectionTable`**.
- `field/sampler.py`: `build_field(contest_facts, slate, public_view, settings) -> FieldSample`: optimizer-like entrants (the C04a solver on public projections plus personal noise, near the cap), casual entrants (popularity-weighted picks above a salary floor; Showdown casuals weighted by salary use with `field.showdown_salary_left_decay`, a labeled BET default), chalk duplicators, stale entrants (built before the latest public facts); mixture weights by contest family; sampled as users with multi-entry users sharing cores; Showdown fields **sampled** by public popularity with rejection for the cap and the both-teams rule, never enumerated and never limited to the subset our candidates search (CONTRACTS section 8); ownership read off the sample with the sum checks (8.0; 1.0 plus 5.0); `lineup_hashes`, `copy_rate` per lineup hash (Showdown: frequency; Classic: exact matches for chalky lineups, ownership product with a correction otherwise) and `sampled_share`. Three settings bundles (default, stronger, concentrated) exist from the start for later sensitivity runs.
- `field/scores.py`: `score_field(field_sample, scenario_set) -> FieldScores` (CONTRACTS section 8): the bulk quantile grid (float32), the tail threshold, the exact weighted top tail in integer eighths with weights, and the fitted upper tail (default: an exponential excess over the sample's top 1%; any family is allowed if it passes the accuracy test), chunked over scenarios (memory under 1 GB for 30,000 scenarios and 20,000 lineups); `p_above` and `p_equal`. **No score is ever stored as float16 or rounded.** If the fit is not ready, `tail_fit_status = "unfitted"` and the brief labels first-place numbers; that never blocks the build.
- `settle/settle.py`: `settle(contest, entry_hashes, entry_points, copy_rate, field, draw_key) -> Settlement` (CONTRACTS section 9): joint ranks with our other entries in every field size; the single tie split and top-1% attribution; copies counted once (only the copy rate above `sampled_share` is added); `top1_exp` and `prize_exp` as exact expectations; `top1_draw` and `prize_draw` from one realized outcome per scenario drawn top-down on the score lattice with portfolio-independent keys; `G1`, `G1_se`, `G1_no_dup`, `p_top1_any` (from realized outcomes, except for a single entry, which uses the exact binomial because one entry has no joint dependence); `facts_status` and `tail_fit_status` carried.
- `settle/night.py`: `night_goal2(settlements, fees_total, alpha, unfilled)`: `P(SD)` from the sum of realized prizes per scenario, the literal washout, winnings mean, `p_recover_fees`, `p_meaningful_prize`, `calibrated = False` until C14 flips it; the shared-field sensitivity hook (the same user sample reused across contests on a slate) computed when the setting is on.
- `dfs field --slate <key>`: prints ownership by player, the top 20 most common lineups with copy counts, each contest's top-1% and min-cash lines by scenario quantile, and the tail fit status.
- Checkpoint 0, only if C04b deferred them: the payout-paste parser and the facts cache, because Goal 1 needs real payout curves.

**Out of scope:** selection (C09), the insurance control (C12), the ownership shock and the field family runs (C16), standings calibration (C14).

## Contracts

- **Consumes:** `lineup_hash` (C01); `ContestFacts` and the facts cache (C04a, C04b), `ScenarioSet` and `fixtures/synthetic/night8.json` (C07), `ProjectionTable` only for *our* lineups' scores (never for the public view), the solver wrapper `select/solver.py` (C04a) for optimizer-like entrants.
- **Produces:** `PublicView`, `FieldSample`, `FieldScores` with `p_above` and `p_equal`, `Settlement`, `Goal2`, `settle`, `night_goal2`.

## Definition of done

- Tiny-contest tests: every settlement fixture matches its hand values to 1e-9 (CONTRACTS section 14), including `tiny_tie_100_60` ($80 and $50), `tiny_tie_across_k`, `tiny_joint_vs_additive` (one first prize, not two), `tiny_goal2_binary` (P(severe drawdown) = 0.9, and the two-entry variant), `tiny_same_score_diff_hash`, `tiny_eighth_apart` and `tiny_conservation`; `tiny_crn_swap`'s property holds (unchanged entries keep their realized ranks). The infeasible-cap and same-team cases belong to C09 and C10.
- Precision tests: two scores 0.125 apart near 300 give different `p_above`; a static check finds no float16 in `field/` or `settle/`.
- Tail accuracy test: on a synthetic field where the truth comes from a ten-times-larger sample, first-place probability for a high-scoring lineup is within a factor of 1.5 of the truth (recorded); if not, `tail_fit_status` stays `unfitted` and PROGRESS.md records it.
- Public-view tests, three directions: a public scratch raises the beneficiary's ownership; a private fact leaves it unchanged; a change to our baseline model leaves it unchanged always; the static import test passes.
- Field tests: ownership sums; Showdown copy rates sum consistently; the most-owned Classic player falls in 40% to 60% on the saved Oct 16 slate under the default bundle (adjust the bundle's casual share if not, and record it); multi-entry users share cores.
- Settlement tests: `G1` equals exact enumeration on a 50-entry field; `G1_no_dup >= G1`; for n = 1, `p_top1_any` equals the exact binomial (the one exception to realized outcomes, since one entry has no joint dependence), and for two or more entries it comes from the realized draws; Goal 2 at `alpha` near zero equals the literal washout; payouts conserve the pool on a random 200-entry contest.
- Mechanics regression (ADR-027): on the synthetic night, the top-1% and min-cash lines agree with the spike within Monte Carlo tolerance.
- Runtime: fields and settlement for a 12-game night with 10 contests under 4 minutes at 15,000 scenarios, including the realized draws; a Showdown field on the real Oct 14 DEN@LAC pool (41 players) sampled and scored in under 30 seconds; both recorded.

## What I check

Run on the saved Oct 16 files in drill mode:

```bash
uv run dfs field --slate classic_main --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"
```

Expected: an ownership table whose top player is between about 40% and 60%, a list of the most common lineups with their copy counts, each contest's top-1% line in DraftKings points, and a line saying whether the first-place tail is "fitted" or "unfitted". The numbers should look like a real slate: stars and cheap value plays at the top, nobody above 70%.

## Size estimate and checkpoints

About 2.5 to 3 hours. Checkpoint 1: public view, the static test, the sampler, ownership and copy rates (commit). Checkpoint 2: field scores with the exact tail and the fit, `p_above` and `p_equal`, the precision and tail tests (commit). Checkpoint 3: settlement with expected and realized outputs, Goal 1, Goal 2, every tiny test, `dfs field` (commit).

## Usage budget

About 40% of a five-hour window and 8% of a weekly window (estimates). If the session passes 55% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **No Daily Fantasy Fuel file exists** (none in preseason). The formula path is the rehearsed path; the brief labels the public view "formula".
- **Memory on 12 games.** Chunk scenarios; keep the tail to `field.tail_share` of the field; store tail scores as integer eighths. Never use float16 for scores (it merges 300.375 into 300.5, ADJUDICATION-R2 V-R2-2).
- **The realized draws are slow.** Draw only bins down to the lowest of our entries' scores; vectorize over scenarios; profile before optimizing.
- **The tail fit misses its accuracy bar.** Ship with `tail_fit_status = "unfitted"` and the label; C16's field-family work revisits it.
- **Copy rates are guesses.** They are labeled "unfitted" on every number until C14's tolerances pass; Goal 1 is shown with and without them.
