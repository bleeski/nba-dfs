# ADR-008: Ownership and the field come from simulated opponents who see only public information

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

Goal 1 needs each contest's top-1% line and duplicate counts, which depend on how opponents combine players, not just how often they pick each one (brief problem 6). There is no free ownership feed and no past NBA standings for this user. Your NHL engine read ownership off a simulated field and still missed news-driven chalk by about 10x (50.7% actual against 4.7% predicted) because news never reached its field (RR3, VERIFIED). If simulated opponents could see our private research, our edge would vanish inside the simulation.

## Options considered

1. **Ownership regression** (salary, projection, value, news timing) with a separate lineup sampler. Needs history we do not have; ownership and combinations can disagree.
2. **Field of simulated opponents built from our full model.** Reacts to news, but leaks private overrides into the field.
3. **Field of simulated opponents built from a public view of the night**, with ownership read off the field.

## Decision

Option 3.

- Two belief sets: the **engine view** (everything, including private overrides) for our lineups, and the **public view** (baseline model plus official statuses, DraftKings `Status` and `Starting`, market lines, and free consensus projections where the posture allows) for the field.
- Opponents are a mixture per contest family: optimizer-like entrants on noisy public projections, casual entrants weighted by public popularity with a salary floor, chalk duplicators, and stale entrants whose lineups predate late news.
- Ownership is read off the field in one unit with nightly sum checks; Captain and UTIL are separate; 5 to 10 field realizations per contest carry ownership uncertainty.
- Settings start from rules of thumb and are fitted from the user's standings files from night 2, with heavy shrinkage and only stable shapes.
- Tests in both directions: a public scratch must raise the beneficiary's simulated ownership; a private override must not change it.

## Consequences

- **Results:** thresholds and duplicate counts reflect the field the user faces, including late chalk, without giving away our private edge.
- **Cost:** field generation is the costliest compute step (measured in R9); a few thousand optimizer opponents plus cheap samples.
- **Workload:** the morning standings download, which the learning loop needs anyway.
