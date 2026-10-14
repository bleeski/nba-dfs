# C11b: The news researcher: agent, allowlisted fetch, fact validator, game-day pass

**State:** Optimizer (after opening night; the capability ships off until its dry run passes). **Size:** M (one session, about 1.5 to 2 hours, three checkpoints). **Depends on:** C10, C11a. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the clause allowing a run on Monday morning Oct 19 is deleted; this chunk runs after opening night (BUILD_PLAN: no new chunks on Monday). 2026-10-14 (ADJUDICATION-R2): created from the researcher half of v1's C11 (R2-1). Moved after opening night because the researcher was always allowed to ship off (round 1 entry 38) and the owner's `dfs out`, `dfs in` and `dfs start` are the rehearsed opening-night path.

## Goal, and why it sits here

Add the LLM news researcher as a flagged capability: a subagent that reads the deterministic news digest, searches sparingly, fetches only allowlisted pages through the engine (which saves them), and files fact records and separate inference records that code validates before anything reads them. Then put a capped researcher pass in front of `dfs night --game-day`. It sits after the re-solve because the facts it files trigger the re-solve, and after the shell because it uses the shell's hooks and capability gate.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.2, 4.3, 4.5, 13 (`dfs research fetch`, `dfs night --game-day`), 15 (`[llm]`).
2. `docs/ARCHITECTURE.md` section 7 "The short version", "Agents, inputs and outputs", "Guardrails", "Logging", "The LLM budget"; section 3 component row 22.
3. `docs/adr/ADR-003-llm-sets-beliefs-solver-sets-lineups.md` (revision note), `docs/adr/ADR-005-data-posture-and-source-layer.md` ("Other details": the allowlist), `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (the Subagents and Hooks bullets).
4. `docs/research/R7-claude-code-runtime.md` section 3 (subagents).
5. `.claude/settings.json` and `.claude/commands/night.md` from C11a (the hook and command patterns to extend).
6. `docs/review/ADJUDICATION.md` entries 12 and 38 only.

## Scope

**Build:**

- `.claude/agents/news-researcher.md`: `model: sonnet`; tools WebSearch, `uv run dfs research fetch <url>`, Read; reads `news_digest.json`; writes `facts_<n>.json` and `inferences_<n>.json`; search and fetch caps from settings; the allowlist (official.nba.com, nba.com news, Bluesky public API); never ESPN, RotoWire, sportsbooks, DraftKings.
- `src/nbadfs/llm/fetch.py`: `dfs research fetch <url>`: allowlist by domain from the posture; saves the page to `data/snapshots/`; returns text; reads the publish time where the page carries it.
- `src/nbadfs/llm/validate.py`: the fact and inference checks (CONTRACTS 4.2 and 4.3: schema, ranges, quote present in the saved page, publish time known and within 24 hours for `acts`); a `SubagentStop` hook added to `.claude/settings.json` that runs it and returns exit 2 to send the subagent back.
- `dfs night --game-day`: a capped researcher pass (at most `llm.game_day_max_searches` searches, 3 minutes) in front of C11a's rebuild when the `researcher` capability is enabled and `passed`; otherwise nothing.
- The researcher dry run on the saved Oct 16 digest (drill mode), recorded with `dfs rehearsed researcher` if it passes.

**Out of scope:** the QA audit (C18), the watcher (C17), the weekly analyst (C19), the inference blend (C14 sets the gate).

## Contracts

- **Consumes:** `NewsDigest`, `FactRecord`, `InferenceRecord` (C06); the re-solve and the commands (C10); hooks, capability enforcement, `--game-day` (C11a).
- **Produces:** the researcher agent, `dfs research fetch`, the fact validator and its hook, the game-day researcher pass.

## Definition of done

- Fact validator tests: a fabricated quote is rejected; a page older than 24 hours yields `acts = False`; an unknown publish time yields `acts = False`; a valid fact passes; the `SubagentStop` hook returns 2 on an invalid file.
- Fetch tests: a non-allowlisted domain is refused; an allowlisted page is saved with its hash.
- Researcher dry run on the saved Oct 16 digest: at most 12 searches and 8 fetches; every fetched page saved; output files pass validation; the run's token usage recorded.
- Capability test: with `researcher` not `passed`, `dfs night --game-day` skips the pass and says so in the brief.

## What I check

Run, in a fresh Claude Code session:

```bash
uv run dfs night --game-day --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"
```

Expected: the brief's first line says DRILL, the researcher pass lists the facts it filed (or "researcher off: not rehearsed"), and nothing under `out/uploads/` changed.

## Size estimate and checkpoints

About 1.5 to 2 hours. Checkpoint 1: fetch, the validator and the `SubagentStop` hook (commit). Checkpoint 2: the researcher agent and its dry run (commit). Checkpoint 3: the game-day pass and the capability check (commit).

## Usage budget

About 30% of a five-hour window and 6% of a weekly window, including the dry run's subagent tokens (estimates). If the session passes 45% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The researcher cannot be rehearsed on live news before Oct 20.** It ships with `enabled = false` until its dry run passes and the owner enables it; the manual commands are the rehearsed path (round 1 entry 38).
- **Search results lead to a blocked domain.** The fetch refuses; the researcher records the gap; nothing defeats a block.
