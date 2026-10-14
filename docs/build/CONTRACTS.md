# Contracts: the interfaces between components

**Changelog:** 2026-10-14 created (Stage 3 of the adjudication session). **Owner of this file:** chunk C01 turns every contract here into code (pydantic models, function signatures with docstrings, and fixture files) and every later chunk builds against those, never against prose. If a chunk must change a contract, it changes this file and the code in the same commit and records the change in `docs/build/PROGRESS.md`.

**How to read this.** Each contract has: what it is, who produces it, who consumes it, its fields or signature, and the rule that must hold. Sections are numbered so chunk files can point to them ("CONTRACTS section 4.2"). Field names are the names used in code. "Person key" means the engine's stable identifier for a human player (`<normalized name>|<team>`), never a DraftKings ID, because DraftKings IDs change between slates and between Captain and UTIL roles.

---

## 1. Directory layout and naming

```
nba-dfs/
  pyproject.toml            uv-managed; package `nbadfs`; CLI entry point `dfs`
  src/nbadfs/
    cli.py                  Typer app; every command returns JSON on --json and plain text otherwise
    schemas/                pydantic models, one module per contract section below
    ingest/  facts/  history/  projections/  sim/  field/  settle/  select/  validate/  export/  resolve/  brief/  learn/  llm/
  tests/                    pytest; `-m smoke` under 60 s; full suite under 5 min
  fixtures/                 real DraftKings NBA files (2026-27 preseason), hashed standings tables, synthetic nights; never other users' raw names
  config/
    settings.toml           every tunable named in this file, with defaults
    posture.toml            data posture: permissive_plus_nba_api (D1)
    capabilities.toml       per capability: enabled, rehearsed_on (date or empty)
  inbox/                    auto-filed DraftKings downloads (gitignored)
  data/archive/<date>/      every raw download and pre-lock snapshot (gitignored)
  data/snapshots/<date>/    source responses and fetched pages (gitignored)
  data/history/             parquet history (gitignored)
  runs/<run_id>/            one folder per engine run (gitignored)
  out/uploads/              upload files; out/uploads/stale/ for superseded ones (gitignored)
```

- **Run id:** `YYYYMMDD-HHMMSS-<mode>` in local time, mode one of `night`, `news`, `swap`, `repair`, `results`.
- **Upload file name:** `<slate_key>_<lock HHMM local>_v<n>.csv`, for example `classic_main_1800_v5.csv`, `sd_BOS-DET_1400_v2.csv`. `n` increases per slate per night; the latest valid file is also symlinked or copied as `<slate_key>_latest.csv`.
- **Slate key:** `classic_<draft group id>` or `sd_<AWAY>-<HOME>`; `classic_main` is an alias the night plan assigns to the largest Classic slate.
- **Times:** stored as ISO 8601 with offset; displayed in Central. DraftKings Game Info is Eastern and is converted on parse.

### 1.1 Clock and saved-night mode (owned by C03)

Every command accepts `--night <YYYY-MM-DD>` and `--as-of <ISO datetime>`. `--night` points the engine at `inbox/<date>/` (or `fixtures/dk/<date>/` when `--fixtures` is given) instead of the Downloads folder and at that night's ledger and news state; `--as-of` is the clock every lock rule reads (`lock_now` in `validate`, the started-game rule, the insufficient-time rule, the "valid until" stamp) instead of the wall clock. Without them the engine uses today and now. Rule: no module reads the wall clock directly; all read `Clock.now()`. This is what makes the weekend drills on the saved Oct 16 files runnable.

## 2. DraftKings input files (consumed by chunk C02; produced by the owner)

### 2.1 Entries file (`DKEntries*.csv`)

The export from "Edit entries" for one draft group. Rows 1..n describe entries; after a blank line the file lists the slate's player pool.

