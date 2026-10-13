# ADR-011: Ready-made "if out" files, a narrow re-run, a per-entry ledger, and late swap that edits DraftKings' current export in place

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

## Context

NBA statuses resolve close to tip, tips are staggered, and news that breaks 30 minutes before tip must be acted on. Free news reaches us about 1 to 20 minutes after it breaks (R4). The red team walked the first version minute by minute and found that a ruling at T-25 finished at about T-0, that single-slot contingency swaps are wrong for Showdown, and that two news events could undo each other (RT1 ranks 2, 9, 13). The user's prior engines lost entries to a late file refused after first tip, locked players moved when a swap file was regenerated from the blank template, and a stale lock list (RR1 to RR3). What DraftKings does with uploaded `(LOCKED)` cells and post-lock fills is undocumented (R6).

## Options considered

1. **Re-run the night on every piece of news.** Too slow near lock.
2. **Single-slot contingency swaps** applied by a re-run. Still needs a run and re-exports; wrong for Showdown.
3. **Ready-made, validated "if out" upload files built with the main build,** a narrow re-run only when no file fits, a ledger, and in-place late swap.

## Decision

Option 3.

- Questionable players stay random in the simulation.
- For each with a probability of playing between 10% and 90%, and each slate he is on, a complete validated if-out file: a full alternate portfolio for Showdown (from enumeration), a 2- to 3-slot re-optimization per affected Classic entry using only players in games that have not started. Files are rebuilt whenever a newer upload file is exported.
- The news watcher (plain Python) polls the official injury report every 15 minutes and Bluesky reporter mirrors every 60 seconds and names the file to upload.
- The narrow re-run (when no file fits) re-simulates only the affected game, refreshes the field and candidates only for slates containing it, re-selects affected contests before the first lock or changes only unlocked slots after it, and rebuilds the remaining if-out files. In Phase 1, after the first lock it only swaps out ruled-out players.
- A per-entry ledger and a one-run-at-a-time lock stop a stale file from reverting a newer one; simultaneous events merge.
- After each lock, `/swap` pins every `(LOCKED)` cell exactly as downloaded, never regenerates from the blank template, and never moves a locked player.
- Lock times come from each file's Game Info on every run.
- $0.25 tests on Oct 14 and 15 settle locked-cell behavior and post-lock fills (Decision D8).

## Consequences

- **Results:** acting on late news takes one upload; late scratches become pivots instead of zeros; Showdown alternates reflect how a star's absence changes the whole game.
- **Cost:** if-out files add a few selection runs per build (measured in R9).
- **Workload:** about 5 minutes per news alert (upload, re-download, status), instead of a re-export and rebuild.
