# ADR-013: How the LLM layer maps onto Claude Code, and how it stays inside the budget

**Status:** Accepted (design); budget numbers set by Phase 1 measurement. **Date:** 2026-10-13.

## Context

Claude Code is both the builder and the nightly LLM layer; there is no paid API. The user's plans are a Team standard seat (1.25x Pro per five-hour window, shared with work chat) and a Pro plan (1x); no absolute limits are published (R7, VERIFIED). The Consumer Terms that govern Pro bar "automated or non-human means" except via an API key (R7, VERIFIED), so unattended scheduled Claude runs are a terms risk. Claude Code has no temperature or seed control. Hooks can block tool calls with exit code 2; subagents run in isolated contexts with their own model and tools.

## Options considered

1. **Headless scheduled runs** (`claude -p` from Task Scheduler). Hands-off, but a terms risk on Pro and hard to supervise near lock.
2. **The Agent SDK.** Documented for API keys; subscription login is unsupported.
3. **User-initiated interactive sessions** with skills, subagents, hooks and a deterministic CLI underneath.

## Decision

Option 3.

- **Skills:** `/night`, `/news`, `/swap`, `/results`, `/weekly`, `/status`, `/replay`, each with an Owns / Invokes / Does not own block (the user's library convention), each calling `uv run dfs ...` commands rather than restating rules that live in code.
- **Subagents:** `news-researcher`, `qa-adversary`, `results-analyst`, all `model: sonnet`, each with a narrow tool list, reading an input packet and writing one JSON output that a `SubagentStop` hook validates.
- **Hooks:** `SessionStart` preflight (account check; warns if `ANTHROPIC_API_KEY` is set, which would silently bill a key instead of the login); `PreToolUse` guards on `Edit,Write` (upload folder, snapshots, model configs, and `src/` during a night run, liftable with `/night unlock`); a `Bash` guard against `draftkings.com`.
- **Permissions:** allow `uv run dfs *` and the posture's web domains; deny web fetches to DraftKings.
- **Budget:** search and fetch caps per run in configuration; QA capped at 2 iterations on Pro-only nights; fresh sessions for `/news` and `/swap` because long sessions re-read the whole conversation; target at most about 50% of one Pro five-hour window per night including two late-news runs, measured on the Oct 16 dress rehearsal.
- **When Claude is unavailable or over budget,** the night continues with `--no-llm` and the brief says what was skipped.
- The news watcher is plain Python; it alerts and never invokes Claude.

## Consequences

- **Results:** research and QA reach the build when the budget allows; the files never depend on them.
- **Cost:** within the existing plans; the Team seat is overflow only after the user confirms personal use is allowed on it (Decision D4).
- **Workload:** the user types one command per step and reads plain-language summaries.