- **Entry row columns (Classic):** `Entry ID, Contest Name, Contest ID, Entry Fee, PG, SG, SF, PF, C, G, F, UTIL`. **Showdown:** `Entry ID, Contest Name, Contest ID, Entry Fee, CPT, UTIL, UTIL, UTIL, UTIL, UTIL`. Slot labels are read from the header, never assumed.
- **Slot cell:** empty, or `<Name> (<dk_id>)`, or `<Name> (<dk_id>) (LOCKED)` after the player's game has started. The engine writes bare integer `dk_id` values on export (section 10).
- **Player-pool columns:** `Position, Name + ID, Name, ID, Roster Position, Salary, Game Info, TeamAbbrev, AvgPointsPerGame`. `Roster Position` is a `/`-joined eligibility list (Classic: for example `PG/G/UTIL`; Showdown: `CPT` or `UTIL`). `Game Info` is `AWAY@HOME MM/DD/YYYY HH:MMPM ET`.
- **Rule:** the pool inside the entries file is the authoritative player list for that slate (158 of 158 IDs matched the salary file, R6). The salary export is optional.
- **Parsed model:** `EntriesFile(slate_key, draft_group_id, downloaded_at, entries: list[Entry], pool: list[PoolPlayer], encoding, bom, newline)`. `Entry(entry_id, contest_id, contest_name, fee, slots: list[SlotCell])`, `SlotCell(slot_label, dk_id | None, locked: bool, raw)`. `PoolPlayer(dk_id, name, person_key, team, roster_positions, salary, game: GameRef, role: "CPT"|"UTIL"|"CLASSIC", avg_points)`.

### 2.2 Salary file (`DKSalaries*.csv`), optional

Columns as the pool above; 2026 exports for other sports add `Status` and `Starting`; an April 2026 NBA file did not (RR4). Parsed to the same `PoolPlayer` plus optional `status`, `starting`. Rule: when present and newer than the entries file for the same draft group, its `Status` values feed availability (section 6).

### 2.3 Payout paste (`inbox/payouts/<contest_id>.txt`)

Free text copied from the contest's payout table. Parser accepts lines like `1st $200,000`, `2nd-3rd $50,000`, `352nd-500th $50`, `Top 23% $...`. Produces `PayoutCurve` (section 3.2) with `facts_status = "verified"`.

### 2.4 Entry-history export (`draftkings-contest-entry-history.csv`), weekly

The 14-column export; parser ported from the NHL engine (ADR-018). Gives `field_size`, `places_paid`, `prize_pool`, our `place`, `points`, `winnings` per past contest. Feeds contest-facts templates (`facts_status = "template"`) and the results step.

### 2.5 Standings file (`contest-standings-<id>.zip` or `.csv`), after the MVP

Columns `Rank, EntryId, EntryName, TimeRemaining, Points, Lineup, Player, Roster Position, %Drafted, FPTS`. Parsed in the private folder; `EntryName` is replaced by `sha256(name + salt)[:12]` before any row enters the project.

### 2.6 Official injury report (PDF)

`https://ak-static.cms.nba.com/referee/injury/Injury-Report_<YYYY-MM-DD>_<HH_MM>[AP]M.pdf`; one file per 15-minute slot (2026 pattern) or one hourly file overwritten within the hour (October 2025 pattern); the adapter tries both. Parsed rows: `(game_date, matchup, team, player_name, status in {Out, Doubtful, Questionable, Probable, Available}, reason)`. Unrecognized statuses are logged and the row kept with `status = "Unknown"`.

## 3. Slate, contest and contest facts (produced by C02 and C04; consumed by everything)

### 3.1 `Slate`

`Slate(slate_key, format: "classic"|"showdown", draft_group_id, games: list[GameRef], first_lock, last_lock, pool: list[PoolPlayer], entries: list[Entry], contests: list[Contest], source_file, source_hash)`. `GameRef(game_id, away, home, tip_local, tip_et)`. Rule: `first_lock` is the earliest `tip_local` among games; Showdown `first_lock == last_lock`.

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

## 4. News state, facts and inferences (produced by C06, C10, C11; consumed by projections, the re-solve, the brief)

### 4.1 `NewsState` (`runs/<night>/news_state.json`, one per night, append-only with supersession)

`NewsState(night_date, facts: list[FactRecord], inferences: list[InferenceRecord], applied_at: datetime)`.

### 4.2 `FactRecord`

