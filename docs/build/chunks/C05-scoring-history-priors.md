# C05: Scoring adapter, history, priors

**State:** Baseline. **Size:** M (one session, about 1 to 2 hours). **Depends on:** C01. **Parallel with:** C02, C03, C04 (it touches only `src/nbadfs/history/`, `src/nbadfs/scoring/`, `data/history/`, and their tests).

## Goal, and why it sits here

Give the model layer its foundations: exact DraftKings scoring with tests from real results, last season's box scores loaded from the sportsdataverse file, the `nba_api` adapter for current-season box scores and game logs (the only `nba_api` use the owner approved), and per-possession rates with shrinkage, recency decay, aging and early-season variance inflation. It can run in parallel with the Floor chunks because nothing in the Floor depends on it.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 5, 7 (scoring function only), 15 (`llm` and `redistribution` keys are not needed; read `[scenarios]` for context).
2. `docs/ARCHITECTURE.md` section 4 "Rates and early-season priors" and "Captain handling"; section 10 sources table rows for sportsdataverse and `nba_api`; section 11 "Scoring tests".
3. `docs/adr/ADR-020-scoring-adapter.md` (with its revision note), `docs/adr/ADR-016-early-season-priors.md`, `docs/adr/ADR-005-data-posture-and-source-layer.md` (revision note only: the `nba_api` scope).
4. `docs/research/R6-draftkings-mechanics.md` section 5 (the triple-double and Captain evidence) and `spikes/dk/scoring_formula_test.py`.
5. `docs/research/R3-nba-modeling.md` section 3 (rates, shrinkage, DARKO's method) only.
6. `spikes/data/s07b_sportsdataverse_parquet.py` and `spikes/data/s01_nba_api.py` (what the sources return).

## Scope

**Build:**

- `scoring/dk.py`: `score_line(box_line, rules_version="dk_nba_2026_v1") -> (util_points, cpt_points)`: points, threes, rebounds, assists, steals, blocks, turnovers, double-double +1.5, triple-double +3 (so +4.5 total), Captain 1.5x the bonus-inclusive total stored eighth-point exact; a vectorized version over arrays for the simulator.
- `history/sportsdataverse.py`: load `player_box_<season>.parquet` into the CONTRACTS 5 schema (`player_box.parquet`, `team_game.parquet`), with `starter`, minutes and the counting stats; a freshness check that reports the file's last game date and flags a lag over 24 hours.
- `history/nba_api_adapter.py`: box scores and game logs for a date range through `nba_api` (`PlayerGameLogs`, `BoxScoreTraditionalV3`), rate-limited to one request every 2 seconds, at most a setting's worth per run (default 10), every response snapshotted; never called for live games; a posture check refuses any other endpoint.
- `history/merge.py`: one history table from both sources with `source` recorded and duplicates resolved by date and source priority.
- `projections/rates.py`: `build_rates(history, as_of_date, settings) -> dict[person_key, Rates]`: per-36 and per-possession rates with empirical Bayes shrinkage toward a position and role prior, a separate recency decay per stat, an aging adjustment, team-change and coaching-change hooks (pace shrunk toward league average on a coaching change), and the early-season variance multiplier that decays with minutes played.
- `fixtures/history/`: the last-season parquet and a small `nba_api` snapshot for tests.

**Out of scope:** minutes, availability, usage shares (C06); the simulator (C07); props and lines (C06); DuckDB.

## Contracts

- **Consumes:** fixtures from C01; settings.
- **Produces:** `score_line` and its vectorized form; `player_box.parquet` and `team_game.parquet` schemas as code; `Rates`; `build_rates`; the `nba_api` adapter under the posture check.

## Definition of done

- Scoring tests: the five real triple-doubles from R6 (all +4.5, none +3), three double-double controls, synthetic lines at every 9 and 10 threshold, a quadruple-double (+4.5 total), lines where threes or turnovers would wrongly trigger a bonus, an inactive line scoring 0, and Captain cases with and without bonuses (85.875 exact).
- History tests: the 2026 parquet loads with 34,883 rows and the expected columns; `starter` is boolean; minutes sum per team-game within 0.5 of 240 plus 25 per overtime for 99% of games.
- `nba_api` tests: the adapter refuses a non-approved endpoint; honors the rate limit (timed); parses a snapshot fixture; a live smoke test against one past date is marked `slow` and skipped when offline.
- Rates tests: shrinkage pulls a 3-game player toward the prior and a 70-game player toward his own rate; recency decay weights last month more than last October; the early-season multiplier is above 1.0 on Oct 20 and decays with minutes; rates are identical on two runs.
- Backtest harness stub: `as_of_date` strictly precedes the slate date and a test proves no future rows leak.

## What I check

Run:

```bash
uv run pytest tests/scoring tests/history tests/projections/test_rates.py -q
```

Expected: all pass. Then:

```bash
uv run dfs history status
```

Expected: a line giving the last game date in the sportsdataverse file and whether `nba_api` is approved for box scores and game logs (it is), with the request budget shown.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: scoring with all tests (commit). Checkpoint 2: history loaders and the `nba_api` adapter (commit). Checkpoint 3: rates and the backtest leak test (commit).

## Risks

- **sportsdataverse's file is stale** (last updated Sept 9). Expected; that is why `nba_api` is approved for current-season box scores. The freshness check reports it.
- **`nba_api` times out** (a March 2026 issue reported timeouts). Retries with backoff, then fail soft; the brief shows history freshness.
- **Possession counts are not in the box-score file.** Estimate possessions from the standard formula (FGA + 0.44 FTA + TOV minus ORB) per team-game and record the method.
