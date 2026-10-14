# ADR-009: Duplication counts a top-1% finish at the expected share of prize it keeps, switched on after calibration

**Status:** Proposed; needs the user's confirmation (Decision D2). Revised after red-team round 1. **Date:** 2026-10-13.

## Context

A lineup tied with opponent copies still finishes in the top 1%, so duplication does not change the raw probability; it changes the money. DraftKings pools tied places' prizes and splits them evenly (terms, R6). In the user's NFL data, 83% to 98% of top-1% Showdown entries were shared by six or more players, a 23-way tie for first paid each entry 5.4% of the advertised prize, and unique Showdown lineups were the worst performers (RR2). The red team found three problems with the first version: taking the share from the highest-scoring entry broke the "adding a lineup never hurts" property the greedy guarantee needs; the share must be averaged over the number of copies (not computed at the average number); and duplicate rates are unfitted guesses until real NBA standings exist (RT1 rank 8).

## Options considered

1. **Pure probability.** Matches the brief's literal wording; favors the chalkiest version of a good lineup.
2. **Flat penalty 1/(1 + D).** Overcharges ties deep in the top 1%.
3. **Expected prize share,** per lineup, from the payout table and the distribution of opponent copies.

## Decision

Option 3, staged:

- Each scenario's value for a contest is the **maximum over our entries of P(top 1% | s, L) x share(L, s)**, which keeps the objective's diminishing-returns property and the greedy method's guarantee.
- `share(L, s)` is the expected fraction of the prize kept, averaged over the number of copies (drawn from the field model's copy rate for that lineup), using the contest's payout table: near 1 deep in the top 1%, much lower for ties at the top of a top-heavy payout.
- **Phase 1:** selection uses the raw probability; the brief shows the duplicate-adjusted number beside it.
- **Switch-on, per format:** selection uses the adjusted version for Showdown, and separately for Classic slates of 3 games or fewer, once a calibration check passes: predicted copy counts (for our entries and for the field's most common lineups) match the counts observed in standings within a stated tolerance, expected after roughly five files per format. R9 showed why it matters: on a synthetic night, duplicate-aware selection kept only 4, 1 and 0 of 10 raw picks in three Showdown 20-max contests and cut expected copies per entry from 0.5 to 2.2 down to about 0.1; on a 2-game Classic slate our lineups averaged about 1 expected copy.

## Consequences

- **Results:** in Showdown and in fields under 200, the engine stops favoring lineups whose wins would be split many ways, once its duplicate estimates are trustworthy; elsewhere the effect is small.
- **Cost:** duplicate estimates come from the field model the engine needs anyway.
- **Workload:** none beyond the morning standings downloads.
- **If the user prefers pure probability:** one setting keeps option 1 permanently; duplicate estimates are still reported.