```
FactRecord(
  fact_id, created_at, kind: "out"|"in"|"questionable"|"starter_announced"|"bench_announced"|"restriction"|"pool_exclusion"|"data_flag",
  visibility: "public"|"private",
  player: {person_key, name}, team, game_id,
  detail: {restriction_minutes: int|None, in_place_of: person_key|None, status: str|None},
  source: {kind: "user"|"llm"|"official_report"|"dk_status", model: str|None,
           evidence: [{url, snapshot_id, quote, published_at: datetime|None}]},
  supersedes: fact_id | None,
  acts: bool                   # computed: True only if (source.kind in user/official/dk_status) or (quote verified and published_at known and within 24h)
)
```

Rules: a later fact for the same `person_key` supersedes an earlier one of any kind; `acts == False` records are stored and shown, never applied; `kind == "out"` from any acting source sets `p_active = 0`; `starter_announced` sets `p_start = 1` and uses the role's starter minutes prior; `restriction` sets `minutes.hard_cap`; `in` restores the model prior and marks lineups built for the absence for re-selection.

### 4.3 `InferenceRecord`

Same header as a fact plus `minutes: {q10, q50, q90, hard_cap}`, `usage_multiplier: {q10, q50, q90}`, `stat_multipliers: {stat: {q10, q50, q90}}`, `redistribution_hint: [{person_key, minutes_weight}]`, `no_history_prior: {comparable_role, minutes_range}|None`, `condition: [{person_key, status}]|None`, `rationale`. Rule: weight 0 in the simulation until `settings.llm.inference_blend_enabled` is true (set only by the learning loop after two weeks of coverage evidence).

### 4.4 Commands that write facts

`dfs out "<name>"`, `dfs in "<name>"`, `dfs start "<TEAM>: <A>, <B>, <C>, <D>, <E>"` (writes five `starter_announced` facts and `bench_announced` for the previous expected starters), `dfs fact veto <fact_id>`. Each fuzzy-matches names against tonight's pools (accent folding, suffixes), asks one confirmation unless `--yes`, then, unless `--no-run`: runs the re-solve (section 11.4) when the `resolve` capability is enabled, and otherwise runs the legal repair (section 11.6) on the latest committed lineups. The flag-off path never rebuilds the Floor over an uploaded portfolio; `dfs night --floor` is the explicit way to rebuild.

### 4.5 `NewsDigest` (`runs/<run_id>/llm/news_digest.json`)

List of items `{person_key, name, team, game_id, reason: str, official_status, dk_status, p_active, exposure_entries, fees_at_risk, minutes_to_lock}` sorted by `fees_at_risk` descending, then `minutes_to_lock` ascending; includes unrostered players whose status moves a rostered beneficiary.

## 5. History and priors (produced by C05; consumed by C06)

- `data/history/player_box.parquet`: one row per player-game: `game_id, date, season, person_key, team, opp, home, starter, minutes, pts, fg2m, fg2a, fg3m, fg3a, ftm, fta, reb, ast, stl, blk, tov, dk_points, source ("sportsdataverse"|"nba_api")`.
- `data/history/team_game.parquet`: `game_id, date, team, opp, possessions, pts, pace, margin, ot_periods, spread_close, total_close` (lines filled when available).
- `Rates` per player: `rate_per36[stat]`, `usage_share`, `shrinkage_weight`, `games`, `minutes_total`, `early_season_var_mult`. Function: `build_rates(history, as_of_date, settings) -> dict[person_key, Rates]`.
- Rule: `as_of_date` strictly precedes the slate date in every backtest.

## 6. Projections (produced by C06; consumed by C07 and the Floor)

```
PlayerProjection(
  person_key, team, game_id, dk_ids: {"CLASSIC"|"CPT"|"UTIL": dk_id}, salary_by_role,
  p_active, p_start,
  minutes: {q10, q50, q90, hard_cap: float|None}, minutes_source: "model"|"fact:<kind>"|"user",
  usage_share, rates: Rates, early_season_var_mult,
  simple_points: float          # the Floor's projection: last-season dk_points/minute * minutes.q50, salary-implied when no history
)
ProjectionTable(run_id, as_of, players: list[PlayerProjection], team_totals: {team: {implied_total, pace, spread}}, facts_applied: [fact_id])
```

