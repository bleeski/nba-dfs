# C06: Projections, fact translation, market anchor, news state

**State:** Baseline. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C04b, C05, C11a (its definition of done runs `dfs start`).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): The Odds API's team names map through C02's team map; game lines cost 2 credits a pull (markets x regions), not 3; `dfs digest` is in scope. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): depends on C11a as well (its definition of done runs `dfs start`); `restriction_cleared` gets its translation function; `dfs restrict` added so the owner can enter a minutes restriction before the researcher exists (R2-10); a risk line for the saved Oct 16 night having no archived lines. 2026-10-14 (ADJUDICATION-R2): the news state, fact supersession by attribute and the commands already exist from C04a, C04b and C11a, so this chunk wires facts into projections instead of building the commands (R2-1, R2-10); usage budget added. 2026-10-14: created. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Turn rates and news into the engine's projection table: probability of playing and starting, minutes by role, the share model that moves minutes and usage when a teammate sits, the market anchor from The Odds API, the fixed rules that translate fact records from the night's news state (written by `dfs out`, `dfs in`, `dfs fact veto` from C04a, `dfs status --apply` from C04b, `dfs start` from C11a and `dfs restrict` from this chunk) into distributions, and the news digest. The simulator (C07) draws from this table; the Floor keeps using `simple_points`.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 3.1 (the "Team codes" bullet only), 4 (all), 6 (all), 15 (`redistribution`, `llm`, `facts` keys).
2. `docs/ARCHITECTURE.md` section 4 "Minutes and role come first", "Minutes and usage when a player sits", "Where LLM facts and inferences meet the model", "Rates and early-season priors"; section 7 "The news digest" paragraph and the fact and inference record JSON.
3. `docs/adr/ADR-003-llm-sets-beliefs-solver-sets-lineups.md` (with its revision note), `docs/adr/ADR-016-early-season-priors.md`, `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the news state and commands paragraphs only).
4. `docs/research/R3-nba-modeling.md` section 2 (the share model, position-similarity prior, with-or-without-you shrinkage) and section 1 (minutes and role, including the 75% season plus 25% last-five baseline).
5. The Odds API facts you need (do not read the saved 63 KB guide dump): base `https://api.the-odds-api.com/v4/`; `GET /sports/basketball_nba/odds?regions=us&markets=spreads,totals&apiKey=...` returns game lines and costs markets x regions credits (2 per pull here); `GET /sports/basketball_nba/events/{eventId}/odds?regions=us&markets=player_points,player_rebounds,player_assists,player_threes&apiKey=...` returns one event's props and costs unique markets returned x regions; every response carries `x-requests-remaining` and `x-requests-used` headers; the free plan is 500 credits a month; empty responses are free. Verified 2026-10-14 (ADJUDICATION V12).
6. `docs/review/ADJUDICATION.md` entry 12 only.

## Scope

**Build:**

- `projections/availability.py`: `p_active` from official status, DraftKings `Status` if present, and acting facts (Out 0, Doubtful 0.25, Questionable 0.55, Probable 0.9, Available 1.0; settings); `p_start` from last season's starts, the depth order, and `starter_announced` or `bench_announced` facts.
- `projections/minutes.py`: a role-specific center and spread per player (truncated normal core on 0 to 48), from season-long and recent minutes with recency decay, the 75/25 practitioner baseline kept as a named comparator; `hard_cap` from restriction facts; early-season variance inflation from C05.
- `projections/share.py`: `redistribute(team_players, absent, evidence)`: each team's possessions as a fixed pool; usage share = base usage x minutes, renormalized to 100%; freed minutes and usage flow by a position-similarity prior updated by with-or-without-you evidence with `shrink_minutes = 300`; the efficiency cost of extra usage (about 1 point per 100 possessions per 1% of usage, settings); one record may move a teammate by at most 8 minutes unless the evidence is an official status change.
- `projections/facts.py`: one pure function per fact `kind` (CONTRACTS 4.2 rules): `out`, `in`, `questionable`, `starter_announced`, `bench_announced`, `restriction`, `restriction_cleared`, `pool_exclusion`, `data_flag`; `acts` computed exactly as CONTRACTS says; supersession by `(person_key, game_id, attribute)` and the precedence rule, read from C04a's `news/state.py` (never re-implemented); inference records carry weight 0 while `llm.inference_blend_enabled` is false.
- `projections/anchor.py`: The Odds API adapter (`/sports/basketball_nba/odds` for spreads and totals, 2 credits a pull (markets x regions), twice a day; props per event only when the credit budget allows, largest slates first; the remaining-credit header read and a reserve kept); The Odds API's team names mapped to DraftKings codes through C02's team map (`ingest/teams.py`); team implied totals and pace from the lines; stat means pulled toward props when present; every response snapshotted; the key read from `config/secrets.toml`.
- Wiring: `build_projections` reads the news state from C04a's `news/state.py` and the injury state from C04b; the commands keep running the legal repair while the `resolve` capability is off (CONTRACTS 4.4); C10 adds the re-solve path. The existing commands are not rebuilt here; `dfs restrict` (next item) and `dfs digest` are the only commands this chunk adds.
- `dfs restrict "<name>" <minutes>` and `dfs restrict "<name>" --clear` (CONTRACTS 4.4): write a `restriction` fact with `detail.restriction_minutes`, or a `restriction_cleared` fact, with `source.kind = "user"`, through C04a's `news/state.py`, so a minutes restriction can be entered before the researcher exists (C11b); the same name matching as `dfs out` (an ambiguous name asks for a number, even with `--yes`) and the same repair or re-solve path.
- `projections/table.py`: `build_projections(slate, rates, history, news_state, lines, props, settings) -> ProjectionTable` with `minutes_source` and `facts_applied` recorded; `simple_points` kept for the Floor.
- `facts/digest.py`: `NewsDigest` ordered by fees at risk then minutes to lock, including unrostered players whose status moves a rostered beneficiary; `dfs digest` prints it (CONTRACTS 13).

