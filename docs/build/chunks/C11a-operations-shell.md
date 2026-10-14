# C11a: The operations shell: launcher, slash commands, hooks, preflight, capability flags, drill timer, repair stage 2

**State:** Floor (completes the Floor's operations; rehearsed live on Oct 16). **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C04a. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): `dfs enable` and `dfs disable` switch capabilities (`floor` starts enabled; enabling needs `passed` or a recorded `dfs unlock`; drill mode runs any capability regardless of its flag); `dfs news` and `dfs swap` get their Floor bodies (the repair over the current news state, and the post-lock repair with the freshness check) until C10 replaces them; the drill check names the saved Oct 15 night. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): owns setting `export.tight_minutes` from the measured upload times of rehearsals 1 and 2. 2026-10-14 (ADJUDICATION-R2): created from the Floor-path half of v1's C11 so the Floor-only route is an ordinary dependency chain and the shell is rehearsed live on Friday Oct 16 (R2-1). Adds versioned capability rehearsals (R2-16), the slot-reassignment repair (R2-15), the export recovery tests and start-up sweep (R2-17), the post-lock download freshness rule (R2-14), `dfs start` (moved from C10), and the drill timer for whichever late-news path is on. The news researcher is C11b, after opening night.

## Goal, and why it sits here

Wrap the Floor for the owner and for opening night: the nightly slash commands, the hooks that keep Claude out of upload files and DraftKings, the preflight, the capability flags with versioned rehearsals, `dfs start`, `dfs night --game-day`, the desktop launcher, the repair's slot-reassignment stage, the export recovery checks, and the drill timer. It depends only on the Floor core, so it runs first on Friday and the owner rehearses the same launcher and commands live on Oct 16 that he will use on Oct 20. Whatever happens to the Baseline, after this chunk the Floor is a complete, rehearsable product.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1 (the `capabilities.toml` bullet and 1.1), 4.4, 11.3, 11.5 (the freshness rule), 11.6, 11.7, 12 (`RunManifest.capabilities`), 13.
2. `docs/adr/ADR-030-operations-v2-floor-route-lock-labels-drills-exports.md` in full.
3. `docs/ARCHITECTURE.md` section 7 "How it maps onto Claude Code" and "Guardrails"; section 8 "Opening night, Tuesday Oct 20", "Fallback ladder", "The 'if the engine is down' card", "Process limits during a night"; section 3 component row 21.
4. `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (with its revision note), `docs/adr/ADR-023-release-states-and-feature-flags.md`.
5. `docs/research/R7-claude-code-runtime.md` section 5 (hooks) and section 1 (usage limits).
6. `CLAUDE.md` and `.claude/commands/run-chunk.md` (the conventions already in the repo; the nightly commands follow the same Owns / Invokes / Does not own block).
7. `docs/review/ADJUDICATION.md` entries 15 and 38 only.

## Scope

**Build:**

- `.claude/commands/night.md`, `news.md`, `swap.md`, `status.md`, `results.md` (results is a stub until C13): thin wrappers over `uv run dfs ...`, each with the Owns / Invokes / Does not own block, each reporting the four states, what is off, the file to upload (and any tight rows) and the one next action; `/news` and `/swap` tell the owner to use a fresh session; none calls the advisor.
- `.claude/settings.json`: hooks (`SessionStart` preflight; `PreToolUse` on Edit, Write, NotebookEdit blocking `out/uploads/`, `data/snapshots/`, `config/models/`, and `src/` during the game-night freeze; `PreToolUse` on Bash and PowerShell blocking any command mentioning `out/uploads`, `draftkings.com`, the private standings folder, or `contest-standings` unless it is `uv run dfs`); permissions (allow `uv run dfs *` and WebSearch; deny WebFetch; deny Read on the private standings folder). The `SubagentStop` hook arrives with C11b.
- `scripts/preflight.py`: account check and the `ANTHROPIC_API_KEY` warning; inbox summary; next lock; usage from the status-line file or a once-a-day prompt; power and memory; a failing preflight routes to the launcher path.
- Capability enforcement (CONTRACTS section 1): `dfs rehearsed <capability>` records `rehearsed_on`, `rehearsed_commit`, `rehearsed_paths` and `drill_artifact`; status per capability is `passed`, `stale` or `never`; `dfs enable <capability>` and `dfs disable <capability>` switch the flag in `config/capabilities.toml` (`floor` starts enabled, the other seven disabled), and `dfs enable` refuses a capability whose status is not `passed` unless `dfs unlock` is recorded (in the manifest); on a game night a live run does not use an enabled capability that has since become `stale` unless `dfs unlock` is recorded; drill mode runs any built capability regardless of its flag (an unbuilt one falls back as in live mode), live mode only enabled ones; `floor` is labeled, never switched off; the brief lists what is off and what is stale.
- `dfs unlock`: lifts the game-night code freeze (60 minutes before the first lock to the last lock) and the capability gate, recorded in the manifest.
- `dfs start "<TEAM>: A, B, C, D, E"`: writes five `starter_announced` facts and `bench_announced` for the previous expected starters (CONTRACTS 4.4); in the Floor, starter facts are recorded and shown in the brief but do not change `simple_points` (they change projections from C06 on).
- `dfs night --game-day`: a release-state-aware rebuild: runs whatever `dfs night` runs for the enabled release state (the Floor until the Baseline is enabled), reusing every fact still current (supersession applied), with the latest injury state if C04b is built, filling new entries; the Tuesday 12:45 pm CT command. C11b later adds the capped researcher pass in front of it.
- Repair stage 2 (CONTRACTS 11.6): when no direct substitute is legal or a better one needs a slot move, a bipartite matching of the entry's unlocked players plus the substitute to its unlocked slots (locked cells fixed; salary and duplicate rules held); still under 10 seconds for 150 entries.
- Post-lock freshness (CONTRACTS 11.5): `dfs repair` after a slate's first lock refuses when `ledger.last_download.at` is earlier than the latest started tip, with the plain message; the helper is shared with C10's `dfs swap`.
- Floor bodies for `dfs news` and `dfs swap` (CONTRACTS section 13), until C10 replaces them: `dfs news` runs the repair over the current news state (every acting availability fact applied to the latest committed lineups); `dfs swap` runs the post-lock repair with the freshness check above. `/news` and `/swap` wrap them, so the Floor-only route has working late-news and post-lock commands.
- Export recovery (CONTRACTS 11.3): the start-up sweep that removes `.tmp` generations without a ledger record; interrupted-write tests at each boundary.
- `dfs drill news --at <minutes>` (drill mode, CONTRACTS 1.1): replays a scripted scratch on a saved night with the clock at the tip minus the given minutes, runs the late-news path that exists (the repair in the Floor; C10 adds the re-solve, which drill mode runs regardless of its flag), times it, and prints the window arithmetic using `export.tight_minutes` as the upload time, including any tight rows.
- The desktop launcher: `scripts/dfs.cmd` plus a `.lnk` note; keep-awake during night runs; the same plain-language output with Claude closed.
- The "if the engine is down" card at the top of every brief carries the five fallback lines verbatim (already in the brief-lite from C04a; verify and keep).
- Re-run C03's locked-cell tests on the real NBA post-lock fixture (`fixtures/dk/2026-10-15/post_lock_entries.csv`) and record the locked-cell format in its README.

**Out of scope:** the news researcher, `dfs research fetch`, the fact validator and its `SubagentStop` hook (C11b); the re-solve and the Baseline swap (C10); the watcher (C17); the QA audit (C18).

## Contracts

- **Consumes:** `NewsState`, `dfs out`, `dfs in`, `repair` stage 1, `dfs night --floor`, the brief-lite (C04a); `export`, `Ledger`, `Clock`, `Paths`, drill mode (C03); `capabilities.toml` (C01).
- **Produces:** the slash commands, hooks and permissions, preflight, capability enforcement with fingerprints, `dfs rehearsed`, `dfs enable`, `dfs disable`, `dfs unlock`, the Floor bodies of `dfs news` and `dfs swap`, `dfs start`, `dfs night --game-day`, repair stage 2, the freshness helper, the export sweep, `dfs drill news`, the launcher.

## Definition of done

- Hook tests: a Write to `out/uploads/x.csv` is blocked; a Bash command mentioning `draftkings.com` is blocked; `uv run dfs repair` is allowed; a `src/` edit during the game-night freeze is blocked and `dfs unlock` lifts it with a manifest record.
- Capability tests: `config/capabilities.toml` starts with `floor` enabled and the other seven disabled; `dfs rehearsed floor` records the commit and paths; a change to a file under those paths turns the status to `stale`; `dfs enable` on a `stale` or `never` capability is refused with the plain reason and succeeds after `dfs unlock` (recorded); `dfs enable` on a `passed` capability succeeds and `dfs disable` switches it off; a disabled capability is skipped in live mode and runs in drill mode (a stub capability in the test); on a game night a live run skips an enabled capability that has gone `stale` unless unlocked; `floor` stays on and is labeled `stale`.
- Floor-body tests: `dfs news` after `dfs out "<name>" --no-run` produces a repaired file with only the affected rows changed; `dfs swap` after the first lock on the saved Oct 15 night refuses a pre-lock download with the freshness message and, with a post-lock download, runs the repair.
- Repair stage 2 test: the hand-counted SG and G case (an OUT player at SG, an SG-eligible player at G, a PG-eligible replacement) is repaired by moving the G player to SG and placing the replacement at G, with the other six players unchanged; the 150-entry benchmark stays under 10 seconds.
- Freshness test: after the first lock on the saved Oct 15 night, `dfs repair` with only a pre-lock download refuses with the message; with a post-lock download it runs.
- Recovery tests: a simulated stop after the CSV write, after validation, after the manifest, and mid-ledger leaves `dfs status` naming only the last committed file, and the next start sweeps the leftovers.
- `dfs start` test: five starter facts and the bench facts are written; a restriction recorded earlier for one of the five survives.
- `dfs drill news --at 30`, `--at 10`, `--at 2` run in drill mode on the saved Oct 15 night, time the repair, print the window arithmetic, and leave every live record byte-identical.
- After rehearsal 2, `export.tight_minutes` is set to the measured 90th-percentile upload time from rehearsals 1 and 2 (rounded up to a whole minute) and recorded in PROGRESS.md.
- The launcher drill with Claude closed and the Floor determinism test (the night twice under artificial CPU load, byte-identical files) pass and are logged in PROGRESS.md's drill log.

## What I check (before, during and after rehearsal 2, Friday Oct 16)

Close Claude Code. Double-click the desktop launcher and run `dfs night --floor`, then `dfs out "<a player in your test lineup>" --yes`, then `dfs status`.

Expected: each prints plain-language output; `dfs out` names a new repaired file and the player who replaced him; no Claude session was needed. (This is your real $0.25 test entry: upload the repaired file as part of the drill, or run `dfs in "<same player>"` and ignore it.) Then open Claude Code in the repo and type `/status`.

Expected: a short report of each slate's four states, which capabilities are off or stale, the file to upload, and the one next action. During rehearsal 2, do the news steps live on the Oct 16 slate; after it, time the same path with `uv run dfs drill news --at 10 --night 2026-10-15` on the saved Oct 15 night; record both in PROGRESS.md's drill log.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1 (what Friday's rehearsal needs): the launcher, the slash commands, hooks, permissions, preflight (commit). Checkpoint 2: capability flags with fingerprints, `dfs rehearsed`, `dfs enable`, `dfs disable`, `dfs unlock`, `dfs start`, `--game-day`, the drill timer, the freshness rule, the Floor bodies of `dfs news` and `dfs swap` (commit). Checkpoint 3: repair stage 2, the export recovery tests and sweep, the NBA locked-cell re-run, the drills logged (commit; if the session runs long, this checkpoint is the part to carry into a fresh session on Saturday morning, before C05).

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates). If the session passes 50% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **A hook blocks a legitimate engine command.** The allow rule is the `uv run dfs` prefix; test it; never widen it to arbitrary Python.
- **Usage fields are not readable on the Team seat.** The once-a-day prompt is the fallback (R7).
- **Friday's rehearsal starts before checkpoint 2.** Checkpoint 1 is all the rehearsal needs; the drill timer can be run on Saturday on the saved Oct 16 files.
