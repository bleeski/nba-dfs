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

- Three independent scenario sets (revised after red-team round 1, RT1 rank 18): candidates are shortlisted on a screening set, re-scored on a selection set, and every reported number and insurance guarantee comes from a reporting and validation set.
- Per contest, lazy greedy on the top-1% objective (raw probability in Phase 1; duplicate-adjusted after calibration, ADR-009), storing per-scenario results as bits for big fields and 8-bit probabilities for fields under about 1,000. Each scenario's value is the best of our entries, so adding a lineup never lowers it and greedy is guaranteed at least about 63% of the best set from the same pool (R2, VERIFIED theorems).
- Night insurance search (replacing a single-weight sweep, which did not enforce per-contest guarantees, RT1 rank 7): starting from each contest's greedy portfolio, accept single-lineup swaps that lower washout while every contest keeps at least `(1 - epsilon) x G1*_c` on the validation set; skipped when washout at 0% is under 1%.
- A deterministic local-improvement pass tries single-player swaps and keeps those that beat noise without breaking a guarantee.
- Guardrails in code: no repeated lineup within a contest; a 60% cap on any one player's share of the night's entries.

## Consequences

- **Results:** the two goals are optimized directly; diversity comes from covering different scenarios, and the frontier table shows the cost of insurance every night.
- **Cost:** selection runs in seconds to a minute (measured in R9); memory stays small because hits are stored as bits.
- **Workload:** no exposure settings to manage.
