# C04a: The Floor core: scoring, simple points, solver, Floor portfolio, brief-lite, news facts with the repair

**State:** Floor (reaches milestone M1). **Size:** L (one session, about 2 to 2.5 hours, three checkpoints). **Depends on:** C03. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the Floor applies the looser (larger) of the minimum feasible cap and the setting; `news/state.py` (the fact writer) moves to checkpoint 1 because the Status facts need it, while `dfs out`, `dfs in` and `dfs fact veto` stay at checkpoint 3; the contest-name tests read the entry-history export copied by `scripts/build_fixtures.py`; the timing test runs on the real Oct 14 Classic file with 150 synthetic entries; the owner's check expects files within 5 minutes and leaves the post-lock re-download for `dfs status` to archive. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the brief says "not checked for injuries" only for a slate with no salary file at all; otherwise it shows DraftKings `Status` with the salary file's download time. 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): DraftKings `Status` from the newest salary file drives availability, so the rehearsals are injury-scrubbed; `simple_points` falls back to DraftKings' `AvgPointsPerGame` before salary; checkpoints reordered so the Floor ships on `AvgPointsPerGame` at checkpoint 2 and the history join plus the scoring self-check against `AvgPointsPerGame` come at checkpoint 3; the triple-double rule is settled (+4.5, VERIFIED). 2026-10-14 (ADJUDICATION-R2): created from the first half of v1's C04 (R2-1: the old C04 is split into C04a, the M1 core, and C04b, the injury report and payout facts). The scoring function moves here from C05 because the history file has no fantasy points or salary (R2-11, VERIFIED V-R2-5); the history join uses the team-free person key (R2-9); facts supersede by attribute (R2-10).

## Goal, and why it sits here

