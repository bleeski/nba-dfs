# ADR-010: One deterministic validator, and it is the only path to an upload file

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

The brief's hardest constraint: the engine never hands the user an invalid file. Invalid uploads come from salary math, slot eligibility, wrong player IDs (Captain versus UTIL), the Classic two-game rule, the Showdown both-teams rule, locked players during late swap, and format drift (for example `UTIL` versus `FLEX` slot labels, new CSV columns, byte-order marks). R6 found several traps: slot labels differ by sport, WNBA contests appear in DraftKings' NBA lobby with reused team codes, standings list slots alphabetically, and Captain IDs are separate rows.

## Options considered

1. Validate inside the optimizer (constraints only). Fast, but a bug in the optimizer's own rule code passes silently.
2. Validate in the exporter, written by the same code that built lineups.
3. **An independent validator module that re-derives every rule from the downloaded files, plus an exporter that refuses to write anything that fails, plus a re-parse of the written file.**

## Decision

Option 3.

- The validator reads slot labels, slot order, eligibility (`Roster Position` split on "/"), salaries, and IDs only from the most recently downloaded DKEntries file for that slate. Nothing is hardcoded except the cap ($50,000) and the roster shape, which are themselves checked against the file header.
- It enforces the full R6 checklist: file and slate integrity (same draft group, no "WNBA" contest names, every matchup on the NBA schedule), Classic rules (8 slots, eligibility, no repeats, cap in integer dollars, at least 2 games, no disabled games), Showdown rules (one CPT row ID in the CPT slot, UTIL row IDs elsewhere, no person in both, cap using each chosen ID's salary, both teams), late-swap rules (locked cells unchanged, no inserted player from a started game, file newer than the last lock), and upload hygiene (bare integer IDs, encoding and line endings mirror the download, only changed rows, at most 500 rows).
- The exporter is the only code that writes to `out/uploads/`. After writing, it re-reads the file and validates it again from scratch.
- A Claude Code `PreToolUse` hook blocks the `Write` and `Edit` tools from touching `out/uploads/`, so the LLM cannot hand-edit an upload.
- On failure the engine ships the last validated portfolio for that slate and says, in plain language, what failed and which entries are affected.
- After each upload the user reads back DraftKings' "uploaded N of N" count; a mismatch is logged.

## Consequences

- **Results:** none directly; this protects every entry from being void.
- **Cost:** a few days of build time in Phase 1, mostly tests: every rule gets a passing and a failing fixture.
- **Workload:** one glance at the upload count per file.
- **Provisional rule:** what DraftKings accepts in a locked cell during late swap (bare ID, `Name (ID)`, or with the `(LOCKED)` suffix) is undocumented (R6 open question 2). Phase 1 writes nothing to locked cells (only changed rows, and unchanged locked IDs where a row must be included) and settles the question with a $0.25 test before relying on it.
