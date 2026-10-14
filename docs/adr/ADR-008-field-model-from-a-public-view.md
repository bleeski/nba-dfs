# ADR-008: Ownership and the field come from simulated opponents who see only public information

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-33): DraftKings' `AvgPointsPerGame` (last season, playoffs included) is a public number every entrant sees, so the public formula may use it as its trailing-points input; Showdown fields are sampled by popularity (ADR-029). 2026-10-14 (ADJUDICATION-R2 entry R2-13): the Decision bullets now match the earlier changelog: when no consensus file has numbers, the public view uses the deterministic public formula, never our baseline; the baseline-change test applies whether or not consensus exists. The superseded wording is kept under "History" below and is not an instruction. Field scores follow ADR-029 (exact eighth-point scores and a fitted top tail).

**Earlier changelog:** 2026-10-14 (ADJUDICATION entries 6 and 14): the public view **never** falls back to the engine's private baseline; when no consensus file exists it is built from a deterministic public formula (salary-implied value blended with the market-implied team share and trailing DraftKings points per minute), so a private edge can never appear as simulated chalk. The field is treated as a family of plausible opponent behaviors and qualified by separate checks: marginal ownership, player-pair co-occurrence, salary left unspent, Captain combinations, exact duplicates, entrant portfolio clustering, realized score cutoffs. Copy-rate calibration tolerances are pre-registered in ADR-024. Goal 2 carries a shared-field sensitivity (the same simulated users entering every contest on a slate) beside the conditional-independence number. Calibration targets for the field (most-owned Classic player 40% to 60% on typical slates) are stated configuration.

## Context

Goal 1 needs each contest's top-1% line and duplicate counts, which depend on how opponents combine players, not just how often they pick each one (brief problem 6). There is no free ownership feed and no past NBA standings for this user. The user's NHL engine read ownership off a simulated field and missed news-driven chalk by about 10x (50.7% actual against 4.7% predicted) because news never reached its field (RR3). The red team found two leaks in the first version: building the field from our own baseline model makes the field share our edge, and withholding all LLM overrides hides public news the real field reacts to (RT1 rank 4).

## Options considered

1. **Ownership regression plus a separate lineup sampler.** Needs history we lack.
2. **A field built from our full model.** Leaks our private edge.
3. **A field built from a public view of the night,** with ownership read off the field.

## Decision

Option 3.

- **Engine view** (everything) for our lineups; **public view** for the field: free consensus projections (Daily Fantasy Fuel's CSV when it has numbers), salary-implied value, betting lines, official statuses, DraftKings `Status`, and overrides tagged `public`. When no consensus source has numbers, the public view comes from the deterministic public formula (salary-implied value blended with the market-implied team share and trailing DraftKings points per minute; settings `public_view.formula_weights`). **The engine's private baseline is never a fallback.**
- Every override carries `visibility`: `public` requires public evidence (official report, team statement, reporter post); `private` is our own inference and never reaches the field.
- Opponents: optimizer-like entrants, casual entrants, chalk duplicators and stale entrants, weighted by contest family; sampled as users so multi-entry lineups share cores.
- Ownership read off the field in one unit with nightly sum checks; Captain and UTIL separate; one ownership shock per slate per scenario, shared by every contest on that slate.
- Settings start from rules of thumb and are fitted from the first standings file on, with heavy shrinkage and only stable shapes.
- Three tests: a public scratch raises the beneficiary's simulated ownership; a private override does not; a baseline-only change does not, **whether or not consensus projections exist**; a static test proves the public-view module never imports the engine's projection table.

### History (not an instruction)

The v4 bullets read "Our baseline model is used only when no consensus source has numbers" and "a baseline-only change does not when consensus projections exist". Both were reversed by round 1 entries 6 and 14 and are superseded by the bullets above (ADJUDICATION-R2 R2-13).

## Consequences

- **Results:** thresholds and duplicate counts reflect the field the user faces, including late chalk, without giving away our edge.
- **Cost:** field generation is the costliest compute step (measured in R9).
- **Workload:** the morning standings download; occasionally a manual Daily Fantasy Fuel CSV download (about 30 seconds) if its table only fills in a browser.
