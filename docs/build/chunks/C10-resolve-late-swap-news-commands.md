# C10: Live re-solve, Baseline late swap, the re-solve path for the news commands, Drill B

**State:** Baseline (reaches milestone M3). **Size:** L (one session, about 2.5 to 3 hours, three checkpoints). **Depends on:** C09, C11a. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time). **Hard cut:** if this chunk is not done by Sunday Oct 18 evening (10:00 pm CT), it is marked `deferred (after opening night)` and the repair is the opening-night late-news path (ADJUDICATION-R2 R2-1).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): this chunk writes `tiny_same_team_two_out.json` (a re-solve acceptance case); it replaces C11a's Floor bodies of `dfs news` and `dfs swap`; in drill mode the re-solve and the open-slot swap run regardless of their flags; the Drill B command names the Oct 16 night; the post-lock fixture comes from `scripts/build_fixtures.py`. 2026-10-14 (ADJUDICATION-R2): depends on C11a, which now owns `dfs start`, the drill timer, the freshness helper and the repair's second stage (R2-1, R2-14, R2-15); `dfs status --apply` moved to C04b; the re-solve is attempted only when the earliest affected lock is at least 8 minutes away, and time to lock is a label, so the T-2 drill expects "re-solve skipped, repair ran, tight" instead of an empty file (R2-6); the Baseline readiness drills (launcher with Claude closed, fallback sequence and determinism on a Baseline file) moved here from v1's C11; usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Make late news one command and one path for the Baseline: `dfs out`, `dfs in` and `dfs start` run the re-solve on the complete current news state when there is time and the capability is on, the open-slot late swap works on a real post-lock file, the repair stands behind everything, and the acceptance scenarios from the adjudication pass. The re-solve budget is timed here (Drill B) and again live on Oct 19; if it misses, the repair is the opening-night path and the re-solve ships flagged off.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.4, 11 (all), 13.
2. `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` in full, then `docs/adr/ADR-030-operations-v2-floor-route-lock-labels-drills-exports.md` "Time to lock" and "Download freshness" bullets (which supersede parts of ADR-026).
3. `docs/ARCHITECTURE.md` section 6 "Late news and late swap: the joint re-solve" and "The ledger and the four states"; section 8 "The late-news path, end to end", "Questionable players before their status is known", "Staggered tips"; section 11 "Lineup validation and file tests" (the ledger, re-solve and repair bullet).
4. `docs/review/ADJUDICATION.md` entries 10, 17 and 19 only.
5. `fixtures/dk/2026-10-15/post_lock_entries.csv` and the note in `fixtures/dk/2026-10-15/README.md` about locked cells (the re-download from rehearsal 1, turned into the fixture by `scripts/build_fixtures.py`; the note from C11a).

## Scope

**Build:**

