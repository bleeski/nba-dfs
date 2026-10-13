# ADR-012: QA proposals are typed, independent, and judged by code; QA starts in week 2

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

## Context

The brief wants an adversarial QA agent with an evidence bar (sample size, effect size, whether the projection already prices the effect in), proposals scored against the two goals, a defined iteration and stop rule, and independence from the builder. Re-simulating under a changed belief always makes the portfolio built for that belief look better, so simulation cannot prove a belief. The red team added that an agent choosing its own queries can pass a fixed bar by trying many splits (RT1 rank 26), and that QA's place in opening week contradicted the build plan (rank 23). The user's MLB QA agent ran 11 to 33 minutes a night (RR1).

## Options considered

1. **QA edits the portfolio.** Unmeasurable; can approve its own beliefs.
2. **Accept proposals when re-simulation improves the goals.** Circular for beliefs.
3. **Typed proposals; beliefs judged by an evidence bar code computes from our own past errors; construction changes judged by simulation with beliefs fixed.**

## Decision

Option 3, starting in week 2 after one measured live night.

- **Independence:** a separate subagent with no web access that sees only a fact packet, never the builder's reasoning.
- **Types:** projection adjustment, availability challenge, swap pair, exposure cap or floor, data flag; at most 8 per iteration.
- **Belief bar (code reruns every cited query):** at least 20 games for a split or 300 minutes for a rate; effect after shrinkage at least 1.5 minutes or 3% of DraftKings points; evidence from the model's own past errors when the model already includes the effect; at most 10 queries per iteration, all logged; the effect must hold in the held-out half of seasons. Simulation then checks materiality and regret (no contest may lose more than 2% of its Goal 1 under the old beliefs).
- **Construction bar:** with beliefs fixed, no contest's Goal 1 falls by more than noise, washout does not rise by more than noise, every insurance guarantee holds, and one goal improves by more than two standard errors.
- **Iteration:** packet, one QA run, validate, judge, apply, rebuild, validate. **Stop:** nothing accepted; 3 iterations (2 on Pro-only nights); 10 minutes per iteration; 45 minutes before lock.
- The pre-QA portfolio is kept for the morning scorecard and scored against real standings.

## Consequences

- **Results:** QA changes need evidence or measured improvement, and QA's value is measured against real fields.
- **Cost:** about one subagent run per iteration; the deterministic local-improvement pass handles most "near-identical, less-owned player" swaps without the LLM.
- **Workload:** accepted changes appear in the brief with evidence; any can be vetoed.
