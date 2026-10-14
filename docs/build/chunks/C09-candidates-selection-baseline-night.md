# C09: Candidates, selection, the Baseline night, the full brief

**State:** Baseline (reaches milestone M2). **Size:** L (one session, about 2.5 to 3 hours, three checkpoints). **Depends on:** C08, C11a (for `dfs rehearsed` and the capability gate). **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the concentration cap applies the looser (larger) of the minimum feasible cap and the setting; this chunk writes and tests `tiny_infeasible_cap_showdown.json`; in drill mode the Baseline runs regardless of the `baseline_model` flag; `lineup_hash` comes from C01; `fixtures/dk/2026-10-16/` comes from `scripts/build_fixtures.py` and Drill A's outputs are recorded in PROGRESS.md; the reading list adds CONTRACTS sections 7 and 8; scenario labels belong to C15. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): a risk line: Drill A runs without archived lines for the saved Oct 16 night. 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): Showdown candidates are every legal lineup over a measured subset of the pool (default 22 players; the real Oct 14 pool of 41 has 13.6 million legal lineups), labeled, with the players left out named in the brief. 2026-10-14 (ADJUDICATION-R2): greedy selection always uses the joint settlement (no additive mode) with exact incremental updates; the 1-1/e bound is claimed only for first-place-only contests (R2-5); `settlement_fn` takes lineup hashes (R2-4); Goal 2 and probabilities come from realized outcomes (R2-2); the determinism test runs under CPU load here; usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Turn scenarios and settlements into a portfolio: a wide candidate pool per slate, greedy selection per contest on Goal 1 with our entries ranked jointly, the feasibility-tested concentration cap, slot assignment, deterministic local improvement, the sanity check, the reporting-set numbers with their labels, `dfs night` in Baseline mode, and the full one-page brief. This is milestone M2 (a sensible portfolio) and the subject of Drill A on the saved Oct 16 files.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 7 and 8 (as consumed: `ScenarioSet`, `FieldScores`), 9 (as consumed), 10 (all), 12 (Brief), 13, 15 (`[select]`, `[concentration]`).
2. `docs/ARCHITECTURE.md` section 6 in full except "Late news and late swap" and "The ledger and the four states"; section 2 "Goal 1" and "Economic diagnostics" subsections; section 8 "A typical night" (the Build and Brief rows); section 3 component row 18 (Brief).
3. `docs/adr/ADR-006-solver-and-candidate-generation.md`, `docs/adr/ADR-007-greedy-coverage-selection.md` (Decision section), `docs/adr/ADR-029-settlement-v2-single-tie-split-joint-ranks-realized-outcomes.md` (the "Greedy as a labeled heuristic" bullet), `docs/adr/ADR-023-release-states-and-feature-flags.md` (the sanity check).
4. `docs/research/R2-optimization-methods.md` sections 4.3 (portfolio selection: greedy and lazy greedy) and 5.1 (the guarantee and its scope; ADJUDICATION-R2 V-R2-4 limits it to first-place-only contests). The solver wrapper is already built (`select/solver.py`, C04a); read its docstrings, not the spike.
5. `docs/SLATE-BRIEF-MOCK.md` (the brief's layout).
6. `docs/review/ADJUDICATION.md` entries 7 and 38 only, and `docs/review/ADJUDICATION-R2.md` entry R2-5.

## Scope

**Build:**

- `select/candidates.py`: Classic candidates through `select/solver.py` (C04a's wrapper: GLPK with OR-Tools CBC fallback, Hall formulation, persistent model, no wall-clock limits, deterministic tie-break), with single-threaded solves in worker processes merged in a fixed order: (a) per-scenario optima on a sample of screening scenarios, (b) mean minus several weights on public-view ownership, (c) game-stack variants, (d) perturbed means; canonical sort, `lineup_hash` (C01's function, consumed, not redefined), and de-duplication; pool size per settings. Showdown: `enumerate_showdown(slate, projections, settings)` lists every legal lineup over a subset of the pool (active players with projected minutes at least `select.showdown_min_minutes`, capped at the `select.showdown_pool_max` highest projected), labels the pool "searched over N of M players", names the players left out in the brief, and screens on the screening set to `showdown_keep`.
- `select/greedy.py`: `select_contest(contest_facts, pool, settlement_fn, n_entries, settings)`: greedy on the marginal gain in Goal 1 using C08's joint settlement for every field size; method `exact_incremental` (after adding an entry, recompute other candidates' gains only in the scenarios where the added entry has nonzero top-1% value), per-scenario values stored sparsely; `search_quality.greedy_bound` = "1-1/e (k=1 contest)" when `k_top1 == 1`, else "none (heuristic)"; `lazy_fallback` only if the runtime test misses, labeled; the result's `G1`, `G1_no_dup`, `p_top1_any`.
- `select/guardrails.py`: the concentration cap as a per-format feasibility-tested soft preference (minimum feasible cap computed from the pool and entry count; the looser (larger) of that and the setting applied, reporting the relaxation); no duplicate lineup within a contest; per-game exposure across formats.
- `fixtures/tiny/tiny_infeasible_cap_showdown.json` (CONTRACTS section 14), written here: six Showdown slots over nine credible players, so the minimum feasible cap is 6/9 = 66.7% per entry on average and a 60% setting cannot hold; the guardrail test below uses it.
- `select/slots.py`: slot assignment placing later-game players in UTIL then G or F (reuse C04a's `assign_slots`).
- `select/improve.py`: deterministic single-player swaps (lower public ownership at the same projection; higher expected dollars at the same raw hit rate) kept only if the gain beats two paired standard errors on the validation set and no guardrail breaks.
- `select/sanity.py`: the `SanityReport` (CONTRACTS 10) with the 85% projection floor default; labels, never blocks.
- `select/night.py`: `dfs night` Baseline mode: ingest, facts, injury state, Floor export (uploaded early), then data, projections, scenarios (four sets), public view, fields, settlements, candidates, selection, guardrails, local improvement, sanity, reporting-set numbers (Goal 2 from `night_goal2` on realized outcomes), validate, export, brief; `--no-llm` is the default (the researcher is C11b); timings recorded in the manifest; the fallback ladder honored (any failing step leaves the Floor file standing and labels the brief); release-state aware so C11a's `--game-day` runs it when the `baseline_model` capability is enabled; in drill mode the Baseline runs regardless of the `baseline_model` flag (CONTRACTS section 1), so Drill A runs before the capability is enabled, and Drill A then records `dfs rehearsed baseline_model`.
- `brief/full.py`: the full one-page brief per slate (CONTRACTS 12): states, capabilities off or stale, contests with facts status and Goal 1 three ways (prize equity in share and dollars, without duplication, raw probability) and the tail-fit label, Goal 2 labeled "model estimate, uncalibrated" with the diagnostics, concentration and per-game exposure, the cap relaxation if any, exposures table, the facts applied, not acting and in conflict, identity warnings, cached injury teams, tight rows, risks, news that would change the build, skipped steps, input freshness, the "if the engine is down" card, and the search-quality label.
- Drill A's outputs (the brief, the step timings, the sanity report) are recorded in PROGRESS.md; the saved Oct 16 files themselves come from `scripts/build_fixtures.py` (C01), which builds `fixtures/dk/2026-10-16/` from `data/archive/2026-10-16/`.

**Out of scope:** the re-solve and late swap (C10), the insurance search (C12), scenario labels (C15, after the MVP), the researcher (C11b).

## Contracts

- **Consumes:** `lineup_hash` (C01); `dfs rehearsed` and the capability gate (C11a); `ScenarioSet` and `fixtures/synthetic/night8.json` (C07), `FieldSample`, `FieldScores`, `settle`, `night_goal2` (C08), `ContestFacts`, `select/solver.py`, `assign_slots` and the Floor (C04a), `InjuryState` (C04b), `validate`, `export`, `Ledger`, the clock and drill mode (C03).
- **Produces:** `Candidate`, `CandidatePool`, `Portfolio` (with `search_quality`), `NightPortfolio` (Baseline), `SanityReport`, the full `Brief`, `dfs night` Baseline mode, `fixtures/tiny/tiny_infeasible_cap_showdown.json`.

## Definition of done

- Candidate tests: 5,000 Classic candidates on the saved Oct 16 main slate in under 60 seconds on 4 workers with 0 invalid lineups; identical lineup hashes on two runs; the Showdown enumeration count matches the combinatorial expectation for the subset; on the real Oct 14 DEN@LAC pool (`fixtures/dk/2026-10-14/`, 41 players, 37 active) enumeration plus screening is measured at `showdown_pool_max` 22 and 26 (the design counted 440,384 legal lineups for the 22 highest-average active players and 13,635,490 for all 37), the larger setting that keeps enumeration plus screening under 60 seconds is kept, and the choice is recorded in PROGRESS.md.
- Selection tests: on `fixtures/tiny/`, greedy reproduces the hand-computed best set for a 3-entry contest; on `tiny_joint_vs_additive`, greedy never values a second near-copy at a second first prize; `exact_incremental` and a full recomputation of every gain pick the same entries on a 20-entry contest; the label is "1-1/e (k=1 contest)" for a field under 200 and "none (heuristic)" for the 35,000-entry Classic; on the synthetic night, the mechanics regression against the spike's greedy (ADR-027) holds within tolerance on the top-1% hit arithmetic.
- Guardrail tests: the infeasible-cap Showdown case (`tiny_infeasible_cap_showdown.json`, written by this chunk) relaxes the cap from 60% to the minimum feasible value, 66.7%, and reports it; no contest holds a duplicate lineup.
- Sanity tests: the report flags a lineup below 85% of the slate's best projection and a lineup holding a `p_active = 0.4` player; the Baseline portfolio on the Oct 16 files passes.
- Determinism: `dfs night` twice on the same inputs gives byte-identical upload files and briefs, also under artificial CPU load.
- Runtime: the Baseline build to the main files inside 15 minutes on the saved 12-game Oct 16 slate at the four set sizes, including greedy on a 150-entry contest in a 35,000-entry field; recorded in PROGRESS.md with the step timings.
- Drill A: the brief on the Oct 16 files reads sensibly (stars at the top of exposures, no absurd lineups, Goal 2 labeled, facts status shown) and the owner's plain-language check below passes; then `dfs rehearsed baseline_model` records it, and the owner switches it on Sunday night with `dfs enable baseline_model`.

## What I check (Drill A, on the saved Oct 16 files)

Run in drill mode:

```bash
uv run dfs night --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"
```

Expected: the first line says DRILL; a Floor file per slate first, then within 15 minutes a Baseline file per slate and a one-page brief per slate, all under `runs/drills/`. In the brief: every contest shows a facts status word and three Goal 1 numbers; Goal 2 is a percentage labeled "model estimate, uncalibrated"; the exposures table's top players are stars or obvious value plays; the sanity line says "passed"; no capability that is off is presented as on. Open the upload-shaped file: 8 bare numeric IDs per Classic row, 6 per Showdown row.

## Size estimate and checkpoints

About 2.5 to 3 hours. Checkpoint 1: candidates for Classic and Showdown with tests (commit). Checkpoint 2: greedy selection with exact incremental updates, guardrails, slots, local improvement, sanity (commit). Checkpoint 3: `dfs night` Baseline mode, the full brief, the determinism-under-load test, Drill A (commit).

## Usage budget

About 40% of a five-hour window and 8% of a weekly window (estimates). If the session passes 55% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **Exact incremental greedy is slow on a 150-entry contest in a 35,000 field.** Profile first; cache per-candidate sparse values; if it still misses the runtime test, switch that contest to `lazy_fallback` with its label and record the trade in PROGRESS.md.
- **The build misses 15 minutes on 12 games.** Reduce the selection set to 10,000 and the candidate pool first; record the trade in PROGRESS.md; the Floor still ships.
- **No archived lines for the saved Oct 16 night.** The Odds API key and adapter arrive Saturday, so the saved Oct 16 night has no archived lines (historical odds are paid-only); Drill A runs with lines labeled "missing" and pace from last season's team averages.
- **The brief is longer than a page.** Cut exposures to the top 15 players and risks to 5; the layout mock is the limit.
