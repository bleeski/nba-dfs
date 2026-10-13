# ADR-003: The LLM sets beliefs; code sets lineups

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief asks where judgment ends and arithmetic begins: should the LLM pick players for lineups, or set theses, player pools, and constraints that a solver turns into lineups? The objective (Goal 1 per contest, Goal 2 across the night) is a probability over thousands of simulated nights and simulated opponents. The LLM runs inside a Pro-sized Claude budget, has no seed or temperature control (R7), and its contributions must be measurable for the learning loop.

## Options considered

1. **LLM builds lineups** (picks players, applies stacking judgment). Flexible, but it cannot evaluate the objective, its choices cannot be replayed, and it costs the most tokens.
2. **LLM sets theses and constraints** (for example "stack game 3", "fade player X", exposure targets). Cheaper, but theses are untested opinions that move every lineup, and there is no model-only baseline to score them against.
3. **LLM files structured beliefs about the world; code does everything that follows.** Beliefs are availability probabilities, minutes ranges, usage shifts, and data-quality flags, each with evidence and a confidence, in the override schema from R3 section 10.

## Decision

Option 3, with a narrow exception for player-pool exclusions.

- The LLM's output types are fixed: `availability` (probability of playing), `role` (probability of starting, minutes q10/q50/q90, optional hard cap), `usage_multiplier` and optional per-stat multipliers (quantiles), `redistribution_hint`, `condition` (applies only in scenarios where another player is out), `data_flag` (stale or conflicting input), and `pool_exclusion` (remove a player, with a stated reason, for example "not with team"). Each record carries evidence links and short quotes.
- Code validates every record (known player, game not locked, quantiles ordered, minutes 0 to 48, multipliers 0.5 to 2.0, evidence present, not expired) and rejects bad ones with a logged reason.
- Code blends overrides with the model by precision weighting after inflating the LLM's stated variance by a coverage factor fitted from its track record (starting at 1.5). Official OUT designations beat everything; the user's overrides beat the LLM's.
- The LLM never writes lineups, exposures, or numbers into upload files. Game-level "theses" are not accepted as constraints; if the LLM believes a game is mispriced, it must say why in terms of a belief the model can use (for example "starter X is out, pace will rise") or leave it to the brief.

## Consequences

- **Results:** the LLM's edge (reading news faster and more completely than a feed) reaches every lineup through the simulation, and its errors are caught by validation and down-weighted by its own track record.
- **Cost:** the smallest LLM footprint of the three options; research reads a diff of news, not the whole slate.
- **Workload:** the user can skim a nightly list of overrides (one line each with the evidence) and veto any of them; there is nothing to approve by default.
- **Measurement:** every override is stored with its model-only twin, so a weekly report answers "did the LLM help?" with minutes and points error, interval coverage, and Brier score for availability.
