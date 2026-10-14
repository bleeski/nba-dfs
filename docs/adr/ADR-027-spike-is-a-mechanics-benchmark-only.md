# ADR-027: The night benchmark spike is a timing and mechanics benchmark, never a statistical oracle

**Status:** Accepted. **Supersedes:** ADR-022. **Source:** ADJUDICATION entries 16, 2, 13, 25 (B-I-06, A-I-02, A-I-12, A-D-06). **Changelog:** 2026-10-14 created.

## Context

ADR-022 made `spikes/night/night_spike.py` the reference implementation and test oracle: "the same synthetic inputs must give the same numbers". I verified that the spike draws each team's points first and back-solves two-point makes, then allocates makes zero-sum within the team (ADJUDICATION V4), while ARCHITECTURE section 4 specifies the opposite order (attempts from possessions and usage share, makes from shrunk percentages). The spike's insurance margin and duplication penalty also differ from the design (V1, V3). A bottom-up engine cannot and should not reproduce a top-down spike's statistical outputs, and reproducing any spike proves regression consistency only.

## Decision

- The spike is kept as a **timing and mechanics benchmark**: the engine's field scoring, threshold computation, bitset and settlement arithmetic, and greedy selection are checked against it on its synthetic night, within Monte Carlo tolerance, as a regression test of arithmetic only.
- The spike is **never** an oracle for the simulator's statistical outputs, for insurance behavior, or for duplication effects. Numbers from it are labeled "spike measurement" wherever cited.
- The engine simulator follows ARCHITECTURE section 4 as written (bottom-up) and is **calibrated against last season's box scores** before any slate, with targets stated in configuration and checked by tests: starter standard deviation 0.22 to 0.25 of the mean; margin around the spread with a standard deviation of about 13; game total around the betting total; overtime 5% to 6%; share of games decided by 20 or more about 19%; double-double and triple-double rates by role; teammate and opponent correlations by role pair; most-owned Classic player in the field model 40% to 60% on typical slates.
- **Adversarial examples** are part of the test suite: exchangeable entrants (our edge must be zero); a stronger field plus a shared error against our preferred players; the same lineup and opponents repeated across contests (the independence product must be wrong and the shared-field sensitivity right); ties at a payout boundary with more tied entries than paid places; two same-team scratches and a failed upload across a lock; a concentrated Showdown pool where the cap is infeasible. Each uses a tiny example whose outcomes can be counted, checked independently of the spike.

## Consequences

- **Results:** the engine's numbers rest on calibration against reality and countable examples, not on agreement with earlier code.
- **Cost:** a calibration test suite in the simulator chunk; the adversarial suite after the MVP.
- **Workload:** none.
