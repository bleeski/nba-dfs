# Contracts: the interfaces between components

**Changelog:**
- **2026-10-14 (ADJUDICATION-R2 entry R2-34, final gate, advisor consultation 5):** degenerate tiny fields defined exactly and binomial hand values computed by a standalone script (section 14); drill mode runs only built capabilities regardless of their flags (sections 1, 4.4, 13).
- **2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit):** a live night is the date of its slates' first lock, and files, ledgers and news state are stored under it (sections 1 and 1.1); `floor` starts enabled, `dfs enable` and `dfs disable` switch the other capabilities, and drill mode runs any capability regardless of its flag (sections 1 and 13); `InjuryState` keys teams by a string (section 2.6); one team map in C02 for ESPN codes, NBA full names and The Odds API's names (sections 3.1 and 5); `team_game` lines stay empty (section 5); expected settlement outputs sum every rank whose binomial probability exceeds 1e-12, and `settle.rank_window_sd` is removed (sections 9 and 15); `lineup_hash` is implemented in C01 (section 10); "only changed rows" is the exporter's default, not a validity rule (sections 11.2 and 11.3); C11a gives `dfs news` and `dfs swap` their Floor bodies, and drill mode ignores the `resolve` flag in the news commands and the drill timer (sections 4.4 and 13); the tiny fixtures are written as explicit point masses and split into eleven settlement fixtures, one property fixture and two built by their consuming chunks, and the real-file fixture sources are corrected (section 14); one `[projections]` line, and any chunk adds the keys its own file names (section 15). Section numbers are unchanged.
- **2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit):** `dfs restrict` (C06) writes `restriction` and `restriction_cleared` facts (sections 4.4 and 13); `p_top1_any` for a single entry is stated as the one exception to realized outcomes (section 9); `RunManifest.capabilities` carries `rehearsed_paths` and `drill_artifact` (section 12); `[insurance] enabled` is removed because the `insurance` capability flag is the one switch (section 15). Section numbers are unchanged.
- **2026-10-14 (v2.1, the owner's real files of Oct 14; ADJUDICATION-R2 entry R2-33):** entries and salary layouts, encodings and the `Status` column confirmed on 2026-27 NBA files; the newest salary file feeds DraftKings Status with an explicit code map; `AvgPointsPerGame` defined (last season, all games including playoffs) and used as the Floor's second source and a scoring self-check; command name matching by whole tokens, never edit distance; ESPN-to-DraftKings team codes; Showdown candidates enumerated over a measured subset and the Showdown field sampled by popularity; real and third-party fixtures stay out of git (the repository is public).
- **2026-10-14 (v2, round 2 adjudication, design final):** person key without team and identity rules (ADJUDICATION-R2 entry R2-9); slate fingerprint, two-table entries layout, optional draft group ID, post-lock Game Info (R2-8); drill mode in section 1.1 (R2-7); injury-report merge and NOT YET SUBMITTED (R2-12); fact supersession by attribute and precedence (R2-10); `simple_points` from the shared scoring function (R2-11); no float16 for points (R2-4); `FieldScores` rewritten with `p_above` and `p_equal` and a fitted tail (R2-4); settlement rewritten: single tie split, top-1% attribution, joint ranks for every field size, expected and realized outputs, portfolio-independent draws (R2-2, R2-3, R2-5); `settlement_fn` takes lineup hashes and greedy is exact incremental (R2-4, R2-5); locked cell definition, time to lock as a label, export write order, swap freshness, two-stage repair (R2-6, R2-14, R2-15, R2-17); capability fingerprints (R2-16); chunk owners updated for the C04a, C04b, C11a and C11b split (R2-1); new tiny fixtures and settings keys (R2-2 to R2-6, R2-23). Section numbers are unchanged so chunk references stay valid.
- **2026-10-14 (v1):** created (Stage 3 of the round 1 adjudication session).

**Owner of this file:** chunk C01 turns every contract here into code (pydantic models, function signatures with docstrings, and fixture files) and every later chunk builds against those, never against prose. A chunk whose own file says it adds a contract (for example C22's `LiveState`, or a later chunk's settings keys) adds it here and in code in the same commit. Any other change to a contract is a change request under the change-control rule in `CLAUDE.md`: log it, stop and ask the owner if it blocks the chunk, and edit this file and the code together only after approval, recorded in `docs/build/PROGRESS.md`. A one-sentence clarification that changes no field, signature or rule is not a change request; record it in PROGRESS.md.

**How to read this.** Each contract has: what it is, who produces it, who consumes it, its fields or signature, and the rule that must hold. Sections are numbered so chunk files can point to them ("CONTRACTS section 4.2"). Field names are the names used in code.

**Person key (R2-9).** `person_key` is the engine's stable identifier for a human player, the same in every slate and every season: his normalized full name (accents folded, lower case, punctuation removed, internal whitespace collapsed, a suffix such as `jr`, `sr`, `ii`, `iii`, `iv` kept as a final token), for example `tim hardaway jr`, `nikola jokic`. It never contains a team (a traded player keeps his history) and never a DraftKings ID (those change between slates and between Captain and UTIL roles). Team lives on each appearance (a pool row, a box-score row).
- **Matching a name from any source** (`identity.match(name, candidates) -> person_key | None`): flip `Last, First` to `First Last` before normalizing (`Hardaway Jr., Tim` becomes `tim hardaway jr`); exact key match first; then the suffix-stripped key only when exactly one candidate matches it; otherwise unmatched, listed for review, and treated as having no history. `config/identity_overrides.toml` maps a source name to a `person_key` (one table `[overrides]` of lines `"<name as the source prints it>" = "<person_key>"`) and is applied first; its hash is recorded in each run manifest.
- **Collisions never stop the night.** If two different players in tonight's pools normalize to the same key, both get a disambiguator (`|<team>`, then `|<dk_id>` if still equal), both carry `identity_ambiguous = True`, their history join is disabled (salary-implied points), `dfs out` and `dfs in` require a pick by number even with `--yes`, and the brief prints a warning.
- **History joins** use the history source's athlete ID (`source_athlete_id`) once a name has matched, so later name variants follow the ID. On the Oct 14 Classic file this matched 226 of 288 players, of whom 70 had changed team since last season; 61 of the 62 unmatched had no NBA games last season (ADJUDICATION-R2 V-R2-15).
- **Matching what the owner types** (`identity.match_query(query, pool)`, used by `dfs out`, `dfs in`, `dfs start`): normalize the query the same way; a player matches when every query token equals a whole token of his normalized name (so `jokic` matches Nikola Jokic and never Nikola Jovic); one match asks one confirmation; more than one match, or none, prints numbered choices (for none, the closest names by edit distance) and requires a number. Edit distance never auto-resolves a name. Tonight's pools hold near-homonyms (Nikola Jokic and Nikola Jovic) and seven Joneses and seven Williamses (V-R2-14).

---

## 1. Directory layout and naming

```
nba-dfs/
  pyproject.toml            uv-managed; package `nbadfs`; CLI entry point `dfs`
  src/nbadfs/
    cli.py                  Typer app; every command returns JSON on --json and plain text otherwise
    schemas/                pydantic models, one module per contract section below
    ingest/  facts/  news/  history/  projections/  scoring/  sim/  field/  settle/  select/  validate/  export/  resolve/  brief/  learn/  llm/
  scripts/
    dfs.cmd                 Windows launcher (C01 stub, C11a full)
    check_docs.py           repo consistency checks (wired into the smoke suite by C01)
  tests/                    pytest; `-m smoke` under 60 s; full suite under 5 min
  fixtures/                 committed: hand-written tiny, identity and synthetic fixtures; local only (gitignored): real DraftKings files, third-party downloads and hashed standings tables, rebuilt by scripts/build_fixtures.py (section 14); never other users' raw names
  config/
    settings.toml           every tunable named in this file, with defaults
    posture.toml            data posture: permissive_plus_nba_api (D1); allowed hosts
    capabilities.toml       per capability: enabled, rehearsed_on, rehearsed_commit, rehearsed_paths, drill_artifact
    identity_overrides.toml manual name-to-person_key fixes
  inbox/<night>/            DraftKings downloads copied in from Downloads, filed by night (the date of the slates' first lock, section 1.1) (gitignored)
  data/archive/<night>/     every raw download and pre-lock snapshot, byte for byte, with a manifest (gitignored)
  data/snapshots/<date>/    source responses and fetched pages (gitignored)
  data/history/             parquet history (gitignored)
  data/contest_facts_cache.json
  runs/<run_id>/            one folder per live engine run (gitignored)
  runs/<night>/             that night's ledgers and news state (gitignored)
  runs/drills/<drill_id>/   everything a drill writes (gitignored)
  runs/replays/<replay_id>/ everything a replay writes (gitignored)
  out/uploads/              live upload files; out/uploads/stale/ for superseded ones; out/uploads/.tmp/ for unfinished writes (gitignored)
```

- **Run id:** `YYYYMMDD-HHMMSS-<mode>` in local time, mode one of `night`, `news`, `swap`, `repair`, `results`, `drill`.
- **Slate fingerprint (R2-8):** `slate_fingerprint` = the first 12 hex characters of `sha1` of the sorted pool `dk_id` values. It is the slate's identity everywhere (archive, ledger, validator). DraftKings' draft group ID is not in the entries file (R6 section 2.3) and is never invented.
- **Slate key (readable):** `classic_<first tip HHMM local>_<games>g` (for example `classic_1400_3g`) or `sd_<AWAY>-<HOME>` (for example `sd_BOS-DET`); if two slates on one night would share a key, append `_<first 4 hex of the fingerprint>`. `classic_main` is an alias the night plan assigns to the Classic slate with the most games.
- **Upload file name:** `<slate_key>_<lock HHMM local>_v<n>.csv`, for example `classic_main_1400_v5.csv`, `sd_BOS-DET_1400_v2.csv`. `n` increases per slate per night; the latest valid file is also copied as `<slate_key>_latest.csv`.
- **Times:** stored as ISO 8601 with offset; displayed in Central. DraftKings Game Info is Eastern and is converted on parse.
- **`capabilities.toml` (R2-16):** one table per capability in `floor, baseline_model, resolve, swap_open_slots, researcher, insurance, qa_audit, watcher`, each with `enabled: bool`, `rehearsed_on: date | ""`, `rehearsed_commit: str` (git commit of the drill), `rehearsed_paths: list[str]` (source folders whose change makes the evidence stale), `drill_artifact: str` (path of the drill's result). Status per capability: `passed` (rehearsed and no file under `rehearsed_paths` changed since `rehearsed_commit`), `stale` (changed since), `never`. **Enabling (R2-34):** `floor` starts `enabled = true`; every other capability starts `enabled = false` and is switched by `dfs enable <capability>` and `dfs disable <capability>` (C11a). `dfs enable` refuses a capability whose status is not `passed` unless `dfs unlock` is recorded. On a game night a live run does not use an enabled capability that has since become `stale` (the brief shows it as off) unless `dfs unlock` is recorded; a new drill and `dfs rehearsed` make it `passed` again. Drill mode runs any **built** capability regardless of its flag (so Drill A can run the Baseline before it is enabled); a capability whose code is still a stub falls back in a drill exactly as in live mode (for example the re-solve before C10 falls back to the repair, and the researcher pass before C11b is skipped). Live mode runs only enabled capabilities. `floor` is the exception to staleness: it is never switched off by it, only labeled.

### 1.1 Clock, live mode and drill mode (owned by C03; R2-7)

Every command accepts `--night <YYYY-MM-DD>`, `--as-of <ISO datetime>` and `--fixtures`. Rule: no module reads the wall clock directly; all read `Clock.now()`, which returns `--as-of` when given, else the wall clock. A static test proves no module under `src/nbadfs/` calls the wall clock.

- **Live mode** (no `--as-of`): the night's files from `inbox/<night>/`, the live ledger and news state under `runs/<night>/`, uploads to `out/uploads/`. **The night (R2-34)** is the date of the slates' first lock, read from Game Info and taken in Central time, never the wall-clock date: Monday's run for Tuesday's slates stores everything under Tuesday's date. A file whose slates have all started is archived under its own night and never used live.
- **Drill mode** (`--as-of` given, with or without `--night`): `Paths` resolves inputs **read-only** from `data/archive/<night>/` (or `fixtures/dk/<night>/` with `--fixtures`), and every write (news state, ledgers, manifests, upload-shaped files, simulated `dfs uploaded` confirmations) goes under `runs/drills/<drill_id>/`, where `drill_id = <night>-<as-of HHMM>-<n>`. A drill never writes to `out/uploads/`, `runs/<night>/`, or `inbox/`. A drill's ledger starts from a copy of the archived ledger snapshot for that night if one exists, otherwise empty. The brief and every file a drill writes say "DRILL" in their first line.
- **Replay mode** (`dfs replay`, C19): writes only under `runs/replays/<replay_id>/`.
- **Test that must hold:** a completed drill, including simulated uploads and failures, leaves every live artifact byte-identical.

## 2. DraftKings input files (consumed by chunk C02; produced by the owner)

### 2.1 Entries file (`DKEntries*.csv`) (R2-8)

The export from "Edit entries" for one draft group, UTF-8 without a byte-order mark, CRLF line endings (VERIFIED on the owner's Oct 14 files, V-R2-12). **Two tables side by side, not one after the other:** the entry table starts at column A with its header in row 1 and runs down the left; the instruction lines and then the player-pool table run down the right, starting after one blank column and an `Instructions` column, **on the same physical rows** as entries (R6 section 2.3). The pool header sits on physical row 8 and pool data starts on row 9, so any contest with more than 7 entries overlaps the pool (VERIFIED, V-R2-12). The pool here has 9 columns (no `Status`, no `Starting`) and `AvgPointsPerGame` to 2 decimals.

- **Parsing rule:** locate the entry header (`Entry ID` in column A) and the pool header (the row and column where `Position, Name + ID, Name, ID, Roster Position, Salary, Game Info, TeamAbbrev, AvgPointsPerGame` begins); read each region by its own column range; never assume a blank row separates them; keep every entry row even when it shares a row with pool data; ragged rows are accepted. Columns are found by header name, never by position; unknown columns are kept and logged.
- **Entry row columns (Classic):** `Entry ID, Contest Name, Contest ID, Entry Fee, PG, SG, SF, PF, C, G, F, UTIL`. **Showdown:** `Entry ID, Contest Name, Contest ID, Entry Fee, CPT, UTIL, UTIL, UTIL, UTIL, UTIL`. Slot labels are read from the header.
- **Slot cell:** empty, or `<Name> (<dk_id>)`, or `<Name> (<dk_id>) (LOCKED)` after the player's game has started. The engine writes bare integer `dk_id` values on export (section 10).
- **Player pool:** `Roster Position` is a `/`-joined eligibility list (Classic, for example `PG/G/UTIL`; Showdown `CPT` or `UTIL`). `Game Info` is `AWAY@HOME MM/DD/YYYY HH:MMPM ET` before the game; after it starts DraftKings may show `In Progress` or `Final` (R6, SUPPORTED); anything else (for example a postponement) is kept raw and marks the game's lock as unresolved.
- **Post-lock Game Info rule:** an `In Progress` or `Final` game is started; its tip time is taken from the last verified schedule for that exact game (the latest archived download of the same `slate_fingerprint` that carried a time); if none exists, the game's lock is unresolved and any edit touching it is refused (validator rule "lock unresolved").
- **Rule:** the pool inside the entries file is the authoritative player list for that slate (158 of 158 IDs matched the salary file, R6; 288 of 288 and 82 of 82 on Oct 14). The salary file is still downloaded every run for `Status` (section 2.2).
- **`AvgPointsPerGame`** is DraftKings' published average of last season's DraftKings points per game over every game played, playoffs and play-in included; 0 means no NBA games last season (VERIFIED: recomputed from last season's box scores with section 7's scoring, it matches to 0.01 for 189 of 224 matched players and to 0.5 for 220, V-R2-16). It is public (every entrant sees it), so the public view may use it (section 8), and it is the Floor's second projection source (section 6).
- **Parsed model:** `EntriesFile(slate_key, slate_fingerprint, draft_group_id: int | None, downloaded_at, entries: list[Entry], pool: list[PoolPlayer], encoding, bom, newline, source_path, source_hash)`. `draft_group_id` is set only from verified metadata (never from the file, which lacks it). `Entry(entry_id, contest_id, contest_name, fee, slots: list[SlotCell])`. `SlotCell(slot_label, dk_id | None, locked_marker: bool, raw)`. `PoolPlayer(dk_id, name, person_key, identity_ambiguous: bool, team, roster_positions, salary, game: GameRef, role: "CPT"|"UTIL"|"CLASSIC", avg_points)`.

### 2.2 Salary file (`DKSalaries*.csv`), recommended on every run

Columns as the pool above plus `Status` and `Starting`, UTF-8 **with** a byte-order mark, CRLF; `AvgPointsPerGame` to 1 decimal. VERIFIED on the owner's 2026-27 NBA files of Oct 14 (V-R2-13): the pool IDs, salaries, positions and Game Info equal the entries file's exactly; `Status` was populated (Classic: 54 `Q`, 8 `OUT`); `Starting` was blank for every player about 6 hours before tip (whether it fills near tip is checked on Oct 14 and 15). In preseason there is no official injury report (R4), so this column is the only automated status source for the rehearsals. Parsed to the same `PoolPlayer` plus `status`, `starting`.
- **Rule:** the newest salary file for a `slate_fingerprint` (by download time) feeds availability through `dk_status` facts (section 4.2); the brief shows its download time. The owner downloads it with the entries file before every run.
- **Status codes** (settings `projections.dk_status`): `OUT`, `O`, `IR`, `SUSP`, `NA` map to 0; `D` to 0.25; `Q` and `GTD` to 0.55; `P` to 0.9; blank to 1.0. Any other value is logged, treated as questionable (0.55), and flagged in the brief.

### 2.3 Payout paste (`inbox/payouts/<contest_id>.txt`)

Free text copied from the contest's payout table. Parser accepts lines like `1st $200,000`, `2nd-3rd $50,000`, `352nd-500th $50`, `Top 23% $...`. Produces `PayoutCurve(tiers: list[(rank_from, rank_to, prize)], places_paid, prize_pool, facts_status = "verified", facts_source = "paste")`.

### 2.4 Entry-history export (`draftkings-contest-entry-history.csv`), weekly

The 14-column export; parser ported from the NHL engine (ADR-018). Gives `field_size`, `places_paid`, `prize_pool`, our `place`, `points`, `winnings` per past contest. Feeds contest-facts templates (`facts_status = "template"`) and the results step.

### 2.5 Standings file (`contest-standings-<id>.zip` or `.csv`), after the MVP

Columns `Rank, EntryId, EntryName, TimeRemaining, Points, Lineup, Player, Roster Position, %Drafted, FPTS`. Parsed in the private folder; `EntryName` is replaced by `sha256(name + salt)[:12]` before any row enters the project. **Rule (R2-18):** standings establish the completed field size and lineup, score and ownership facts only. They carry no winnings, so they never set `places_paid` or prizes unless the specific file has an explicit verified payout field; paid status is never derived from rank.

### 2.6 Official injury report (PDF) (R2-12)

`https://ak-static.cms.nba.com/referee/injury/Injury-Report_<YYYY-MM-DD>_<HH_MM>[AP]M.pdf`; one file per 15-minute slot (2026 pattern) or one hourly file overwritten within the hour (October 2025 pattern); the adapter tries both. Parsed rows: `(report_time, game_date, matchup, team, player_name, status in {Out, Doubtful, Questionable, Probable, Available, NotYetSubmitted, Unknown}, reason)`. A team shown as NOT YET SUBMITTED yields one row with `status = NotYetSubmitted` and no player. Unrecognized statuses are logged and kept as `Unknown`. Player names are matched with the person-key rules (the report prints `Last, First`).

- **Merge rule (`InjuryState`):** state is kept per game and team, keyed by the string `"<game_id>|<team>"` (R2-34; JSON has no tuple keys). A team's newest **submitted** section replaces all its earlier statuses (players not listed are presumed available). A team marked NOT YET SUBMITTED keeps its last submitted statuses, each labeled `cached:<report_time>`. A single report never wipes a team it did not cover.
- **Model:** `InjuryState(as_of, teams: {"<game_id>|<team>": {submitted_at: datetime | None, source_report: str, players: {person_key: {status, reason, label: "current"|"cached:<time>"}}}})`.

## 3. Slate, contest and contest facts (produced by C02 and C04a/C04b; consumed by everything)

### 3.1 `Slate`

`Slate(slate_key, slate_fingerprint, format: "classic"|"showdown", draft_group_id: int | None, games: list[GameRef], first_lock, last_lock, pool: list[PoolPlayer], entries: list[Entry], contests: list[Contest], source_file, source_hash)`. `GameRef(game_id, away, home, tip_local: datetime | None, tip_et: datetime | None, game_info_raw, lock_status: "scheduled"|"started"|"unresolved")`. `game_id` is `<date>_<AWAY>@<HOME>`. `Contest(contest_id, contest_name, fee, entry_ids)`. Rule: `first_lock` is the earliest `tip_local` among games; Showdown `first_lock == last_lock`.

- **Team codes (C02; R2-34):** DraftKings codes are canonical: every `team`, `away` and `home` field holds a DraftKings code. `ingest/teams.py` holds the one map, with aliases: ESPN codes (at least `NY` to `NYK`, `SA` to `SAS`, `GS` to `GSW`, `NO` to `NOP`, `UTAH` to `UTA`, `WSH` to `WAS`; 24 of 226 matched players on Oct 14 differed only by code, V-R2-15), NBA full team names as printed in the injury report (for example `Minnesota Timberwolves`), and The Odds API's team names. The injury report (C04b), the history loader (C05) and the market anchor (C06) map through it; none keeps its own map. A test (C02) proves that every ESPN code in the history file, every team name in the two March 2026 injury PDFs and the 30 NBA full team names map to a DraftKings code.

### 3.2 `ContestFacts`

```
ContestFacts(
  contest_id, contest_name, contest_type: "gpp"|"double_up"|"satellite"|"top_n"|"other",
  fee, entry_limit: int, field_size: int, our_entries: int,
  k_top1: int,                 # max(1, floor(0.01 * field_size))
  places_paid: int,
  payout_curve: list[(rank_from, rank_to, prize)],   # exact or parametric; covers ranks 1..places_paid
  top1_pool: float,            # sum of prizes over ranks 1..k_top1
  facts_status: "verified"|"template"|"default",
  facts_source: str,           # "paste", "entry_history:<date>", "name_prize_pool", "default:<type>"
  observed_entries: int | None, observed_at: datetime | None, capacity: int | None
)
```

- **Type classification** from the contest name: contains "Double Up" or "50/50" -> `double_up`; "Satellite" or "Qualifier" -> `satellite`; matches `Top \d+` -> `top_n`; otherwise `gpp`.
- **Field size** when not verified: `prize_pool / (fee * (1 - rake))` with rake 0.15, from the prize pool in the contest name, else capacity from the entries file if present.
- **Paid share defaults by type:** gpp 0.23, double_up 0.45 (places paid = half, flat), satellite from the name's ticket count, top_n from `n`; these are settings.
- **Default payout curve for gpp:** parametric, `prize(r) = pool * a * r^(-b)` normalized to sum to the pool over paid places, with `(a, b)` fitted per field-size bucket from pasted tables as they accumulate; initial `b = 1.0`, with first place capped at 20% of the pool for fields over 10,000 and 15% under. BET defaults, labeled.
- Rule: every number derived from a contest carries that contest's `facts_status`.

## 4. News state, facts and inferences (produced by C04a, C04b, C06, C10, C11a; consumed by projections, the repair, the re-solve, the brief)

### 4.1 `NewsState` (`runs/<night>/news_state.json` live, or under the drill folder; one per night, append-only with supersession)

`NewsState(night_date, facts: list[FactRecord], inferences: list[InferenceRecord], applied_at: datetime, hash)`.

### 4.2 `FactRecord` (R2-10)

```
FactRecord(
  fact_id, created_at, kind: "out"|"in"|"questionable"|"pool_exclusion"|"starter_announced"|"bench_announced"|"restriction"|"restriction_cleared"|"data_flag",
  attribute: "availability"|"role"|"restriction"|"data_flag",   # computed from kind, see map below
  visibility: "public"|"private",
  player: {person_key, name}, team, game_id,
  detail: {restriction_minutes: int|None, in_place_of: person_key|None, status: str|None},
  source: {kind: "user"|"llm"|"official_report"|"dk_status", model: str|None,
           evidence: [{url, snapshot_id, quote, published_at: datetime|None}]},
  supersedes: fact_id | None,
  vetoed: bool,
  acts: bool                   # computed: True only if not vetoed and (source.kind in user/official_report/dk_status, or quote verified and published_at known and within 24h)
)
```

- **Attribute map:** availability = `out`, `in`, `questionable`, `pool_exclusion`; role = `starter_announced`, `bench_announced`; restriction = `restriction`, `restriction_cleared`; data_flag = `data_flag`.
- **Supersession** is keyed by `(person_key, game_id, attribute)`, never by person alone. Facts about different attributes coexist: a starter announcement never clears a restriction, and an availability update never changes the role. Removing a restriction requires a `restriction_cleared` fact.
- **Precedence within one attribute** (ARCHITECTURE section 4): an acting official-report `out` outranks every non-official source until a later official report changes it; user commands outrank LLM records; otherwise the most recent acting fact wins. The owner overrides an official fact with `dfs fact veto <fact_id>` (recorded). Conflicts between acting facts stay visible in the brief.
- **Effects:** `acts == False` records are stored and shown, never applied; `out` sets `p_active = 0`; `questionable` sets the status probability (section 6); `starter_announced` sets `p_start = 1` and uses the role's starter minutes prior; `bench_announced` sets `p_start = 0`; `restriction` sets `minutes.hard_cap`; `restriction_cleared` removes it; `in` restores the model prior and marks lineups built for the absence for re-selection.
- **Tests that must hold:** restriction then starter, starter then restriction, and an unrelated availability update all keep the restriction; two `out` facts in different games applied in either order never revert each other.

### 4.3 `InferenceRecord`

Same header as a fact plus `minutes: {q10, q50, q90, hard_cap}`, `usage_multiplier: {q10, q50, q90}`, `stat_multipliers: {stat: {q10, q50, q90}}`, `redistribution_hint: [{person_key, minutes_weight}]`, `no_history_prior: {comparable_role, minutes_range}|None`, `condition: [{person_key, status}]|None`, `rationale`. Rule: weight 0 in the simulation until `settings.llm.inference_blend_enabled` is true (set only by the learning loop after two weeks of coverage evidence).

### 4.4 Commands that write facts

`dfs out "<name>"`, `dfs in "<name>"` (C04a), `dfs start "<TEAM>: <A>, <B>, <C>, <D>, <E>"` (C11a; writes five `starter_announced` facts and `bench_announced` for the previous expected starters), `dfs restrict "<name>" <minutes>` and `dfs restrict "<name>" --clear` (C06; write a `restriction` fact with `detail.restriction_minutes`, or a `restriction_cleared` fact, with `source.kind = "user"`, so a minutes restriction can be entered before the researcher exists), `dfs fact veto <fact_id>` (C04a), and `dfs status --apply` (C04b; writes facts from the official-report diff). Each matches names against tonight's pools with the person-key rules and asks one confirmation unless `--yes`. **An ambiguous match (more than one candidate, or an `identity_ambiguous` player) never auto-resolves:** it prints numbered choices with team, salary and position and requires a number, even with `--yes`. Then, unless `--no-run`: it runs the re-solve (section 11.4) when the `resolve` capability is enabled (in drill mode, regardless of the flag once C10 has built it, section 1) and the earliest affected lock is at least `resolve.min_minutes_to_lock` away; otherwise it runs the legal repair (section 11.6) on the latest committed lineups. The flag-off path never rebuilds the Floor over an uploaded portfolio; `dfs night --floor` is the explicit way to rebuild.

### 4.5 `NewsDigest` (`runs/<run_id>/llm/news_digest.json`)

List of items `{person_key, name, team, game_id, reason: str, official_status, dk_status, p_active, exposure_entries, fees_at_risk, minutes_to_lock}` sorted by `fees_at_risk` descending, then `minutes_to_lock` ascending; includes unrostered players whose status moves a rostered beneficiary.

## 5. History and priors (produced by C04a minimally and C05 in full; consumed by C06)

- **Team codes** are stored in DraftKings form everywhere; history sources use ESPN codes, mapped through C02's team map (section 3.1, "Team codes"), and a test proves every code in the history maps. History keeps `season_type` (2 regular, 3 playoffs, 5 play-in).
- `data/history/player_box.parquet`: one row per player-game: `game_id, date, season, season_type, person_key, source_athlete_id, team, opp, home, starter, minutes, pts, fg2m, fg2a, fg3m, fg3a, ftm, fta, reb, ast, stl, blk, tov, dk_points, source ("sportsdataverse"|"nba_api")`. `dk_points` is computed by the scoring function (section 7); the source file has no fantasy points and no salary (VERIFIED, ADJUDICATION-R2 V-R2-5).
- `data/history/team_game.parquet`: `game_id, date, team, opp, possessions, pts, pace, margin, ot_periods, spread_close, total_close`. `spread_close` and `total_close` stay empty: historical lines are paid-only (ADJUDICATION V12), so C07's margin calibration uses last season's net-rating difference between the two teams in place of the closing spread, labeled (R2-34).
- `Rates` per player: `rate_per36[stat]`, `usage_share`, `shrinkage_weight`, `games`, `minutes_total`, `early_season_var_mult`. Function: `build_rates(history, as_of_date, settings) -> dict[person_key, Rates]`.
- Rule: `as_of_date` strictly precedes the slate date in every backtest.

## 6. Projections (produced by C04a for the Floor and C06 in full; consumed by C07, the Floor and the repair)

```
PlayerProjection(
  person_key, team, game_id, dk_ids: {"CLASSIC"|"CPT"|"UTIL": dk_id}, salary_by_role,
  p_active, p_start,
  minutes: {q10, q50, q90, hard_cap: float|None}, minutes_source: "model"|"fact:<kind>"|"user",
  usage_share, rates: Rates | None, early_season_var_mult,
  simple_points: float,          # the Floor's projection, defined below
  simple_points_source: "history"|"dk_average"|"salary_implied"|"ambiguous_identity"
)
ProjectionTable(run_id, as_of, players: list[PlayerProjection], team_totals: {team: {implied_total, pace, spread}}, facts_applied: [fact_id])
```

- **`simple_points` (R2-11):** last regular season's DraftKings points per minute (computed from the box score by the scoring function, section 7) times last regular season's minutes per game, for a player whose `person_key` matched history (any team). Otherwise `AvgPointsPerGame` from the file when it is above 0 (labeled `dk_average`). Otherwise salary-implied: a linear fit of last season's DraftKings points per game on tonight's salary across the matched players in tonight's pool (a cross-sectional fallback, labeled `salary_implied`). C04a ships the Floor on `dk_average` first (checkpoint 2) and adds the history route at checkpoint 3; after Oct 20 DraftKings' average becomes a small current-season sample, so history stays the long-term primary. An `identity_ambiguous` player always uses the salary-implied value. Preseason box scores are never used. Captain `simple_points` is 1.5 times UTIL.
- **Status probabilities** (settings `projections.p_active` for the official report, `projections.dk_status` for DraftKings codes): Out 0, Doubtful 0.25, Questionable 0.55, Probable 0.9, Available or unlisted 1.0.
- **Fact translation rules** (`projections/facts.py`, C06): one pure function per `kind`, unit-tested, no LLM numbers.
- **Share model** (C06): `redistribute(team_players, absent: set[person_key], evidence) -> new minutes and usage shares` with the position-similarity prior and a shrinkage constant setting (`redistribution.shrink_minutes = 300`); minutes sum to 240 per team in expectation.
- **Market anchor** (C06): `anchor(projections, lines: {game_id: {spread, total}}, props: optional) -> projections`; props optional (`None` when the credit budget says so).

## 7. Scoring and scenarios (scoring produced by C04a and C05; scenarios by C07; consumed by C08, C09, C10)

- **Scoring function (C04a; C05 adds the vectorized form, versioning and self-checks):** `score_line(stats: {pts, fg3m, reb, ast, stl, blk, tov}, rules_version) -> (util_points, cpt_points)`, DraftKings NBA rules from `docs/reference/`: points 1, three-pointer made 0.5, rebound 1.25, assist 1.5, steal 2, block 2, turnover -0.5, double-double 1.5, triple-double 3, **both** for a triple-double (+4.5 in total; R6's real exports, and VERIFIED again on last season's data: this rule reproduces DraftKings' averages for 14 of the 16 players with triple-doubles in tonight's pool, Jokic 64.85 against DraftKings' 64.88 where the replace rule gives 64.10, V-R2-17); Captain is 1.5 times the bonus-inclusive total. UTIL values are multiples of 0.25 and Captain values multiples of 0.125, so both are exact in float32.
- `BoxArrays(players: list[person_key], stats: {stat: int16[S, P]})` for `pts, fg3m, reb, ast, stl, blk, tov`, plus `minutes: float16[S, P]`.

```
ScenarioSet(
  name: "screening"|"selection"|"validation"|"reporting", S: int, seed: int,
  players: list[person_key],                     # column order, sorted by person_key
  points_util: float32[S, P], points_cpt: float32[S, P],   # DraftKings points per scenario per player (cpt = 1.5 x util), exact eighth points
  active: bool[S, P], minutes: float16[S, P],
  game_margin: float32[S, G], game_ot: int8[S, G],
  model_error: {team_shift: float32[S, T], player_shift: float32[S, P]}
)
```

- **Precision rule (R2-4):** fantasy points, lineup scores and field scores are float32 (exact for eighth points at these magnitudes) or integer eighths (`int16`, `round(8 * points)`); **never float16, never rounded to two decimals**. Comparisons for ties are exact on the eighth-point lattice. Comparisons against DraftKings' two-decimal display use a 0.01 tolerance (R6; R2-20).
- Sizes: screening 5,000; selection 15,000; validation 15,000; reporting 30,000 (settings; ADR-025 and ARCHITECTURE section 2 must agree; a test checks).
- **Determinism:** every draw keyed by `(run_seed, set_name, scenario_index, game_id, person_key, stat)` with a counter-based generator (`numpy.random.Philox` or equivalent); `simulate_game(night, game_id, S, seed) -> game arrays`; re-simulating one game with new availability changes only that game's columns.
- Function: `simulate(night: NightInputs, set_name, settings) -> ScenarioSet`. `NightInputs(projections: ProjectionTable, slates: list[Slate], news_state: NewsState, lines: dict)`.

## 8. Field model (produced by C08; consumed by settlement, selection, the brief)

```
PublicView(run_id, players: {person_key: {proj_points, value, popularity, p_active_public}}, source: "dff"|"formula", facts_applied_public: [fact_id])
FieldSample(contest_id, lineups: int32[M, slots] (dk_id indices into the pool), lineup_hashes: list[str], weights: float32[M], entrant_type: int8[M], user_id: int32[M],
            ownership: {role: {person_key: float}}, copy_rate: {lineup_hash: float}, sampled_share: {lineup_hash: float}, built_from: PublicView.run_id)
FieldScores(
  contest_id, set_name, n_opponents: int, lattice_step: float,     # 0.25 Classic, 0.125 Showdown
  grid: float32[S, Q],            # bulk quantile grid, Q = 400 (index q holds the score below which a fraction q/(Q-1) of the weighted field falls); display, screening, and P(above) below the tail threshold
  tail_threshold: float32[S],     # the field's (1 - field.tail_share) quantile in each scenario
  tail_scores: int16[S, T],       # the weighted field sample's scores above the threshold, integer eighths, descending, padded with -1
  tail_weights: float32[S, T],    # the share of opponents each tail point represents
  tail_fit: float32[S, 2],        # upper-tail fit parameters, used above the score where fewer than field.tail_min_points sample points remain
  tail_fit_status: "fitted"|"unfitted"
)
p_above(field_scores, s, x) -> float   # share of opponents scoring strictly above x in scenario s
p_equal(field_scores, s, x) -> float   # share of opponents scoring exactly x (x on the lattice)
```

- **Rules (R2-4):** settlement reads the field only through `p_above` and `p_equal`. In the tail region they come from the exact weighted sample scores, and above the sample's resolution from the tail fit (C08 chooses the family; default an exponential excess over the sample's top 1%); below the tail threshold, `p_above` is interpolated from the grid and `p_equal` is the grid's local density times `lattice_step`. If the fit is not ready, `tail_fit_status = "unfitted"` and the brief labels first-place numbers "tail unfitted"; the Baseline is never blocked by it.
- `build_public_view(slate, lines, facts_public, dff_file|None) -> PublicView`; when `dff_file` is `None` or fails to parse, use the deterministic formula (settings `public_view.formula_weights`); never read `ProjectionTable` from the engine view, with or without a consensus file.
- `build_field(contest_facts, slate, public_view, settings) -> FieldSample` with entrant mixture weights by contest family (`settings.field.<family>`), sampled as users (multi-entry users share cores); casual Showdown entrants weighted by salary use (`field.showdown_salary_left_decay`, a labeled BET default, R2-23). **Showdown fields are sampled, not enumerated** (R2-33): lineups are drawn by public popularity with rejection for the cap and the both-teams rule, as in Classic, so the subset our candidates search (section 10) never shapes the field's thresholds or copy rates. A 41-player Showdown pool has 13.6 million legal lineups (V-R2-18).
- `score_field(field_sample, scenario_set) -> FieldScores` in chunks of scenarios.
- Ownership sums: Classic 8.0; Showdown 1.0 CPT + 5.0 UTIL (checked).

## 9. Settlement and the goals (produced by C08; consumed by C09, C12, C13, the brief) (R2-2, R2-3, R2-5)

```
settle(contest: ContestFacts, entry_hashes: list[str], entry_points: float32[S, n], copy_rate: dict[str, float],
       field: FieldScores, draw_key: (run_seed, set_name, contest_id)) -> Settlement
Settlement(
  contest_id, set_name, entry_hashes: list[str],
  top1_exp: float32[S, n],    # expected dollars from top-1% places per entry per scenario
  prize_exp: float32[S, n],   # expected dollars from any paid place per entry per scenario
  top1_draw: float32[S, n],   # top-1% dollars in the one realized outcome per scenario
  prize_draw: float32[S, n],  # dollars from any paid place in the one realized outcome per scenario
  G1: float, G1_se: float,    # mean over s of sum over n of top1_exp / top1_pool
  G1_no_dup: float,           # same with copy rates set to zero
  p_top1_any: float,          # share of scenarios where at least one entry has top1_draw > 0 (the exact binomial when n == 1)
  facts_status: str, tail_fit_status: str
)
night_goal2(settlements: list[Settlement], fees_total: float, alpha: float, unfilled_entries: int) -> Goal2
Goal2(p_sd: float, p_sd_se: float, p_washout: float, winnings_mean: float, p_recover_fees: float, p_meaningful_prize: float,
      alpha: float, facts_status_worst: str, calibrated: bool)
```

- **Joint ranks for every field size.** In each scenario our entries are ranked together with the field: an entry's rank is `1 + (opponents strictly above it) + (our entries strictly above it)`. There is no "additive" mode; a lineup's own copies and our other entries always occupy ranks (VERIFIED ADJUDICATION-R2 V-R2-4: ranking each entry against the field alone pays two first prizes for one).
- **Tie split (the only formula).** A tie group occupying ranks `r` to `r + t - 1`, where `t` counts opponent copies of the lineup, other opponents with the same score, and our own entries with the same score, pays each member `sum(W(j) for j in r .. r+t-1) / t`, and nothing for places beyond `places_paid`. **Top-1% attribution** uses the same rule with `W_top1(j) = W(j)` when `j <= k_top1` and 0 otherwise, so a tie straddling place `k_top1` credits only the top-1% places' money. Example: two entries tied over $100 and $60 with `k_top1 = 1` each get $80 in total and $50 of top-1% money.
- **Conservation (tested):** across all entrants, payouts sum to the paid pool and top-1% allocations sum to `top1_pool`.
- **Copies are counted once.** Equal-score opponents are split into copies of the entry (mean `n_opponents * max(0, copy_rate[h] - sampled_share[h])` added to the field's own mass at that score, Poisson, truncated at `settle.max_copies`) and other equal-score lineups (from `p_equal`).
- **Expected outputs** (`top1_exp`, `prize_exp`): exact expectations over the opponent counts (binomial in `p_above` and `p_equal`, summed over every rank whose binomial probability exceeds 1e-12 (exact to floating-point precision)) and the copies, with our entries' positions fixed by the scenario's scores. Linearity of expectation makes these exact for each entry without the joint distribution of opponent counts.
- **Realized outputs** (`top1_draw`, `prize_draw`): one joint outcome per scenario, **independent of which portfolio is being settled**: opponent counts are drawn top-down on the contest's score lattice, each bin's count drawn conditionally on the bins above it and keyed by `(run_seed, set_name, scenario, contest_id, bin)`; copies are keyed by `(run_seed, set_name, scenario, contest_id, lineup_hash)`; our entries are then placed into that realized field and paid by the tie rule. Bins below the lowest entry's score are never drawn. Probabilities (`p_top1_any`, every Goal 2 quantity) come only from realized outputs, except `p_top1_any` for a single entry, which uses the exact binomial because one entry has no joint dependence.
- **Common random numbers (tested):** two portfolios that differ by one entry give every unchanged entry the same realized rank, apart from the push of the swapped entry.
- **`night_goal2`** sums `prize_draw` over every contest and entry in each scenario and averages the indicator `winnings < alpha * fees_total`; it never thresholds an expected value. `p_washout` is the share of scenarios with zero realized winnings; `p_meaningful_prize` the share where some entry wins at least 10 times its fee.
- Tiny-contest tests (section 14) fix the arithmetic.

## 10. Candidates, selection and the portfolio (produced by C09; consumed by C10, C12, export)

```
Candidate(lineup: tuple[dk_id, ...] in canonical slot order, lineup_hash, salary, games: set, projection_mean)
```

- **`lineup_hash` (one definition for the whole engine; implemented in C01):** `sha1` of the sorted tuple of `f"{person_key}|{role}"` strings, where `role` is `CPT` for the Captain slot and `UTIL` for every other slot in both formats. Slot permutations of the same Classic players hash the same; the same six Showdown players with a different Captain hash differently; field lineups parsed from standings files (names, not DraftKings IDs) hash to the same value as ours. `FieldSample.copy_rate` and every duplicate check key on it.
- **`settlement_fn`** passed to `select_contest` has the signature `settlement_fn(entry_points: float32[S, n], entry_hashes: list[str]) -> Settlement`, closed over the contest facts, the field scores for the set in use, the copy-rate lookup and the draw key.

```
CandidatePool(slate_key, contest_family, candidates: list[Candidate], scores: float32[S, K] per set_name)
Portfolio(contest_id, entries: list[(entry_id, Candidate)], G1, G1_no_dup, p_top1_any, sanity: SanityReport, frozen: bool,
          search_quality: {greedy_bound: "1-1/e (k=1 contest)"|"none (heuristic)", greedy_method: "exact_incremental"|"lazy_fallback", insurance: "best found"|"not run"})
NightPortfolio(run_id, portfolios: list[Portfolio], goal2: Goal2 | None, concentration: {person_key: share}, cap_applied: float, cap_relaxed_from: float|None,
               per_game_exposure: {game_id: share}, release_state: "floor"|"baseline"|"optimizer")
SanityReport(cap_used_mean, duplicate_lineups_in_contest: int, cap_honored: bool, below_projection_floor: int, low_p_active_players: list, passed: bool, notes: list[str])
```

- `generate_classic(slate, scenario_set, public_view, settings) -> CandidatePool` (GLPK via `swiglpk`, OR-Tools CBC fallback, Hall formulation, deterministic tie-break).
- `enumerate_showdown(slate, projections, settings) -> CandidatePool` (R2-33): every legal lineup over a **subset** of the pool: players with `p_active >= 0.5` and projected minutes at least `select.showdown_min_minutes`, capped at the `select.showdown_pool_max` highest projected (C09 measures 22 and 26 and records the choice); the result is labeled "searched over N of M players" and the brief names the players left out. (The Oct 14 DEN@LAC pool had 41 players, 37 active, and 13,635,490 legal lineups; the 22 highest-average active players give 440,384, V-R2-18.) Then `screen(pool, scenario_set_screening, keep=settings.select.showdown_keep)`.
- **`select_contest(contest_facts, pool, settlement_fn, n_entries, settings) -> Portfolio` (R2-5):** greedy on the marginal gain in Goal 1 under the joint settlement. Method `exact_incremental` (default): after adding an entry, recompute other candidates' gains only in the scenarios where the added entry has nonzero top-1% value, since gains change nowhere else. The 1-1/e bound holds only when the payout curve extended by its drop to zero after place `k_top1` is convex, which in practice means `k_top1 == 1` (fields under 200); otherwise the result is "best found (heuristic)" (VERIFIED ADJUDICATION-R2 V-R2-4b). `lazy_fallback` (lazy upper bounds) is allowed only if `exact_incremental` misses the runtime test, and is labeled.
- `assign_slots(lineup, slate) -> slot order` (later-game players into UTIL, then G/F).
- `concentration_cap(portfolios, settings) -> (cap_applied, relaxed_from)`.
- Floor (C04a): `floor_portfolio(slate, projections.simple_points, settings) -> NightPortfolio` (one solver run per entry with a small perturbation, `p_active < 0.5` players excluded, cap applied, release_state "floor", G1 and goal2 `None`).

## 11. Ledger, validator, exporter, re-solve, swap, repair (C03, C04a, C10, C11a)

### 11.1 `Ledger` (`runs/<night>/ledger_<slate_key>.json` live; under the drill folder in drill mode)

```
Ledger(slate_key, slate_fingerprint, night_date, entries: {entry_id: {committed: Lineup|None, pending: Lineup|None, committed_file, pending_file, news_state_hash}},
       states: {file_validity: "valid"|"invalid"|"none", news_state: hash, model_status: "floor"|"baseline"|"optimizer"|"repair"|"none", confirmed_upload: "committed"|"pending"|"none"},
       last_download: {path, hash, at}, run_lock: {holder, heartbeat})
```

- `Lineup` = a tuple of `dk_id | None` in the slate's slot order as read from the header (`None` for an empty slot).
- `dfs uploaded <file>` moves every pending lineup from that file to committed. A re-download reconciles: any entry whose downloaded lineup differs from `committed` is flagged and the downloaded lineup becomes `committed` (the platform is the truth).
- Rule: the exporter refuses to write an entry row that would revert a newer `pending` or `committed` change unless `--force` (recorded).

### 11.2 Validator

`validate(upload_rows, slate, lock_now: datetime, ledger) -> ValidationResult(ok, errors: list[(entry_id, rule, message)], warnings: list[(entry_id, rule, message)])`. Rules: cap; slot count and labels; eligibility from `Roster Position`; no repeated person (Captain and UTIL of one person count as a repeat); Classic two-game rule; Showdown both-teams rule; the CPT slot holds a CPT-role id; **locked cells unchanged**; no inserted player from a locked game; **lock unresolved** (no change touching a game whose lock time is unknown); file and slate integrity (same `slate_fingerprint`, no WNBA contest names, every matchup among the slate's games); bare integer ids; at most 500 rows. Which rows a file carries is the exporter's choice (section 11.3), not a validity rule (R2-34).

- **Locked cell (R2-6):** a cell is locked when it shows `(LOCKED)` in the latest download, **or** its player's game has `tip_local <= lock_now` by the clock, **or** its Game Info reads `In Progress` or `Final`. A download taken before a tip carries no markers, so the clock always counts.
- Every rule above is a DraftKings validity rule and blocks the row. Anything else is a warning or a label.

### 11.3 Exporter (R2-17)

`export(night_portfolio or lineups, slate, ledger, reason) -> UploadFile(path, hash, valid_until, version, changed_rows, tight_rows: list[(entry_id, lock_local)])`. The only writer to `out/uploads/` (in drill mode, to the drill folder's `uploads/`). It mirrors the download's encoding, BOM and line endings. **Rows written (R2-34):** only changed rows by default (DraftKings' instruction 5 says that is faster, R6); every row when no row changed (a round trip of the lineups already held) or with `--all-rows`. **Write order:** write the CSV to `out/uploads/.tmp/<generation_id>/`; re-read and re-validate it; rename it into place (an atomic rename on the same volume); write the manifest and then the ledger the same way (temporary file, then rename), the ledger last. Only files named in a ledger are shown as actionable in `dfs status`; on start-up, any `.tmp` generation without a ledger record is removed (C11a). Older versions move to `stale/`. Exporting never confirms an upload.

### 11.4 Re-solve (C10)

`resolve(night_inputs, news_state, ledger, scope: "pre_lock"|"post_lock", settings) -> list[UploadFile]`: re-simulate affected games on the selection and validation sets at `settings.resolve.S` (default 10,000); refresh public view and fields for slates containing them; rebuild candidates; `scope == "pre_lock"`: re-select affected contests; `scope == "post_lock"`: `swap` below; validate; export. It is attempted only when the earliest lock among affected cells is at least `resolve.min_minutes_to_lock` (default 8) away; otherwise the command runs `repair` directly. It must finish inside `settings.resolve.budget_s` (default 180) or raise `ResolveTimeout`, on which the CLI runs `repair`.

### 11.5 Swap (post-lock) (C10; freshness rule also used by C11a)

`swap(slate, downloaded_entries, projections, pool, ledger, settings) -> list[UploadFile]`: pin locked cells (section 11.2 definition); for each entry, re-optimize open slots with the candidate solver on current projections; rewrite only entries where `ledger.entries[e].news_state_hash != news_state.hash` or the open-slot improvement is at least `settings.swap.min_improvement_points` (default 3.0); re-check the concentration cap; produce a diff `[(entry_id, slot, old, new)]` in the brief.
- **Freshness (R2-14):** `dfs swap`, and `dfs repair` after a slate's first lock, refuse when `ledger.last_download.at` is earlier than the latest started tip on that slate, with the message "download a fresh entries file for <slate> first; the latest one is from <time>, before the <time> game locked".

### 11.6 Repair (C03, extended in C11a) (R2-15)

`repair(slate, lineups, ruled_out: set[person_key], pool, simple_points, lock_now) -> lineups`: for each ruled-out player in an unlocked slot, find the best legal substitute by `simple_points` per dollar subject to the cap, eligibility and locks. **Stage 1 (C03):** direct substitution into the vacated slot. **Stage 2 (C11a):** if no direct substitute is legal or a better one needs a slot move, match the entry's unlocked players plus the substitute to the unlocked slots (a small bipartite matching inside one entry; locked cells fixed). Must run under 10 seconds for a 150-entry slate; result labeled `model_status = "repair"`. Until C04a provides `simple_points`, salary is the proxy.

### 11.7 Time to lock (replaces "insufficient time") (R2-6)

- The exporter blocks only DraftKings-invalid rows (section 11.2): a changed cell that is locked or whose lock is unresolved.
- A changed row whose earliest changed cell locks within `export.tight_minutes` (default 4; replaced by the measured 90th-percentile upload time from rehearsals 1 and 2) **is exported** and listed in `UploadFile.tight_rows`; the CLI prints "tight: <entries> lock at <time>, about <n> minutes; if the upload does not finish before then, the lineup already uploaded stays in place: <file>".
- `resolve.min_minutes_to_lock` (default 8) only decides whether the re-solve is attempted (section 11.4).
- `valid_until` on every file is the earliest lock among its changed cells; an expired file is never named as the file to upload.

## 12. Run manifest and brief (C03, C04a, C09, C11a)

```
RunManifest(run_id, mode, drill_id: str | None, git_commit, config_hash, release_state,
            capabilities: {name: {enabled, status: "passed"|"stale"|"never", rehearsed_on, rehearsed_commit, rehearsed_paths, drill_artifact}},
            seeds, inputs: [{path, hash}], snapshots: [...], news_state_hash, facts_applied, outputs: [{path, hash, valid_until}],
            fallback_level: int, timings: {step: seconds}, llm_usage: {...}|None)
Brief(run_id, drill: bool, slates: [{slate_key, states: Ledger.states, latest_file, floor_file, valid_until, tight_rows, capabilities_off: [..],
      contests: [{contest_id, name, facts_status, G1, G1_no_dup, p_top1_any, n_entries, tail_fit_status}],
      goal2: Goal2|None ("not estimated" in Floor), concentration, per_game_exposure, cap_relaxed_from, sanity, facts_applied: [..], facts_not_acting: [..],
      fact_conflicts: [..], identity_warnings: [..], injury_report: {as_of, cached_teams: [..]} | None, news_that_would_change: [..], skipped: [..], input_freshness: {...}, if_engine_down: {...}}])
```

Rendered to `runs/<run_id>/brief.md` (one page per slate) and printed by `dfs night` and `dfs status`.

## 13. CLI (C01 stubs; filled by later chunks)

| Command | Chunk | Effect |
|---|---|---|
| `dfs status [--apply]` | C02 (slates), C03 (states), C04b (`--apply`: official-report diff to facts, then the repair) | Slates found, four states each, next action, injury-report diff since last run |
| `dfs night [--floor] [--no-llm] [--game-day]` | C04a (Floor), C09 (Baseline), C11a (flags, `--game-day`), C11b (researcher pass) | Ingest, Floor export, then Baseline build if the release state allows |
| `dfs out/in` | C04a (facts and repair), C10 (re-solve) | Write facts; run the repair or the re-solve |
| `dfs fact veto <fact_id>` | C04a | Stop a fact from acting (recorded) |
| `dfs start "<TEAM>: A, B, C, D, E"` | C11a | Write starter facts; run the same path as `dfs out` |
| `dfs restrict "<name>" <minutes>`, `dfs restrict "<name>" --clear` | C06 | Write a `restriction` (minutes cap) or `restriction_cleared` fact with the user as source; run the same path as `dfs out` |
| `dfs news` | C11a (repair path), C10 (re-solve) | The repair over the current news state (C11a's Floor body), replaced by the re-solve on the current news state (C10) |
| `dfs swap` | C11a (post-lock repair), C10 (open-slot) | The post-lock repair with the freshness check (C11a's Floor body), replaced by post-lock open-slot re-optimization (C10) |
| `dfs repair` | C03 (stage 1), C11a (stage 2, freshness) | The legal repair of the latest file |
| `dfs uploaded <file>` | C03 | Commit pending lineups from that file |
| `dfs results` | C13 | Standings ingest, scorecards, flashback |
| `dfs research fetch <url>` | C11b | Allowlisted fetch that saves the page |
| `dfs unlock` | C11a | Lift the game-night code freeze (recorded) |
| `dfs rehearsed <capability>` | C11a | Record a passed drill: date, commit, paths, artifact |
| `dfs enable <capability>` | C11a | Switch a capability on; refused unless its status is `passed` or `dfs unlock` is recorded (section 1) |
| `dfs disable <capability>` | C11a | Switch a capability off |
| `dfs drill news --at <minutes>` | C11a (timer for the late-news path that exists), C10 (re-solve timing; drill mode runs it regardless of the flag once built, section 1) | Replay a scripted scratch in drill mode and time it |
| `dfs replay <run_id>` | C19 | Re-execute from snapshots |
| `dfs history status` | C05 | Freshness of the history sources and the `nba_api` budget |
| `dfs digest` | C06 | Print tonight's news digest |
| `dfs sim --slate <key> --set <name>` | C07 | Write a scenario set and print per-player summaries |
| `dfs field --slate <key>` | C08 | Print ownership, common lineups, cutoffs |
| `dfs insure [--run <run_id>]` | C12 | Re-run the insurance search on a saved run and print the trace |

Chunks after the MVP add their own commands to this table in the same commit.

Global options on every command: `--night <date>`, `--as-of <datetime>`, `--fixtures`, `--json`, `--yes` (section 1.1).

Exit codes: 0 ok; 2 validation failure (no file written); 3 input missing or unparseable (plain-language message names the file and the fix); 4 budget exceeded (repair ran if applicable); 5 refused by a guard (stale download, ambiguous name, capability not rehearsed), with the plain-language reason.

## 14. Fixtures every chunk may rely on (created by C01 and C02; two tiny fixtures by C09 and C10)

**Where they live (R2-33; the GitHub repository is public).** Real DraftKings files (the owner's entries and salary files, his post-lock re-downloads) and third-party downloads (NBA injury PDFs, other people's salary files, the ESPN-derived parquet) **never enter git**. They live in local-only folders listed in `.gitignore` (`fixtures/dk/20*/`, `fixtures/dk/layout/`, `fixtures/dk/public/`, `fixtures/injury/`, `fixtures/history/`) and are rebuilt on this laptop by `scripts/build_fixtures.py` from `spikes/**/out/downloads/`, `data/archive/<night>/` and two files outside the repository named below. Tests that need them carry the `realfiles` marker and **fail with a message naming the missing file and the rebuild command** when it is absent; they skip only when the environment variable `NBADFS_ALLOW_MISSING_REALFILES=1` is set (for example in a cloud session). Hand-written fixtures (`fixtures/tiny/`, `fixtures/identity/`, `fixtures/synthetic/`) are committed. The standings-hashing salt lives in `config/standings_salt.txt`, gitignored, never committed.

- `fixtures/dk/<night>/` (local only; R2-34): `scripts/build_fixtures.py` builds one folder for every archived night in `data/archive/<night>/`, so `2026-10-14`, `2026-10-15` and `2026-10-16` appear as the owner's files are archived; in each, `post_lock_entries.csv` is a copy of the latest Classic entries download taken after that slate's first lock, when one exists. `fixtures/dk/2026-10-14/`: the owner's real files of Oct 14, already archived in `data/archive/2026-10-14/` with a hash manifest: `DKEntries_163.csv` (Classic, 7 games, one entry), `DKEntries_164.csv` (Showdown DEN@LAC, one entry), `DKSalaries_187.csv` and `DKSalaries_188.csv` (with `Status`), plus tonight's post-lock re-downloads if captured. `fixtures/dk/2026-10-15/`: the Oct 15 files and their post-lock re-download (rehearsal 1). `fixtures/dk/2026-10-16/`: the Oct 16 files (rehearsal 2), the saved night for Drills A and B.
- `fixtures/dk/layout/` (C02, R2-8): a many-entry entries file whose entry rows overlap the pool rows (built from a real file by adding entries), and a post-lock re-download with `In Progress` Game Info.
- `fixtures/dk/public/`: public NBA salary files 2018 to 2026 from `spikes/dk/out/downloads/github/`, excluding `rosteropt_nba_wnba_showdown.csv` (a WNBA file); and the April 2026 NBA salary file, `fixtures/dk/public/dk_nba_2026-04-15.csv` (a 2-game slate of 2026-04-15, 70 players, no `Status` column), copied from `C:\Users\benja\Documents\dfs-os\reference-docs\sample-data\dk_nba_salaries_sample.csv` (R2-34).
- `fixtures/injury/`: the two March 2026 injury-report PDFs (from `spikes/data/out/downloads/nba_injury_pdf/`), which include NOT YET SUBMITTED rows.
- `fixtures/history/player_box_2026.parquet`: last season's box scores (from `spikes/data/out/downloads/sportsdataverse/`).
- `fixtures/history/entry_history.csv` (R2-34): the owner's DraftKings entry-history export (432 NBA rows, R8), copied from `C:\Users\benja\Downloads\draftkings-contest-entry-history.csv`; C04a's contest-name tests and C04b's parser test read it.
- `fixtures/identity/names.json` (C02, R2-9, R2-33): a traded player (same person, two teams, for example Giannis Antetokounmpo MIL to MIA), suffix and accent variants (`Tim Hardaway Jr.`, `Hardaway Jr., Tim`, `Nikola Jokić`), the near-homonyms Nikola Jokic and Nikola Jovic, the seven Joneses and seven Williamses from the Oct 14 Classic pool, two different players whose names normalize alike, and an ESPN team code that differs from DraftKings' (`NY`, `NYK`).
- `fixtures/synthetic/night8.json`: the R9 spike's synthetic 8-game night inputs, for the mechanics regression test (ADR-027); serialized by C07, README only from C01.
- `fixtures/tiny/` (committed; R2-34): small contests whose expected values are computed by hand under section 9's rules and written into the file.
  - **How a tiny contest is written.** Each file states `n_opponents`, the payout table, our entries (lineup hash and points per scenario), the copy rates, and the opponents' score distribution per scenario as explicit point masses (score to probability). A **degenerate field** is one where `p_above` and `p_equal` are exactly 0 or 1 at every score our entries take (for example every opponent scores exactly 250); only those give counted ranks. Opponents with different scores are not degenerate: ten opponents of whom three score above our entry are a Binomial(10, 0.3) case, not rank 4. Binomial cases use their full binomial sums (section 9); their hand values come from `fixtures/tiny/compute_expected.py`, a short standalone script that does not import `nbadfs` and prints its arithmetic. Tests compare to 1e-9.
  - **Settlement fixtures with hand values, written by C01 (eleven):** `tiny_10_entries_3_paid.json`; `tiny_tie_at_boundary.json` (more tied entries than paid places); `tiny_two_ours_adjacent.json` (our second entry pushed down one rank by our first); `tiny_copy_at_first.json`; `tiny_tie_100_60.json` (two-way tie over $100 and $60: $80 each, $50 top-1% each with k = 1); `tiny_tie_across_k.json` (a three-way tie straddling place k); `tiny_joint_vs_additive.json` (k = 1, two of our entries above every opponent: total 1,000, not 2,000); `tiny_goal2_binary.json` (one entry with a 10% chance of $100 and fees of $10: P(severe drawdown) = 0.9; plus a two-entry variant with correlated scores); `tiny_same_score_diff_hash.json` (two entries with identical scores and different hashes and copy rates settle differently); `tiny_eighth_apart.json` (scores 300.25 and 300.375 have different `p_above`); `tiny_conservation.json` (payouts sum to the paid pool and top-1% allocations to the top-1% pool). The conservation test runs on every one of them whose field is degenerate (each entrant's payout is countable there), and `tiny_conservation.json` exists to make sure at least one multi-tie case is covered.
  - **One property fixture, written by C01 with inputs only and no hand values:** `tiny_crn_swap.json`: the test asserts that unchanged entries keep their realized ranks across two portfolios differing by one entry, apart from the swapped entry's push.
  - **Built by their consuming chunks:** `tiny_infeasible_cap_showdown.json` (C09: six Showdown slots over nine credible players; the minimum feasible cap is 6/9 = 66.7% per entry on average) and `tiny_same_team_two_out.json` (C10: a re-solve acceptance case).

## 15. Settings (`config/settings.toml`) referenced above, with defaults

```
[inbox] downloads_dir = "~/Downloads", copy_retries = 3, retry_ms = 250, skip_suffixes = [".crdownload", ".part", ".tmp"], skip_prefixes = ["~$"]
[archive] enabled = true
[projections] p_active = {out = 0.0, doubtful = 0.25, questionable = 0.55, probable = 0.9, available = 1.0}, dk_status = {OUT = 0.0, O = 0.0, IR = 0.0, SUSP = 0.0, NA = 0.0, D = 0.25, Q = 0.55, GTD = 0.55, P = 0.9, "" = 1.0}   # unknown codes: 0.55 and flagged
[goal2] alpha = 0.25
[insurance] epsilon = 0.02, min_sd_scenarios = 50   # switched on only by the `insurance` capability in capabilities.toml (section 1)
[scenarios] screening = 5000, selection = 15000, validation = 15000, reporting = 30000
[settle] max_copies = 50
[select] showdown_keep = 5000, classic_pool = 8000, projection_floor_share = 0.85, cap_used_min = 0.95, p_active_min = 0.5, greedy = "exact_incremental", showdown_pool_max = 22, showdown_min_minutes = 12
[concentration] cap = 0.60
[resolve] S = 10000, budget_s = 180, min_minutes_to_lock = 8
[export] tight_minutes = 4
[swap] min_improvement_points = 3.0
[repair] max_seconds_150 = 10
[redistribution] shrink_minutes = 300, max_teammate_shift = 8
[llm] inference_blend_enabled = false, coverage_factor = 1.5, max_searches = 12, max_fetches = 8, game_day_max_searches = 6
[public_view] formula_weights = {salary_value = 0.4, team_share = 0.4, trailing_ppm = 0.2}
[field] tail_share = 0.03, tail_min_points = 20, showdown_salary_left_decay = 2.5   # decay per $1,000 left unspent; BET default (R2-23)
[field.<family>] optimizer_share, casual_share, duplicator_share, stale_share, optimizer_noise, salary_floor   # one table per contest family; C08 sets the defaults
[facts] paid_share = {gpp = 0.23, double_up = 0.45}, rake = 0.15, first_place_cap_large = 0.20, first_place_cap_small = 0.15
```

Removed in v2: `settle.exact_max_field` (there is no additive mode, R2-5). Removed in R2-34: `settle.rank_window_sd` (expected outputs sum every rank above 1e-12, section 9). Any chunk, not only those after the MVP, that introduces a key its own file names (for example `[watch]`, `[qa]`, `[cache]`, `[props]`, `[digest]`, `[learn]`, `[edge]` after the MVP) adds it here and to `config/settings.toml` in the same commit, and the C01 settings test then covers it.
