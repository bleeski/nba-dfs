# C02: DraftKings ingest, identity and slate state

**State:** Floor. **Size:** M (one session, about 1.5 to 2 hours). **Depends on:** C01. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): files are filed by their slates' night (the date of the first lock), and a file whose slates have all started is archived under its own night and never used live; the one team map `ingest/teams.py` (ESPN codes, NBA full team names, The Odds API's names) is built here with its test; the R6 reading narrows to sections 2.1 to 2.3 and the `(LOCKED)` bullet of section 2.5. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the salary-file test reads `Status` and `Starting` (present since Oct 14) and records whether `Starting` is filled near tip. 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): the owner's real Oct 14 Classic and Showdown files exist now (local fixtures from `data/archive/2026-10-14/`), so the parser, encoding, `Status` and identity tests run on them from checkpoint 1; `identity.match_query` (whole-token matching, never edit distance) added. 2026-10-14 (ADJUDICATION-R2): two-table entries layout, optional draft group ID, slate fingerprint, post-lock Game Info (R2-8); team-free person key, matching rules, collision handling (R2-9); copy-on-ingest with retries (R2-14); usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Read the owner's real DraftKings NBA files correctly, identify slates by their pool fingerprint, build the identity map, derive lock times, copy downloads into the inbox, archive every raw file, and print `dfs status`. Everything downstream (validation, the Floor, the build) reads the `Slate` this chunk produces, so it comes right after the contracts. It needs the owner's first real 2026-27 NBA files (BUILD_PLAN "What you provide").

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md`: the preamble "Person key" (including "Matching what the owner types"), sections 1, 2.1, 2.2, 3.1, 11.1 (states only), 13, 14.
2. `docs/adr/ADR-031-person-and-slate-identity.md` in full.
3. `docs/ARCHITECTURE.md` section 3, rows 1 to 3 of the components table, and section 10 "Storage, versioning and snapshots".
4. `docs/research/R6-draftkings-mechanics.md` sections 2.1 to 2.3 and the `(LOCKED)` bullet of section 2.5 (file formats, the side-by-side tables, Game Info, encodings, Captain and UTIL pairing) and the eligibility table.
5. `docs/adr/ADR-004-draftkings-io-is-manual.md` and `docs/adr/ADR-018-reuse-from-prior-engines.md` (the name normalizer is ported here, with suffixes kept).
6. `spikes/dk/inspect_salary_csvs.py` and `spikes/dk/out/20261013-1631_salary_csv_inspect.txt` (what real files looked like).

## Scope

**Build:**

- `ingest/entries.py`: parse `DKEntries*.csv` for Classic and Showdown into `EntriesFile` (CONTRACTS 2.1): find the entry header (`Entry ID` in column A) and the pool header by name, read the two column regions independently, never assume a blank row, keep every entry even when it shares a row with pool data, accept ragged rows; slot labels from the header; `<Name> (<id>)` and `(LOCKED)` cells; encodings (UTF-8 with and without BOM, cp1252); newline style recorded for the exporter; `draft_group_id = None` (the file lacks it); `slate_fingerprint` from the sorted pool IDs.
- `ingest/salaries.py`: parse `DKSalaries*.csv` (CONTRACTS 2.2) with its `Status` and `Starting` columns; a test reads `Status` and `Starting` (VERIFIED present on Oct 14, ADJUDICATION-R2 V-R2-13) and records in the fixture README (`fixtures/dk/2026-10-15/README.md`) whether `Starting` is filled near tip.
- `ingest/identity.py`: the person key (CONTRACTS preamble): the ported normalizer with accents folded and suffixes kept as a final token, no team; `match(name, candidates)` with overrides first, exact match, then suffix-stripped only when unique, else unmatched; `Last, First` flipped before normalizing; within-pool collisions get a disambiguator and `identity_ambiguous = True` and never stop ingest; Captain and UTIL rows paired by name and team, never by ID arithmetic; `config/identity_overrides.toml` applied first and versioned per run; `match_query(query, pool)` for what the owner types: whole-token matching, one match asks one confirmation, several or none print numbered choices, edit distance never auto-resolves (CONTRACTS preamble).
- `ingest/slates.py`: `Slate` from an entries file (CONTRACTS 3.1): format from the header; games from `Game Info` (ET to local) with `lock_status`; `In Progress` or `Final` marks a game started and reuses the last verified tip time for that game from the archive (same fingerprint), else `unresolved`; `first_lock`, `last_lock`; the readable slate key and the `classic_main` alias; the contest list with fee and name.
- `ingest/teams.py` (CONTRACTS section 3.1, "Team codes"): the one team map. DraftKings codes are canonical; aliases cover ESPN codes (at least NY to NYK, SA to SAS, GS to GSW, NO to NOP, UTAH to UTA, WSH to WAS), NBA full team names as printed in the injury report (for example "Minnesota Timberwolves"), and The Odds API's team names. C04b, C05 and C06 consume it and build no map of their own.
- `ingest/inbox.py`: `dfs status` scans the Downloads folder (`inbox.downloads_dir`) for files whose names and headers match DraftKings formats; **copies** them (never moves or deletes anything in Downloads) into `inbox/<night>/` by content (slate fingerprint) and download time, never by name, retrying `inbox.copy_retries` times `inbox.retry_ms` apart when Windows holds the file, skipping partial downloads (`inbox.skip_suffixes`, `inbox.skip_prefixes`), and printing "close the file in Excel and run again" if it stays locked; copies every raw file into `data/archive/<night>/` with a manifest line (path, hash, time); files are filed by their slates' night (the date in Central time of the slates' first lock from Game Info, CONTRACTS 1.1), not by download date; archives a file whose slates have all started under its own night and never uses it live; rejects a file for the wrong slate or a WNBA contest name with a plain-language message.
- `dfs status`: prints each slate found, its games and locks in Central time, entry counts by contest, any identity warnings, and the four states (all "none" until C03).
- Fixtures (local only, built by `scripts/build_fixtures.py`; never committed): the owner's Oct 14 files (already in `data/archive/2026-10-14/`: Classic 7 games with 288 players and one entry, Showdown DEN@LAC with 82 rows and one entry, both salary files with `Status`) in `fixtures/dk/2026-10-14/`, and the owner's Oct 15 Classic and Showdown entries files and salary exports in `fixtures/dk/2026-10-15/` (the owner's own entries only; no other users' names appear in these files); `fixtures/dk/layout/` (a many-entry file built from a real one so entry rows overlap pool rows, and a post-lock re-download with `In Progress` Game Info, built from the real one if the owner's post-lock file does not exist yet); `fixtures/identity/names.json` (CONTRACTS section 14).

**Out of scope:** validation, export, the ledger's write side, contest facts, standings files, the history join (C04a uses `match`).

## Contracts

- **Consumes:** CONTRACTS 2.1, 2.2 (file formats), 1 (naming, fingerprint), the person-key preamble, 15 (`[inbox]`, `[archive]`).
- **Produces:** `EntriesFile`, `Slate`, `PoolPlayer` (with `identity_ambiguous`) as populated objects; `identity.match`; the team map `ingest/teams.py`; the archive manifest; `fixtures/dk/2026-10-15/`, `fixtures/dk/layout/`, `fixtures/identity/names.json`.

## Definition of done

- Parser tests on: the owner's Oct 14 files (Classic and Showdown entries files read as two regions with the pool header on row 8; 288 and 82 pool rows; IDs equal to the salary files; entries files UTF-8 without BOM and salary files UTF-8 with BOM, both CRLF; `Status` read with 54 `Q` and 8 `OUT` on the Classic file, recorded in the fixture README); the owner's Oct 15 Classic and Showdown files; the many-entry overlap fixture (every entry kept, pool complete); the post-lock fixture (`In Progress` read as started); the April 2026 NBA salary file; public salary files 2018 to 2026; each in the three encodings.
- `Slate` tests: lock times correct in Central for a 7:00 PM ET game; Showdown `first_lock == last_lock`; the two-role pairing finds every CPT and UTIL pair in the Showdown pool with zero unmatched; `draft_group_id` is `None`; the fingerprint is stable across two downloads of the same slate.
- Query tests: on the Oct 14 Classic pool, `match_query("Jokic")` returns only Nikola Jokic (never Nikola Jovic), `match_query("Jones")` returns seven numbered choices, and a misspelling returns numbered suggestions without auto-selecting.
- Identity tests on `fixtures/identity/names.json`: a traded player keeps one key across teams; `Hardaway Jr., Tim` matches `Tim Hardaway Jr.`; an accented name matches its plain spelling; two players who normalize alike get disambiguated keys, `identity_ambiguous = True`, and ingest completes; two similar names on one team are not merged.
- Team-map test: every ESPN code in `fixtures/history/player_box_2026.parquet`, every team name in the two March 2026 injury PDFs (`fixtures/injury/`), and the 30 NBA full team names map to a DraftKings code.
- Inbox tests: `DKEntries (1).csv` is filed by content; a Classic file dropped with a Showdown name is identified by its header; a WNBA contest name is rejected with a message naming the file; a `.crdownload` file is skipped; a Monday download of Tuesday's slates is filed under Tuesday's night; a file whose slates have all started is archived under its own night and not used live; a file held open (simulated with an exclusive handle) is retried and then reported in plain language; nothing in Downloads is moved or deleted.
- Determinism: parsing the same file twice gives identical objects and hashes.
- `uv run pytest -m smoke` under 60 seconds.

## What I check

Download your Oct 15 entries files to Downloads, then run:

```bash
uv run dfs status
```

Expected: both slates listed (one Classic, one Showdown), each game with its tip time in Central, your entry counts per contest, a line saying where each file was archived, and your files still in Downloads. No error.

## Size estimate and checkpoints

About 1.5 to 2 hours. Checkpoint 1: entries and salary parsers with the layout fixtures and the public files (commit). Checkpoint 2: identity, slates, lock clock, fingerprint (commit). Checkpoint 3: inbox copying, archive, `dfs status` on the owner's real files (commit).

## Usage budget

About 25% of a five-hour window and 4% of a weekly window (estimates until M1 is measured). If the session passes 40% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The owner's Oct 15 files are not in Downloads yet.** The Oct 14 real files already exist (local fixtures); build checkpoints 1 and 2 on them; leave checkpoint 3's Oct 15 test as the first step of C03, and say so in PROGRESS.md.
- **The 2026-27 export adds columns or moves the pool.** Headers are found by name and region; unknown columns are kept and logged.
- **Game Info differs for Showdown, a TBD time, or a postponement.** Kept raw; the game's lock is `unresolved`; the validator refuses edits touching it (C03), and the brief says why.
- **A name collision in tonight's pool.** Never fatal: disambiguated, flagged, and shown; the owner can add an override line.