**Out of scope:** the simulator; the other news commands (C04a, C04b, C11a); the LLM researcher (C11b); props-implied minutes (C21); DFF projections (C08).

## Contracts

- **Consumes:** `Rates`, history (C05); `Slate` and the team map `ingest/teams.py` (C02); `ContestFacts`, `NewsState`, `FactRecord` supersession, `simple_points` (C04a); `InjuryState` (C04b); `dfs start` (C11a); `Ledger` (C03) for exposure counts in the digest.
- **Produces:** `PlayerProjection` (full), `ProjectionTable`, `InferenceRecord` handling, `NewsDigest`, the fact translation functions, `dfs restrict`, `dfs digest`, the Odds API adapter and its snapshot format.

## Definition of done

- Fact translation tests, one per kind: an `out` sets `p_active = 0` and moves minutes to teammates with the team still summing to 240; `in` restores the prior; `starter_announced` sets `p_start = 1` and the starter minutes prior; `restriction 24` caps minutes at 24; a fact with `published_at = None` is stored and does not change the table; a later fact supersedes an earlier one only for the same player, game and attribute, so a `restriction 24` followed by `starter_announced` keeps the 24-minute cap; an inference record changes nothing while the blend is off.
- Share model tests: a guard's absence lifts guards most; a 300-minute "without" history moves the prior halfway; no teammate moves more than 8 minutes from one non-official record.
- Minutes tests: coverage of the 80% range on last season's held-out games between 75% and 85% for rotation players; the 75/25 baseline computed alongside.
- Anchor tests: a snapshot fixture produces implied totals and pace; the credit reserve stops props when the header is under the reserve; the key is never logged.
- Facts-to-projections tests: on the saved Oct 15 night in drill mode, `dfs out` then `dfs in` for one player changes and then restores his `p_active` and his teammates' minutes in the projection table; `dfs start "BOS: A, B, C, D, E"` sets `p_start = 1` for the five; the repair still runs while `resolve` is off.
- `dfs restrict` test: on the saved Oct 15 night in drill mode, `dfs restrict "<name>" 24` then `dfs start` naming him among the five keeps his 24-minute cap in the projection table; `dfs restrict "<name>" --clear` writes a `restriction_cleared` fact and removes the cap; an ambiguous name asks for a number even with `--yes`.
- Digest test: ordering by fees at risk; an unrostered questionable player whose absence lifts a rostered beneficiary appears.

## What I check

On the saved Oct 15 files (so no live file is touched), with your Odds API key in `config/secrets.toml`, run:

```bash
uv run dfs out "<a player from the Oct 15 Showdown>" --yes --night 2026-10-15 --as-of "2026-10-15T17:00-05:00" --fixtures
```

Expected: the first line says DRILL; one confirmation line naming the matched player; a new repaired file version for the Showdown with him replaced, written under `runs/drills/` (nothing in `out/uploads/` changes); and `uv run dfs status --night 2026-10-15 --as-of "2026-10-15T17:00-05:00" --fixtures` listing the fact under "news state" and his teammates' minutes moving up. Then run the same command with `in` instead of `out`: the fact is superseded and the next file version restores him. Then:

```bash
uv run dfs digest --night 2026-10-15 --fixtures
```

Expected: a short list of that night's uncertain players ordered by how much of your money depended on them, with minutes to lock as of 5:00 pm.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: availability, minutes, share model, the `ProjectionTable` populated from rates (commit; C07 may start). Checkpoint 2: fact translation, news state, the facts-to-projections wiring and `dfs restrict` (commit). Checkpoint 3: the Odds API anchor and the digest (commit).

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates). If the session passes 50% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **No Odds API key yet.** Checkpoint 3 runs on a snapshot fixture; the live pull is a `slow` test; the brief labels lines "missing" and pace uses last season's team averages.
- **No archived lines for the saved Oct 16 night.** The Odds API key and adapter arrive Saturday, so the saved Oct 16 night has no archived lines (historical odds are paid-only); Drill A runs with lines labeled "missing" and pace from last season's team averages.
- **Preseason minutes are unrepresentative.** Use last regular season for the baseline and preseason only to confirm roles; say so in the table's `minutes_source`.
- **Name matching picks the wrong player.** The person-key rules apply (CONTRACTS preamble): an ambiguous match always asks for a number, even with `--yes`.