Produce the first real, sensible upload file from real files: contest facts with an honest status label, fantasy points computed from last season's box scores, a projection-ranked Floor portfolio under the concentration cap and the sanity check, `dfs night --floor`, the brief-lite with the "if the engine is down" card, and `dfs out` / `dfs in` writing facts and running the legal repair. This is milestone M1 and rehearsal 1 on Thursday Oct 15. The Floor is the opening-night fallback no matter what else ships.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` the "Person key" preamble; sections 2.1 (the `AvgPointsPerGame` bullet), 2.2 (Status), 3.2, 4.1, 4.2, 4.4, 6 (`simple_points` and status probabilities), 7 (the scoring function only), 10 (`floor_portfolio`, `SanityReport`, `NightPortfolio`), 11.6, 12 (Brief), 13, 15 (`[projections]`, `[facts]`, `[select]`, `[concentration]`).
2. `docs/ARCHITECTURE.md` section 3 component rows 4, 13, 14, 18, 21; section 6 "Guardrails (in code)"; section 8 "A typical night" (the Floor rows), "Fallback ladder", and "The 'if the engine is down' card".
3. `docs/adr/ADR-023-release-states-and-feature-flags.md` (the Floor and the sanity check), `docs/adr/ADR-006-solver-and-candidate-generation.md` (the solver), `docs/adr/ADR-019-delivery-first-only-validity-blocks.md` (with its revision note), `docs/adr/ADR-020-scoring-adapter.md` (the scoring rules and the eighth-point rule).
4. `docs/reference/NBA Classic.txt` and `docs/reference/NBA Showdown Captain Mode.txt`, the scoring sections only.
5. `spikes/solvers/bench_solvers.py`: only the GLPK (`swiglpk`) wrapper and the Hall formulation functions (about 200 lines); this chunk owns the solver wrapper `select/solver.py` that C08 and C09 consume.
6. `spikes/data/s07b_sportsdataverse_parquet.py` (the history file's columns: `athlete_id`, `athlete_display_name`, counting stats, `minutes`; no salary, no fantasy points).
7. `docs/review/ADJUDICATION.md` entry 1 only (contest facts status).

## Scope

**Build:**

- `scoring/dk.py`: `score_line(stats, rules_version) -> (util_points, cpt_points)` (CONTRACTS section 7), a small pure function: points 1, three-pointer 0.5, rebound 1.25, assist 1.5, steal 2, block 2, turnover -0.5, double-double 1.5, triple-double 3; Captain 1.5 times the bonus-inclusive total. A triple-double earns both bonuses (+4.5 in total): VERIFIED by R6's real exports and again on last season's data against DraftKings' own averages (ADJUDICATION-R2 V-R2-17), so it is a fixed rule, not a setting. C05 reuses this function and adds the vectorized form, versioning and self-checks.
- `facts/contests.py` (defaults only; C04b adds pastes, entry history and the cache): `ContestFacts` per contest (CONTRACTS 3.2) from the contest name: type classification; field size from the prize pool in the name or the entries file's capacity; `k_top1`, `places_paid` from the type's paid share, the parametric default payout curve, `top1_pool`; `facts_status = "default"`, `facts_source = "default:<type>"`.
- `projections/simple.py`: `simple_points` per pool player (CONTRACTS section 6), in this order: (1) **history**: load `fixtures/history/player_box_2026.parquet` directly (the full history layer is C05), match each pool player by `identity.match` against the file's names (any team), follow `athlete_id`, and use last regular season's DraftKings points per minute (from `score_line`) times last regular season's minutes per game; (2) **`dk_average`**: `AvgPointsPerGame` from the file when above 0; (3) **salary-implied**: a linear fit of last season's DraftKings points per game on tonight's salary across matched players in tonight's pool. `identity_ambiguous` players always salary-implied; Captain 1.5 times UTIL; never preseason box scores. Checkpoint 2 ships with sources (2) and (3) only; checkpoint 3 adds (1).
- `facts/dk_status.py`: read `Status` from the newest salary file for each slate fingerprint (CONTRACTS 2.2), write `dk_status` facts through `news/state.py`, and map codes with `projections.dk_status` (unknown codes 0.55, flagged); `p_active` comes from these facts (and from the official report once C04b exists); the brief shows the salary file's download time.
- `select/solver.py`: the one solver wrapper for the whole engine (GLPK via `swiglpk`, OR-Tools CBC fallback behind the same interface; Hall formulation; persistent model with replaceable objective; no wall-clock limit; deterministic tie-break keyed by `person_key`), ported from the spike; C08 and C09 consume it and never port it again.
- `select/floor.py`: `floor_portfolio(slate, simple_points, settings)`: one solver run per entry through `select/solver.py` maximizing `simple_points` with a small fixed perturbation per entry index so entries differ; players with `p_active < 0.5` excluded; the concentration cap applied as a feasibility-tested soft preference (compute the minimum feasible cap for the pool and entry count, use the looser (larger) of that and the setting, reporting the relaxation); `assign_slots` placing later-game players in UTIL then G/F; the sanity check (`SanityReport`); `release_state = "floor"`; Goal 1 and Goal 2 `None`.
- `news/state.py`: the `NewsState` file (live or drill folder per `Paths`), append-only; `FactRecord` with the attribute map, supersession by `(person_key, game_id, attribute)`, the precedence rule, `vetoed`, and `acts` (CONTRACTS 4.2); `ruled_out(news_state, slate) -> set[person_key]` reads the availability attribute only.
- `dfs out "<name>"`, `dfs in "<name>"`, `dfs fact veto <fact_id>`: match the name with the person-key rules (an ambiguous match prints numbered choices and requires a number, even with `--yes`), write the fact, and, unless `--no-run`, run the **legal repair** (C03, stage 1) on the latest committed lineups (CONTRACTS 4.4: the flag-off path is always the repair, never a Floor rebuild over an uploaded file). `dfs night --floor` is the explicit rebuild. All honor `--night` and `--as-of` (drill mode).
- `dfs night --floor`: ingest, default facts, simple points, Floor portfolio, validate, export one file per slate, write the brief-lite. The brief shows the DraftKings `Status` applied and the salary file's download time; only for a slate with no salary file at all (and, before C04b, no official report) does it say "not checked for injuries".
- `brief/lite.py`: one page per slate: the four states, the latest file and its "valid until", any tight rows, the Floor file, contests with `facts_status`, players removed and why, identity warnings, the sanity report, "Goal 2 not estimated", capabilities off, and the "if the engine is down" card with the five fallback lines (`uv run dfs out "Name" --no-run`; `uv run dfs repair --slate <slate>`; upload in the browser; `uv run dfs uploaded <file>`; `uv run dfs status`).

**Out of scope:** the injury report, `dfs status --apply`, payout pastes, the entry-history parser and the facts cache (all C04b); `dfs start` (C11a); the simulation, the field, the settlement, Goal 1 and Goal 2 numbers, the researcher.

## Contracts

- **Consumes:** `Slate`, `EntriesFile`, `identity.match` (C02); `validate`, `export`, `Ledger`, `repair`, `Clock`, `Paths` (C03); fixtures from C01.
- **Produces:** `score_line`; `ContestFacts` with default status; `simple_points` and `simple_points_source` on `PlayerProjection`; `select/solver.py`; `floor_portfolio`, `SanityReport`, `NightPortfolio` (Floor); `NewsState` and fact supersession; `dfs out`, `dfs in`, `dfs fact veto` (repair path); the brief-lite; `dfs night --floor`.

## Definition of done

- Scoring tests: hand-computed lines including a double-double, a triple-double, a Captain line with an odd rebound count (an eighth-point value), and a pair of players whose rebounds and assists make their fantasy ranking differ from their ordinary points ranking.
- Simple-points tests: a schema check against the real parquet (no salary or fantasy column is assumed); on the Oct 14 Classic file a player traded since last season (Giannis Antetokounmpo, MIL to MIA) gets his history; a player with no history but `AvgPointsPerGame > 0` gets `dk_average`; a rookie with `AvgPointsPerGame = 0` gets the salary-implied value, labeled; an ambiguous identity gets the salary-implied value.
- Scoring and join self-check (checkpoint 3): on the Oct 14 Classic file, last season's DraftKings points per game recomputed with `score_line` over every game played (playoffs and play-in included) equals `AvgPointsPerGame` within 0.01 for at least 80% of matched players and within 0.5 for at least 95% (the design measured 189 and 220 of 224, V-R2-16).
- Status tests: on the Oct 14 Classic file the 8 `OUT` players are excluded from every Floor lineup, the 54 `Q` players carry `p_active = 0.55`, an unknown code is flagged, and a newer salary file replaces an older one's statuses.
- Contest classification tests on 20 real contest names from the owner's entry-history export (`fixtures/history/entry_history.csv`, copied by `scripts/build_fixtures.py`) (gpp, double-up, satellite, top-N); the parametric default sums to the pool and respects the first-place cap.
- Fact tests: restriction then starter, starter then restriction, and an unrelated availability fact all keep the restriction; two `out` facts in different games applied in either order never revert each other; an ambiguous `dfs out` with `--yes` still asks for a number; `dfs fact veto` stops a fact acting and is recorded.
- Floor tests on the Oct 15 fixtures: every lineup valid; `cap_used_mean >= 0.95`; no duplicate lineup in a contest; no excluded player present; the cap honored or the relaxation reported; the sanity report `passed`; byte-identical output on two runs.
- Timing test: `dfs night --floor` end to end under 5 minutes on the real Oct 14 Classic file (7 games, 288 players) with 150 synthetic entries added.
- `dfs out "<name>"` in Floor mode removes the player through the repair and re-exports a new version with the ledger updated, leaving every other row unchanged.

## What I check (rehearsal 1, Thursday Oct 15, before 5:00 pm CT)

With your Oct 15 entries files in Downloads, run:

```bash
uv run dfs night --floor
```

Expected: within 5 minutes, one upload file per slate named in the output, a one-page brief per slate showing your test contests with their facts status ("default" until you paste payout tables after C04b), "injury status from DraftKings Status, salary file downloaded at <time>" with any players removed as OUT (no official injury reports exist in preseason), and "Goal 2 not estimated". Download the salary files together with the entries files before running. Upload each file in your browser; DraftKings must report "uploaded N of N" with N equal to your entries. Then `uv run dfs uploaded <file>` for each, re-download each entries file before its lock, and run `uv run dfs status`: every slate shows file validity "valid", confirmed upload "committed", and no mismatches. After the 6:30 pm CT lock, re-download the Classic entries file and leave it in Downloads; the next `dfs status` archives it under `data/archive/2026-10-15/` and `scripts/build_fixtures.py` makes the fixture from it; note in PROGRESS.md what the locked cells look like.

## Size estimate and checkpoints

About 2 to 2.5 hours, ordered so milestone M1 comes first. Checkpoint 1: `score_line`, default contest facts, `news/state.py` (the `NewsState` file, the fact writer and supersession, which the DraftKings Status facts need), DraftKings Status facts, `simple_points` from `dk_average` and salary, the solver wrapper (commit). Checkpoint 2 (the M1 core): the Floor portfolio with the cap and sanity check, `dfs night --floor`, brief-lite, the Oct 15 run (commit). Checkpoint 3: the history route for `simple_points` and the scoring self-check against `AvgPointsPerGame`; `dfs out`, `dfs in`, `dfs fact veto` through the repair, on the news state built at checkpoint 1 (commit; if time runs short, this checkpoint moves to the start of C11a, and PROGRESS.md says so, because rehearsal 2 on Friday is the first live use of the news commands).

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates). This chunk closes milestone M1: record C01 to C04a usage together in PROGRESS.md; if it passes about 35% of a weekly window, the Floor-only branch applies (BUILD_PLAN "Build usage budget").

## Risks

- **DraftKings may offer no Classic slate on a 2-game Thursday.** The owner checks the lobby Wednesday night; if so, Thursday rehearses the Showdown path and Friday the Classic path; say so in PROGRESS.md.
- **Preseason minutes mislead `simple_points`.** Use last regular season's minutes and rates only; the sanity check's projection floor catches absurd lineups.
- **`AvgPointsPerGame` ages.** After Oct 20 DraftKings' average becomes a small current-season sample; the history route stays the long-term primary and `dk_average` the fallback.
- **Preseason `Q` tags are common** (54 of 288 on Oct 14). They stay eligible at 0.55; the brief lists them so the owner can rule players out with `dfs out`.
- **The Floor's projections are crude.** That is the point: valid, injury-scrubbed, sensible.
- **GLPK fails to install.** OR-Tools CBC is the fallback behind the same interface (ADR-006); note it in PROGRESS.md.
