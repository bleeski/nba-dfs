# ADR-020: Versioned DraftKings scoring adapter with nightly self-checks

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entry 23): Captain totals are stored **eighth-point** exact: 1.5 x a quarter-point UTIL total ends in .125 or .875 (VERIFIED: 1.5 x 57.25 = 85.875). The phrase "quarter-point-exact" in the decision below was wrong wording and is corrected in place.

## Context

Every probability the engine produces passes through DraftKings scoring. The brief asked two edge cases to be confirmed from real results, not assumed. R6 ran discriminating tests:

- **Triple-double earns +4.5** (double-double +1.5 and triple-double +3). DraftKings' own export shows Russell Westbrook (2017-03-29: 57 points, 6 threes, 13 rebounds, 11 assists, 3 steals, 7 turnovers) at 99.75. Base is 95.25; base + 4.5 = 99.75 matches, base + 3 = 98.25 does not. Four more triple-doubles in RotoGuru's DraftKings logs match +4.5 and none match +3. VERIFIED arithmetic on a third-party copy of a DraftKings export.
- **Captain 1.5x applies to the bonuses.** In a 2020 NBA Showdown export, Bam Adebayo (double-double) shows 89.25 = 1.5 x (58.0 + 1.5); the other rule gives 88.5. Jayson Tatum matches the same way (85.875, displayed 85.88). SUPPORTED for NBA (third-party copy, older season).
- Overtime counts (Westbrook's 99.75 includes overtime). Inactive players score 0. Ties split prizes evenly (DraftKings terms).

## Options considered

1. Hardcode scoring in the simulator.
2. **A separate, versioned scoring module with rule tests, plus a nightly check of every standings file against box scores.**

## Decision

Option 2.

- Scoring is a pure function of a box-score line and a rules version (`dk_nba_2026_v1`). Captain points are 1.5 x the full bonus-inclusive total and are stored in eighth-point-exact form (Captain totals can end in .125 or .875; DraftKings displays two decimals).
- Regression tests: the five triple-doubles and three double-double controls from R6, synthetic lines at every 9/10 threshold, a quadruple-double (+4.5 total), a line where turnovers or threes would wrongly create a bonus, and Captain cases with and without bonuses.
- Every morning, the results step recomputes each player's DraftKings points from the box score and compares them with the standings file's FPTS, and asserts Captain FPTS = 1.5 x UTIL FPTS within 0.01 for every player rostered at both. A mismatch stops learning for that night and is reported in plain language. This turns the Captain rule from SUPPORTED into VERIFIED on opening night at no extra effort.

## Consequences

- **Results:** correct bonus handling matters most for triple-double candidates and Captains, whose tails decide top-1% finishes.
- **Cost:** about half a day of build time.
- **Workload:** none; the check runs inside the morning results step.
