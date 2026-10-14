# C13: Results ingest, scorecards, contest flashback

**State:** Optimizer (milestone M4). **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C09, C12 (the `InsuranceVariants` model it scores). **Parallel with:** none.

## Goal, and why it sits here

Close the loop with real data. Every morning the owner downloads one flagship standings file per slate; this chunk parses it in the private folder, replaces other users' names with hashes, checks our scoring against DraftKings, scores each layer of last night's work against its own baseline, and runs the contest flashback: our portfolios settled against the actual opponent lineups, twice, with our real entries replaced rather than added. It introduces DuckDB (a single-file analytics database) as the learning store that C14, C15 and C19 read.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1, 2.4, 2.5, 9, 10 (`NightPortfolio`), 12 (`RunManifest`), 13.
2. `docs/ARCHITECTURE.md` section 9 in full; section 11 "Scoring tests (ADR-020)" and "Calibration metrics (tracked nightly)"; section 10 "Storage, versioning and snapshots".
3. `docs/adr/ADR-015-learning-and-model-adoption.md` (with its revision note), `docs/adr/ADR-014-reproducibility-and-storage.md` (Storage bullet, revision note), `docs/adr/ADR-020-scoring-adapter.md` (the eighth-point rule).
4. `docs/review/ADJUDICATION.md` entries 13, 24 and 27 only.
5. `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (the Skills and Hooks bullets) and the `/night` skill file from C11 under `.claude/commands/` (the pattern for `/results`).

## Scope

**Build:**

- `ingest/standings.py`: find new `contest-standings-<id>.zip` or `.csv` files in the private folder (`results.private_dir`, outside the project); refuse zero-byte or truncated files and any with `TimeRemaining` above 0 (the contest is not finished); parse the CONTRACTS 2.5 columns by header name; replace `EntryName` with `sha256(name + salt)[:12]` using `standings_salt` from `config/secrets.toml` before any row leaves the function; identify our entries by `EntryId`; write hashed rows to `data/standings/<date>/<contest_id>.parquet`. One flagship file per slate is expected; extra files are accepted.
- `learn/scoring_check.py`: recompute every player's DraftKings points from the morning box scores (the C05 history adapter) and compare with the standings `FPTS`, Captain equal to 1.5x UTIL; any mismatch is a failing scorecard row naming the player and stat.
- `learn/store.py`: `data/learn.duckdb` with tables for predictions as they stood at decision time, with their baselines, actuals, scorecard rows, flashback rows and diagnostics; `dfs results` is the only writer; Parquet for arrays.
- `learn/scorecards.py`: the fast table in ARCHITECTURE section 9, one row per layer from availability through scoring, each with its measure and the baseline the table names (for example minutes against 75% season plus 25% last five games). Entry-history rows (`facts/entry_history.py` from C04) supply our place, points and winnings per contest.
- `learn/flashback.py`: for each flagship file, remove our real entries from the standings and insert each evaluated portfolio in their place (field size unchanged), then settle with C08's `settle`: the final portfolio, the pre-QA portfolio (identical to the final until C18), the pre-fact portfolio, a simple control (maximum projection with exposure caps), a seeded random-entry benchmark, and C12's three insurance variants when `runs/<run_id>/insurance/variants.json` exists ("not available" otherwise). Twice: under the pre-lock scenario set as it stood at lock, and under hindsight-known availability and minutes with per-minute conversion re-simulated. Output per portfolio: prize equity won, winnings as a share of fees, fraction of entries cashing.
- `learn/joint_failure.py`: projection errors grouped by game and by news event; the fraction cashing; the best entry's distance from each contest's cash line; winnings as a share of fees; each against its pre-lock prediction, bootstrapped by night (resampling whole nights); an attribution when one assumption explains the night.
- `dfs results [--date <date>]`: run id mode `results`; prints the scoring check, the scorecard, the flashback table and the joint-failure notes; writes `runs/<run_id>/results.md`.
- `.claude/commands/results.md`: `/results` wraps `dfs results` with an Owns / Invokes / Does not own block and never reads the private folder.

- `learn/scorecards.py` also carries, as separate rows with their own baselines (ADJUDICATION entries 6 and 12): "LLM inferences (shadow)" (coverage of the stated minutes and usage ranges against actuals; this is what C14's blend gate reads), player-pair co-occurrence, salary left unspent, Captain combinations, exact-duplicate counts and entrant portfolio clustering in the field scorecard.

**Out of scope:** the calibration gates and template curves (C14), the economic diagnostics and readouts (C15), the weekly analyst and adoption (C19), the Showdown audit (C16).

## Contracts

- **Consumes:** `NightPortfolio` (C09), `RunManifest` (C03), `ProjectionTable` (C06), `ScenarioSet` (C07); `settle`, `FieldSample` (C08); the entry-history parser (C04); `player_box.parquet` (C05); `InsuranceVariants` (C12, optional).
- **Produces:** `StandingsTable` (the parsed, hashed model for CONTRACTS 2.5), `ScorecardRow`, `FlashbackRow`, `JointFailureReport`, the DuckDB schema, `dfs results`, `/results`. The new models and a "Learning store" section go into CONTRACTS.md in the same commit.

## Definition of done

- Parser tests on a real standings file from an Oct 15 or 16 test contest, saved hashed under `fixtures/standings/`: every `EntryName` is a 12-character hash; no raw name appears under the project (a smoke test greps `data/` and `fixtures/`); our entries match by `EntryId`; zero-byte, truncated and unfinished files are refused with a plain message.
- Scoring check: zero mismatches on the fixture, Captain rows included.
- Scorecard: every row in the section 9 table exists with a value and its baseline, or "not measurable yet" with the reason.
- Flashback: the field size after replacement equals the file's row count; the control and random rows are present; the variants rows say "not available" when C12 has not run; both passes appear; under a minute per slate.
- Joint failure: intervals by night; a synthetic two-night fixture with one shared bad assumption is attributed to it.
- `dfs results` is idempotent (a second run writes nothing new) and runs with Claude closed.

## What I check

The morning after a real night, with the flagship files in the private folder:

```bash
uv run dfs results
```

Expected: one block per slate: "scoring check: exact", a scorecard with each layer's number beside its baseline, a flashback table with rows for the final portfolio, the control, the random benchmark and the three insurance variants (or "not available"), each with prize equity and winnings share under "pre-lock" and "hindsight", and a note on any joint failure. No real user name appears anywhere.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: the standings parser with hashing, the scoring check, the DuckDB store (commit). Checkpoint 2: the scorecards and the entry-history join (commit). Checkpoint 3: the flashback, the joint-failure diagnostics, `dfs results`, the `/results` skill (commit).

## Risks

- **The real standings columns differ from CONTRACTS 2.5.** Parse by header name; record the real header in the fixture README and amend the contract in the same commit.
- **The salt or a raw name leaks.** Hashing happens inside the parser; the PreToolUse guard on the private folder stays; the grep test is in the smoke suite.
- **Box scores lag in the morning.** The scoring check uses the standings points that morning and re-runs when box scores arrive; the hindsight pass is labeled "pending box scores".
- **Few files in the first week.** Scorecards show intervals and say "n nights"; nothing is adopted from them (C19).
