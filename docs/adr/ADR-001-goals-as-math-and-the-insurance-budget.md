# ADR-001: Both goals are computed on one simulated night, and one setting trades them off

**Status:** Accepted (design), revised after red-team rounds 1 and 2 and the R9 benchmark. **Date:** 2026-10-13. The scenario-set sizes and the margin rule below must read the same as ARCHITECTURE.md section 2; a test checks it.

## Context

The brief fixes two goals: (1) within each contest, maximize the probability of a top-1% finish (multi-entry: at least one entry; fields under 100: first place); (2) across the night, minimize the probability of a total washout (zero cashing entries in every contest). It asks for both as math, how each is estimated, how they trade off, and one control. The red team and the R9 benchmark found: a simulation that treats our projections as truth reports washout as about zero at the user's volume; symmetric model error barely changes that; an engine that assumes its own view is right underestimated washout about 9x at 25 entries (0.22% believed, 1.91% true); a single weight swept across contests does not enforce per-contest guarantees; and a search checked on one scenario set exploits that set's noise (a 5% budget kept only 0.919 of a contest's odds out of sample).

## Options considered for the control

1. **Fixed weight** on Goal 1 plus washout. No meaning the user can reason about; not monotone in practice.
2. **Washout ceiling.** Infeasible on small nights, slack on big ones.
3. **Insurance budget:** minimize P(washout) subject to every contest keeping at least (1 - epsilon) of its best Goal 1.

## Decision

- **Goal 1, per contest:** the average over scenarios of the best (over our entries) of `P(top 1% | s, L) = BinomCDF(k_c - 1; N'_c, 1 - F_{c,s}(X_L(s)))`, with `k_c = max(1, floor(0.01 x N_c))`; beta-binomial once standings show multi-entry clustering; first-place contests always reported with the binomial formula. The duplicate-adjusted version (ADR-009) switches on per format after a calibration check.
- **Goal 2, per night:** `P(W)` = average over scenarios of the product over contests of `P(no cash in c | s)`.
- **Uncertainty in every scenario:** outcome noise; symmetric model error (team and player shifts, one ownership shock per slate shared by its contests); and edge uncertainty (a night-wide weight on our view versus the public view, allowed below zero). In Phase 1 edge uncertainty feeds reporting only; Phase 2 decides whether it feeds selection, against the bar written in ARCHITECTURE section 2.
- **Four independent scenario sets:** screening 5,000; selection 15,000; validation 15,000 (insurance search and guarantees); reporting 30,000 (every number in the brief, and the roll-back check).
- **Control:** option 3. A swap is accepted only if it lowers `P(W)` and every contest satisfies `G1_c(new) >= (1 - epsilon) x G1*_c + 2 x SE_paired(change)` on the validation set. Contests whose budget is within noise are frozen. After the search, any contest more than two standard errors below its guarantee on the reporting set is rolled back. The search runs only when the validation set holds at least 50 washout scenarios. Every later step re-checks the guarantee.
- **Default epsilon: 2%.** R9, synthetic, 25 entries, with the margin: 2% cut washout 68% (0.75% to 0.24%) for 0.2% of average top-1% odds (worst contest 2.0%), and every contest stayed inside its budget out of sample. At 118 entries washout was 0 in 30,000 scenarios, so nothing to trade.
- **Hunch test on real fields:** the 0%, 20% and lowest-washout portfolios are computed nightly and scored against the next morning's standings on paired per-contest measures; verdict after 20 nights with an interval, or "undecided".

## Consequences

- **Results:** each contest's top-1% odds stay within its budget on fresh scenarios; washout estimates carry our own fallibility.
- **Cost:** the search takes about a second (R9).
- **Workload:** one number to set, once. At 50 or more entries a night the control will usually do nothing; it matters on thin nights and during the volume ramp. Opening week may not have it (it is the last Phase 1 item).
