# C07: Night simulator

**State:** Baseline. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C05, C06. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): this chunk assembles `NightInputs`; historical closing lines are paid-only, so `team_game` lines stay empty and margins are calibrated against last season's net-rating difference, labeled; the reading list names the R3 spike output; the owner's check runs in drill mode; the header's dependency note is dropped. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): `dfs sim` writes scenario files under the run folder in live mode and under the drill folder in drill mode (CONTRACTS 1.1). 2026-10-14 (ADJUDICATION-R2): `points_util` and `points_cpt` are float32 holding exact eighth points, never float16, with a test on the dtype and on every Captain value times 8 being an integer (R2-4, CONTRACTS section 7 precision rule, ADR-029); scoring uses C05's vectorized `score_line`, which extends C04a's function (R2-11); the Captain definition-of-done line is exact, with no float32 rounding tolerance; usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Simulate the whole night tens of thousands of times, bottom-up and stat by stat, with shared game, team and player factors, availability draws, blowout and overtime effects, the symmetric model-error layer, DraftKings scoring, and determinism by construction, then prove it against last season's box scores. Everything that follows (field, settlement, selection, Goal 1 and Goal 2) runs on these scenarios, so the simulator must be calibrated before it touches a slate.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 5 (the `team_game.parquet` bullet: its lines stay empty), 6 (as consumed), 7 (all, including the precision rule), 15 (`[scenarios]`).
2. `docs/ARCHITECTURE.md` section 4 "The simulator", "Correlation, and what it means for Classic and Showdown", "Captain handling", "Distributions and definitions"; section 2 "Three kinds of uncertainty in every scenario" (the MVP carries outcome noise and symmetric error only); section 11 "Model tests" (the calibration targets).
3. `docs/adr/ADR-002-one-shared-stat-level-night-simulation.md` (with its revision note), `docs/adr/ADR-021-determinism.md`, `docs/adr/ADR-027-spike-is-a-mechanics-benchmark-only.md`, `docs/adr/ADR-029-settlement-v2-single-tie-split-joint-ranks-realized-outcomes.md` (the "Field interface" bullet: scores are float32 or integer eighths, never float16, never rounded to two decimals).
4. `docs/research/R3-nba-modeling.md` section 4 (the simulation structure) and the R3 spike output `spikes/modeling/out/20261013-1644_sim_shape_and_mc_error.txt` (Monte Carlo error, and fantasy-point tails against a normal approximation).
5. `docs/reference/NBA_DraftKings_DAG_Expanded.md` sections 3.2 and 3.3 (possessions, opportunities, conversions) as the structural reference.
6. `docs/review/ADJUDICATION.md` entry 16 only.
7. `spikes/night/night_spike.py`: only the night-generator function (the one that builds the synthetic players, teams, games and contests; about 150 lines near the top) so this chunk can serialize `fixtures/synthetic/night8.json`; do not read the rest of the file.

## Scope

**Build:**

