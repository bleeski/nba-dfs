# C04: Contest facts, injury report, Floor portfolio, brief-lite

**State:** Floor (reaches milestone M1). **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C03. **Parallel with:** C05.

## Goal, and why it sits here

Produce the first real, sensible, injury-scrubbed upload file from real files: contest facts with an honest status label, the official injury report parsed and applied, a projection-ranked Floor portfolio under the concentration cap and the sanity check, `dfs night --floor`, and the brief-lite with the "if the engine is down" card. This is milestone M1 and rehearsal 1 on Thursday Oct 15. The Floor is the opening-night fallback no matter what else ships.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 2.3, 2.4, 2.6, 3.2, 6 (`simple_points` only), 10 (`floor_portfolio`, `SanityReport`, `NightPortfolio`), 12 (Brief), 13, 15 (`facts`, `select`, `concentration`).
2. `docs/ARCHITECTURE.md` section 3 component rows 4, 13, 14, 18, 21; section 6 "Guardrails (in code)"; section 8 "A typical night" (the Floor rows), "Fallback ladder", and "The if the engine is down card".
3. `docs/adr/ADR-023-release-states-and-feature-flags.md` (the Floor and the sanity check), `docs/adr/ADR-006-solver-and-candidate-generation.md` (the solver), `docs/adr/ADR-019-delivery-first-only-validity-blocks.md` (with its revision note).
4. `docs/research/R4-data-sources.md` section 4.3 (the injury report: URL patterns, cadence, parser evidence) and `spikes/data/s03g_injury_pdf_parse_v3.py` (the working parser to port).
5. `docs/research/R8-user-nba-history.md` (paid-share facts) and `spikes/history/nba_entry_history.py` (the parser to port, per ADR-018).
6. `docs/review/ADJUDICATION.md` entry 1 only (contest facts status).

## Scope

**Build:**

- `facts/contests.py`: `ContestFacts` per contest (CONTRACTS 3.2): type classification from the name; field size from a pasted table, the entry-history template, the prize pool in the name, or the entries file's capacity; `k_top1`, `places_paid`, the payout curve (exact from a paste; parametric default by type and size bucket), `top1_pool`, `facts_status`, `facts_source`. A cache `data/contest_facts_cache.json` keyed by (name pattern, fee, field size bucket) so a contest seen before is "template" without a new paste.
- `facts/payout_paste.py`: the paste parser (CONTRACTS 2.3) with tests on five real DraftKings payout layouts (GPP, double-up, satellite, top-N, Showdown GPP).
- `facts/entry_history.py`: the ported 14-column parser with tests on the owner's real export.
- `ingest/injury_report.py`: fetch the latest official injury report PDF trying both naming patterns (15-minute slots; hourly file by last-modified), snapshot it, parse rows (port the v3 spike parser), map statuses; `dfs status` prints the diff since the last run; the fetch is rate-limited and fails soft (the brief marks "not checked for injuries").
- `projections/simple.py`: `simple_points` per pool player: last-season DraftKings points per minute times last-season minutes per game from `fixtures/history/player_box_2026.parquet` (loaded directly here; the full history layer is C05), salary-implied points when no history (a linear fit of points on salary from the same file); `p_active = 0` for Out, 0.25 Doubtful, 0.55 Questionable, 0.9 Probable (settings).
- `select/floor.py`: `floor_portfolio(slate, simple_points, settings)`: one solver run per entry (GLPK via `swiglpk`, OR-Tools CBC fallback; Hall formulation; deterministic tie-break) maximizing `simple_points` with a small fixed perturbation per entry index so entries differ; players with `p_active < 0.5` excluded; the concentration cap applied as a feasibility-tested soft preference (compute the minimum feasible cap for the pool and entry count, use the stricter of that and the setting, report relaxation); `assign_slots` placing later-game players in UTIL then G/F; the sanity check (`SanityReport`); `release_state = "floor"`; Goal 1 and Goal 2 `None`.
- `dfs night --floor`: ingest, facts, injury report, Floor portfolio, validate, export one file per slate, write the brief-lite; `dfs out`/`dfs in` in Floor mode re-run the Floor with the fact applied (the full re-solve is C10).
- `brief/lite.py`: one page per slate: the four states, the latest file and its "valid until", the Floor file, contests with `facts_status`, players removed and why, the sanity report, "Goal 2 not estimated", capabilities off, and the "if the engine is down" card (`dfs status`, `dfs out "Name"`, `dfs in "Name"`, `dfs repair`).

**Out of scope:** the simulation, the field, the settlement, Goal 1 and Goal 2 numbers, the researcher, observed-entries capture (C14).

## Contracts

- **Consumes:** `Slate`, `EntriesFile` (C02); `validate`, `export`, `Ledger`, `repair` (C03); fixtures from C01.
- **Produces:** `ContestFacts`, `PayoutCurve`, the injury-report adapter and its snapshot format, `simple_points` on `PlayerProjection`, `floor_portfolio`, `SanityReport`, `NightPortfolio` (Floor), the brief-lite, `dfs night --floor`.

## Definition of done

- Contest classification tests on 20 real contest names from the owner's entry history (gpp, double-up, satellite, top-N).
- Payout paste tests on five layouts; the parametric default sums to the pool and respects the first-place cap.
- Injury-report tests: both March 2026 PDFs parse with 0 unrecognized statuses; both URL patterns are tried; a 404 fails soft with the brief label.
- Floor tests on the Oct 15 fixtures: every lineup valid; `cap_used_mean >= 0.95`; no duplicate lineup in a contest; no excluded player present; the cap honored or the relaxation reported; the sanity report `passed`; byte-identical output on two runs.
- Timing test: `dfs night --floor` end to end under 5 minutes on a 12-game synthetic slate with 150 entries.
- `dfs out "<name>"` in Floor mode removes the player and re-exports a new version with the ledger updated.

## What I check (rehearsal 1, Thursday Oct 15, before 5:00 pm CT)

With your Oct 15 entries files in Downloads, run:

```bash
uv run dfs night --floor
```

Expected: within 10 minutes, one upload file per slate named in the output, a one-page brief per slate showing your test contests with their facts status ("verified" if you pasted the payout table, otherwise "default"), any player removed as Out, and "Goal 2 not estimated". Upload each file in your browser; DraftKings must report "uploaded N of N" with N equal to your entries. Then `uv run dfs uploaded <file>` for each, re-download each entries file before its lock, and run `uv run dfs status`: every slate shows file validity "valid", confirmed upload "committed", and no mismatches. After the 6:30 pm CT lock, re-download the Classic entries file, save it as `fixtures/dk/2026-10-15/post_lock_entries.csv`, and note in PROGRESS.md what the locked cells look like.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: contest facts, paste parser, entry-history port, with tests (commit). Checkpoint 2: injury report adapter and `simple_points` (commit). Checkpoint 3: Floor portfolio, sanity check, `dfs night --floor`, brief-lite, the Oct 15 run (commit). If time runs short, checkpoint 2 can ship without the injury adapter: the brief then says "not checked for injuries" and the rehearsal still proves the upload path.

## Risks

- **The 2026-27 injury-report file naming is unknown until Oct 19.** The adapter tries both known patterns and a directory probe; a miss is a label, not a failure.
- **No preseason injury reports exist** (R4). Test on the March fixtures; the first live parse is Monday Oct 19 evening, when parser fixes are allowed.
- **The Floor's projections are crude.** That is the point: valid, injury-scrubbed, sensible. The sanity check's projection floor keeps lineups from being absurd.
- **GLPK fails to install.** OR-Tools CBC is the fallback behind the same interface (ADR-006); note it in PROGRESS.md.
