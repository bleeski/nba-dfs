# ADR-011: Stored replacements and `dfs apply` for late news, a ledger with pending state, and late swap that edits DraftKings' current export in place

**Status:** Accepted (design), revised after red-team rounds 1 and 2. **Date:** 2026-10-13.

## Context

NBA statuses resolve close to tip, tips are staggered, and news that breaks 30 minutes before tip must be acted on. Free news reaches us about 1 to 20 minutes after it breaks (R4). Round 1 found that a rebuild-on-news path finished at about tip. Round 2 found that finished "if out" files written at build time do not combine (two outs in different games on one Classic slate: uploading the second file puts the first player back), go stale when the first game locks, ignore the more common outcome (the questionable player plays), and give the user no way to enter news without Claude. The user's prior engines lost entries to a late file refused after first tip, locked players moved when a swap file was regenerated from the blank template, and a stale lock list (RR1 to RR3). DraftKings disqualifies any swap involving a game that has started (R6).

## Options considered

1. **Re-run the night on every piece of news.** Too slow near lock.
2. **Finished if-out files written at build time.** Do not combine; go stale; ignore "he plays".
3. **Stored replacement sets plus a seconds-long composition step,** a ledger with committed and pending state, a narrow re-run only when nothing stored fits, and in-place late swap.

## Decision

Option 3.

- **Stored replacements** for each material questionable player (default setting, BET: in at least 5% of our entries, or his absence moves a beneficiary in at least 5% of our entries by 3 or more projected points), for both outcomes: full alternate Showdown portfolios ("sits" and "plays", about 1 to 2 seconds per contest by enumeration), and ranked replacement sets per affected Classic entry, limited to slots whose current and new players tip at or after his game. Computed after the main files are exported, in lock order, in a background queue.
- **`dfs apply`:** combines every confirmed status change, in any order, on top of committed and pending lineups in the ledger, and writes one versioned file per slate stamped "valid until" (the earliest lock among changed cells). Expired files are never named; older files move to `out/uploads/stale/`.
- **Two alert classes:** official (injury report, DraftKings `Status`) runs `dfs apply` through the run lock (queued and merged if a build is running) and names the file; possible (Bluesky reporter posts) shows the post and asks the user to confirm with `dfs out "<name>"` or `dfs in "<name>"`, which also work from the desktop launcher for news the user sees first. The user's own phone alerts are the primary fast channel.
- **Ledger:** committed lineups (confirmed by re-download) and pending lineups (named but not confirmed); never revert a newer change; one run at a time with a heartbeat lock that clears itself after about 2 minutes.
- **Narrow re-run** (`/news`, `dfs news`) only when nothing stored fits: re-simulate the affected game, refresh fields and candidates for slates containing it, re-select before the first lock or change only unlocked slots after it, export, then refresh stored replacements in the background. Measured 44 seconds at 10,000 scenarios (R9).
- **Late swap:** `/swap` pins every `(LOCKED)` cell exactly as downloaded, never regenerates from the blank template, never moves a locked player; Phase 1 swaps only ruled-out players. Lock times come from Game Info on every run.
- $0.25 tests on Oct 14 and 15 settle locked-cell behavior and post-lock fills (Decision D8).

## Consequences

- **Results:** late news reaches every affected entry in seconds, two pieces of news never undo each other, and a questionable player who plays does not leave entries built for his absence.
- **Cost:** stored replacements add about a minute per material player in the background (R9 timings).
- **Workload:** about 3 to 5 minutes per news event: `dfs out` if needed, upload, re-download, status.
