# ADR-030: Operations v2: a walkable Floor-only route, time to lock as a label, isolated drills, recoverable exports, versioned rehearsals

**Status:** Accepted. **Date:** 2026-10-14. **Supersedes in part:** ADR-023 (the usage bullet's "C10 and C11 are built in Floor mode only"; `rehearsed_on` as a bare date), ADR-026 (the acceptance bullet's "insufficient time to act" as a drop rule, and the saved-night bullet's write behavior). **Source:** ADJUDICATION-R2 entries R2-1, R2-6, R2-7, R2-14, R2-15, R2-16, R2-17 (A-R2-I-01, A-R2-I-04, A-R2-I-09, A-R2-D-02, A-R2-D-03, A-R2-D-04, B-R2-I-03, B-R2-I-10); advisor consultation 3. **Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the "Versioned rehearsals" bullet adds how capabilities are switched on (`floor` starts enabled; `dfs enable` and `dfs disable`; drills run any capability regardless of its flag). 2026-10-14 created.

## Context

Round 2 found that the opening-night safety net had holes in its operation, not its intent:

- The usage branch said "C05 to C09 move after Oct 20 and C10 and C11 are built in Floor mode only", but C10 depended on C09 and C11 on C10, and the build protocol stops a session on unmet dependencies, so the fallback could not be walked. The launcher, hooks and flags arrived on Sunday, after both live rehearsals.
- The exporter dropped any changed row whose game locked within eight minutes, so the seconds-long repair (the fallback for news minutes before a tip) produced nothing at T-5. Dropping a row DraftKings would accept also broke the rule that only DraftKings validity blocks a file.
- Saved-night drills pointed at that night's real ledger and news state, so Drill B could overwrite the Oct 16 confirmation history.
- An interrupted export could leave a file with no ledger record; and a bare `rehearsed_on` date let a later code change ride on an old rehearsal.

## Options considered

1. **Mode-dependent chunks** (C10-F and C11-F resolved by mode in the tracker). Asks a fresh session to make the judgment the protocol exists to remove.
2. **Move the shell into C04.** Overloads the Thursday chunk on the rehearsal day.
3. **Split chunks so the Floor route is an ordinary dependency chain, and make the export, drill and rehearsal rules explicit.**

## Decision

Option 3.

- **Chunk split.** C04 becomes C04a (the M1 core) and C04b (injury report with the per-team merge, `dfs status --apply`, payout paste, entry history, facts cache). C11 becomes C11a (the operations shell: slash commands, hooks, preflight, capability flags, `dfs rehearsed`, `dfs unlock`, launcher, fallback card, `dfs start`, `dfs night --game-day`, the drill timer, the slot-reassignment repair, the export recovery tests), which depends on C04a only, and C11b (the news researcher), after opening night. C10 depends on C09 and C11a. The Floor-only branch is C01, C02, C03, C04a, C11a, C04b; PROGRESS has a `deferred (after opening night)` status, and a deferred dependency counts as not done.
- **Time to lock.** The exporter blocks only DraftKings-invalid rows: a changed cell that is locked (`(LOCKED)` in the download, its game started by the clock, or Game Info `In Progress` or `Final`) or whose lock time is unresolved. A row locking within `export.tight_minutes` (default 4, replaced by the measured upload time) is exported and labeled "tight", and the command names the lineup that stays if the upload misses. `resolve.min_minutes_to_lock` (8) only decides whether the full re-solve is attempted; inside it, the repair runs.
- **Drill mode.** `--as-of` reads archived inputs read-only and writes everything under `runs/drills/<drill_id>/`; replays write under `runs/replays/`. A test proves a drill leaves every live artifact byte-identical.
- **Recoverable exports.** Every upload, manifest and ledger is written to a temporary name, re-read and validated, and renamed into place, the ledger last; only ledger-named files are actionable; unfinished temporary files are swept on start-up.
- **Download freshness.** `dfs swap`, and `dfs repair` after a slate's first lock, refuse when the latest download predates the latest started tip (enforcing round 1 entry 19).
- **Two-stage repair.** Direct substitution (C03), then a small matching of players to unlocked slots inside one entry (C11a).
- **Versioned rehearsals.** Each capability records `rehearsed_commit`, `rehearsed_paths` and `drill_artifact`; status is `passed`, `stale` or `never`; a stale capability needs a replay drill or a recorded `dfs unlock` on a game night. The Floor is labeled, never switched off. **Enabling (R2-34):** `floor` starts enabled; every other capability starts off and is switched by `dfs enable <capability>` and `dfs disable <capability>` (C11a); `dfs enable` refuses a capability whose status is not `passed` unless `dfs unlock` is recorded. Drill mode runs any capability regardless of its flag, so Drill A can run the Baseline before it is enabled; live mode runs only enabled capabilities. The owner enables what passed on Sunday night, Oct 18.

## Consequences

- **Results:** a repair can still save an entry minutes before a lock; the Oct 16 evidence survives the weekend drills.
- **Cost:** two more build sessions (the split chunks), offset by C11b leaving the opening-night path.
- **Workload:** on Friday Oct 16 the owner rehearses the same launcher, hooks and commands used on opening night; a "tight" label instead of an empty file; a "download a fresh file first" message instead of a silent stale swap.