- `resolve/resolve.py`: `resolve(night_inputs, news_state, ledger, scope, settings)`: re-simulate affected games on the selection and validation sets at `resolve.S` (keyed draws leave other games untouched); refresh the public view and fields for slates containing them; rebuild candidates for those slates (Showdown re-enumerated; Classic adds solves around beneficiaries and drops lineups holding an out player); `scope == "pre_lock"`: re-select affected contests on Goal 1; `scope == "post_lock"`: the swap below; validate; export a versioned file stamped "valid until" with any tight rows; update the ledger; `ResolveTimeout` at `resolve.budget_s` falls through to the repair; timings recorded.
- The news commands (`dfs out`, `dfs in`, `dfs start`, and `dfs status --apply` from C04b) run the re-solve when the `resolve` capability is enabled and `passed` (in drill mode, regardless of the flag, CONTRACTS section 1) and the earliest affected lock is at least `resolve.min_minutes_to_lock` away; otherwise, or on a timeout, the legal repair on the latest committed lineups (CONTRACTS 4.4, 11.4).
- `resolve/swap.py`: `swap(slate, downloaded_entries, projections, pool, ledger, settings)`: pin locked cells (marker or clock, CONTRACTS 11.2) and started-game players; per entry, re-optimize open slots with the candidate solver on current projections (locked games at their pre-lock distributions); rewrite only entries whose `news_state_hash` changed or whose improvement clears `swap.min_improvement_points`; re-check the concentration cap on the post-swap portfolio; produce the diff; never regenerate from the blank template; never move a locked player. `dfs swap` reads the latest re-download and refuses a download older than the latest started tip (C11a's freshness helper). This replaces C11a's Floor body for `dfs swap` (the post-lock repair with the freshness check); `/swap` keeps wrapping it.
- `dfs news`: the re-solve on the current news state, replacing C11a's Floor body (the repair over the current news state); `/news` keeps wrapping it.
- `dfs drill news`: extend C11a's timer so it times the re-solve (drill mode runs it regardless of the `resolve` flag, CONTRACTS section 1).
- Acceptance scenario tests (CONTRACTS section 11 rules and ADR-026): two same-team absences modeled jointly (on `fixtures/tiny/tiny_same_team_two_out.json`, which this chunk writes in the format of CONTRACTS section 14: two players from one team ruled out together); conflicting pivots resolve to one legal lineup; a status reversal (`dfs in` after `dfs out`) removes lineups built for the absence and never restores a player ruled out by another fact; an unrostered scratch changes our beneficiaries' minutes and the portfolio; a failed upload crossing a lock leaves the ledger pending and `/status` names it; two outs in different games applied in either order never revert each other; a changed cell locking in 5 minutes skips the re-solve and runs the repair (not tight: 5 is outside the default 4-minute window); one locking in 3 minutes is also exported labeled tight; a changed cell in a started game is refused; the repair runs under 10 seconds.
- Baseline readiness drills, all in drill mode on the saved Oct 16 files and logged in PROGRESS.md's drill log: the launcher drill with Claude closed on a Baseline night (`dfs night`, `dfs out`, `dfs repair`); the opening-night fallback sequence on a Baseline file (`dfs out --no-run`, `dfs repair`, a simulated upload, `dfs uploaded`, `dfs status`); `dfs rehearsed resolve` and `dfs rehearsed swap_open_slots` for each drill that passes (C09 already recorded `baseline_model` after Drill A). In drill mode the re-solve and the open-slot swap run regardless of the `resolve` and `swap_open_slots` flags (CONTRACTS section 1), so Drill B runs before either is enabled; the owner enables each one that passed on Sunday night (`dfs enable resolve`, `dfs enable swap_open_slots`).

**Out of scope:** the news watcher (C17), live-score conditioning (C22), the field-score cache (C20), the researcher (C11b), `dfs start` and the repair stages (C04a, C11a).

## Contracts

- **Consumes:** `NightPortfolio`, `select_contest`, candidates (C09); `simulate_game` (C07); fields and settlement (C08); `NewsState`, the commands and the repair stage 1 (C04a, C03); `dfs status --apply` (C04b); `dfs start`, the freshness helper, repair stage 2, the drill timer, capability enforcement (C11a).
- **Produces:** `resolve`, `swap`, `dfs news` and `dfs swap` (replacing C11a's Floor bodies), `fixtures/tiny/tiny_same_team_two_out.json`, the re-solve path of the news commands, the Baseline readiness drills.

## Definition of done

- Every acceptance scenario test above passes.
- The re-solve on the saved Oct 16 12-game slate (one star ruled out in a game shared by the main Classic and a Showdown) finishes inside 180 seconds at 10,000 scenarios; the time is recorded. If it does not, PROGRESS.md records it and `config/capabilities.toml` keeps `resolve.enabled = false` with the reason.
- Swap test on `fixtures/dk/2026-10-15/post_lock_entries.csv`: locked cells byte-identical; only entries that need rewriting change; the diff lists every change; the exported file validates; a pre-lock download is refused with the freshness message.
- Determinism: the same news state twice gives byte-identical files.
- `dfs drill news --at 30`, `--at 10`, `--at 2` run in drill mode and print the window arithmetic; at 30 and 10 the re-solve runs; at 2 the output says the re-solve was skipped, the repair ran, and the affected rows are labeled tight with the lineup that stays if the upload misses.
- Flag-off test (live mode, since drill mode ignores the flag): with `resolve.enabled = false`, `dfs out` writes the fact and produces a repaired file in under 10 seconds, leaving every other row of the committed portfolio unchanged.
- The Baseline readiness drills pass and are logged.

## What I check (Drill B, on the saved Oct 16 files)

Run:

```bash
uv run dfs drill news --at 30 --night 2026-10-16
```

Expected: a line like "re-solve finished in 71 s; with a 4-minute upload you would have about 25 minutes to spare". Then `--at 10` and `--at 2`: the last should say "re-solve skipped (under 8 minutes); repair ran in 3 s; tight: <entries> lock at <time>; if the upload misses, the lineup already uploaded stays". Then, on the saved Oct 15 post-lock file:

```bash
uv run dfs swap --slate classic_main --night 2026-10-15 --as-of "2026-10-15T19:00-05:00" --fixtures
```

Expected: the first line says DRILL; a short diff of changed cells, every locked cell untouched, a new versioned upload-shaped file under `runs/drills/` that passes validation.

## Size estimate and checkpoints

About 2.5 to 3 hours. Checkpoint 1: the re-solve with the pre-lock scope and the command wiring, timing recorded (commit). Checkpoint 2: the swap with the scope rule, the freshness refusal and the diff (commit). Checkpoint 3: the acceptance scenarios, the drill timer extension, the Baseline readiness drills (commit).

## Usage budget

About 40% of a five-hour window and 8% of a weekly window (estimates). If the session passes 55% of a five-hour window, stop at the next checkpoint and hand off; mind the Sunday 10:00 pm CT hard cut.

## Risks

- **The re-solve misses 180 seconds on 12 games.** First reduce `resolve.S` to 7,500 and limit field refresh to the affected slates' contests; if still over, ship the re-solve flagged off and make the repair the opening-night path (ADJUDICATION entry 10); C20 is the structural fix.
- **The post-lock fixture shows an unexpected locked-cell format.** C11a recorded the real format; locks are taken from the marker or the clock, whichever marks more cells.
- **A swap diff is large on a 150-entry slate.** The scope rule limits it; if more than 30% of entries change, the brief flags it and asks the owner to confirm before upload.
- **The Sunday hard cut arrives.** Mark the chunk deferred in PROGRESS.md with handoff notes; opening night runs the Baseline build (if C09 passed) with the repair as the late-news path, or the Floor.
