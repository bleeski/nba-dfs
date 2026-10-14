# ADR-015: Learn per layer on dense signals; adopt changes only through shadow tests and the user's sign-off

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entries 13, 24 and 27): the Nov 3 volume-ramp gate is (1) zero delivery failures over the window, (2) minutes and ownership accuracy beating the named baselines with intervals excluding zero, (3) positive contest-flashback prize equity against the control portfolio and a random-entry benchmark on real fields, with the fee-recovery and expected-return diagnostics beside it; realized finishing percentile is reported but is not the gate. Challengers are frozen before their evaluation window; held-out nights are used once per challenger family; predictions are stored as they stood at decision time; in flashback scoring our historical entries are replaced, not added. Near-drawdown diagnostics (errors grouped by game and news event, fraction of entries cashing, best-entry distance to each cash line, returns across the night, bootstrapped by night) are tracked and can reject a model but never certify a small Goal 2.

## Context

A few contests a night are mostly noise: detecting a top-1% rate moving from 1.0% to 1.5% needs about 7,700 independent entries per version (R3, VERIFIED arithmetic), and your NFL engine's data put detection of a 5-point percentile shift at about 88 slates (RR2). Per-player projection and ownership errors give hundreds of observations a night. Your prior engines either never learned (dfs-os and dfs-architect held learning until 30 slates and logged zero rows, RR4) or chased construction features that flipped sign game to game (RR2).

## Options considered

1. **Tune strategy from our own contest results.** Mostly noise.
2. **Learn nothing until a large sample exists.** Wastes the dense signals.
3. **Score every layer against its own baseline nightly; run challengers in shadow; adopt on held-out paired tests with sign-off.**

## Decision

Option 3.

- Nightly scorecards for availability, minutes, points, LLM overrides, the user's overrides, ownership, the field model, scoring, and per-entry cash-probability calibration, each against a named baseline.
- Counterfactual ranks against real standings for the final portfolio, the pre-QA portfolio, the pre-override portfolio, and a simple control portfolio.
- Adoption: pre-registered hypothesis; at least two weeks in shadow; held-out nights; the 95% interval of the average nightly difference excludes zero and the effect holds in at least two of three subgroups; the user approves with `/weekly adopt`; versioned and reversible.
- Nothing is fitted to one night; field shapes are fitted with heavy shrinkage.
- At most 5 open decisions queued for the user.

## Consequences

- **Results:** calibration improves within days to weeks, and claims about beating the field wait for evidence.
- **Cost:** compute in the morning step; the weekly analyst run.
- **Workload:** about 3 minutes each morning and a weekly review.
