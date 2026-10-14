# ADR-007: Select portfolios by greedy scenario coverage, with a constrained insurance search across the night

**Status:** Accepted (design), revised after red-team rounds 1 and 2 and the R9 benchmark; the guarantee statement superseded by ADR-029. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the concentration cap applies the looser (larger) of the minimum feasible cap and the setting, reporting the relaxation (Guardrails bullet); the earlier changelog's "stricter" is marked superseded inline. 2026-10-14 (ADJUDICATION-R2 entries R2-5 and R2-13): the Decision bullets are rewritten to match ADR-024 and ADR-029. The per-scenario value is the sum of our entries' top-1% allocations under the joint settlement, not the best of our entries; diminishing returns hold only for contests that pay first place only, so the 1-1/e bound is claimed only there and every other result is "best found (heuristic)" (VERIFIED, ADJUDICATION-R2 V-R2-4 and V-R2-4b). The superseded wording is kept under "History" below and is not an instruction.

**Earlier changelog:** 2026-10-14 (ADJUDICATION entries 5 and 7): the per-contest objective is Goal 1 as defined in ADR-024 (top-1% prize equity, with duplication and ties inside it), not raw top-1% probability; greedy still applies because the objective keeps diminishing returns, and the result is reported as "best found". The concentration cap is a per-format, feasibility-tested soft preference: the selector computes the minimum feasible cap for tonight's pools and entry counts, applies the stricter **[superseded wording (ADJUDICATION-R2 R2-34): the looser (larger), because the stricter value is the infeasible one]** of that and the setting, and reports when it relaxed; it never blocks delivery. The 63% guarantee is stated for the per-contest greedy step on a count limit only; the insurance search (ADR-025) and local improvement are heuristic refinements reported with in-sample and out-of-sample numbers. A deterministic sanity check (ADR-023) labels every portfolio.

## Context

The engine must choose 1 to 150 entries per contest across about 10 contests so that each contest's top-1% probability is high and the night's severe-drawdown probability is low (ADR-025, formerly ADR-001). The user's prior engines tuned exposure and overlap rules by hand and showed no edge (RR1, RR2). Generating lineups in sequence with "share at most K players" constraints is slow (R2: 30.8 seconds for 150 lineups with GLPK, up to 370 seconds with other solvers) and ignores the field and the night.

## Options considered

1. **Sequential optimizer with overlap caps** (Hunter, Vielma and Zaman style).
2. **Exposure targets set by hand or by the LLM.**
3. **Greedy coverage over a candidate pool scored on shared scenarios,** then a constrained swap search for the insurance budget.

## Decision

Option 3.

- **Four independent scenario sets** (ADR-025, formerly ADR-001): candidates are shortlisted on screening (5,000), selected on selection (15,000), the insurance search runs on validation (15,000), and every reported number comes from reporting (30,000). On synthetic data greedy's in-sample probabilities ran 0.7 to 3 points high (R2).
- **Per contest, greedy** on Goal 1 as defined in ADR-024 and settled as in ADR-029: each scenario's value is the **sum of our entries' top-1% prize allocations**, with our entries ranked jointly against the field and each other, so a second entry that would also beat the field finishes behind our first. Adding a lineup never lowers that sum. Diminishing returns hold only when the payout curve extended by its drop to zero after place k is convex (in practice, contests that pay first place only), so the 1-1/e bound (about 63%) is claimed only there; elsewhere the result is labeled "best found (heuristic)". Updates are exact and incremental (an added entry changes other candidates' gains only in scenarios where it has top-1% value); lazy upper bounds are a labeled fallback. Values are stored sparsely for scenarios where a candidate is in the top 1%. On fresh synthetic scenarios greedy beat taking the top projections (47% against 35% with 20 entries, R2).
- **Insurance search:** superseded on 2026-10-14 by ADR-025 (the exact paired constraint, no pre-freeze rule, roll-back as a label, Goal 2 as severe drawdown). The v3 text read: single-lineup swaps that lower washout while every contest keeps `G1_c(new) >= (1 - epsilon) x G1*_c + 2 x SE_paired`; frozen contests when the budget is within noise.
- **Local improvement:** deterministic single-player swaps kept only if they beat noise without breaking a guarantee.
- **Guardrails in code:** no repeated lineup within a contest; a 60% cap on any one player's share of a format's entries, feasibility-tested: the selector applies the looser (larger) of the minimum feasible cap and the setting, reporting the relaxation (revised 2026-10-14; ADJUDICATION-R2 R2-34).

### History (not an instruction)

The v4 bullet read: "Each scenario's value is the best of our entries, so adding a lineup never lowers it and greedy keeps its guarantee of at least about 63% of the best set from the same pool." That described the max-over-entries objective of v3, not the dollar Goal 1 the owner chose; it is superseded by the bullet above (ADJUDICATION-R2 R2-5, R2-13).

## Consequences

- **Results:** the two goals are optimized directly; diversity comes from covering different scenarios.
- **Cost:** on a synthetic 8-game, 118-entry night, greedy for every contest took 0.3 seconds and the search about 1 second; scoring candidates and computing field lines dominate the 211-second build (R9).
- **Workload:** no exposure settings to manage.
