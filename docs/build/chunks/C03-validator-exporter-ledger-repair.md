# C03: Validator, exporter, ledger, drill mode, legal repair

**State:** Floor. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C02. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): "only changed rows" leaves the validator and becomes the exporter's default, with every row written when nothing changed or with `--all-rows`; the exporter writes the `<slate_key>_latest.csv` copy; live paths use the night of the slates' first lock; the post-lock fixture comes from `scripts/build_fixtures.py`; the reading list adds R6's validator checklist; the owner's check names the Showdown alternative. 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): the round trip and the clock-locked tests run on the owner's real Oct 14 files, including tonight's post-lock re-download if he captured it. 2026-10-14 (ADJUDICATION-R2): drill mode isolates every write (R2-7); a cell is locked by marker or clock, an unresolved lock refuses the edit, and time to lock is a label instead of a drop (R2-6); export write order with temporary files and the ledger last (R2-17, basic version; the interrupted-write tests and start-up sweep are in C11a); slate fingerprint check (R2-8); the slot-reassignment repair moved to C11a (R2-15); usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Make it impossible for an invalid file to reach the owner, and make every exported file traceable: one validator that re-derives every DraftKings rule from the downloaded file, one exporter that is the only writer to `out/uploads/`, a per-slate ledger with four separately tracked states, `dfs uploaded`, the run lock, the manifest, drill mode, and the seconds-long legal repair. It sits before the Floor because the Floor's only promise is a valid, confirmed upload.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1 (including 1.1), 2.1, 11.1, 11.2, 11.3, 11.6, 11.7, 12 (`RunManifest` only), 13.
2. `docs/adr/ADR-030-operations-v2-floor-route-lock-labels-drills-exports.md` in full.
3. `docs/ARCHITECTURE.md` section 6 "The ledger and the four states", section 8 "Fallback ladder", section 11 "Lineup validation and file tests".
4. `docs/adr/ADR-010-validator-is-the-only-writer.md` (with its 2026-10-14 revision note) and `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the ledger, re-download policy and repair paragraphs only).
5. `docs/research/R6-draftkings-mechanics.md` section 2 (upload hygiene: bare integer IDs, only changed rows, encodings, the 500-row limit) and section 2.5 (late swap; the disqualification rule itself is in the two reference files below), and its "Validator checklist" near the end.
6. `docs/reference/NBA Classic.txt` and `docs/reference/NBA Showdown Captain Mode.txt` (the rules, about 1,500 words together).

## Scope

**Build:**

- `validate/rules.py`: `validate(upload_rows, slate, lock_now, ledger) -> ValidationResult` with one function per rule from CONTRACTS 11.2: cap $50,000; slot count and labels from the header; eligibility from `Roster Position`; no repeated person (Captain and UTIL of one person count); Classic two-game minimum; Showdown both-teams rule; CPT slot holds a CPT-role id; **locked cells unchanged**, where a cell is locked if it shows `(LOCKED)`, or its game's tip is at or before `lock_now`, or its Game Info reads `In Progress` or `Final`; no inserted player from a locked game; **lock unresolved** (no change touching a game whose lock time is unknown); file and slate integrity (same `slate_fingerprint`, no WNBA names, every matchup among the slate's games); bare integer ids; at most 500 rows. These are the only blocking rules (which rows a file carries is the exporter's choice, below, not a validity rule).
- `export/writer.py`: `export(lineups, slate, ledger, reason) -> UploadFile`: writes the CSV to `out/uploads/.tmp/<generation_id>/` mirroring the download's encoding, BOM and newline; writes only changed rows by default (DraftKings' instruction 5 says that is faster, R6), and every row when no row changed (a round trip of the lineups already held) or with `--all-rows`; re-reads and re-validates it; renames it into `out/uploads/<slate_key>_<lock>_v<n>.csv` and copies the latest valid file to `out/uploads/<slate_key>_latest.csv` (CONTRACTS section 1); writes the manifest and then the ledger by the same temporary-file-then-rename pattern, the ledger last (CONTRACTS 11.3); stamps `valid_until`; lists `tight_rows` (changed rows locking within `export.tight_minutes`) and prints the "tight" message with the incumbent file (CONTRACTS 11.7); moves older versions to `out/uploads/stale/`; refuses to write when validation fails (exit 2) and names the failing rule and entry in plain language. It never drops a valid row for being close to its lock.
- `export/ledger.py`: the `Ledger` per slate (CONTRACTS 11.1): committed and pending lineups per entry, file hashes, the news-state hash, the four states, `last_download`; `dfs uploaded <file>` commits; `reconcile(downloaded_entries)` after a re-download (the platform is the truth; differences are flagged); refusal to revert a newer change without `--force` (recorded).
- `export/runlock.py`: one engine run at a time with a heartbeat file that clears itself after about 2 minutes.
- `clock.py` and modes (CONTRACTS 1.1): `Clock.now()` returns `--as-of` when given, else the wall clock; `Paths` resolves live mode to `inbox/<night>/`, `runs/<night>/` and `out/uploads/`, where the night is the date in Central time of the slates' first lock read from Game Info, never the wall-clock date (so Monday's run for Tuesday's slates stores everything under Tuesday), and **drill mode** (`--as-of` given) to read-only inputs from `data/archive/<night>/` (or `fixtures/dk/<night>/` with `--fixtures`) and every write under `runs/drills/<drill_id>/`, including upload-shaped files and simulated confirmations; every lock rule reads the clock; a static test proves no module under `src/nbadfs/` calls the wall clock directly; a static test proves only `export/writer.py` writes under `out/uploads/`.
- `export/manifest.py`: `RunManifest` written for every run, with input and output hashes and `drill_id`.
- `validate/repair.py`: `repair(slate, lineups, ruled_out, pool, simple_points, lock_now)`, stage 1 (CONTRACTS 11.6): remove each ruled-out player from unlocked slots and insert the best legal substitute by `simple_points` per dollar directly into the vacated slot, under the cap; `dfs repair` runs it on the latest file and exports with `model_status = "repair"`; must finish under 10 seconds for 150 entries.
- `dfs status` now shows the four states per slate from the ledger, and only ledger-named files as actionable.

**Out of scope:** contest facts, projections (the repair uses whatever `simple_points` the Floor provides; until C04a it uses salary as the proxy), the re-solve, late swap, the slot-reassignment repair stage and the interrupted-write tests (C11a), the swap freshness rule (C11a, C10).

## Contracts

- **Consumes:** `Slate`, `EntriesFile`, `PoolPlayer` (C02); settings `[export]`, `[repair]`, `resolve.min_minutes_to_lock`.
- **Produces:** `ValidationResult`, `UploadFile` (with `tight_rows`), `Ledger`, `RunManifest`, `Clock`, `Paths` with drill mode, the `repair` function (stage 1), the `out/uploads/` layout. (The post-lock fixture `fixtures/dk/2026-10-15/post_lock_entries.csv` is not saved by hand: `scripts/build_fixtures.py` builds it from the owner's post-lock re-download once `dfs status` has archived it under `data/archive/2026-10-15/`.)

## Definition of done

- One passing and one failing fixture for every validator rule listed in CONTRACTS 11.2 (counting a clock-locked cell with no marker, and an unresolved lock, as cases of their own), each a real-format file.
- Round trip: export, re-read, re-validate; unchanged cells byte-identical to the download, including BOM and line endings, for all three encodings and for the owner's real Oct 14 entries files (UTF-8 without BOM, CRLF).
- Rows-written tests: a repair with no change writes every row and the file validates; a file with one changed entry writes only that row; `--all-rows` writes every row; the latest valid file is also copied as `<slate_key>_latest.csv`.
- Ledger tests: `dfs uploaded` commits exactly the pending lineups of that file; a reconcile after a re-download flags a changed entry and adopts the platform's lineup; a write that would revert a newer change is refused; the run lock blocks a second run and clears after a simulated crash.
- Write-order test: the CSV appears under its final name only after it re-validates, and the ledger is written after the CSV and the manifest.
- Repair test: a 150-entry slate with two ruled-out players repaired in under 10 seconds with every lineup valid.
- Time-to-lock tests (replacing v1's five-minute drop test): (a) a changed cell whose game locks in 3 minutes (inside the default 4-minute window) is **exported** and listed in `tight_rows` with the message naming the incumbent file; (b) a changed cell whose game started 1 minute ago by the clock, with no `(LOCKED)` marker in the download, is refused (exit 2) and named; (c) a changed cell in a game whose lock is unresolved is refused.
- Drill-mode tests: `--night 2026-10-15 --as-of "2026-10-15T17:00-05:00" --fixtures` validates the pre-lock file with no started games, and `--as-of "2026-10-15T19:00-05:00"` treats the 6:30 pm game as started; a completed drill, including a simulated `dfs uploaded` and a failed export, leaves every file under `out/uploads/`, `runs/2026-10-15/` and `inbox/` byte-identical (hash before and after); the static wall-clock and single-writer tests pass.
- Property test: 2,000 random lineups per pool; every invalid one rejected, every valid one accepted.

## What I check

Your Oct 15 entries file holds the lineups you built by hand in the DraftKings browser page (a blank cell means a reserved entry with no lineup, which the repair cannot fill). Run (with the Showdown slate key in place of `classic_main` if Thursday had no Classic slate):

```bash
uv run dfs repair --slate classic_main
```

Expected: a file named like `out/uploads/classic_main_1830_v1.csv` containing your own lineups with bare numeric IDs (unchanged, and every row written, because nobody is ruled out), a line saying it passed validation, and `dfs status` showing that slate's file validity as "valid" and confirmed upload as "pending". This round trip of your own lineups is the minimum rehearsal even if the Floor slips. Then upload that file to DraftKings in your browser (it is your own test entry) and run:

```bash
uv run dfs uploaded out/uploads/classic_main_1830_v1.csv
```

Expected: `dfs status` shows confirmed upload "committed".

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: the validator with all rule fixtures, including the clock-locked and unresolved cases (commit). Checkpoint 2: clock, drill mode, exporter with the write order, ledger, run lock, manifest, `dfs uploaded` (commit). Checkpoint 3: repair stage 1, the time-to-lock label, the drill isolation test, the static writer and wall-clock checks, `dfs status` states (commit).

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates until M1 is measured). If the session passes 50% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The post-lock `(LOCKED)` fixture does not exist yet** (it needs the owner's re-download after 6:30 pm CT on Oct 15, or tonight's optional capture). Use tonight's Oct 14 post-lock re-download if the owner captured it (`fixtures/dk/2026-10-14/`); otherwise write the locked-cell tests against the MLB 2026 locked file's format from R6 and the clock rule, and mark them to be re-run on the NBA fixture in C11a.
- **Encoding drift.** Mirror the download exactly; never normalize; a test compares bytes.
- **Rule disagreement with DraftKings on upload.** The owner's read-back is the final check; any rejection is logged with the file hash and becomes a fixture.
- **The rename is not atomic across volumes.** `out/uploads/.tmp/` sits inside `out/uploads/`, on the same volume by construction.
