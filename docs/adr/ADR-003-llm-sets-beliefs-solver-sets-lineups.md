# ADR-003: The LLM sets beliefs; code sets lineups

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entry 12): the researcher's output splits into **fact records** (announced starter, restriction, absence, return; each with source, publish time and quote) and **inference records** (minutes and usage percentiles). In the MVP only fact records with a verified quote and a known publish time inside 24 hours change the simulation, and fixed code rules translate each fact type into a distribution; inference records are stored and scored in shadow, and the precision-weighted blend with the 1.5 coverage factor switches on only after two weeks show stated ranges cover actuals at the stated rate. Records with unknown publish time never change availability or role. A later fact about the same player supersedes an earlier one. The researcher itself is a flagged capability that may ship off (ADR-023); `dfs out`, `dfs in` and `dfs start` are the rehearsed path.

## Context

The brief asks where judgment ends and arithmetic begins: should the LLM pick players for lineups, or set theses, player pools and constraints that a solver turns into lineups? The objective is a probability over thousands of simulated nights and opponents. The LLM runs inside a Pro-sized budget, has no seed or temperature control (R7), and its contributions must be measurable. The red team added three requirements: overrides must be checked against their sources (RT1 rank 15), role changes must not be averaged into impossible values (rank 16), and public news must reach the field model (rank 4).

## Options considered

1. **The LLM builds lineups.** Cannot evaluate the objective; not replayable; the most expensive.
2. **The LLM sets theses and constraints.** Untested opinions move every lineup; no baseline to score them against.
3. **The LLM files structured beliefs about the world; code does everything that follows.**

## Decision

Option 3, with player-pool exclusions allowed with a reason.

- Output types: `availability`, `role` (probability of starting; minutes q10/q50/q90; optional hard cap), `usage_multiplier` and per-stat multipliers (percentiles), `redistribution_hint`, `condition`, `no_history_prior`, `data_flag`, `pool_exclusion`, each with evidence and a `visibility` tag (public or private).
- **Checks before use:** schema and ranges; the quoted words must appear in the page the researcher fetched through `dfs research fetch`, which saves it; the page must be no older than 24 hours. Failing records are dropped and listed.
- **Blending:** role changes (a different probability of starting, or a condition) become mixtures drawn per scenario; within the same role, precision weighting after inflating the LLM's stated uncertainty by a coverage factor fitted from its track record (starting at 1.5). Official OUT beats everything; the user's overrides beat the LLM's. One override moves a teammate's minutes by at most 8 unless the evidence is an official status change.
- The LLM never writes lineups, exposures, or numbers into upload files; game "theses" are not accepted as constraints.
- Every override is one line in the brief with a one-command veto.

## Consequences

- **Results:** the LLM's edge (reading news faster and more completely than a feed) reaches every lineup through the simulation; fabricated or stale evidence is rejected; public news also reaches the simulated field.
- **Cost:** the smallest LLM footprint of the three options.
- **Workload:** skim the override list; veto when needed.
- **Measurement:** every override is stored with its model-only twin; the weekly scorecard answers "did the LLM help?"
