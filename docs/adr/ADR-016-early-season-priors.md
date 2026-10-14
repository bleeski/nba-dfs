# ADR-016: Early-season priors from last season, shrinkage, and widened uncertainty

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entry 31): after the MVP, market-implied minutes back-solved from player prop ladders (The Odds API per event, largest slates first; ESPN ladders only if the posture ever widens) join the priors with a stated blend weight, and the news digest flags any player where the market disagrees with our depth chart by 4 or more minutes.

## Context

Opening week brings new rosters, rookies, coaching changes, and no current-season data. DARKO, the best free projection method found, has no preseason data and restricts commercial use (R1, R4). Salaries anchor to last season and adjust slowly, while betting markets move fast (R5).

## Options considered

1. **Use DARKO's outputs as the prior.** Strong method, but terms restrict commercial use and its preseason coverage is empty.
2. **Last season's rates as fixed projections until data arrives.** Ignores role changes.
3. **Our own priors from last season's per-possession rates, with aging, rookie, team-change and coaching adjustments, empirical Bayes shrinkage, per-stat recency decay, a widened early-season variance that narrows as minutes accumulate, and heavier weight on market lines early.**

## Decision

Option 3, with DARKO used only as a methodological reference.

- Players with no NBA history (rookies, two-way players): in Phase 1, salary-implied production plus the researcher's `no_history_prior` (a comparable role and a minutes range), because no permissive free source of draft slot and college statistics was verified (RT1 rank 12). A draft-slot prior is a Phase 3 candidate if a permissive source is found.
- Team changes: moved through the usage share model.
- Coaching changes: pace shrunk toward league average.
- The LLM researcher's role overrides carry the most current information about rotations, with evidence, and are scored.
- The early-season variance multiplier is a setting that decays with minutes played and is checked against coverage in the first two weeks.

## Consequences

- **Results:** opening-week distributions are honest about uncertainty, so the selector naturally spreads exposure on uncertain roles.
- **Cost:** about a day of build in Phase 1.
- **Workload:** none.
