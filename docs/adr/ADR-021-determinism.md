# ADR-021: Deterministic by construction

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

Common random numbers (comparing portfolios on the same scenarios) and replay both need the same inputs to give the same outputs. Your NHL engine's solver used wall-clock time limits, so a busy laptop changed the lineups; golf drew random noise by row position (RR3, VERIFIED).

## Decision

- Every random draw is keyed by (run seed, scenario index, game, person, stat) with a counter-based generator, so adding or removing a player never shifts anyone else's draws.
- Solvers run without wall-clock time limits (the problems are small); any limit is a deterministic work limit; single-threaded solves inside parallel worker processes, with results merged in a fixed order.
- Iteration over players and contests uses sorted stable keys, never file row order.
- The determinism test runs the same night twice, once under artificial CPU load, and requires byte-identical upload files.

## Consequences

- **Results:** comparisons are precise and replays are exact.
- **Cost:** none measurable.
- **Workload:** none.
