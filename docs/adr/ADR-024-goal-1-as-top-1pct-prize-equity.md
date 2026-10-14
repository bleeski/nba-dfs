# ADR-024: Goal 1 is top-1% prize equity in dollars; duplication and ties are inside the objective

**Status:** Accepted (owner decision, 2026-10-14). **Supersedes:** ADR-009 (duplication as prize share, switched on after calibration) and the Goal 1 definition in ADR-001. **Source:** ADJUDICATION entries 5 and 6 (B-I-01, A-I-05, B-I-07, A-I-06), escalation answer of 2026-10-14. **Changelog:** 2026-10-14 created.

## Context

The original Goal 1 was the probability of at least one top-1% finish per contest. Critique B showed that under that objective a 352nd-place finish worth a few dollars counts the same as a first-place finish worth thousands, and that once one entry clears the line the selector gives zero value to a second entry that would win first. Critique A showed that the v3 duplication adjustment (probability times the *fraction* of prize kept) rewards uniqueness rather than money: it prefers a unique $100 over a $1,000 share of $10,000. I also verified that the R9 spike applied a flat `E[1/(1+D)]` penalty across the whole top 1% (ADJUDICATION V3), so the numbers ADR-009 cited described the method ADR-009 rejected. I recommended keeping the raw probability as the objective with dollars as a bounded tie-breaker; the owner chose Critique B's proposal.

## Options considered

1. **Raw top-1% probability** (original): simple; blind to prize size; needs no payout table.
2. **Raw probability with a bounded dollar tie-breaker** (my recommendation): robust in week 1; captures most first-place upside.
3. **Expected top-1% prize equity in dollars** (chosen by the owner): values first place correctly; depends on payout curves and copy rates from night one.

## Decision

Option 3, by the owner's decision.

- **Definition.** For contest `c`, scenario `s`, and our set of entries `E_c`: settle the contest jointly. Each of our entries gets its rank among the simulated field and our other entries; an entry at rank `r` within the top-1% places `k_c = max(1, floor(0.01 x N_c))` wins `W_c(r)`, the contest's payout at that rank; tied places pool their prizes and split evenly (DraftKings rule, VERIFIED V13). For a lineup with `D` opponent copies (drawn from its field copy rate), its expected prize at rank `r` is the average of `W_c(r + j)` for `j = 0..D`, divided by `1 + D`. `G1_c = E_s[ sum over our entries of prize won from top-1% places ] / (top-1% prize pool of c)`. Finishes outside the top 1% contribute zero.
- **Computation.** For each entry and scenario, the number of opponents above it is binomial in the field's per-scenario score distribution (beta-binomial once clustering is fitted). Fields under 10,000 entries use the exact joint settlement of all our entries (our entries push each other down ranks); larger fields use the additive approximation during selection and the exact settlement in reporting.
- **Copy rates.** From the field model: Showdown by frequency in the enumerated field sample; Classic by exact-match frequency for chalky lineups and the product of ownerships with a fitted correction for rare ones. Until the calibration tolerances pass (predicted copy counts for the field's 20 most common lineups within a factor of 2 of observed on at least 4 of the first 5 standings files per format; our entries' predicted expected copies within 1.0 of observed on average), the brief labels copy rates "unfitted" and shows Goal 1 with and without duplication.
- **Payout facts.** From the contest-facts component: exact table when pasted or known from the entry-history export; otherwise a parametric payout curve by contest type and size, labeled "template" or "default". Every Goal 1 number carries that label.
- **Selection.** Greedy per contest on the marginal gain in `G1_c` (the objective keeps diminishing returns, SUPPORTED, ADJUDICATION V16), reported as "best found". Raw top-1% probability is reported beside Goal 1 as a diagnostic.
- Decision D2 (when duplication switches on) is retired.

## Consequences

- **Results:** the selector values first-place upside and penalizes ties at the top heavily and ties near the top-1% boundary barely; it can be led astray by wrong payout curves or copy rates in week 1, which is why both are labeled on every number.
- **Cost:** per-scenario payout values per candidate instead of hit bits; memory is managed by storing values only for scenarios where the candidate is in the top 1%.
- **Workload:** pasting the payout table for each new contest in week 1 is recommended (about 45 seconds each, cached afterward).