- **Fact translation rules** (`projections/facts.py`): one pure function per `kind`, unit-tested, no LLM numbers.
- **Share model:** `redistribute(team_players, absent: set[person_key], evidence) -> new minutes and usage shares` with the position-similarity prior and a shrinkage constant setting (`settings.redistribution.shrink_minutes = 300`); minutes sum to 240 per team in expectation.
- **Market anchor:** `anchor(projections, lines: {game_id: {spread, total}}, props: optional) -> projections`; props optional (`None` when the credit budget says so).

## 7. Scenarios (produced by C07; consumed by C08, C09, C10)

```
ScenarioSet(
  name: "screening"|"selection"|"validation"|"reporting", S: int, seed: int,
  players: list[person_key],                     # column order, sorted by person_key
  points_util: float32[S, P], points_cpt: float32[S, P],   # DraftKings points per scenario per player (cpt = 1.5 x util)
  active: bool[S, P], minutes: float16[S, P],
  game_margin: float32[S, G], game_ot: int8[S, G],
  model_error: {team_shift: float32[S, T], player_shift: float32[S, P]}
)
```

- Sizes: screening 5,000; selection 15,000; validation 15,000; reporting 30,000 (settings; ADR-025 and ARCHITECTURE section 2 must agree; a test checks).
- **Determinism:** every draw keyed by `(run_seed, set_name, scenario_index, game_id, person_key, stat)` with a counter-based generator (`numpy.random.Philox` or equivalent); `simulate_game(night, game_id, S, seed) -> game arrays`; re-simulating one game with new availability changes only that game's columns.
- **Scoring:** `score_lines(box: BoxArrays, rules_version) -> (points_util, points_cpt)`; Captain stored as float32 of an eighth-point exact value.
- Function: `simulate(night: NightInputs, set_name, settings) -> ScenarioSet`. `NightInputs = (projections, slates, news_state, lines)`.

## 8. Field model (produced by C08; consumed by settlement, selection, the brief)

```
PublicView(run_id, players: {person_key: {proj_points, value, popularity, p_active_public}}, source: "dff"|"formula", facts_applied_public: [fact_id])
FieldSample(contest_id, lineups: int32[M, slots] (dk_id indices into the pool), weights: float32[M], entrant_type: int8[M], user_id: int32[M],
            ownership: {role: {person_key: float}}, copy_rate: {lineup_hash: float}, built_from: PublicView.run_id)
FieldScores(contest_id, set_name, cdf_grid: float32[S, Q])   # per scenario, the field's score at Q = 400 evenly spaced probabilities from 0 to 1 (a quantile grid: index q holds the score below which a fraction q/(Q-1) of the weighted field falls); F_{c,s}(x) by interpolation of x into that row
```

- `build_public_view(slate, lines, facts_public, dff_file|None) -> PublicView`; when `dff_file` is `None` or fails to parse, use the deterministic formula (settings `public_view.formula_weights`); never read `ProjectionTable` from the engine view.
- `build_field(contest_facts, slate, public_view, settings) -> FieldSample` with entrant mixture weights by contest family (`settings.field.<family>`), sampled as users (multi-entry users share cores).
- `score_field(field_sample, scenario_set) -> FieldScores` in chunks of scenarios.
- Ownership sums: Classic 8.0; Showdown 1.0 CPT + 5.0 UTIL (checked).

## 9. Settlement and the goals (produced by C08; consumed by C09, C12, C13, the brief)

```
settle(contest: ContestFacts, our_scores: float32[S, n], copy_rates: float32[n], field: FieldScores, mode: "exact"|"additive") -> Settlement
Settlement(
  contest_id, set_name,
  prize_top1: float32[S, n],      # expected prize from top-1% places per entry per scenario (after tie splits)
  prize_all: float32[S, n],       # expected prize from any paid place
  rank_mean: float32[S, n],
  G1: float,  G1_se: float,       # mean over s of sum over n of prize_top1 / top1_pool
  G1_no_dup: float,               # same with copy rates set to zero
  p_top1_any: float,              # raw probability at least one entry in the top 1%
  facts_status: str
)
night_goal2(settlements: list[Settlement], fees_total: float, alpha: float, unfilled_entries: int) -> Goal2
Goal2(p_sd: float, p_sd_se: float, p_washout: float, winnings_mean: float, p_recover_fees: float, p_meaningful_prize: float, alpha: float, facts_status_worst: str, calibrated: bool)
```

