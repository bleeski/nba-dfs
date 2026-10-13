# ADR-012: QA proposals are typed, independent, and judged by code

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief wants an adversarial QA agent with an evidence bar (sample size, effect size, whether the projection already prices the effect in), proposals scored against the two goals, a defined iteration and stop rule, and independence from the builder. A subtle trap: if a QA proposal changes a belief (for example "X plays fewer minutes on back-to-backs"), re-simulating under that belief always makes the portfolio built for it look better, so simulation cannot prove a belief. Your MLB engine's QA agent ran 11 to 33 minutes a night (RR1).

## Options considered

1. **QA edits the portfolio directly.** Fast, unmeasurable, can approve its own beliefs.
2. **QA proposals accepted when re-simulation improves the goals.** Circular for belief changes.
3. **Typed proposals; beliefs gated by an evidence bar computed by code from the model's own past errors; construction changes gated by simulation with beliefs fixed.**

## Decision

Option 3.

- **Independence:** a separate subagent that sees only a packet of facts (portfolio, frontier, exposures, baseline and final projections, overrides with evidence, public-view ownership, contest facts, the list of effects the model already includes, and earlier rejected proposals with reasons), never the builder's reasoning. No web access.
- **Types:** projection adjustment, availability challenge, swap pair, exposure cap or floor, data flag. At most 8 per iteration.
- **Belief bar (code reruns the cited query):** at least 20 games for a split or 300 minutes for a rate; effect after shrinkage at least 1.5 minutes or 3% of DraftKings points; and if the model already includes the effect, the evidence must come from the model's own past errors in that split. Simulation then checks materiality and regret (under the old beliefs, no contest may lose more than 2% of its Goal 1).
- **Construction bar:** with beliefs fixed, accept only if no contest's Goal 1 falls by more than noise, washout does not rise by more than noise, and at least one improves by more than two standard errors on common random numbers.
- **Iteration:** packet, one QA run, validate, score, apply accepted, rebuild, validate.
- **Stop rule:** no accepted proposals; or 3 iterations (2 on a Pro-only night); or 10 minutes per iteration; or 45 minutes before the slate's lock.
- The pre-QA portfolio is always kept for the morning scorecard.

## Consequences

- **Results:** QA can only change the portfolio with evidence or measured improvement, and its value is scored against the pre-QA portfolio on real standings.
- **Cost:** about one subagent run per iteration; the deterministic swap pass handles most "near-identical lower-owned player" improvements without the LLM.
- **Workload:** accepted changes appear in the brief with evidence; you can veto any.
