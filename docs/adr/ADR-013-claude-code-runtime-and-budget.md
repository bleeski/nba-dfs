# ADR-013: How the LLM layer maps onto Claude Code, and how the night survives without it

**Status:** Accepted (design), revised after red-team round 1; budget numbers set by Phase 1 measurement. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entries 15 and 36): the advisor is used in build sessions (when a chunk is stuck, and once before it is declared done), in design and adjudication, and in the weekly results review; never inside `/night`, `/news`, `/swap` or `/results`; one call per named decision; logged in `docs/research/advisor-log.md`; the deterministic path continues if it is unavailable. The build runs as chunked sessions started with `/run-chunk <id>`, each recording its usage in `docs/build/PROGRESS.md` (ADR-023). The QA subagent follows ADR-028. `dfs apply` is removed; `dfs news`, `dfs repair`, `dfs start` and `dfs uploaded` are added (ADR-026).

## Context

Claude Code is both the builder and the nightly LLM layer; there is no paid API. The user's plans are a Team standard seat (1.25x Pro per five-hour window, shared with work chat, governed by the employer) and a Pro plan; both have five-hour and weekly windows, with no published absolute limits (R7). The Consumer Terms that govern Pro bar "automated or non-human means" except via an API key (R7). Claude Code has no seed control. The red team found that a "no-LLM path" typed as Claude commands stops working exactly when Claude hits its limit, and that the build week draws on the same weekly window as opening night (RT1 rank 6).

## Options considered

1. **Headless scheduled runs.** A terms risk on Pro; hard to supervise near lock.
2. **The Agent SDK.** Documented for API keys only.
3. **User-initiated interactive sessions** with skills, subagents and hooks over a deterministic CLI, **plus a desktop launcher** that runs every night step without Claude.

## Decision

Option 3.

- **Skills:** `/night`, `/news`, `/swap`, `/results`, `/weekly`, `/status`, `/replay`, each a thin wrapper over a `dfs` command, each with an Owns / Invokes / Does not own block.
- **Desktop launcher:** `dfs night`, `dfs out "<name>"`, `dfs in "<name>"`, `dfs apply`, `dfs news`, `dfs swap`, `dfs status` from a desktop shortcut, with the same plain-language output; it also starts the news watcher in its own window with keep-awake. The user runs it in rehearsal (acceptance criterion 6).
- **Subagents:** `news-researcher` (opening night), `qa-adversary` (week 2), `results-analyst` (week 3), all `model: sonnet`, each with a narrow tool list and one JSON output checked by a `SubagentStop` hook.
- **Hooks:** `SessionStart` preflight (account, `ANTHROPIC_API_KEY` warning, inbox, next lock, usage read from a file a status-line script writes, or a once-a-day prompt to read `/usage` when the weekly figure is not readable); `PreToolUse` guards on Edit, Write, NotebookEdit, Bash and PowerShell for `out/uploads/`, `data/snapshots/`, `config/models/`, `draftkings.com`, the private standings folder, `contest-standings`, and `src/` during night runs (liftable with `dfs unlock`).
- **Permissions:** allow `uv run dfs *` and WebSearch; deny WebFetch (pages are fetched through `dfs research fetch`, which enforces the posture's allowlist and saves each page for the quote check); deny Read on the private standings folder outside the project.
- **Budget:** search and fetch caps in configuration; QA capped at 2 iterations on Pro-only nights; fresh sessions for `/news` and `/swap`; target at most about 50% of one Pro five-hour window per night, measured on the Monday Oct 19 build; no Claude build or design work after noon on game days once weekly usage passes 70%; build-week rule in ARCHITECTURE section 13.
- The news watcher is plain Python and never invokes Claude.

## Consequences

- **Results:** research and QA reach the build when the budget allows; files never depend on them.
- **Cost:** within the existing plans; the Team seat only after the user confirms personal use is allowed (Decision D4).
- **Workload:** one command per step; the launcher when Claude is unavailable.