- `mode = "exact"` when `field_size < settings.settle.exact_max_field` (default 10,000): our entries' ranks interact. `"additive"` otherwise during selection; reporting always `"exact"`.
- The binomial for opponents-above uses `F_{c,s}` from `FieldScores`; the expectation sums the binomial mass over ranks within `settings.settle.rank_window` (default mean plus or minus 4 standard deviations) and the payout at each rank; copies `D ~ Poisson(N' * q)` truncated at `settings.settle.max_copies` (default 50).
- **Tie split:** prize at rank r with D copies = mean of `W(r + j)` for `j = 0..D`, divided by `1 + D`.
- Tiny-contest tests (CONTRACTS section 14) fix the arithmetic.

## 10. Candidates, selection and the portfolio (produced by C09; consumed by C10, C12, export)

```
Candidate(lineup: tuple[dk_id, ...] in canonical slot order, lineup_hash, salary, games: set, projection_mean)
```

- **`lineup_hash` (one definition for the whole engine):** `sha1` of the sorted tuple of `f"{person_key}|{role}"` strings, where `role` is `CPT` for the Captain slot and `UTIL` for every other slot in both formats. Slot permutations of the same Classic players hash the same; the same six Showdown players with a different Captain hash differently; field lineups parsed from standings files (names, not DraftKings IDs) hash to the same value as ours. `FieldSample.copy_rate` and every duplicate check key on it.
- **`settlement_fn`** passed to `select_contest` has the signature `settlement_fn(entry_scores: float32[S, n]) -> Settlement`, closed over the contest facts, the field scores for the set in use, the copy-rate lookup by `lineup_hash`, and the mode.

```
CandidatePool(slate_key, contest_family, candidates: list[Candidate], scores: float32[S, K] per set_name)
Portfolio(contest_id, entries: list[(entry_id, Candidate)], G1, G1_no_dup, p_top1_any, sanity: SanityReport, frozen: bool, search_quality: {greedy_bound: "1-1/e on count limit", insurance: "best found"|"not run"})
NightPortfolio(run_id, portfolios: list[Portfolio], goal2: Goal2, concentration: {person_key: share}, cap_applied: float, cap_relaxed_from: float|None, per_game_exposure: {game_id: share}, release_state: "floor"|"baseline"|"optimizer")
SanityReport(cap_used_mean, duplicate_lineups_in_contest: int, cap_honored: bool, below_projection_floor: int, low_p_active_players: list, passed: bool, notes: list[str])
```

- `generate_classic(slate, scenario_set, public_view, settings) -> CandidatePool` (GLPK via `swiglpk`, OR-Tools CBC fallback, Hall formulation, deterministic tie-break).
- `enumerate_showdown(slate) -> CandidatePool` (all legal lineups), `screen(pool, scenario_set_screening, keep=settings.select.showdown_keep)`.
- `select_contest(contest_facts, pool, settlement_fn, n_entries, settings) -> Portfolio` (lazy greedy on marginal G1).
- `assign_slots(lineup, slate) -> slot order` (later-game players into UTIL, then G/F).
- `concentration_cap(portfolios, settings) -> (cap_applied, relaxed_from)`.
- Floor: `floor_portfolio(slate, projections.simple_points, settings) -> NightPortfolio` (one solver run per entry with a small perturbation, OUT players excluded, cap applied, release_state "floor", G1 and goal2 `None`).

## 11. Ledger, validator, exporter, re-solve, swap, repair (C03, C10)

### 11.1 `Ledger` (`runs/<night>/ledger_<slate_key>.json`)

```
Ledger(slate_key, night_date, entries: {entry_id: {committed: Lineup|None, pending: Lineup|None, committed_file, pending_file, news_state_hash}},
       states: {file_validity: "valid"|"invalid"|"none", news_state: hash, model_status: "floor"|"baseline"|"optimizer"|"repair"|"none", confirmed_upload: "committed"|"pending"|"none"},
       last_download: {path, hash, at}, run_lock: {holder, heartbeat})
```

