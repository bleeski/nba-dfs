# ADR-018: Reuse from the prior engines: one parser port, a name normalizer, and lessons only

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief says reuse nothing by default and justify any reuse on its merits. The repo review (RR1 to RR4) found no engine with a measured edge, large coupled codebases, and a few small, well-tested pieces that read file formats shared across sports.

## Options considered for each candidate

| Candidate | Evidence | Decision |
|---|---|---|
| Entry-history export parser (NHL `learn/entry_history.py` plus `results.py`; NFL and MLB built the same independently) | Three independent implementations of the same 14-column DraftKings export; NHL's uses only the standard library and numpy (RR3, VERIFIED) | **Port** into the new package with new tests on the user's real export; it gives exact field size, places paid, and results for every contest (R8) |
| NHL `normalize_name` (accent folding, suffixes) | Small, sport-independent; name mismatches blocked 5+ NFL slates (RR2) | **Port** with NBA test cases (Doncic, Jokic, Jr., III) |
| NFL `dk.py` file-layout rules, MLB `day_plan.py`, MLB standings-pull rules, golf's 11-check blocking list, NHL skill setup | Encoded hard-won knowledge, but entangled with each engine's structure | **Learn from, do not copy:** their rules are restated in R6, S2 and the validator checklist |
| Any optimizer, allocator, selector, field sampler, pipeline, claims or gate registry | No measured edge; MLB's field miner had a Showdown duplicate bug; gates blocked delivery (RR1, RR2, RR3) | **Do not reuse** |
| Anything that calls DraftKings endpoints | Conflicts with DraftKings' terms (R6) | **Do not reuse** |

## Decision

Port the entry-history parser and the name normalizer, each rewritten to the new package's conventions with its own tests; learn from the rest.

## Consequences

- **Results:** exact contest facts from week 1, and fewer identity mismatches.
- **Cost:** about two hours of build time saved and spent on tests.
- **Workload:** the user downloads the entry-history export about once a week (30 seconds).
