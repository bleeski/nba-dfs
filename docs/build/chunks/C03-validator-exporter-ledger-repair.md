# C03: Validator, exporter, ledger, legal repair

**State:** Floor. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C02. **Parallel with:** C05.

## Goal, and why it sits here

Make it impossible for an invalid file to reach the owner, and make every exported file traceable: one validator that re-derives every DraftKings rule from the downloaded file, one exporter that is the only writer to `out/uploads/`, a per-slate ledger with four separately tracked states, `dfs uploaded`, the run lock, the manifest, and the seconds-long legal repair. It sits before the Floor because the Floor's only promise is a valid, confirmed upload.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1, 2.1, 11.1, 11.2, 11.3, 11.6, 11.7, 12 (RunManifest only), 13.
2. `docs/ARCHITECTURE.md` section 6 "The ledger and the four states", section 8 "Fallback ladder", section 11 "Lineup validation and file tests".
3. `docs/adr/ADR-010-validator-is-the-only-writer.md` (with its 2026-10-14 revision note) and `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the ledger, re-download policy and repair paragraphs only).
4. `docs/research/R6-draftkings-mechanics.md` section 2 (upload hygiene: bare integer IDs, only changed rows, encodings, the 500-row limit) and section 3.2 (late-swap disqualification rule).
5. `docs/reference/NBA Classic.txt` and `docs/reference/NBA Showdown Captain Mode.txt` (the rules, about 1,500 words together).

## Scope

**Build:**

- `validate/rules.py`: `validate(upload_rows, slate, lock_now, ledger) -> ValidationResult` with one function per rule from CONTRACTS 11.2: cap $50,000; slot count and labels from the header; eligibility from `Roster Position`; no repeated person in a lineup (Captain and UTIL of the same person counts as a repeat); Classic two-game minimum; Showdown both-teams rule; CPT slot holds a CPT-role id; locked cells unchanged from the download; no inserted player whose game started before `lock_now`; file and slate integrity (same draft group, no WNBA names, every matchup on the slate); bare integer ids; at most 500 rows; only changed rows when `changed_only` is set.
- `export/writer.py`: `export(lineups, slate, ledger, reason) -> UploadFile`: writes `out/uploads/<slate_key>_<lock>_v<n>.csv` mirroring the download's encoding, BOM and newline; re-reads and re-validates the written file; computes its hash; records it in the manifest and the ledger as pending with `valid_until`; moves older versions to `out/uploads/stale/`; refuses to write when validation fails (exit 2) and names the failing rule and entry in plain language.
- `export/ledger.py`: the `Ledger` per slate (CONTRACTS 11.1): committed and pending lineups per entry, file hashes, the news-state hash, the four states; `dfs uploaded <file>` commits; `reconcile(downloaded_entries)` after a re-download (the platform is the truth; differences are flagged); refusal to revert a newer change without `--force` (recorded).
- `export/runlock.py`: one engine run at a time with a heartbeat file that clears itself after about 2 minutes.
- `export/manifest.py`: `RunManifest` written for every run, with input and output hashes.
- `validate/repair.py`: `repair(slate, lineups, ruled_out, pool, simple_points)`: remove each ruled-out player from unlocked slots and insert the cheapest legal substitute by `simple_points` per dollar under the cap; `dfs repair` runs it on the latest file and exports with `model_status = "repair"`; must finish under 10 seconds for 150 entries.
- `dfs status` now shows the four states per slate from the ledger.

**Out of scope:** contest facts, projections (the repair uses whatever `simple_points` the Floor provides; until C04 it uses salary as the proxy), the re-solve, late swap.

## Contracts

- **Consumes:** `Slate`, `EntriesFile`, `PoolPlayer` (C02); settings `resolve.min_minutes_to_lock`.
- **Produces:** `ValidationResult`, `UploadFile`, `Ledger`, `RunManifest`, the `repair` function, the `out/uploads/` layout; `fixtures/dk/2026-10-15/post_lock_entries.csv` once the owner re-downloads after the first lock on Oct 15 (added by whoever runs next).

## Definition of done

- One passing and one failing fixture per validator rule (14 rules), each a real-format file.
- Round trip: export, re-read, re-validate; unchanged cells byte-identical to the download, including BOM and line endings, for all three encodings.
- Ledger tests: `dfs uploaded` commits exactly the pending lineups of that file; a reconcile after a re-download flags a changed entry and adopts the platform's lineup; a write that would revert a newer change is refused; the run lock blocks a second run and clears after a simulated crash.
- Repair test: a 150-entry slate with two ruled-out players repaired in under 10 seconds with every lineup valid.
- Insufficient-time test: a changed cell whose game locks in 5 minutes is dropped with the message.
- Property test: 2,000 random lineups per pool; every invalid one rejected, every valid one accepted.
- A test that nothing but `export/writer.py` writes under `out/uploads/` (a static check over `src/`).

## What I check

Run, on your Oct 15 Classic entries file:

```bash
uv run dfs repair --slate classic_main
```

Expected: a file named like `out/uploads/classic_main_1830_v1.csv`, a line saying it passed validation, and `dfs status` showing that slate's file validity as "valid" and confirmed upload as "pending". Then upload that file to DraftKings in your browser (it is your own test entry) and run:

```bash
uv run dfs uploaded out/uploads/classic_main_1830_v1.csv
```

Expected: `dfs status` shows confirmed upload "committed".

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: the validator with all rule fixtures (commit). Checkpoint 2: exporter, ledger, run lock, manifest, `dfs uploaded` (commit). Checkpoint 3: repair, insufficient-time rule, the static writer check, `dfs status` states (commit).

## Risks

- **The post-lock `(LOCKED)` fixture does not exist yet** (it needs the owner's re-download after 6:30 pm CT on Oct 15). Write the locked-cell tests against the MLB 2026 locked file's format from R6 and mark them to be re-run on the NBA fixture in C10.
- **Encoding drift.** Mirror the download exactly; never normalize; a test compares bytes.
- **Rule disagreement with DraftKings on upload.** The owner's read-back is the final check; any rejection is logged with the file hash and becomes a fixture.
