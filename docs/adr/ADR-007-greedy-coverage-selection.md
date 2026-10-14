# ADR-007: Select portfolios by greedy scenario coverage, with a constrained insurance search across the night

**Status:** Accepted (design), revised after red-team rounds 1 and 2 and the R9 benchmark. **Date:** 2026-10-13.

## Context

The engine must choose 1 to 150 entries per contest across about 10 contests so that each contest's top-1% probability is high and the night's washout probability is low (ADR-001). The user's prior engines tuned exposure and overlap rules by hand and showed no edge (RR1, RR2). Generating lineups in sequence with "share at most K players" constraints is slow (R2: 30.8 seconds for 150 lineups with GLPK, up to 370 seconds with other solvers) and ignores the field and the night.

## Options considered

1. **Sequential optimizer with overlap caps** (Hunter, Vielma and Zaman style).
2. **Exposure targets set by hand or by the LLM.**
3. **Greedy coverage over a candidate pool scored on shared scenarios,** then a constrained swap search for the insurance budget.

## Decision

Option 3.

- **Four independent scenario sets** (ADR-001): candidates are shortlisted on screening (5,000), selected on selection (15,000), the insurance search runs on validation (15,000), and every reported number comes from reporting (30,000). On synthetic data greedy's in-sample probabilities ran 0.7 to 3 points high (R2).
- **Per contest, lazy greedy** on the top-1% objective (raw probability in Phase 1; duplicate-adjusted per format after calibration, ADR-009), storing per-scenario results as bits for big fields and 8-bit probabilities under about 1,000 entries. Each scenario's value is the best of our entries, so adding a lineup never lowers it and greedy keeps its guarantee of at least about 63% of the best set from the same pool (R2, VERIFIED theorems). On fresh synthetic scenarios greedy beat taking the top projections (47% against 35% with 20 entries, R2).
- **Insurance search:** single-lineup swaps that lower washout while every contest keeps `G1_c(new) >= (1 - epsilon) x G1*_c + 2 x SE_paired` on the validation set; frozen contests when the budget is within noise; roll-back on the reporting set; runs only with at least 50 washout scenarios on validation.
- **Local improvement:** deterministic single-player swaps kept only if they beat noise without breaking a guarantee.
- **Guardrails in code:** no repeated lineup within a contest; a 60% cap on any one player's share of the night's entries.

## Consequences

- **Results:** the two goals are optimized directly; diversity comes from covering different scenarios.
- **Cost:** on a synthetic 8-game, 118-entry night, greedy for every contest took 0.3 seconds and the search about 1 second; scoring candidates and computing field lines dominate the 211-second build (R9).
- **Workload:** no exposure settings to manage.
