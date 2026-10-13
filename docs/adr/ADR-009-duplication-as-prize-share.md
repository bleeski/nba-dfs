# ADR-009: Duplication counts a top-1% finish at the share of prize money it keeps

**Status:** Proposed; needs the user's confirmation (Decision D2 in ARCHITECTURE.md). **Date:** 2026-10-13.

## Context

A lineup tied with opponent copies still finishes in the top 1%, so duplication does not change the raw probability of a top-1% finish. It changes the money: DraftKings pools the prizes for tied places and splits them evenly (terms, R6). Showdown makes this acute: one 2020 NBA Showdown ended in a 19-way tie for first (R5, SUPPORTED), and an NFL Showdown lineup built about 500 times turned a $500,000 first prize into about $1,559 each (R5, VERIFIED for NFL). Every vendor ranks lineups by ROI, which penalizes duplicates (R1).

## Options considered

1. **Pure probability.** Count a tied finish as a full finish. Matches the brief's literal wording. Pushes the optimizer toward the chalkiest version of a good lineup, especially in Showdown.
2. **Flat penalty 1/(1 + D)**, where D is the expected number of opponent copies. Simple, but overcharges ties deep in the top 1%, where neighboring prizes are nearly equal and a tie barely changes the payout.
3. **Prize-share factor.** Count a tied finish at (pooled prize for the tied places, split evenly) divided by (the prize for that place alone), using the contest's payout table and the field model's duplicate estimate.

## Decision

Option 3, reported side by side with option 1.

- For each candidate lineup, the field model estimates opponent copies (exact-match frequency in the simulated field for Showdown and for chalky Classic lineups; ownership product times a fitted factor for rare Classic lineups).
- In each scenario where our best entry is top 1%, the engine computes the expected share of prize kept given its rank and the copies, from the contest's payout table (or the class default when no table was pasted).
- Goal 1 is the average of that share; the raw probability is shown next to it in the brief.

## Consequences

- **Results:** in Showdown and in fields under 200 (where top 1% means first place), the engine avoids lineups whose top-1% finishes would be split many ways; elsewhere the penalty is small because ties deep in the top 1% cost little.
- **Cost:** duplicate estimates come from the field model the engine needs anyway; the payout lookup is cheap.
- **Workload:** none, beyond the optional payout pastes that improve every contest estimate.
- **If the user prefers option 1:** a single setting switches Goal 1 to the raw probability; the duplicate estimates are still reported.
