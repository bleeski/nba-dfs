# ADR-019: Delivery first; only DraftKings validity can block a file

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the old fallback-ladder bullet and the P(washout) bullet below are marked superseded inline (the six-level ladder in this changelog; Goal 2 as a severe-drawdown night, ADR-025). 2026-10-14 (ADJUDICATION-R2 entries R2-1 and R2-6): the chunk reference now names C03, C04a and C11a; time to lock is a label, so the exporter blocks only DraftKings-invalid rows, which is this record's rule applied to late news (ADR-030). 2026-10-14 (ADJUDICATION entries 3, 10 and 11): stored replacements and `dfs apply` are replaced by the live re-solve and the legal repair (ADR-026). The Floor file is uploaded early on opening night, not "only if the full build looks at risk". The fallback ladder is: Optimizer; Baseline; Baseline without LLM steps; Floor; the last validated file for that slate re-validated against the newest download; the legal repair. Four states per slate are shown separately (ADR-010). Release states and the sanity check are in ADR-023.

## Context

The brief says deadline beats perfection: if an advanced step fails near lock, ship a valid portfolio from what we have and say what was skipped. Your prior engines lost more to delivery than to models: 67 MLB entries locked blank in slates nobody built; a weather check that changed no number blocked two NFL slates; a convention enforced as a rule helped cause a 37-entry MLB night with no file; 12 of 13 NFL entries locked blank after a file was built; golf lost 7 entries to environment repair inside the entry window; never-passing gates were bypassed in three sports (RR1 to RR3, VERIFIED).

## Decision

- **Only DraftKings validity blocks a file** (ADR-010). Every other check (data freshness, concentration, QA, strategy) labels the output in the brief.
- **Night plan in lock order:** every slate gets a validated fallback file before any slate is improved.
- **Fallback that depends only on the entries file:** salary-implied points when nothing else is available, with players DraftKings marks OUT or the latest official report lists as Out removed; marked "not checked for injuries" when neither file is present (RT1 rank 22).
- **The live re-solve and the legal repair** (ADR-026; the v3 text here read "stored replacements and `dfs apply` (ADR-011)", superseded 2026-10-14), so acting on news takes one command and about a minute, with a seconds-long repair behind it, and works from the launcher without Claude.
- **A desktop launcher** runs every night step without Claude (ADR-013), and the top of every brief carries an "if the engine is down" card listing the latest validated file and the fallback file for each slate, with "valid until" stamps, and how to enter news with `dfs out`.
- **Fallback ladder:** full build with QA; without QA; without any LLM step; the fallback portfolio; the last validated file for that slate, re-validated against the newest download. **[Superseded by the six-level ladder in this record's changelog: Optimizer; Baseline; Baseline without LLM steps; Floor; the last validated file re-validated against the newest download; the legal repair.]**
- **Completeness check after every upload,** with versioned file names and the user's "uploaded N of N" read-back.
- **No environment repair inside the entry window:** a failing 60-second preflight sends the night to the no-LLM path.
- **The brief lists unfilled entries next to P(washout).** **[Superseded by ADR-025: Goal 2 is the probability of a severe-drawdown night, so the brief lists unfilled entries next to Goal 2.]**

## Consequences

- **Results:** removes the largest avoidable loss in the prior engines.
- **Cost:** the fallback path is a small, well-tested part of the Floor (chunks C03, C04a and C11a), built first.
- **Workload:** `dfs uploaded` after each upload; re-downloads before each Showdown lock, before the Classic first lock, and before any swap (ADR-026, revised 2026-10-14).
