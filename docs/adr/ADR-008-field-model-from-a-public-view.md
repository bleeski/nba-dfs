# ADR-008: Ownership and the field come from simulated opponents who see only public information

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

## Context

Goal 1 needs each contest's top-1% line and duplicate counts, which depend on how opponents combine players, not just how often they pick each one (brief problem 6). There is no free ownership feed and no past NBA standings for this user. The user's NHL engine read ownership off a simulated field and missed news-driven chalk by about 10x (50.7% actual against 4.7% predicted) because news never reached its field (RR3). The red team found two leaks in the first version: building the field from our own baseline model makes the field share our edge, and withholding all LLM overrides hides public news the real field reacts to (RT1 rank 4).

## Options considered

1. **Ownership regression plus a separate lineup sampler.** Needs history we lack.
2. **A field built from our full model.** Leaks our private edge.
3. **A field built from a public view of the night,** with ownership read off the field.

## Decision

Option 3.

- **Engine view** (everything) for our lineups; **public view** for the field: free consensus projections (Daily Fantasy Fuel's CSV when it has numbers), salary-implied value, betting lines, official statuses, DraftKings `Status`, and overrides tagged `public`. Our baseline model is used only when no consensus source has numbers.
- Every override carries `visibility`: `public` requires public evidence (official report, team statement, reporter post); `private` is our own inference and never reaches the field.
- Opponents: optimizer-like entrants, casual entrants, chalk duplicators and stale entrants, weighted by contest family; sampled as users so multi-entry lineups share cores.
- Ownership read off the field in one unit with nightly sum checks; Captain and UTIL separate; one ownership shock per slate per scenario, shared by every contest on that slate.
- Settings start from rules of thumb and are fitted from the first standings file on, with heavy shrinkage and only stable shapes.
- Three tests: a public scratch raises the beneficiary's simulated ownership; a private override does not; a baseline-only change does not when consensus projections exist.

## Consequences

- **Results:** thresholds and duplicate counts reflect the field the user faces, including late chalk, without giving away our edge.
- **Cost:** field generation is the costliest compute step (measured in R9).
- **Workload:** the morning standings download; occasionally a manual Daily Fantasy Fuel CSV download (about 30 seconds) if its table only fills in a browser.
