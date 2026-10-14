# C09: Candidates, selection, the Baseline night, the full brief

**State:** Baseline (reaches milestone M2). **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C08. **Parallel with:** nothing.

## Goal, and why it sits here

Turn scenarios and settlements into a portfolio: a wide candidate pool per slate, greedy selection per contest on Goal 1, the feasibility-tested concentration cap, slot assignment, deterministic local improvement, the sanity check, the reporting-set numbers with their labels, `dfs night` in Baseline mode, and the full one-page brief. This is milestone M2 (a sensible portfolio) and the subject of Drill A on the saved Oct 16 files.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 9 (as consumed), 10 (all), 12 (Brief), 13, 15 (`[select]`, `[concentration]`).
2. `docs/ARCHITECTURE.md` section 6 in full except "Late news and late swap" and "The ledger and the four states"; section 2 "Goal 1" and "Economic diagnostics" subsections; section 8 "A typical night" (the Build and Brief rows); section 3 component row 18 (Brief).
3. `docs/adr/ADR-006-solver-and-candidate-generation.md`, `docs/adr/ADR-007-greedy-coverage-selection.md` (with its revision note), `docs/adr/ADR-024-goal-1-as-top-1pct-prize-equity.md` (the selection paragraph), `docs/adr/ADR-023-release-states-and-feature-flags.md` (the sanity check).
4. `docs/research/R2-optimization-methods.md` sections 2 (greedy, lazy greedy, the guarantee's scope) and 7.3 (the Hall formulation), and `spikes/solvers/bench_solvers.py` (the working GLPK wrapper to port).
5. `docs/SLATE-BRIEF-MOCK.md` (the brief's layout).
6. `docs/review/ADJUDICATION.md` entries 7 and 38 only.

## Scope

**Build:**

- `select/candidates.py`: Classic candidates from GLPK (`swiglpk`, OR-Tools CBC fallback) with the Hall formulation, a persistent model whose objective is replaced per solve, no wall-clock limits, single-threaded solves in worker processes merged in a fixed order, the deterministic tie-break: (a) per-scenario optima on a sample of screening scenarios, (b) mean minus several weights on public-view ownership, (c) game-stack variants, (d) perturbed means; canonical sort and de-duplication; pool size per settings. Showdown: full enumeration of legal lineups (about 440,000 for 22 players), screened on the screening set to `showdown_keep`.
- `select/greedy.py`: `select_contest(contest_facts, pool, settlement_fn, n_entries, settings)`: lazy greedy on the marginal gain in Goal 1 using C08's settlement (exact joint for fields under the threshold, additive above), per-scenario values stored sparsely; the result's `G1`, `G1_no_dup`, `p_top1_any`, and the "best found" label.
- `select/guardrails.py`: the concentration cap as a per-format feasibility-tested soft preference (minimum feasible cap computed from the pool and entry count; stricter of that and the setting applied; relaxation reported); no duplicate lineup within a contest; per-game exposure across formats.
- `select/slots.py`: slot assignment placing later-game players in UTIL then G or F.
- `select/improve.py`: deterministic single-player swaps (lower public ownership at the same projection; higher expected dollars at the same raw hit rate) kept only if the gain beats two paired standard errors on the validation set and no guardrail breaks.
- `select/sanity.py`: the `SanityReport` (CONTRACTS 10) with the 85% projection floor default; labels, never blocks.
- `select/night.py`: `dfs night` Baseline mode: ingest, facts, injury report, Floor export (uploaded early), then data, projections, scenarios (four sets), public view, fields, settlements, candidates, selection, guardrails, local improvement, sanity, reporting-set numbers, validate, export, brief; `--no-llm` is the default until C11 adds the researcher; timings recorded in the manifest; the fallback ladder honored (any failing step leaves the Floor file standing and labels the brief).
- `brief/full.py`: the full one-page brief per slate (CONTRACTS 12): states, capabilities off, contests with facts status and Goal 1 three ways (prize equity in share and dollars, without duplication, raw probability), Goal 2 labeled "model estimate, uncalibrated" with the diagnostics, concentration and per-game exposure, the cap relaxation if any, exposures table, the facts applied and not acting, risks, news that would change the build, skipped steps, input freshness, the "if the engine is down" card.
- `fixtures/dk/2026-10-16/`: the saved Oct 16 files (added by the owner after rehearsal 2) and Drill A's recorded outputs.

**Out of scope:** the re-solve and late swap (C10), the insurance search (C12), scenario labels (after the MVP), the researcher (C11).

## Contracts

- **Consumes:** `ScenarioSet` (C07), `FieldSample`, `FieldScores`, `settle`, `night_goal2` (C08), `ContestFacts` (C04), `validate`, `export`, `Ledger` (C03), the Floor (C04).
- **Produces:** `Candidate`, `CandidatePool`, `Portfolio`, `NightPortfolio` (Baseline), `SanityReport`, the full `Brief`, `dfs night` Baseline mode.

## Definition of done

- Candidate tests: 5,000 Classic candidates on the saved Oct 16 main slate in under 60 seconds on 4 workers with 0 invalid lineups; identical lineup hashes on two runs; the Showdown enumeration count matches the combinatorial expectation for the pool.
- Selection tests: on `fixtures/tiny/`, greedy reproduces the hand-computed best set for a 3-entry contest; on the synthetic night, the mechanics regression against the spike's greedy (ADR-027) holds within tolerance on the top-1% hit arithmetic; the exact joint settlement is used for the 1,189-entry Showdown and the additive one for the 35,000-entry Classic.
- Guardrail tests: the infeasible-cap Showdown case from `fixtures/tiny/` relaxes the cap to the minimum feasible value and reports it; no contest holds a duplicate lineup.
- Sanity tests: the report flags a lineup below 85% of the slate's best projection and a lineup holding a `p_active = 0.4` player; the Baseline portfolio on the Oct 16 files passes.
- Determinism: `dfs night` twice on the same inputs gives byte-identical upload files and briefs.
- Runtime: the Baseline build to the main files inside 15 minutes on the saved 12-game Oct 16 slate at the four set sizes; recorded in PROGRESS.md with the step timings.
- Drill A: the brief on the Oct 16 files reads sensibly (stars at the top of exposures, no absurd lineups, Goal 2 labeled, facts status shown) and the owner's plain-language check below passes.

## What I check (Drill A, on the saved Oct 16 files)

Run:

```bash
uv run dfs night
```

Expected: a Floor file per slate first, then within 15 minutes a Baseline file per slate and a one-page brief per slate. In the brief: every contest shows a facts status word and three Goal 1 numbers; Goal 2 is a percentage labeled "model estimate, uncalibrated"; the exposures table's top players are stars or obvious value plays; the sanity line says "passed"; no capability that is off is presented as on. Open the upload file: 8 bare numeric IDs per Classic row, 6 per Showdown row.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: candidates for Classic and Showdown with tests (commit). Checkpoint 2: greedy selection, guardrails, slots, local improvement, sanity (commit). Checkpoint 3: `dfs night` Baseline mode, the full brief, Drill A (commit).

## Risks

- **The settlement makes greedy slow.** Lazy greedy with cached per-candidate values; the additive mode above 10,000 entries; profile before optimizing; a 20-max in a 1,200-entry field is the hard case.
- **The build misses 15 minutes on 12 games.** Reduce the selection set to 10,000 and the candidate pool first; record the trade in PROGRESS.md; the Floor still ships.
- **The brief is longer than a page.** Cut exposures to the top 15 players and risks to 5; the layout mock is the limit.
