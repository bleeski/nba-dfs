# ADR-002: One shared, stat-level simulation of the whole night

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

Goal 1 needs each contest's top-1% line and Goal 2 needs the joint chance that every contest misses its cash line on the same night. Classic and Showdown share games, and NBA correlation runs mostly through the game (pace, overtime, blowouts) rather than player pairs (R3, R5). The blueprint suggested a possession-level game simulation; the main open-source NBA simulator draws fantasy points from a multivariate normal (R3, VERIFIED in code).

## Options considered

1. **Separate simulation per contest.** Simple, but makes washout look rarer than it is because a bad game no longer hurts every contest at once.
2. **Fantasy points from a multivariate normal** with a correlation matrix. Cheap, but thins the upper tail tournaments are decided in, and cannot compute double-doubles (R3 spike: about 2.6 points lower at the 99th percentile in a toy, VERIFIED direction).
3. **Possession-level game simulation.** Potentially the most realistic; very many parameters to calibrate, each a place to drift.
4. **Stat-level counts with shared game, team and player factors**, one set of scenarios for the whole night.

## Decision

Option 4, with a **model-error layer** added after red-team round 1 (RT1 rank 1): each scenario also draws shifts in each team's and player's expected production (sized from our own past projection errors, wider in October and for rookies), a slate-wide scoring shift, and one ownership shock per slate shared by every contest on it. Without it, the simulation treats our projections as truth and reports washout as essentially zero at the user's volume. Per scenario, in addition: game pace, final margin around the spread, and overtime; team efficiency centered on the implied team total; availability draws for questionable players; minutes with blowout trims and early exits, reconciled to 240 per team; a per-player shared "big night" factor; negative binomial counts; rebounds and assists allocated from team totals; DraftKings scoring with exact bonuses. Captain points are 1.5x the same scenario's total. 10,000 scenarios to screen, 30,000 to finalize, with common random numbers. Every draw is keyed by stable identifiers (ADR-021).

## Consequences

- **Results:** correlation, blowout and overtime effects, Captain math and double-double odds come out of the same simulated games, and washout across Classic and Showdown is measured, not guessed.
- **Cost:** days of build time rather than weeks; every parameter checkable against free box scores. Runtime measured in R9.
- **Workload:** none.
- **Upgrade path:** possession-level detail can be added later for specific situations only if scorecards show the stat-level version is miscalibrated.
