# Build progress

**Every build session reads this file first and updates it last.** The plan is `docs/build/BUILD_PLAN.md`; chunk files are in `docs/build/chunks/`; interfaces are in `docs/build/CONTRACTS.md`; the protocol is in `CLAUDE.md`.

**Changelog:** 2026-10-14 created. No chunk has started; the owner has not yet approved the build.

## Status board

| Chunk | Status | Started | Finished | Commit | Usage (5h share / weekly share) | Deviations |
|---|---|---|---|---|---|---|
| C01 Scaffold and contracts | not started | | | | | |
| C02 DraftKings ingest and slate state | not started | | | | | |
| C03 Validator, exporter, ledger, repair | not started | | | | | |
| C04 Contest facts, injury report, Floor, brief-lite | not started | | | | | |
| C05 Scoring adapter, history, priors | not started | | | | | |
| C06 Projections, facts translation, market anchor, news state | not started | | | | | |
| C07 Night simulator | not started | | | | | |
| C08 Field model and settlement | not started | | | | | |
| C09 Candidates, selection, Baseline night, full brief | not started | | | | | |
| C10 Live re-solve, late swap, news commands | not started | | | | | |
| C11 Claude layer, capability flags, launcher, readiness | not started | | | | | |
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

Status values: `not started`, `in progress (checkpoint N)`, `blocked: <reason>`, `done`.

## Milestones

| Milestone | Status | Evidence |
|---|---|---|
| M0 contracts | not reached | |
| M1 valid upload (Floor), rehearsal 1 Oct 15 | not reached | |
| M2 sensible portfolio, Drill A | not reached | |
| M3 opening-night ready, Drill B, Oct 19 live run | not reached | |
| Opening night Oct 20 | | |

## Release state and capability flags (mirror of `config/capabilities.toml`)

| Capability | Enabled | Rehearsed on |
|---|---|---|
| floor | | |
| baseline_model | | |
| resolve | | |
| swap_open_slots | | |
| researcher | | |
| insurance | | |
| qa_audit | | |
| watcher | | |

## Handoff notes (newest first)

_None yet. A session that stops at a checkpoint writes: chunk, checkpoint reached, what works, what is failing, the exact next step, and any contract change it made._

## Deviations from the plan (newest first)

_None yet. Record scope cuts, contract changes, reordered chunks, and the reason._

## Things found but out of scope (newest first)

_None yet. One line each with the chunk that should own it._

## Rehearsal and drill log

| Date | What | Result | Timings |
|---|---|---|---|
| | | | |
