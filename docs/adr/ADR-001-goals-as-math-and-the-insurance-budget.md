# ADR-001: Both goals are computed on one simulated night, and one setting trades them off

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief fixes two goals: (1) within each contest, maximize the probability of a top-1% finish (multi-entry: at least one entry; fields under 100: first place); (2) across the night, minimize the probability of a total washout (zero cashing entries in every contest, Classic and Showdown combined). It asks for both as math, how each is estimated, how they trade off, and one control for choosing a point on that tradeoff.

## Options considered for the control

1. **Fixed weight** (maximize Goal 1 + lambda x (1 - washout)). Simple, but lambda has no meaning the user can reason about, and the same lambda means different things on a 3-contest night and a 12-contest night.
2. **Washout ceiling** (maximize Goal 1 subject to P(washout) at most X%). Intuitive, but infeasible on small nights (a single-entry night washes out about 80% of the time whatever we do) and slack on big ones.
3. **Insurance budget** (minimize P(washout) subject to every contest keeping at least (1 - epsilon) of its best achievable Goal 1). Scale-free, always feasible, protects each contest individually, and needs no weighting between contests.

## Decision

- **Goal 1, per contest c:** `G1_c = average over scenarios of P(top 1% in c | s) x share_c(s)`, where `P(top 1% in c | s) = BinomCDF(k_c - 1; N'_c, 1 - F_{c,s}(B_c(s)))`, `k_c = max(1, floor(0.01 x N_c))`, `B_c(s)` is our best entry's score in scenario s, `F_{c,s}` is the simulated field's score distribution in that scenario, and `share_c(s)` is the fraction of prize kept after ties with duplicate opponent lineups (ADR-009). Raw P(top 1%) is reported alongside.
- **Goal 2, per night:** `P(W) = average over scenarios of the product over contests of P(no cash in c | s)`, with `P(no cash in c | s) = 1 - BinomCDF(m_c - 1; N'_c, 1 - F_{c,s}(B_c(s)))` and `m_c` the paid places.
- **Estimation:** Monte Carlo on one shared simulation of the whole night (10,000 scenarios to screen, 30,000 to finalize), with common random numbers for every comparison.
- **Control:** option 3, called the **insurance budget** epsilon, default 5%. Implementation: lazy greedy on `sum_c G1_c / G1*_c + lambda x (1 - P(W))`, sweeping lambda upward and keeping the largest lambda for which every contest satisfies `G1_c >= (1 - epsilon) x G1*_c`.
- **Reporting:** each night's brief shows the frontier at epsilon = 0, 2, 5, 10, and 20%, so the user sees what each step of insurance buys before choosing.

## Consequences

- **Results:** each contest's top-1% odds can never fall more than epsilon below the best the engine found for it; the night's washout risk is as low as that allows.
- **Cost:** selection runs the greedy several times (once per lambda step); seconds to a minute of compute (R9 measures it).
- **Workload:** one number to set, once; the frontier table tells the user whether to move it.
- **Testing the user's hunch:** the frontier's slope at small epsilon is the measurement. A steep drop in washout for a small Goal 1 cost supports the hunch; a flat line refutes it. It is tracked nightly and reviewed after 20 nights.
