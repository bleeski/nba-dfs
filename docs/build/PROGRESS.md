# Build progress

**Every build session reads this file first and updates it last.** The plan is `docs/build/BUILD_PLAN.md`; chunk files are in `docs/build/chunks/`; interfaces are in `docs/build/CONTRACTS.md`; the protocol, including change control, is in `CLAUDE.md`; the owner's day-by-day list is `docs/build/OWNER_CHECKLIST.md`.

**Changelog:** 2026-10-14 (owner's request): the owner's build tracker page added; every session mirrors its status there (CLAUDE.md step 12). 2026-10-14 (ADJUDICATION-R2 entries R2-33 and R2-34): the owner's Oct 14 files recorded as captured; `floor` starts enabled. 2026-10-14 (design final, ADJUDICATION-R2): reset for the final design. C04 replaced by C04a and C04b, C11 by C11a and C11b (R2-1); status `deferred (after opening night)` added; milestone M1b added; capability table carries versioned rehearsals (R2-16); a change-request log added (change control in `CLAUDE.md`). 2026-10-14: created.

**Build tracker (the owner's progress page):** https://claude.ai/artifact/894yJvrf5PpRwaKXyxA4Tm. It explains each chunk in business terms and shows its status; every build session mirrors this file's status for its chunk there (CLAUDE.md step 12). This file stays the source of truth.

**Owner files already captured:** the owner's real Oct 14 Classic and Showdown entries and salary files (pre-lock) are archived in `data/archive/2026-10-14/` with a hash manifest (local only; never committed). C01's `scripts/build_fixtures.py` copies them into `fixtures/dk/2026-10-14/`.

**Next chunk: C01.** Type `/run-chunk C01` once the owner has approved the plan. No chunk has started.

## Status board

| Chunk | Status | Started | Finished | Commit | Usage (5h share / weekly share) | Deviations |
|---|---|---|---|---|---|---|
| C01 Scaffold and contracts | not started | | | | | |
| C02 DraftKings ingest, identity and slate state | not started | | | | | |
| C03 Validator, exporter, ledger, drill mode, legal repair | not started | | | | | |
| C04a The Floor core | not started | | | | | |
| C04b Injury report, `dfs status --apply`, payout facts | not started | | | | | |
| C05 Scoring adapter (versioned), history, priors | not started | | | | | |
| C06 Projections, fact translation, market anchor | not started | | | | | |
| C07 Night simulator | not started | | | | | |
| C08 Field model and settlement | not started | | | | | |
| C09 Candidates, selection, Baseline night, full brief | not started | | | | | |
| C10 Live re-solve, Baseline late swap, Drill B | not started | | | | | |
| C11a The operations shell | not started | | | | | |
| C11b The news researcher | not started | | | | | |
| C12 Insurance control | not started | | | | | |
| C13 Results ingest, scorecards, contest flashback | not started | | | | | |
| C14 Contest facts v2 and calibration gates | not started | | | | | |
| C15 Economic diagnostics, ramp-gate readout, hunch report | not started | | | | | |
| C16 Adversarial suite, field family, edge uncertainty, Showdown audit | not started | | | | | |
| C17 News watcher | not started | | | | | |
| C18 QA coherence audit | not started | | | | | |
| C19 Weekly analyst, adoption workflow, replay | not started | | | | | |
| C20 Incremental field-score cache (conditional) | not started | | | | | |
| C21 Props-implied minutes; value-of-information digest | not started | | | | | |
| C22 Late swap v2: live-score conditioning | not started | | | | | |

Status values: `not started`, `in progress (checkpoint N)`, `blocked: <reason>`, `deferred (after opening night)`, `done`. A `deferred` chunk counts as not done for dependency checks. The Floor-only branch (BUILD_PLAN "Build usage budget") marks C05 to C10 and C11b `deferred`; C11a and C04b still run.

**Usage at M1 (C01 to C04a together):** _not measured yet._ If more than about 35% of a weekly window, take the Floor-only branch.

## Milestones

| Milestone | Status | Evidence |
|---|---|---|
| M0 contracts (C01) | not reached | |
| M1 valid upload, rehearsal 1 Oct 15 (C02, C03, C04a) | not reached | |
| M1b Floor complete, rehearsal 2 Oct 16 (C11a, C04b) | not reached | |
| M2 sensible portfolio, Drill A (C05 to C09) | not reached | |
| M3 opening-night ready, Drill B, Oct 19 live run (C10) | not reached | |
| Opening night Oct 20 | | |

## Release state and capability flags (mirror of `config/capabilities.toml`)

| Capability | Enabled | Status (passed / stale / never) | Rehearsed on | Commit | Drill artifact |
|---|---|---|---|---|---|
| floor | yes (starts enabled) | never | | | |
| baseline_model | | never | | | |
| resolve | | never | | | |
| swap_open_slots | | never | | | |
| researcher | | never | | | |
| insurance | | never | | | |
| qa_audit | | never | | | |
| watcher | | never | | | |

## Change requests (newest first)

_None yet. A build session that finds a design problem writes: date, chunk, the problem, why it matters (results, opening night, cost or workload), the proposed change, whether it blocks the chunk, and then "awaiting owner". The owner's answer is recorded here before anything in the design changes._

## Handoff notes (newest first)

_None yet. A session that stops at a checkpoint writes: chunk, checkpoint reached, what works, what is failing, the exact next step, and any contract clarification it recorded._

## Deviations from the plan (newest first)

_None yet. Record scope cuts, approved contract changes, reordered or deferred chunks, and the reason._

## Things found but out of scope (newest first)

_None yet. One line each with the chunk that should own it._

## Rehearsal and drill log

| Date | What | Result | Timings |
|---|---|---|---|
| 2026-10-14 | Owner's pre-lock files captured (Classic 7 games, 288 players, 1 entry; Showdown DEN@LAC, 82 rows, 1 entry; both salary files with `Status`) | Archived; analyzed in ADJUDICATION-R2 V-R2-12 to V-R2-18 | |