- `sim/game.py`: per game and scenario: a pace factor shared by both teams; the final margin around the spread; overtime more likely when the margin is small (target 5% to 6%); a team offensive-efficiency factor centered on the implied team total.
- `sim/minutes.py`: availability draws from `p_active`; minutes from each player's role distribution (truncated normal core on 0 to 48); blowout trims above about 15 points (starters lose, bench gains); early exits with a small probability; reconciliation to 240 plus 25 per overtime per team in every scenario; `hard_cap` honored; the share model applied in scenarios where a questionable player sits.
- `sim/stats.py`: **bottom-up order:** team possessions from pace; each active player's attempts (two-point, three-point, free-throw) from possessions times usage share times minutes, with a shared per-player "big night" factor and stat-specific overdispersion (negative binomial counts); makes from shrunk conversion percentages adjusted by the team efficiency factor (a hot star raises team points; he does not steal makes from teammates); rebounds allocated from both teams' simulated misses; assists as a share of the team's made shots; steals and blocks on opponent possessions and attempts; turnovers from usage. Model error: per-scenario team and player expectation shifts drawn once per scenario (CONTRACTS 7 `model_error`), sized by salary tier and role with October inflation; **no ownership shock and no edge-uncertainty weight in the MVP** (C16).
- `sim/score.py`: DraftKings scoring (C05's vectorized `score_line`, which extends the scalar function from C04a) on every simulated line; Captain points 1.5x the bonus-inclusive total. `points_util` and `points_cpt` are float32 holding exact eighth points (UTIL values are quarter-point multiples, Captain values eighth-point multiples, both exact in float32), never float16 and never rounded to two decimals (CONTRACTS section 7 precision rule; ADR-029). The float16 allowance in CONTRACTS section 7 covers `minutes` only, never points.
- `sim/night.py`: assembles `NightInputs(projections, slates, news_state, lines)` (CONTRACTS section 7) from C06's `ProjectionTable` and lines, C02's slates and C04a's news state; `simulate(night_inputs, set_name, settings) -> ScenarioSet` for the four named sets with their sizes; every draw keyed by `(run_seed, set_name, scenario_index, game_id, person_key, stat)` through a counter-based generator; `simulate_game` re-runs one game with changed availability and leaves every other game's columns byte-identical (the re-solve relies on this).
- `sim/calibrate.py` and tests: run the simulator on last season's games and compare with box scores; historical closing lines are paid-only, so `spread_close` and `total_close` stay empty (CONTRACTS section 5), margins are centered on last season's net-rating difference between the two teams in place of the closing spread, and totals on the season average, both labeled "net-rating proxy" in the calibration report: margin standard deviation about 13; total standard deviation about 18; overtime 5% to 6%; 20-plus-point games about 19%; starter standard deviation 0.22 to 0.25 of the mean; double-double and triple-double rates by role within 20% relative; coverage of the 80% range for points between 75% and 85%; teammate correlation near zero to slightly negative and opponent correlation slightly positive by role pair.
- `dfs sim --slate <key> --set screening`: writes a `ScenarioSet` under `runs/<run_id>/scenarios/` in live mode and under the drill folder (`runs/drills/<drill_id>/`) in drill mode (CONTRACTS 1.1), and prints summary statistics (medians, 99th percentiles, boom and bust rates per player) so the owner can eyeball a slate.
- `fixtures/synthetic/night8.json`: the R9 synthetic 8-game night (players, teams, base minutes, rates, games with spread and total, the contests list) serialized from the spike's generator with its default seed, with a loader test; C08 and C09 consume it for their mechanics regressions.

**Out of scope:** the field, settlement, candidates, the ownership shock, edge uncertainty, rotation regimes (backlog).

## Contracts

- **Consumes:** `ProjectionTable` and lines (C06), `Slate` (C02), `NewsState` (C04a), `score_line` and its vectorized form (C04a, vectorized and versioned by C05), settings.
- **Produces:** `NightInputs` (assembled); `ScenarioSet` for the four sets; `simulate`; `simulate_game`; the calibration report format `runs/<id>/calibration.json`.

## Definition of done

- Calibration tests pass against last season for every target above, on at least 200 held-out games.
- Determinism: two runs give byte-identical arrays; re-simulating one game with a player ruled out leaves every other game's columns identical.
- Reconciliation: minutes sum to 240 plus 25 per overtime in every scenario for every team (exact to 0.01).
- Captain points equal 1.5x UTIL points for every player and scenario, exactly (zero tolerance).
- Precision test (CONTRACTS section 7 precision rule; ADR-029): `points_util` and `points_cpt` have dtype float32 (never float16); every UTIL value times 4 and every Captain value times 8 is an integer in every scenario.
- Runtime: 30,000 scenarios for a 12-game night under 60 seconds on this laptop (the R9 spike did 8 games in 6.7 seconds; the bottom-up order costs more); recorded in PROGRESS.md.
- Memory: the reporting set for a 12-game night under 1 GB.
- Mechanics regression (ADR-027): on `fixtures/synthetic/night8.json`, game totals and margins match the spike's summary statistics within Monte Carlo tolerance (this checks the game layer's arithmetic only; player tails are expected to differ).

## What I check

Run on the saved Oct 16 files in drill mode:

```bash
uv run dfs sim --slate classic_main --set screening --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"
```

Expected: a table of tonight's players with median, 99th-percentile and boom rate; stars near the top; players ruled out at zero; no player with a 99th percentile above about 110 DraftKings points. Then:

```bash
uv run pytest tests/sim -q
```

Expected: all pass, including the calibration tests.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: game and minutes layers with reconciliation and determinism tests (commit). Checkpoint 2: the bottom-up stat layer, scoring, the four sets (commit). Checkpoint 3: calibration against last season, `dfs sim`, the mechanics regression (commit).

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates until measured). If the session passes 50% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **Calibration misses a target.** Adjust the named setting (overdispersion shapes, blowout trim slope, early-exit rate), never a hidden constant; record the before and after in PROGRESS.md. A target still missed ships with the label "uncalibrated: <target>" in the brief.
- **Runtime over budget on 12 games.** Reduce the screening set first; profile the allocation step; chunk scenarios.
- **No closing lines for last season's games** (historical lines are paid-only, ADJUDICATION V12). Margins are calibrated around last season's net-rating difference in place of the spread, labeled "net-rating proxy"; totals on the season average with a wider tolerance.
