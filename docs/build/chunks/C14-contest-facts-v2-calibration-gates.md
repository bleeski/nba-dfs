# C14: Contest facts v2 and calibration gates

**State:** Optimizer (milestone M4). **Size:** M (one session, about 1 to 2 hours, two checkpoints). **Depends on:** C13. **Parallel with:** C16.

## Goal, and why it sits here

Make contest facts earn their labels, and let the field model earn its trust. C04 shipped contest facts with honest labels and a cache; this chunk feeds the cache from real evidence (standings files, the weekly entry-history export, pasted payout tables), captures observed entries and capacity, and fits the template payout curves. It then runs the two pre-registered calibration gates written before any standings file existed: the copy-rate tolerance that removes the "unfitted" label from Goal 1's duplication numbers, and the threshold tolerance that sets `Goal2.calibrated`. Both gates read C13's hashed standings tables.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 2.3, 2.4, 2.5, 3.2, 8 (`FieldSample.copy_rate`, `FieldScores`), 9 (`Goal2.calibrated`), 15 (`[facts]`, `[settle]`).
2. `docs/ARCHITECTURE.md` section 5 "Cold start, qualification and calibration (ADJUDICATION entry 6)", "Duplicates and copy rates", "Thresholds"; section 9 "What gets measured" (the copy-rate and settlement rows only).
3. `docs/adr/ADR-024-goal-1-as-top-1pct-prize-equity.md` (the Copy rates and Payout facts bullets), `docs/adr/ADR-008-field-model-from-a-public-view.md` (its revision note).
4. `docs/review/ADJUDICATION.md` entries 1 and 6 only.
5. `docs/build/chunks/C04-contest-facts-injury-report-floor.md`, the scope bullets for `facts/contests.py` and `facts/payout_paste.py` (what already exists).

## Scope

**Build:**

- `facts/observed.py`: `dfs facts observe <contest_id> <entries> [<capacity>]` records what the owner sees in the DraftKings lobby, timestamped, into `ContestFacts.observed_entries`, `observed_at` and `capacity`; the entries file's capacity is read when it carries one; the standings row count becomes the exact `field_size` after the contest. Before lock, field size uses, in order: a verified paste, observed entries, template, default.
- `facts/cache.py`: the C04 cache keyed by (name pattern, fee, field-size bucket) is now written by three sources: pasted tables (`verified`), the weekly entry-history export (exact field size, places paid and prize pool, `template`), and standings files (exact field size and places paid from the last paid rank, `template`). Every entry records its source and date; the newest verified source wins.
- `facts/curve_fit.py`: fit the parametric curve `prize(r) = pool x a x r^(-b)` per contest type and field-size bucket from every pasted table, with the first-place caps from `[facts]`; a fit needs at least `facts.min_tables_per_bucket` (setting, default 3) tables, otherwise the initial `b = 1.0` stays; each fit reports its worst relative error by rank band.
- `learn/calibration.py`, the copy-rate gate per format: on each standings file, take the field's 20 most common lineups and compare predicted copy count with observed; a file passes when all 20 are within a factor of 2; the gate passes when at least 4 of the first 5 files for that format pass and our entries' predicted expected copies are within 1.0 of observed on average over those files. The threshold gate: each contest's realized top-1% and min-cash cutoffs are placed inside the predicted cutoff distribution as a percentile position; the gate passes when every position over the first 5 files lies inside the predicted range and the positions are spread rather than clustered at one end (setting `calibration.cutoff_position_min_spread`, default 0.5; a judgment call). Passing the copy-rate gate flips the "unfitted" label for that format; passing both sets `Goal2.calibrated = True`. Both are re-checked weekly on a rolling window of 5 files and can flip back.
- `dfs calibration`: prints each gate's state per format with "n of 5 files seen", the per-file results and the date it flipped; the brief reads `CalibrationStatus` for its labels.
- The brief's labels live in their own module (`brief/calibration.py`) behind a one-line hook, so C16's brief additions do not collide.

**Out of scope:** fitting field shapes with shrinkage, which goes through C19's challenger workflow; the ownership shock and the field family (C16); any change to settlement arithmetic.

## Contracts

- **Consumes:** `ContestFacts`, `PayoutCurve`, the paste and entry-history parsers (C04); `StandingsTable` and the DuckDB store (C13); `FieldSample.copy_rate`, `FieldScores`, `Settlement` (C08); `NightPortfolio` (C09).
- **Produces:** `ContestFacts` with `observed_entries`, `observed_at` and `capacity` filled; `PayoutCurveFit(contest_type, bucket, a, b, n_tables, worst_error)`; `CalibrationStatus(format, copy_rates_fitted, thresholds_calibrated, files_seen, per_file, flipped_on)`; the `Goal2.calibrated` flip; `dfs facts observe`, `dfs calibration`. `PayoutCurveFit` and `CalibrationStatus` go into CONTRACTS.md in the same commit.

## Definition of done

- Cache test: a contest seen in the entry-history export is `template` on its next appearance with the exact field size and places paid, no paste needed; a later paste upgrades it to `verified`.
- Observed entries: `dfs facts observe` writes the three fields with a timestamp; the standings row count overwrites `field_size` after the contest.
- Curve fit: on five pasted tables in one bucket the fit sums to the pool, respects the first-place cap and reports its worst error; with two tables it does not fit.
- Copy-rate gate on synthetic standings files with known copy counts: 4 of 5 passing files flip the label; 3 of 5 do not; mean expected copies 1.1 off does not flip even at 5 of 5.
- Threshold gate: cutoffs inside the range and spread pass; every cutoff at the top of the range fails.
- The brief shows "unfitted" and `calibrated = False` before the gates and the new labels after; a flip is recorded in DuckDB with the file list and is reversible.
- `dfs calibration` runs under 10 seconds on 5 files.

## What I check

After five mornings of flagship downloads:

```bash
uv run dfs calibration
```

Expected: two blocks, Classic and Showdown, each reading like "copy rates: 3 of 5 files within a factor of 2 (need 4); our copies off by 0.6 on average (need 1.0): unfitted" and "thresholds: 5 of 5 cutoffs inside the predicted range, spread 0.7: calibrated". The brief's Goal 1 line should carry "unfitted" exactly when this page says so.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: observed entries, the cache sources, the curve fit, with tests (commit). Checkpoint 2: the two gates, `CalibrationStatus`, `dfs calibration`, the brief labels (commit).

## Risks

- **Fewer than five files per format by the end of October.** The gate says "n of 5" and nothing flips; Showdown may take longer because fewer are entered.
- **The 20 most common lineups are mostly singletons in small fields.** A factor of 2 on counts of 1 is weak evidence; the gate applies as written and PROGRESS.md notes the field sizes behind each pass.
- **The spread test is a judgment call.** It is a setting with its default recorded; the raw positions are printed on the `dfs calibration` page.
- **Entry history and standings disagree on field size.** The standings row count wins and the disagreement is logged.
