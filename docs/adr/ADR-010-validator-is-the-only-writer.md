# ADR-010: One deterministic validator, and the exporter is the only path to an upload file

**Status:** Accepted (design), revised after red-team round 1. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): "only changed rows" is no longer a validator rule but the exporter's default, marked inline below (CONTRACTS 11.2 and 11.3). 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): file and slate integrity checks the same slate fingerprint and every matchup among the slate's games (R2-8, ADR-031); the repair's wording in the entry below is marked superseded by CONTRACTS 11.6. 2026-10-14 (ADJUDICATION entries 11 and 19): four states per slate are tracked and shown separately (file validity against the identified input snapshot and lock time; news state; model status; confirmed upload). The promise is restated: every exported file passes the validator against its identified input snapshot and lock time; platform acceptance is confirmed separately by the owner's read-back and the re-downloads required in ADR-026. The legal repair (remove a ruled-out player, insert the cheapest legal substitute by projection **[superseded wording, CONTRACTS 11.6: insert the best legal substitute by `simple_points` per dollar, moving an unlocked player between slots when that makes the repair legal]**) is a validator function and the rehearsed late-news fallback. Identity or lock uncertainty stops an edit rather than shipping it.

## Context

The brief's hardest constraint: the engine never hands the user an invalid file. Invalid uploads come from salary math, slot eligibility, wrong player IDs (Captain versus UTIL), the Classic two-game rule, the Showdown both-teams rule, locked players, and format drift (`UTIL` versus `FLEX` labels, new columns, byte-order marks, cp1252 encodings). R6 found WNBA contests inside DraftKings' NBA lobby with reused team codes. The red team found that guarding only Claude's Edit and Write tools leaves Bash and Python open, which is how the user's prior engines ended up with hand-built upload files (RT1 rank 10).

## Options considered

1. Validate inside the optimizer only.
2. Validate in the exporter, written by the same code that built lineups.
3. An independent validator that re-derives every rule from the downloaded files, an exporter that refuses anything failing, a re-read of every written file, and integrity checks that catch files made any other way.

## Decision

Option 3.

- The validator reads slot labels, slot order, eligibility (`Roster Position` split on "/"), salaries and IDs only from the most recent download for that slate; the cap and roster shape are checked against the file header.
- It enforces the R6 checklist: file and slate integrity (same slate fingerprint; no "WNBA" contest names; every matchup among the slate's games), Classic rules, Showdown rules, late-swap rules (locked cells unchanged; no inserted player from a started game; file newer than the last lock), and upload hygiene (bare integer IDs; encoding and line endings mirror the download; only changed rows **[superseded (ADJUDICATION-R2 R2-34): not a validity rule; the exporter writes only changed rows by default and every row when nothing changed or with `--all-rows`, CONTRACTS 11.3]**; at most 500 rows).
- The exporter is the only writer to `out/uploads/`; it re-reads each file, validates it again, and records its hash in the run manifest and the per-entry ledger.
- Claude Code hooks block Edit, Write, Bash and PowerShell calls that touch `out/uploads/` unless the command is `uv run dfs`.
- `/status` and the completeness check flag any upload file whose hash is not in a manifest.
- On failure, the last validated file for that slate ships and the brief says, in plain language, what failed.
- After each upload the user reads back DraftKings' "uploaded N of N".
- The locked-cell rule is settled by a $0.25 test on Oct 15 (rehearsal 1) before it is relied on.

## Consequences

- **Results:** protects every entry from being void.
- **Cost:** chunk C03, mostly tests (a passing and a failing fixture per rule).
- **Workload:** one glance at the upload count per file.
