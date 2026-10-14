# ADR-019: Delivery first; only DraftKings validity can block a file

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief says deadline beats perfection: if an advanced step fails near lock, ship a valid portfolio from what we have and say what was skipped. Your prior engines lost more to delivery than to models: 67 MLB entries locked blank in slates nobody built; a weather check that changed no number blocked two NFL slates; a convention enforced as a rule helped cause a 37-entry MLB night with no file; 12 of 13 NFL entries locked blank after a file was built; golf lost 7 entries to environment repair inside the entry window; never-passing gates were bypassed in three sports (RR1 to RR3, VERIFIED).

## Decision

- **Only DraftKings validity blocks a file** (ADR-010). Every other check (data freshness, concentration, QA, strategy) labels the output in the brief.
- **Night plan in lock order:** every slate gets a validated fallback file before any slate is improved.
- **Fallback that depends only on the entries file:** salary-implied points when nothing else is available, with players DraftKings marks OUT or the latest official report lists as Out removed; marked "not checked for injuries" when neither file is present (RT1 rank 22).
- **Stored replacements and `dfs apply`** for each material questionable player (ADR-011), so acting on news takes seconds and no full run, and works from the launcher without Claude.
- **A desktop launcher** runs every night step without Claude (ADR-013), and the top of every brief carries an "if the engine is down" card listing the latest validated file and the fallback file for each slate, with "valid until" stamps, and how to enter news with `dfs out`.
- **Fallback ladder:** full build with QA; without QA; without any LLM step; the fallback portfolio; the last validated file for that slate, re-validated against the newest download.
- **Completeness check after every upload,** with versioned file names and the user's "uploaded N of N" read-back.
- **No environment repair inside the entry window:** a failing 60-second preflight sends the night to the no-LLM path.
- **The brief lists unfilled entries next to P(washout).**

## Consequences

- **Results:** removes the largest avoidable loss in the prior engines.
- **Cost:** the fallback path is a small, well-tested part of Phase 1, built first.
- **Workload:** one re-download and `/status` after each upload.
