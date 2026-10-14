# ADR-007: Select portfolios by greedy scenario coverage, with a constrained insurance search across the night

**Status:** Accepted (design), revised after red-team rounds 1 and 2 and the R9 benchmark. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entries 5 and 7): the per-contest objective is Goal 1 as defined in ADR-024 (top-1% prize equity, with duplication and ties inside it), not raw top-1% probability; greedy still applies because the objective keeps diminishing returns, and the result is reported as "best found". The concentration cap is a per-format, feasibility-tested soft preference: the selector computes the minimum feasible cap for tonight's pools and entry counts, applies the stricter of that and the setting, and reports when it relaxed; it never blocks delivery. The 63% guarantee is stated for the per-contest greedy step on a count limit only; the insurance search (ADR-025) and local improvement are heuristic refinements reported with in-sample and out-of-sample numbers. A deterministic sanity check (ADR-023) labels every portfolio.

## Context

The engine must choose 1 to 150 entries per contest across about 10 contests so that each contest's top-1% probability is high and the night's severe-drawdown probability is low (ADR-025, formerly ADR-001). The user's prior engines tuned exposure and overlap rules by hand and showed no edge (RR1, RR2). Generating lineups in sequence with "share at most K players" constraints is slow (R2: 30.8 seconds for 150 lineups with GLPK, up to 370 seconds with other solvers) and ignores the field and the night.

## Options considered

1. **Sequential optimizer with overlap caps** (Hunter, Vielma and Zaman style).
2. **Exposure targets set by hand or by the LLM.**
3. **Greedy coverage over a candidate pool scored on shared scenarios,** then a constrained swap search for the insurance budget.

## Decision

Option 3.

- **Four independent scenario sets** (ADR-025, formerly ADR-001): candidates are shortlisted on screening (5,000), selected on selection (15,000), the insurance search runs on validation (15,000), and every reported number comes from reporting (30,000). On synthetic data greedy's in-sample probabilities ran 0.7 to 3 points high (R2).
- **Per contest, lazy greedy** on Goal 1 as defined in ADR-024 (top-1% prize equity with duplication and ties inside it; the v3 text read "raw probability in Phase 1; duplicate-adjusted per format after calibration, ADR-009", superseded 2026-10-14), storing per-scenario settlement values sparsely for scenarios where a candidate is in the top 1%. Each scenario's value is the best of our entries, so adding a lineup never lowers it and greedy keeps its guarantee of at least about 63% of the best set from the same pool (R2, VERIFIED theorems). On fresh synthetic scenarios greedy beat taking the top projections (47% against 35% with 20 entries, R2).
- **Insurance search:** superseded on 2026-10-14 by ADR-025 (the exact paired constraint, no pre-freeze rule, roll-back as a label, Goal 2 as severe drawdown). The v3 text read: single-lineup swaps that lower washout while every contest keeps `G1_c(new) >= (1 - epsilon) x G1*_c + 2 x SE_paired`; frozen contests when the budget is within noise.
- **Local improvement:** deterministic single-player swaps kept only if they beat noise without breaking a guarantee.
- **Guardrails in code:** no repeated lineup within a contest; a 60% cap on any one player's share of a format's entries, feasibility-tested and reported when relaxed (revised 2026-10-14).

## Consequences

- **Results:** the two goals are optimized directly; diversity comes from covering different scenarios.
- **Cost:** on a synthetic 8-game, 118-entry night, greedy for every contest took 0.3 seconds and the search about 1 second; scoring candidates and computing field lines dominate the 211-second build (R9).
- **Workload:** no exposure settings to manage.
