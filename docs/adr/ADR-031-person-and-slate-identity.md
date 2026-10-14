# ADR-031: A player's identity has no team; a slate's identity is a fingerprint of its pool

**Status:** Accepted. **Date:** 2026-10-14. **Supersedes in part:** the v1 definition of person key in `docs/build/CONTRACTS.md` (`<normalized name>|<team>`), the v1 slate key `classic_<draft group id>`, and ADR-018's suffix stripping as a matching step. **Source:** ADJUDICATION-R2 entries R2-8 and R2-9 (A-R2-I-07, A-R2-D-01, B-R2-I-08, X-R2-03); advisor consultation 3. **Changelog:** 2026-10-14 created.

## Context

- The person key joined a normalized name to a team, so a player traded in the offseason looked like a new person when tonight's salaries met last season's history, in exactly the week that history matters most. Suffix stripping can merge two different people, and a fuzzy name match in `dfs out` can pick the wrong one of two similar names on one team.
- The entries file runs its entry table and its player pool side by side on the same rows, and does not contain the draft group ID (R6 section 2.3), yet the contract assumed a pool after a blank line, required the ID, and built the slate key and the validator's "same draft group" check on it.

## Options considered

1. **Keep the team in the key and add aliases.** Every trade needs a manual alias.
2. **A permanent internal ID table maintained by hand.** Robust, but a maintenance job before Thursday.
3. **A team-free normalized name with strict matching rules, automatic disambiguation on collision, and the history source's athlete ID once matched; a slate fingerprint from the pool's IDs.**

## Decision

Option 3. The contract is `docs/build/CONTRACTS.md` (preamble, sections 1, 2.1, 3.1, 4.4, 11.2).

- `person_key` is the normalized full name with the suffix kept and no team. Matching: overrides first, then exact, then suffix-stripped only when exactly one candidate matches, else unmatched and listed. `Last, First` is flipped before normalizing. History joins use the source's athlete ID once a name has matched.
- A collision never stops the night: both players get a disambiguator, carry `identity_ambiguous`, lose their history join (salary-implied points), require a pick by number in `dfs out` and `dfs in` even with `--yes`, and appear as a warning in the brief.
- The entries file is parsed as two column regions found by their headers; no blank-row assumption; every entry kept.
- The slate is identified by `slate_fingerprint` (a hash of its sorted pool IDs), with a readable key from its first tip and game count (or the Showdown matchup). `draft_group_id` is optional and only from verified metadata.
- After a game starts, `In Progress` or `Final` in Game Info reuses the last verified tip time for that game from the archive; an unresolved lock stops an edit.

## Consequences

- **Results:** traded players keep last season's history on opening week; a name mix-up cannot silently bench the wrong star.
- **Cost:** a small identity module in C02; one fixture of tricky names.
- **Workload:** an occasional numbered prompt in `dfs out` when two names collide.