- `dfs uploaded <file>` moves every pending lineup from that file to committed. A re-download reconciles: any entry whose downloaded lineup differs from `committed` is flagged and the downloaded lineup becomes `committed` (the platform is the truth).
- Rule: the exporter refuses to write an entry row that would revert a newer `pending` or `committed` change unless `--force` (recorded).

### 11.2 Validator

`validate(upload_rows, slate, lock_now: datetime, ledger) -> ValidationResult(ok, errors: list[(entry_id, rule, message)], warnings)`. Rules: cap, slot count and labels, eligibility from `Roster Position`, no repeated player, Classic two-game rule, Showdown both-teams rule, CPT row holds a CPT id and the same person not at UTIL, locked cells unchanged, no inserted player from a started game, file and slate integrity (same draft group, no WNBA contest names, every matchup on the schedule), bare integer ids, at most 500 rows, only changed rows.

### 11.3 Exporter

`export(night_portfolio or lineups, slate, ledger, reason) -> UploadFile(path, hash, valid_until, version, changed_rows)`. The only writer to `out/uploads/`; mirrors the download's encoding, BOM and line endings; re-reads and re-validates; writes the hash into the run manifest and the ledger as `pending`; moves older versions to `stale/`.

### 11.4 Re-solve

`resolve(night_inputs, news_state, ledger, scope: "pre_lock"|"post_lock", settings) -> list[UploadFile]`: re-simulate affected games on the selection and validation sets at `settings.resolve.S` (default 10,000); refresh public view and fields for slates containing them; rebuild candidates; `scope == "pre_lock"`: re-select affected contests; `scope == "post_lock"`: `swap` below; validate; export. Must finish inside `settings.resolve.budget_s` (default 180) or raise `ResolveTimeout`, on which the CLI runs `repair`.

### 11.5 Swap (post-lock)

`swap(slate, downloaded_entries, projections, pool, ledger, settings) -> list[UploadFile]`: pin `(LOCKED)` cells and started-game players; for each entry, re-optimize open slots with the candidate solver on current projections; rewrite only entries where `ledger.entries[e].news_state_hash != news_state.hash` or the open-slot improvement is at least `settings.swap.min_improvement_points` (default 3.0); re-check the concentration cap; produce a diff `[(entry_id, slot, old, new)]` in the brief.

### 11.6 Repair

`repair(slate, lineups, ruled_out: set[person_key], pool, projections.simple_points) -> lineups`: for each ruled-out player in an unlocked slot, insert the cheapest legal substitute by `simple_points` per dollar subject to the cap and eligibility; must run under 10 seconds for a 150-entry slate; result labeled `model_status = "repair"`.

### 11.7 Insufficient time

If any changed cell's game locks within `settings.resolve.min_minutes_to_lock` (default 8) at export time, the exporter drops those rows and the CLI prints "insufficient time to act for <entries>".

## 12. Run manifest and brief (C03, C04, C09)

```
RunManifest(run_id, mode, git_commit, config_hash, release_state, capabilities: {name: {enabled, rehearsed_on}}, seeds, inputs: [{path, hash}], snapshots: [...], news_state_hash, facts_applied, outputs: [{path, hash, valid_until}], fallback_level: int, timings: {step: seconds}, llm_usage: {...}|None)
Brief(run_id, slates: [{slate_key, states: Ledger.states, latest_file, floor_file, valid_until, capabilities_off: [..], contests: [{contest_id, name, facts_status, G1, G1_no_dup, p_top1_any, n_entries}],
      goal2: Goal2|None ("not estimated" in Floor), concentration, per_game_exposure, cap_relaxed_from, sanity, facts_applied: [..], facts_not_acting: [..], news_that_would_change: [..], skipped: [..], input_freshness: {...}, if_engine_down: {...}}])
```

Rendered to `runs/<run_id>/brief.md` (one page per slate) and printed by `dfs night` and `dfs status`.

## 13. CLI (C01 stubs; filled by later chunks)

