# ADR-007: Select portfolios by greedy scenario coverage, with the insurance budget across the night

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The engine must choose 1 to 150 entries per contest across about 10 contests so that each contest's top-1% probability is high and the night's washout probability is low (ADR-001). Classic optimizers usually generate N lineups in sequence with exposure and overlap rules; the user's prior engines tuned such rules by hand and showed no edge (RR1, RR2).

## Options considered

1. **Sequential optimizer with overlap caps** (Hunter, Vielma and Zaman style). Proven for "at least one wins", but slow when the constraints accumulate (68 to 370 seconds for 150 lineups, R2, indicative) and it ignores the field and the night.
2. **Exposure targets set by hand or by the LLM.** Cheap, unmeasurable, and the pattern that failed before.
3. **Greedy coverage over a candidate pool scored on shared scenarios.** Each step adds the candidate that wins the most scenarios the portfolio does not already win; a night-level pass applies the insurance budget.

## Decision

Option 3.

- Per contest, lazy greedy on the duplication-adjusted top-1% objective, using per-scenario hit bits for every candidate. The objective has diminishing returns, so greedy is guaranteed at least about 63% of the best set from the same pool (R2, VERIFIED theorems).
- Night pass: greedy on `sum_c G1_c / G1*_c + lambda x (1 - P(W))`, sweeping `lambda` and keeping the largest value that leaves every contest at least `(1 - epsilon) x G1*_c`.
- A deterministic local-improvement pass tries single-player swaps and keeps those that beat simulation noise.
- Guardrails in code: no repeated lineup within a contest; a 60% cap on any one player's share of the night's entries.
- Reported probabilities come from fresh scenarios not used for selection.

## Consequences

- **Results:** the two goals are optimized directly; diversity comes from covering different scenarios, and the frontier table shows the cost of insurance every night.
- **Cost:** selection runs in seconds to a minute (measured in R9); memory stays small because hits are stored as bits.
- **Workload:** no exposure settings to manage.
