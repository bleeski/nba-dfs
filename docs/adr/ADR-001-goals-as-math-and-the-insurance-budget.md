# ADR-001: Both goals are computed on one simulated night that includes model error, and one setting trades them off

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

## Context

The brief fixes two goals: (1) within each contest, maximize the probability of a top-1% finish (multi-entry: at least one entry; fields under 100: first place); (2) across the night, minimize the probability of a total washout (zero cashing entries in every contest). It asks for both as math, how each is estimated, how they trade off, and one control for choosing a point on the tradeoff. The red team found that a simulation treating our projections as truth reports washout as essentially zero at the user's volume (P(W) 0.0 on an 11-contest, 118-entry synthetic night), so the control would do nothing; and that a single weight swept across all contests does not enforce per-contest guarantees (RT1 ranks 1 and 7).

## Options considered for the control

1. **Fixed weight** (Goal 1 + lambda x (1 - washout)). No meaning the user can reason about; not monotone in practice.
2. **Washout ceiling.** Infeasible on small nights and slack on big ones.
3. **Insurance budget:** minimize P(washout) subject to every contest keeping at least (1 - epsilon) of its best Goal 1.

## Decision

- **Goal 1, per contest:** the average over scenarios of the best (over our entries) of `P(top 1% | s, L)`, with `P(top 1% | s, L) = BinomCDF(k_c - 1; N'_c, 1 - F_{c,s}(X_L(s)))` and `k_c = max(1, floor(0.01 x N_c))`; beta-binomial once standings show multi-entry clustering. The duplicate-adjusted version (ADR-009) switches on after calibration.
- **Goal 2, per night:** `P(W)` = average over scenarios of the product over contests of `P(no cash in c | s)`.
- **Three kinds of uncertainty in every scenario:** outcome noise; symmetric model error (team and player shifts in expectations, plus one ownership shock per slate shared by all its contests); and **edge uncertainty**, a night-wide weight on our view versus the public view, which can fall below zero (we were wrong in the direction we disagreed). R9 showed symmetric error barely moves washout, while an engine that assumes its own view is right underestimated washout about 9x at 25 entries (0.22% believed, 1.91% true). `P(W)` is reported with and without the edge-uncertainty layer.
- **Measured trade (R9, synthetic, 25 entries, with edge uncertainty and a two-standard-error margin):** a 2% budget cut washout 68% (0.75% to 0.24%) for 0.2% of average top-1% odds; at 118 entries washout was 0 in 30,000 scenarios, so nothing to trade. Default epsilon: 2%.
- **Estimation:** Monte Carlo with three independent scenario sets: screening (10,000), selection (10,000), reporting and validation (30,000); common random numbers for every comparison.
- **Control:** option 3, the insurance budget epsilon. Enforced by a constrained swap search from each contest's greedy portfolio, accepting a swap only if it lowers `P(W)` while every contest keeps its guarantee on the validation set; re-checked after every later step. A budget smaller than two standard errors of a contest's Goal 1 is reported as "within noise". If `P(W)` at 0% is under 1%, the brief says washout is negligible tonight and skips the search.
- **Hunch test on real fields:** the 0%, 20% and lowest-washout portfolios are stored nightly and scored against the next morning's standings; verdict after 20 nights with an interval.

## Consequences

- **Results:** each contest's top-1% odds never fall more than epsilon below the best the engine found (on fresh scenarios); washout risk reflects shared model errors, not just game noise.
- **Cost:** the search runs in seconds to a minute (measured in R9).
- **Workload:** one number to set, once; the brief shows what each step buys and whether washout is live tonight.
