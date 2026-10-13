# ADR-011: Questionable players stay random, contingency swaps are precomputed, and late swap edits DraftKings' current export in place

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

NBA statuses resolve close to tip, tips are staggered, and news that breaks 30 minutes before tip must be acted on (brief). Your prior engines lost entries at lock: a late file refused after first tip (NHL), locked players moved in 107 cells when a swap file was regenerated from the blank template (NFL), a stale lock list that got 7 of 16 rows rejected (MLB) (RR1 to RR3, VERIFIED). What DraftKings does with uploaded `(LOCKED)` cells and post-lock fills is undocumented (R6).

## Options considered

1. **Re-run the whole night on every piece of news.** Simple, slow near lock.
2. **Separate "in" and "out" lineup sets for every questionable player.** Doubles the work and ignores probabilities.
3. **Questionable players random in the simulation; precomputed contingency swaps; a narrow re-run of the affected game; lock-wave swap mode that edits the current export in place.**

## Decision

Option 3.

- Each scenario draws whether a questionable player plays, with the probability from the official status and any evidence-backed override.
- For every entry holding a questionable player, the best legal same-slot replacement under the "out" outcome is stored; `/news` applies it in seconds with no LLM.
- `/news` then re-runs only the affected game and slates and writes a versioned file; the LLM interprets ambiguous news only if time and budget allow.
- After each lock, `/swap` reads the user's freshly downloaded entries file, pins every `(LOCKED)` cell exactly as downloaded, treats started and finished games as known, and changes only open cells. It never regenerates from the blank template and never moves a locked player.
- Slot assignment puts later-game players in UTIL, G and F where eligibility allows.
- Lock times come from each file's Game Info on every run, with a 10-minute warning per changed cell.
- Before Oct 20, $0.25 tests settle the `(LOCKED)` cell behavior and whether entries in later games can be filled after the first lock (Decision D8).

## Consequences

- **Results:** late scratches become low-owned pivots instead of zeros; Showdown files are final before their single tip.
- **Cost:** contingency swaps take seconds; the narrow re-run's budget is measured in R9.
- **Workload:** about 5 minutes per lock wave with news: re-export, run, upload, re-download, check.
