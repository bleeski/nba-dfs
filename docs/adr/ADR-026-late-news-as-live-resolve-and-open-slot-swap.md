# ADR-026: Late news is a live re-solve on the joint news state; late swap re-optimizes every open slot; the legal repair is the rehearsed fallback

**Status:** Accepted. **Supersedes:** ADR-011 (stored replacements and `dfs apply`). **Source:** ADJUDICATION entries 10, 11, 17, 19, 33 (B-I-04, A-I-09, B-D-06, A-I-10, B-I-08, B-I-12, X-02), advisor consultation 1. **Changelog:** 2026-10-14 created.

## Context

v3 precomputed per-entry replacement tuples for each questionable player and combined them at news time with `dfs apply`, to get a seconds-long response. Critique B showed two tuples for the same Classic entry can collide (both touch the same third player, both insert the same pivot, together exceed the cap), and that two teammates out is not two one-out cases; Critique A made the same argument from the modeling side. The measured narrow re-run was 44 seconds at 10,000 scenarios in the spike (R9, VERIFIED), inside the brief's requirement to act on news 30 minutes before tip. v3 also restricted Phase 1 late swap to removing ruled-out players, which forbids moving into a scratch's beneficiary from entries that never held the scratched player. No permitted automated source gives confirmed starters before tip in any posture (ADJUDICATION V7).

## Options considered

1. **Stored replacements composed at news time** (v3). Fast; cannot compose; two code paths.
2. **Compose compatible plans, bounded rerun otherwise** (Critique A). Still two paths; "compatible" is hard to define.
3. **One live re-solve on the joint state, with a seconds-long legal repair as the fallback.**

## Decision

Option 3.

- **News state.** One file per night holds every confirmed status change with its time and source: `dfs out "<name>"`, `dfs in "<name>"`, `dfs start "<team>: A, B, C, D, E"` (confirmed starters you read in your own browser), and official injury-report changes. A later fact about a player supersedes an earlier one.
- **The re-solve** (`dfs news`, run by the commands above): re-simulate affected games (draws keyed by game keep common random numbers elsewhere); refresh the public view and fields for slates containing them; rebuild candidates; before the first lock re-select the affected contests on Goal 1; after it re-optimize open slots (below); validate; export a versioned file stamped "valid until" (the earliest lock among changed cells); update the ledger. Budget 3 minutes at 10,000 scenarios, measured on the Oct 16 twelve-game slate; the spike's 44 seconds is not evidence for the rewritten engine. If a 12-game slate exceeds the budget, the first optimization is cached field scores with sparse per-game deltas (B-D-06).
- **Legal repair** (`dfs repair`; automatic when the re-solve misses its budget or crashes, and the path the news commands take whenever the `resolve` capability is off, so the flag-off behavior is defined and rehearsed): remove each ruled-out player from unlocked slots and insert the cheapest legal substitute by projection; export in seconds, labeled "repair". If the Oct 16 drill shows detection-to-confirmed-upload exceeding the window at 30, 10 or 2 minutes before tip, the repair is the opening-night late-news path and the re-solve ships flagged off.
- **Late swap** (`/swap`, `dfs swap`): pin every `(LOCKED)` cell and every player whose game has started exactly as downloaded; subtract their salaries; re-optimize the open slots with the same candidate solver on current projections (locked games at their pre-lock distributions in the MVP; conditioning on finished games after). Scope rule: an entry is rewritten only when a news fact changed since that entry's last exported file, or when the open-slot improvement clears a threshold (setting, default 3 projected points); every other entry stays as uploaded; the concentration cap is re-checked on the post-swap portfolio; the brief shows the diff before upload. Never regenerate from the blank template; never move a locked player.
- **Ledger.** One JSON per slate: each entry's committed lineup, pending lineup, the file each came from, and the news state the file assumed. An upload is committed when you confirm the read-back (`dfs uploaded <file>`). A re-download is required before each Showdown's lock, before the main Classic slate's first lock, and before any `/swap`; optional otherwise. The engine refuses to write a row that would revert a newer change; one run at a time with a heartbeat lock.
- **Saved-night mode:** every command accepts `--night <date>` and `--as-of <datetime>`, which point the engine at a past night's files and freeze the clock, so drills on saved files obey the lock rules as they stood (built in chunk C03).
- **Four states per slate**, tracked and shown separately: file validity (validator result against the identified input snapshot and lock time), news state, model status (which capabilities ran), confirmed upload.
- **Acceptance tests:** two same-team absences; conflicting pivots; a status reversal; an unrostered scratch that changes our beneficiaries; a failed upload crossing a lock; a `dfs in` that removes lineups built for his absence; "insufficient time to act" when a changed cell's game locks within the set number of minutes (default 8).

## Consequences

- **Results:** every late-news file is built on the complete current state; late-game value plays reach every entry with an open slot; a wrong-file Showdown upload is caught before its lock.
- **Cost:** about a minute of compute per news event instead of seconds; a repair in seconds when it matters.
- **Workload:** the same commands as before, about 1 to 2 minutes longer per event; about four re-downloads a night timed to matter instead of one after every upload.
