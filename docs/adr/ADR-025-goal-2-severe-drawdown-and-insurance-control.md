# ADR-025: Goal 2 is the probability of a severe-drawdown night; the insurance control with an exact paired margin

**Status:** Accepted (goal by owner decision, 2026-10-14; control after the MVP). **Supersedes:** ADR-001. **Source:** ADJUDICATION entries 8, 9, 2, 4 (A-I-08, B-I-02, A-I-02, A-I-04), escalation answer of 2026-10-14. **Changelog:** 2026-10-14 created.

## Context

The original Goal 2 was the probability of zero cashing entries across the night. In the model it was near zero at 50 or more entries (R9), and a $0.25 min-cash on a $1,000 night counted as success. I recommended keeping the literal definition and reporting fee-recovery diagnostics beside it; the owner chose Critique B's proposal. Separately, both critiques found that the spike's insurance safety margin used the unpaired standard error of the level rather than the paired standard error of the change (VERIFIED, ADJUDICATION V1, V2), which froze every contest with top-1% odds under about 40%, so the R9 insurance numbers are indicative only. Critique A also found that a reporting set which triggers rollbacks is no longer untouched.

## Decision

- **Goal 2.** `P(SD) = E_s[ 1{ total winnings(s) < alpha x total fees } ]`, where total winnings sum every contest's settled prizes for all our entries (every paid place, not only the top 1%) in scenario `s`, and `alpha` is the setting `goal2.alpha`, default 0.25. Setting `alpha` near zero recovers the literal zero-cash definition, which is reported beside Goal 2 as a diagnostic together with unfilled entries and per-game concentration.
- **Settlement.** The same per-scenario joint settlement as Goal 1 (ADR-024), extended to every paid rank: payout at rank from the contest's table or template curve, ties split evenly, copy rates from the field model, facts status labeled.
- **The control.** Choose the night's portfolio that minimizes `P(SD)` subject to `G1_c >= (1 - epsilon) x G1*_c` for every contest, where `G1*_c` is the best Goal 1 found for `c` alone. Starting from each contest's best portfolio, search single-lineup swaps in any contest. A swap is accepted only if it lowers `P(SD)` on the validation set and every contest satisfies, on the validation set, `Delta_c - 2 x SE_paired(Delta_c) >= -epsilon x G1_c(E*_c)`, where `Delta_c = G1_c(E_c) - G1_c(E*_c)` is the cumulative change from the contest's best portfolio and `SE_paired` is the standard error of the per-scenario differences of those two portfolios' values. There is no pre-freeze rule; after the search a contest is labeled "frozen" when no candidate swap in it satisfied the constraint, and the brief names those contests. A test feeds a known case and checks the implementation reproduces this formula exactly.
- **Scenario sets.** Screening 5,000; selection 15,000; validation 15,000 (the search and its constraint); reporting 30,000 (every number in the brief). The roll-back check on the reporting set is a label; if a roll-back is applied, the final numbers are recomputed on a fresh 30,000-scenario reporting draw.
- **Wording.** The budget is a model-based target under stated assumptions, not a real-world guarantee. "Zero washouts in N synthetic draws" never appears as a bound on real risk; synthetic tests establish speed and arithmetic only. Goal 2 is reported with a sensitivity range under three field-strength settings (no edge, stronger field, concentrated chalk) once the field model has those settings.
- **Default epsilon:** 2% as a starting value (Decision D3), re-measured with the corrected formula on the first real nights; the R9 figures are indicative because they used the wrong margin.
- **When it runs:** after the MVP (chunk C12), and only when the validation set holds at least 50 severe-drawdown scenarios (`insurance.min_sd_scenarios`); otherwise the brief says Goal 2 is too rare to trade tonight. The Baseline reports Goal 2 as a labeled, uncalibrated model estimate and does not act on it; the Floor prints "not estimated".
- **The hunch test** (do the goals conflict less than they look) runs on real fields: the 0%, 20% and lowest-drawdown portfolios are computed nightly and scored against the next morning's standings, with a verdict after 20 nights or "undecided".

## Consequences

- **Results:** at the owner's volume the control is expected to act regularly, because a 25% fee-recovery floor binds far more often than literal washout; every contest's Goal 1 stays within its budget on fresh scenarios up to noise, honestly stated.
- **Cost:** the search takes about a second; a roll-back costs about 3 minutes of extra reporting.
- **Workload:** one number to set, once.
