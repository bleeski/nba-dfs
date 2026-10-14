# C22: Late swap v2: live-score conditioning

**State:** Optimizer. **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C10, C13. **Parallel with:** any.

## Goal, and why it sits here

Make the post-lock swap see the scoreboard. C10's swap re-optimizes open slots with locked games still at their pre-lock distributions, so at 9:30 pm it pretends the 7:00 pm games have not happened. This chunk conditions each scenario on what is known: finished games take their actual DraftKings points (from the morning box-score source if it has them, otherwise from a standings file the owner downloads mid-slate), and in-progress games take points so far plus a remaining-time distribution with the variance scaled by the share of the game left. The scope rule from C10 stays: only entries whose news state changed or whose improvement clears the threshold are rewritten. It needs C13's standings parser. B-D-02, conditioning on the opponents' locked lineups from a mid-slate standings export, stays in the backlog with its trigger.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 2.5, 7 (`simulate_game`, determinism), 11.1, 11.5, 11.7, 15 (`[swap]`, `[resolve]`).
2. `docs/ARCHITECTURE.md` section 6 "Late news and late swap: the joint re-solve (ADR-026)", "The ledger and the four states"; section 8 "Staggered tips"; section 4 "The simulator" (how a game's arrays are drawn, to add the partial-game path); section 10 "Sources table" (box scores and the posture).
3. `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` in full; `docs/adr/ADR-005-data-posture-and-source-layer.md` (what `nba_api` may be used for under D1).
4. `docs/review/ADJUDICATION.md` entries 17, 22 and 28 only.
5. `docs/build/chunks/C10-resolve-late-swap-news-commands.md` "Scope" (`resolve/swap.py`) and `docs/build/chunks/C13-results-scorecards-flashback.md` "Scope" (`ingest/standings.py`, which this chunk reuses with one relaxation).

## Scope

**Build:**

- `resolve/live.py`: `live_state(slate, now, sources, settings) -> LiveState`: per game, `status` in finished, in progress, not started. Finished games: actual DraftKings points per player from the box-score adapter (C05's history source, under the D1 posture) when present, else from a mid-slate standings file parsed by C13's parser with `TimeRemaining` above 0 allowed only on this path and the result labeled `source = "standings_midslate"`. In-progress games: points so far per player from the same sources, and `fraction_remaining` from the game clock when the source carries it, else from `dfs live "<AWAY>@<HOME> <quarter> <mm:ss>"` typed by the owner. Not-started games untouched. Everything snapshotted.
- `sim/partial.py`: `simulate_game_partial(night, game_id, S, seed, points_so_far, fraction_remaining)`: the C07 draw for the game with each player's remaining minutes equal to projected minutes times `fraction_remaining` (hard caps respected), stat rates unchanged, the variance of the remaining draw scaled by the same fraction, and the actual points so far added; a finished game is the special case `fraction_remaining = 0` with zero variance. Keyed draws leave other games' columns untouched.
- `swap --live` (C10's `swap` given a `LiveState`): build the conditioned scenario set for the slate, re-optimize open slots against it, keep the C10 scope rule (`news_state_hash` changed or improvement at least `swap.min_improvement_points`), the concentration re-check, the diff, the "valid until" stamp and the insufficient-time rule. The brief's swap block names each game's status and source.
- `dfs swap --slate <key> --live [--standings <file>]` and `dfs live "<game> <clock>"`.
- Late-swap scorecard rows (C13): per swap night, entries rewritten, predicted against realized improvement, and when the triggering news became available against when the owner could act; these rows are the trigger evidence for backlog item B-D-02.

**Out of scope:** B-D-02 (locked-field conditioning: opponents' locked lineups from the mid-slate export; backlog until the late-swap scorecard shows how often late scratches changed our entries); B-D-03 (game-script regimes for blowouts; backlog with its own trigger); any live-odds feed; the watcher (C17).

## Contracts

- **Consumes:** `swap`, `resolve`, the drill harness (C10); `simulate_game`, `ScenarioSet` (C07); the standings parser (C13); the box-score adapter (C05); `Ledger`, `validate`, `export` (C03); `NewsState` (C06).
- **Produces:** `LiveState(slate_key, as_of, games: {game_id: {status, fraction_remaining, source, points_so_far: {person_key: float}}})`, `simulate_game_partial`, `dfs swap --live`, `dfs live`, the late-swap scorecard rows. `LiveState` and the partial-game signature go into CONTRACTS.md sections 7 and 11.5 in the same commit.

## Definition of done

- Finished game: every scenario column for that game's players equals the actual points, variance zero; a player who did not play gets zero.
- In-progress game on a hand-made fixture: the mean equals points so far plus projected minutes times the fraction remaining times the rate; the variance equals the full-game variance times the fraction; `fraction_remaining = 1` reproduces the C07 draw exactly.
- Not-started games have byte-identical columns before and after conditioning.
- Source order: box scores when present, else the mid-slate standings file (labeled), else the typed clock, else the C10 behavior with the brief saying "no live scores".
- The mid-slate standings file is accepted only on this path; `dfs results` still refuses it.
- Swap on `fixtures/dk/2026-10-15/post_lock_entries.csv` with a conditioned set: locked cells byte-identical; only entries meeting the scope rule change; the diff lists every change; the file validates; the run finishes inside `resolve.budget_s`.
- Determinism: the same live state twice gives byte-identical files.
- The scorecard rows exist after a swap night.

## What I check

On a real evening with staggered tips, after the first games finish, download one standings file for the main Classic and run:

```bash
uv run dfs swap --slate classic_main --live --standings "<path to the download>"
```

Expected: a header like "2 games final (actual points), 1 in progress (14 minutes left, from your download), 9 not started", then a short diff of changed cells with every locked cell untouched, and a new versioned file that validates. Save that standings file hashed as `fixtures/standings/midslate_<date>.zip` for the tests. Next morning `dfs results` should show the late-swap rows.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: `LiveState` with the three sources and the mid-slate relaxation (commit). Checkpoint 2: the partial-game draw with its tests (commit). Checkpoint 3: `swap --live`, the scorecard rows, the real-evening check (commit).

## Risks

- **No permitted live source for the clock.** Under D1, `nba_api` is for box scores and game logs; if its live endpoints are outside the posture, the rehearsed paths are the owner's standings download and `dfs live`, and the brief says which was used.
- **Box scores lag during the night.** The standings download is the fallback; its `FPTS` values are DraftKings' own numbers.
- **Blowouts break the linear remaining-minutes rule.** Known and accepted; B-D-03 in the backlog covers garbage-time regimes with its trigger.
- **Swap churn late in the night.** The scope rule and `swap.min_improvement_points` limit it; if more than 30% of entries change, the brief asks for confirmation as in C10.
