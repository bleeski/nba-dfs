# C02: DraftKings ingest and slate state

**State:** Floor. **Size:** M (one session, about 1 to 2 hours). **Depends on:** C01. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Read the owner's real DraftKings NBA files correctly, identify slates, build the identity map, derive lock times, auto-file downloads, archive every raw file, and print `dfs status`. Everything downstream (validation, the Floor, the build) reads the `Slate` this chunk produces, so it comes right after the contracts. It needs the owner's first real 2026-27 NBA files (BUILD_PLAN "What you provide").

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1, 2.1, 2.2, 3.1, 11.1 (states only), 13, 14.
2. `docs/ARCHITECTURE.md` section 3, rows 1 to 3 of the components table, and section 10 "Storage, versioning and snapshots".
3. `docs/research/R6-draftkings-mechanics.md` sections 2.1 to 2.4 (file formats, `(LOCKED)` cells, encodings, Captain and UTIL pairing) and the eligibility table.
4. `docs/adr/ADR-004-draftkings-io-is-manual.md` and `docs/adr/ADR-018-reuse-from-prior-engines.md` (the name normalizer is ported here).
5. `spikes/dk/inspect_salary_csvs.py` and `spikes/dk/out/20261013-1631_salary_csv_inspect.txt` (what real files looked like).

## Scope

**Build:**

- `ingest/entries.py`: parse `DKEntries*.csv` for Classic and Showdown into `EntriesFile` (CONTRACTS 2.1): slot labels from the header; `<Name> (<id>)` and `(LOCKED)` cells; the player pool after the blank line; encodings (UTF-8 with and without BOM, cp1252); newline style recorded for the exporter.
- `ingest/salaries.py`: parse `DKSalaries*.csv` (CONTRACTS 2.2), optional `Status` and `Starting`; a test records whether the owner's 2026-27 NBA file has them and writes the answer into `fixtures/dk/2026-10-15/README.md`.
- `ingest/identity.py`: `person_key` from the ported name normalizer (accent folding, suffixes Jr., III) plus team; Captain and UTIL rows paired by name and team, never by ID arithmetic; a reviewed-matches file `config/identity_overrides.toml` for manual fixes, versioned per run.
- `ingest/slates.py`: `Slate` from an entries file: format from the header, games and lock times from `Game Info` (ET to local), `first_lock`, `last_lock`; `classic_main` alias; contest list with fee and name.
- `ingest/inbox.py`: `dfs status` scans the Downloads folder (path in settings) for files whose names and headers match DraftKings formats, files them into `inbox/<date>/` by content (draft group from the pool IDs) and download time, never by name; copies every raw file into `data/archive/<date>/` with a manifest line (path, hash, time); rejects a file for the wrong slate, yesterday's file, or a WNBA contest name with a plain-language message.
- `dfs status`: prints each slate found, its games and locks in Central time, entry counts by contest, and the four states (all "none" until C03).
- Fixtures: the owner's Oct 15 Classic and Showdown entries files and salary exports copied into `fixtures/dk/2026-10-15/` (the owner's own entries only; no other users' names appear in these files).

**Out of scope:** validation, export, the ledger's write side, contest facts, standings files.

## Contracts

- **Consumes:** CONTRACTS 2.1, 2.2 (file formats), 1 (naming), 15 (settings keys `inbox.downloads_dir`, `archive.enabled`).
- **Produces:** `EntriesFile`, `Slate`, `PoolPlayer` as populated objects; the archive manifest; `fixtures/dk/2026-10-15/`.

## Definition of done

- Parser tests on: the owner's Oct 15 Classic and Showdown files; the April 2026 NBA salary file; public salary files 2018 to 2026; each in the three encodings.
- `Slate` tests: lock times correct in Central for a 7:00 PM ET game; Showdown `first_lock == last_lock`; the two-role pairing finds every CPT and UTIL pair in the Showdown pool with zero unmatched.
- Auto-filing tests: `DKEntries (1).csv` is filed by content; a Classic file dropped with a Showdown name is identified by its header; a WNBA contest name is rejected with a message naming the file.
- Determinism: parsing the same file twice gives identical objects and hashes.
- `uv run pytest -m smoke` under 60 seconds.

## What I check

Download your Oct 15 entries files to Downloads, then run:

```bash
uv run dfs status
```

Expected: both slates listed (one Classic, one Showdown), each game with its tip time in Central, your entry counts per contest, and a line saying where each file was archived. No error.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: entries and salary parsers with tests on the public files (commit). Checkpoint 2: identity, slates, lock clock (commit). Checkpoint 3: inbox filing, archive, `dfs status` on the owner's real files (commit).

## Risks

- **The owner's real files are not in Downloads yet.** Build and test on the public files and the April 2026 file; leave checkpoint 3's real-file test as the first step of C03, and say so in PROGRESS.md.
- **The 2026-27 export adds columns.** Parse by header name, never by position; unknown columns are kept and logged.
- **Game Info format differs for Showdown or for games with a TBD time.** Fail closed with a message naming the row; a TBD tip time is a validation error later, not a parse error now.