| Command | Chunk | Effect |
|---|---|---|
| `dfs status` | C02 | Slates found, four states each, next action, injury-report diff since last run |
| `dfs night [--floor] [--no-llm] [--game-day]` | C04 (Floor), C09 (Baseline), C11 (flags) | Ingest, Floor export, then Baseline build if the release state allows |
| `dfs out/in/start/fact veto` | C06, C10 | Write facts; run the re-solve |
| `dfs news` | C10 | The re-solve on the current news state |
| `dfs swap` | C10 | Post-lock open-slot re-optimization |
| `dfs repair` | C03 | The legal repair of the latest file |
| `dfs uploaded <file>` | C03 | Commit pending lineups from that file |
| `dfs results` | C13 | Standings ingest, scorecards, flashback |
| `dfs research fetch <url>` | C11 | Allowlisted fetch that saves the page |
| `dfs unlock` | C11 | Lift the game-night code freeze (recorded) |
| `dfs replay <run_id>` | C19 | Re-execute from snapshots |
| `dfs history status` | C05 | Freshness of the history sources and the `nba_api` budget |
| `dfs digest` | C06 | Print tonight's news digest |
| `dfs sim --slate <key> --set <name>` | C07 | Write a scenario set and print per-player summaries |
| `dfs field --slate <key>` | C08 | Print ownership, common lineups, cutoffs |
| `dfs drill news --at <minutes>` | C10 | Replay a scripted scratch on a saved night and time the re-solve |
| `dfs rehearsed <capability> <date>` | C11 | Record a drill in `capabilities.toml` |
| `dfs insure [--run <run_id>]` | C12 | Re-run the insurance search on a saved run and print the trace |

Global options on every command: `--night <date>`, `--as-of <datetime>`, `--fixtures`, `--json`, `--yes` (section 1.1).

Exit codes: 0 ok; 2 validation failure (no file written); 3 input missing or unparseable (plain-language message names the file and the fix); 4 budget exceeded (repair ran if applicable).

## 14. Fixtures every chunk may rely on (created by C01 and C02)

- `fixtures/dk/2026-10-15/`: the owner's real Classic and Showdown entries files and salary exports from the Oct 15 preseason slates, plus the post-lock re-download with `(LOCKED)` cells (added after rehearsal 1).
- `fixtures/dk/public/`: public NBA salary files 2018 to 2026 and the April 2026 NBA Classic salary file (from `spikes/dk/out/downloads/github/`).
- `fixtures/injury/`: the two March 2026 injury-report PDFs (from `spikes/data/out/downloads/nba_injury_pdf/`).
- `fixtures/history/player_box_2026.parquet`: last season's box scores (from `spikes/data/out/downloads/sportsdataverse/`).
- `fixtures/synthetic/night8.json`: the R9 spike's synthetic 8-game night inputs, for the mechanics regression test (ADR-027).
- `fixtures/tiny/`: hand-countable contests for settlement tests: `tiny_10_entries_3_paid.json`, `tiny_tie_at_boundary.json`, `tiny_two_ours_adjacent.json`, `tiny_copy_at_first.json`, `tiny_infeasible_cap_showdown.json`, `tiny_same_team_two_out.json`.

## 15. Settings (`config/settings.toml`) referenced above, with defaults

```
[goal2] alpha = 0.25
[insurance] epsilon = 0.02, min_sd_scenarios = 50, enabled = false
[scenarios] screening = 5000, selection = 15000, validation = 15000, reporting = 30000
[settle] exact_max_field = 10000, rank_window_sd = 4, max_copies = 50
[select] showdown_keep = 5000, classic_pool = 8000, projection_floor_share = 0.85, cap_used_min = 0.95, p_active_min = 0.5
[concentration] cap = 0.60
[resolve] S = 10000, budget_s = 180, min_minutes_to_lock = 8
[swap] min_improvement_points = 3.0
[redistribution] shrink_minutes = 300, max_teammate_shift = 8
[llm] inference_blend_enabled = false, coverage_factor = 1.5, max_searches = 12, max_fetches = 8, game_day_max_searches = 6
[public_view] formula_weights = {salary_value = 0.4, team_share = 0.4, trailing_ppm = 0.2}
[field] ... per family: optimizer_share, casual_share, duplicator_share, stale_share, optimizer_noise, salary_floor
[facts] paid_share = {gpp = 0.23, double_up = 0.45}, rake = 0.15, first_place_cap_large = 0.20, first_place_cap_small = 0.15
```
