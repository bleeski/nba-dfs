# ADR-023: Three release states (Floor, Baseline, Optimizer) and a feature flag per capability

**Status:** Accepted; the usage bullet and the bare `rehearsed_on` date superseded in part by ADR-030. **Date:** 2026-10-14. **Source:** ADJUDICATION entries 3, 32, 36, 38 (A-I-03, B-I-03, X-01, X-05, X-07). **Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the live Oct 16 rehearsal is Floor-only (the news and post-lock repair drills); the Baseline model is ready Sunday Oct 18 (M2, Drill A) and the re-solve by Sunday 10:00 pm CT (M3, Drill B); the researcher is built in C11b after opening night and stays off until rehearsed. 2026-10-14 (ADJUDICATION-R2 entries R2-1 and R2-16): the Floor-only branch is now the dependency chain C01, C02, C03, C04a, C11a, C04b, with C05 to C10 and C11b deferred after opening night, and the trigger is measured at M1 (C01 to C04a) at about 35% of a weekly window; capabilities record the commit, paths and drill artifact that passed, and a capability changed since is `stale` (ADR-030). 2026-10-14 created.

## Context

The v3 plan let "Tier A" launch alone while the document described a product it did not deliver, and its Phase 1 schedule assumed building on Oct 14 with a live rehearsal that night. Today is Oct 14; the first build session starts after approval; the only live preseason nights left are Thursday Oct 15 (2 games) and Friday Oct 16 (12 games) (VERIFIED, ADJUDICATION V10). The owner is at the laptop both evenings and from 12:30 to 2:00 pm CT on Oct 20. The build runs as chunks in fresh Claude Code sessions, sharing the weekly usage window with opening night.

## Options considered

1. **One MVP definition with tiers inside it.** What v3 had; a slipped tier leaves nothing rehearsed and the brief over-promises.
2. **Two honest release states** (Critique A): a baseline that ships sensible entries and an optimizer that has earned probability-based selection.
3. **Three release states with a feature flag per capability and a rehearsal rule.** Adds a Floor beneath the Baseline so the Oct 15 night produces a rehearsed upload, and makes "rehearsed" a recorded fact.

## Decision

Option 3.

- **Floor:** parsers, validator, exporter, contest facts, injury-scrubbed lineups ranked on simple projections under the concentration cap, no simulation; brief-lite. Rehearsed with a real upload on Oct 15 and at scale with the news and post-lock repair drills on Oct 16.
- **Baseline:** adds the night simulation, a first field model, per-contest selection on Goal 1, the live late-news re-solve, the open-slot late swap, the manual news commands (`dfs out`, `dfs in`, `dfs start`), and the one-page brief. It cannot exist by Oct 16: the Baseline model is ready on Sunday Oct 18 (milestone M2, Drill A) and the re-solve by Sunday 10:00 pm CT (milestone M3, Drill B), both drilled on saved Oct 16 files against a written bar, and it runs live for the first time on Monday Oct 19 evening with the Floor already uploaded; the upload mechanics it shares with the Floor are live-rehearsed on Oct 15 and 16.
- **Optimizer:** adds the insurance control, QA, the learning loop, the news watcher, and the edge-uncertainty layer, after opening night.
- Every capability is a flag in `config/capabilities.toml` with `enabled`, `rehearsed_on`, `rehearsed_commit`, `rehearsed_paths` and `drill_artifact` (ADR-030); a capability whose paths changed since its drill is `stale` and counts as not rehearsed; a capability with no `rehearsed_on` date cannot be enabled on a game night without `dfs unlock`, which is recorded. The brief lists every capability that is off as "not yet available".
- The LLM news researcher is a flagged capability that is built in C11b after opening night and stays off until rehearsed; the manual commands are the rehearsed path.
- "Sensible" is a deterministic sanity check per slate: at least 95% of the cap used on average, no two identical lineups in one contest, the concentration cap honored or its relaxation reported, no lineup below the projection floor (default 85% of the slate's best single-lineup projection), and no player with `p_active` under 0.5 unless the owner asked for him. It labels; it never blocks.
- The Floor file is uploaded early on opening night and replaced only when an improved file passes checks.
- Every raw download and pre-lock snapshot is archived from Oct 15 onward, so week 1 is learnable before the results parser exists.
- Usage: each build session records its Claude usage in `docs/build/PROGRESS.md`; if C01 to C04a (milestone M1) use more than about 35% of a weekly window, the Floor is the opening-night release: C04b and C11a still run (they are on the Floor path), and C05 to C10 and C11b are marked `deferred (after opening night)` (superseded wording, v4: "the first four MVP chunks use more than about 40%... C10 and C11 are built in Floor mode only"; ADR-030).

## Consequences

- **Results:** opening night runs a rehearsed product; an unrehearsed feature cannot quietly degrade it.
- **Cost:** none.
- **Workload:** one extra upload early on opening night (about 2 minutes per slate); two rehearsal evenings with about $0.50 of test entries each.
