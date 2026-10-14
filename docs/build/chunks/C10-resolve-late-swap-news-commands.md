# C10: Live re-solve, late swap, news commands

**State:** Baseline. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C09. **Parallel with:** C11's Claude-layer half (skills, hooks, agents) but not its flags and launcher work.

## Goal, and why it sits here

Make late news one command and one path: `dfs out`, `dfs in` and `dfs start` run the re-solve on the complete current news state, the open-slot late swap works on a real post-lock file, "valid until" and "insufficient time" rules hold, the legal repair stands behind everything, and the acceptance scenarios from the adjudication pass. The re-solve budget is timed here (Drill B) and again live on Oct 19; if it misses, the repair is the opening-night path.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.4, 11 (all), 13.
2. `docs/ARCHITECTURE.md` section 6 "Late news and late swap: the joint re-solve" and "The ledger and the four states"; section 8 "The late-news path, end to end", "Questionable players before their status is known", "Staggered tips"; section 11 "Lineup validation and file tests" (the ledger, re-solve and repair bullet).
3. `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` in full.
4. `docs/review/ADJUDICATION.md` entries 10, 17 and 19 only.
5. `fixtures/dk/2026-10-15/post_lock_entries.csv` and the note in `fixtures/dk/2026-10-15/README.md` about locked cells (from rehearsal 1).

## Scope

**Build:**

- `resolve/resolve.py`: `resolve(night_inputs, news_state, ledger, scope, settings)`: re-simulate affected games on the selection and validation sets at `resolve.S` (keyed draws leave other games untouched); refresh the public view and fields for slates containing them; rebuild candidates for those slates (Showdown re-enumerated; Classic adds solves around beneficiaries and drops lineups holding an out player); `scope == "pre_lock"`: re-select affected contests on Goal 1; `scope == "post_lock"`: the swap below; validate; export a versioned file stamped "valid until"; update the ledger; `ResolveTimeout` at `resolve.budget_s` falls through to the repair; timings recorded.
- The news commands now trigger the re-solve instead of a Floor re-run (`--floor` keeps the Floor behavior as the fallback); an official injury-report diff found by `dfs status --apply` writes facts from the report and runs the re-solve through the run lock.
- `resolve/swap.py`: `swap(slate, downloaded_entries, projections, pool, ledger, settings)`: pin `(LOCKED)` cells and started-game players; per entry, re-optimize open slots with the candidate solver on current projections (locked games at their pre-lock distributions); rewrite only entries whose `news_state_hash` changed or whose improvement clears `swap.min_improvement_points`; re-check the concentration cap on the post-swap portfolio; produce the diff; never regenerate from the blank template; never move a locked player. `dfs swap` reads the latest re-download.
- Insufficient-time rule and the "valid until" stamp enforced in the exporter for re-solve and swap outputs (CONTRACTS 11.7).
- `dfs repair` wired as the automatic fallback of the re-solve and the swap.
- Acceptance scenario tests (CONTRACTS section 11 rules and ADR-026): two same-team absences modeled jointly; conflicting pivots resolve to one legal lineup; a status reversal (`dfs in` after `dfs out`) removes lineups built for the absence and never restores a player ruled out by another fact; an unrostered scratch changes our beneficiaries' minutes and the portfolio; a failed upload crossing a lock leaves the ledger pending and `/status` names it; two outs in different games applied in either order never revert each other; a changed cell locking in 5 minutes is dropped with the message; the repair runs under 10 seconds.
- Timing harness: `dfs drill news --at 30|10|2` replays a scripted scratch on the saved Oct 16 files, times the re-solve, and prints the owner's remaining window after a nominal 3-minute upload; results go to PROGRESS.md's drill log.

**Out of scope:** the news watcher (C17), live-score conditioning (C22), the field-score cache (C20), the researcher (C11).

## Contracts

- **Consumes:** `NightPortfolio`, `select_contest`, candidates (C09); `simulate_game` (C07); fields and settlement (C08); `NewsState` and the commands (C06); `validate`, `export`, `Ledger`, `repair` (C03).
- **Produces:** `resolve`, `swap`, the drill harness, `dfs news`, the upgraded `dfs out`, `dfs in`, `dfs start`, `dfs status --apply`.

## Definition of done

- Every acceptance scenario test above passes.
- The re-solve on the saved Oct 16 12-game slate (one star ruled out in a game shared by the main Classic and a Showdown) finishes inside 180 seconds at 10,000 scenarios; the time is recorded. If it does not, PROGRESS.md records it and `config/capabilities.toml` keeps `resolve.enabled = false` with the reason.
- Swap test on `fixtures/dk/2026-10-15/post_lock_entries.csv`: locked cells byte-identical; only entries that need rewriting change; the diff lists every change; the exported file validates.
- Determinism: the same news state twice gives byte-identical files.
- `dfs drill news --at 30`, `--at 10`, `--at 2` run and print the window arithmetic.

## What I check (Drill B, on the saved Oct 16 files)

Run:

```bash
uv run dfs drill news --at 30
```

Expected: a line like "re-solve finished in 71 s; with a 3-minute upload you would have about 25 minutes to spare". Then `--at 10` and `--at 2`: the last should say "insufficient time to act for <entries>" for cells in the game about to lock and name `dfs repair`. Then:

```bash
uv run dfs swap --slate classic_main
```

Expected (on the saved post-lock file): a short diff of changed cells, every locked cell untouched, a new versioned file that passes validation.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: the re-solve with the pre-lock scope, timing recorded (commit). Checkpoint 2: the swap with the scope rule and the diff (commit). Checkpoint 3: the acceptance scenarios, the drill harness, the repair fallback wiring (commit).

## Risks

- **The re-solve misses 180 seconds on 12 games.** First reduce `resolve.S` to 7,500 and limit field refresh to the affected slates' contests; if still over, ship the re-solve flagged off and make the repair the opening-night path (ADJUDICATION entry 10); C20 is the structural fix.
- **The post-lock fixture shows an unexpected locked-cell format.** Parse by the `(LOCKED)` suffix and by the game's tip time, whichever marks more cells; record the format in the fixture README.
- **A swap diff is large on a 150-entry slate.** The scope rule limits it; if more than 30% of entries change, the brief flags it and asks the owner to confirm before upload.
