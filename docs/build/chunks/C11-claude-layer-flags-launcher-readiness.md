# C11: Claude layer, capability flags, launcher, opening-night readiness

**State:** Baseline (reaches milestone M3). **Size:** L (one session, about 2 to 3 hours, three checkpoints; the advisor's review relabeled it from M). **Depends on:** C09, C10. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Wrap the engine for the owner and for opening night: the nightly skills, the hooks that keep Claude out of upload files and DraftKings, the preflight, the capability flags with their rehearsed-on dates, the news researcher as a flagged capability that files facts and inferences, `dfs night --game-day`, the desktop launcher, and the readiness drills (determinism, launcher with Claude closed, the full replay of the Oct 16 night). After this chunk the engine is ready for Monday Oct 19's live run and for Tuesday.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.2, 4.3, 4.5, 13, and the `capabilities.toml` lines in section 1.
2. `docs/ARCHITECTURE.md` section 7 in full; section 8 "Opening night, Tuesday Oct 20", "Fallback ladder", "Process limits during a night"; section 3 component rows 21 and 22.
3. `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (with its revision note), `docs/adr/ADR-023-release-states-and-feature-flags.md`, `docs/adr/ADR-003-llm-sets-beliefs-solver-sets-lineups.md` (revision note).
4. `docs/research/R7-claude-code-runtime.md` sections 3 (subagents), 4 (hooks) and the usage notes.
5. `CLAUDE.md` and `.claude/commands/run-chunk.md` (the conventions already in the repo; the nightly skills follow the same Owns / Invokes / Does not own block).
6. `docs/review/ADJUDICATION.md` entries 12, 15 and 38 only.

## Scope

**Build:**

- `.claude/commands/night.md`, `news.md`, `swap.md`, `status.md`, `results.md` (results is a stub until C13): thin wrappers over `uv run dfs ...`, each with the Owns / Invokes / Does not own block, each reporting the four states, what is off, the file to upload and the one next action; `/news` and `/swap` tell the owner to use a fresh session.
- `.claude/agents/news-researcher.md`: `model: sonnet`; tools WebSearch, `uv run dfs research fetch <url>`, Read; reads `news_digest.json`; writes `facts_<n>.json` and `inferences_<n>.json`; search and fetch caps from settings; the allowlist (official.nba.com, nba.com news, Bluesky public API); never ESPN, RotoWire, sportsbooks, DraftKings.
- `src/nbadfs/llm/fetch.py`: `dfs research fetch <url>`: allowlist by domain from the posture; saves the page to `data/snapshots/`; returns text; reads the publish time where the page carries it.
- `src/nbadfs/llm/validate.py`: the fact and inference checks (CONTRACTS 4.2 and 4.3: schema, ranges, quote in the saved page, publish time known and within 24 hours for `acts`); a `SubagentStop` hook that runs it and returns exit 2 to send the subagent back.
- `.claude/settings.json`: hooks (`SessionStart` preflight; `PreToolUse` on Edit, Write, NotebookEdit blocking `out/uploads/`, `data/snapshots/`, `config/models/`, and `src/` during a night run; `PreToolUse` on Bash and PowerShell blocking any command mentioning `out/uploads`, `draftkings.com`, the private standings folder, or `contest-standings` unless it is `uv run dfs`; `SubagentStop` validation); permissions (allow `uv run dfs *` and WebSearch; deny WebFetch; deny Read on the private standings folder).
- `scripts/preflight.py`: account check and the `ANTHROPIC_API_KEY` warning; inbox summary; next lock; usage from the status-line file or a once-a-day prompt; power and memory; a failing preflight routes to the launcher path.
- `config/capabilities.toml` enforcement: `dfs night` refuses to enable a capability without `rehearsed_on` on a game night unless `dfs unlock` (recorded in the manifest); the brief lists what is off; `dfs rehearsed <capability> <date>` records a drill.
- `dfs night --game-day`: a capped researcher pass (at most 6 searches, 3 minutes) if the researcher is on, else nothing; a deterministic rebuild reusing every fact still current (supersession applied); fills new entries; the Tuesday 12:45 pm CT command.
- The desktop launcher: `scripts/dfs.cmd` plus a `.lnk` note; keep-awake during night runs; the same plain-language output with Claude closed.
- Readiness drills recorded in PROGRESS.md's drill log, all in saved-night mode on the Oct 16 files: the determinism test (the night twice under artificial CPU load, byte-identical files); the launcher drill with Claude closed (`dfs night`, `dfs out`, `dfs repair`); the opening-night fallback sequence on a Baseline file (`dfs out --no-run`, `dfs repair`, a dry upload to a file, `dfs uploaded`, `dfs status`); the full replay with the researcher on against the saved digest (if a fresh session and budget allow); the usage reading.
- The "if the engine is down" card at the top of every brief carries the five fallback lines verbatim: `uv run dfs out "Name" --no-run`; `uv run dfs repair --slate <slate>`; upload in the browser; `uv run dfs uploaded <file>`; `uv run dfs status`.

**Out of scope:** the QA audit (C18), the watcher (C17), the results skill body (C13), the replay command (C19).

## Contracts

- **Consumes:** `NewsDigest`, `FactRecord`, `InferenceRecord` (C06); `dfs night`, the brief (C09); the re-solve and commands (C10); `capabilities.toml` (C01).
- **Produces:** the skills, the researcher agent, `dfs research fetch`, the fact validator and hook, the preflight, the capability enforcement, `dfs night --game-day`, `dfs rehearsed`, the launcher.

## Definition of done

- Hook tests: a Write to `out/uploads/x.csv` is blocked; a Bash command mentioning `draftkings.com` is blocked; `uv run dfs repair` is allowed; a `src/` edit during a night run is blocked and `dfs unlock` lifts it with a manifest record.
- Fact validator tests: a fabricated quote is rejected; a page older than 24 hours yields `acts = False`; an unknown publish time yields `acts = False`; a valid fact passes; the `SubagentStop` hook returns 2 on an invalid file.
- Researcher dry run on the saved Oct 16 digest: at most 12 searches and 8 fetches; every fetched page saved; output files pass validation; the run's token usage recorded.
- Capability enforcement test: enabling `resolve` with no `rehearsed_on` on a game night is refused without `dfs unlock`.
- The determinism drill and the launcher drill pass and are logged with timings.
- `dfs night --game-day` on the saved Oct 16 files finishes under 10 minutes for a 3-game subset.

## What I check

Close Claude Code. Double-click the desktop launcher and run `dfs night --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"`, then `dfs out "<player>" --yes --night 2026-10-16 --as-of "2026-10-16T17:30-05:00"`, then `dfs repair --slate classic_main --night 2026-10-16 --as-of "2026-10-16T17:30-05:00"`.

Expected: each prints plain-language output and names a valid file; no Claude session was needed. Then open Claude Code in the repo and type `/status`.

Expected: a short report of each slate's four states, which capabilities are off, and the one next action.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: skills, hooks, preflight, fetch, the fact validator and hook (commit). Checkpoint 2: the researcher agent with its dry run, capability enforcement, `--game-day` (commit). Checkpoint 3: the launcher, the readiness drills logged, the fallback card (commit). If the session runs long, checkpoint 3's drills are the part to carry into a fresh session on Monday morning.

## Risks

- **The researcher cannot be rehearsed on live news before Oct 20.** It ships with `enabled = false` unless its dry run on the saved digest passes and the owner enables it for Monday evening's run, where the Floor is already uploaded; the manual commands are the rehearsed path (ADJUDICATION entry 38).
- **Usage fields are not readable on the Team seat.** The once-a-day prompt is the fallback (R7).
- **A hook blocks a legitimate engine command.** The allow rule is the `uv run dfs` prefix; test it; never widen it to arbitrary Python.
