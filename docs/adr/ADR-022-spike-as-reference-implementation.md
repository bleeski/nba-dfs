# ADR-022: The night benchmark spike is a reference and test oracle, not engine code

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief marks `spikes/` as throwaway. The R9 night benchmark (`spikes/night/night_spike.py`) already simulates a synthetic night with shared factors, builds fields and candidates, scores them in bit arrays, and runs selection and the insurance search. Phase 1 has five build days (RT1 rank 5 asked for an explicit decision on whether to promote it).

## Options considered

1. **Promote the spike into the engine as is.** Fastest, but untested, written for measurement rather than maintenance, and against the brief's throwaway rule.
2. **Ignore it and rewrite from the design.** Wastes verified logic and measured parameters.
3. **Rewrite its logic into the engine package with tests, using the spike as a test oracle:** the same synthetic inputs must give the same numbers.

## Decision

Option 3. The engine's simulator, field generator, candidate scorer and selector are written fresh to the engine's conventions (deterministic keys, schemas, chunking), and a test runs both on the spike's synthetic night and compares outputs within Monte Carlo tolerance.

## Consequences

- **Results:** the engine starts from logic that has already been measured on this laptop.
- **Cost:** saves design time in Phase 1 without importing untested code.
- **Workload:** none.
