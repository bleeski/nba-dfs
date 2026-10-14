# C19: Weekly analyst, adoption workflow, replay

**State:** Optimizer (milestone M5). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C11, C13, C18 (the researcher pattern, snapshots and the QA decision records). **Parallel with:** none.

## Goal, and why it sits here

Turn the scorecards into decisions without chasing variance. The weekly analyst subagent reads a week of scorecards and flashback rows and proposes challengers in plain language with a pre-registered hypothesis. The adoption workflow runs each challenger in shadow for at least two weeks, compares it with the current model on held-out nights that each challenger family may use only once, and lets the owner adopt or reject with `/weekly adopt` and `/weekly reject`, versioned and reversible, with at most 5 open decisions. The same chunk ships `dfs replay <run_id>`, which re-executes a night from snapshots and decision records with no network and no LLM and checks the output hashes, so every adoption claim and surprising night is reproducible. It needs C13's store only.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 1 (run id, the `runs/` layout), 4.1, 4.3 (the blend rule), 12 (`RunManifest`), 13 (`dfs replay`), 15.
2. `docs/ARCHITECTURE.md` section 9 "Guardrails against chasing variance (ADJUDICATION entry 13)", "How a model change gets adopted"; section 10 "Storage, versioning and snapshots"; section 7 "Agents, inputs and outputs" (the results-analyst row) and "Where the advisor fits (ADJUDICATION entry 15)".
3. `docs/adr/ADR-015-learning-and-model-adoption.md` in full; `docs/adr/ADR-014-reproducibility-and-storage.md` in full; `docs/adr/ADR-021-determinism.md`; `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (the Skills and Subagents bullets).
4. `docs/review/ADJUDICATION.md` entries 13 and 15 only.
5. `docs/build/chunks/C13-results-scorecards-flashback.md` "Contracts" and `.claude/agents/news-researcher.md` from C11 (the subagent pattern).

## Scope

**Build:**

- `learn/challengers.py`: a challenger is a versioned configuration change under `config/models/challengers/<id>.toml` with `family` (minutes, points, ownership, field, availability), `hypothesis` (which scorecard row it should improve, and by how much), `frozen_at` (a hash of the change; any edit after freezing is a new challenger) and `shadow_start`. Each night `dfs night` also produces every active challenger's predictions, stored as they stood at decision time in the DuckDB store, never touching lineups.
- `learn/adoption.py`: the paired test per ADR-015: the average nightly difference between challenger and current on the hypothesis's scorecard row, with a block bootstrap by night (whole nights resampled); eligible when shadow has run at least `learn.shadow_min_days` (default 14), the 95% interval excludes zero, and the effect holds in at least two of three subgroups (starters, bench, news-affected). Held-out nights: a ledger of which nights each family has consumed; a family's second challenger cannot reuse them. Every promotion claim prints its independent nights, news regimes, interval and repeated-testing policy.
- `dfs weekly`: the review page from the store (each layer improving or not, open challengers with their status, the open-decision queue capped at `learn.max_open_decisions`, default 5; a sixth waits). `dfs weekly adopt <id>` bumps the version in `config/models/current.toml`, records the decision with its evidence, and takes effect on the next run; `dfs weekly reject <id>` archives it; `dfs weekly rollback <id>` restores the prior version in one command. `RunManifest` records the model versions used.
- `.claude/agents/results-analyst.md`: `model: sonnet`, no web, reads a weekly export from the store; one JSON output with a plain-language summary and up to `learn.max_proposals_per_week` (setting, default 3) challenger proposals, each a configuration diff plus hypothesis; the `SubagentStop` hook checks the schema; proposals enter the queue as challengers, never as adopted changes. `/weekly`, `/weekly adopt <id>` and `/weekly reject <id>` wrap the commands with the Owns / Invokes / Does not own block. The advisor may be consulted in the weekly review per ADR-013, never inside the nightly commands.
- `learn/replay.py` and `dfs replay <run_id>`: re-run every deterministic step in the manifest from `data/snapshots/`, `data/archive/`, the seeds and the decision records (researcher, QA, owner commands); sockets disabled; no Claude call; compare every output hash with the manifest and name the first differing step.

**Out of scope:** the QA audit (C18), the ramp gate and hunch report (C15), fitting field shapes (challengers do it through this workflow), any automatic adoption.

## Contracts

- **Consumes:** the DuckDB store, `ScorecardRow`, `FlashbackRow` (C13); `RunManifest`, snapshots and the archive (C03, C11); decision records (C11, C18); `config/models/` and settings (C01).
- **Produces:** `Challenger(id, family, hypothesis, config_diff, frozen_at, shadow_start, status)`, `AdoptionDecision(challenger_id, decision, nights, interval, subgroups, held_out_nights, decided_at, version_before, version_after)`, `WeeklyReview`, `ReplayResult(run_id, steps, matched, first_mismatch)`, the agent file, `dfs weekly ...`, `dfs replay`, `/weekly`. The four models go into CONTRACTS.md as a new section 16 in the same commit.

## Definition of done

- Freeze test: editing a frozen challenger's file is rejected; a new id is required.
- Shadow test: a challenger with 13 shadow days is not eligible; 14 is.
- Held-out test: the second challenger in a family cannot evaluate on the first's held-out nights; the ledger shows them consumed.
- Adoption rule on a synthetic 20-night fixture: an interval excluding zero and two of three subgroups gives eligible; either condition failing gives not eligible, with the printed claim.
- Queue: a sixth open decision is held back and the page says so.
- `adopt` bumps the version and the next `RunManifest` records it; `rollback` restores the prior version and is itself recorded.
- Analyst JSON: a proposal without a configuration diff or a hypothesis is rejected by the hook.
- Replay: `dfs replay` on the saved Oct 16 night run gives byte-identical output hashes with sockets disabled; a run with researcher records replays from the records; a deliberately altered snapshot makes replay name the first differing step.

## What I check

Pick any night's run id from `runs/`:

```bash
uv run dfs replay 20261020-124500-night
```

Expected: "replayed 14 steps from snapshots; every output hash matches the manifest; no network, no Claude". Then:

```bash
uv run dfs weekly
```

Expected: one page: each layer marked improving, flat or worse with its interval; open challengers with "shadow day n of 14"; "open decisions: 0 of 5"; nothing adopted unless you typed `/weekly adopt`.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: challengers, shadow predictions, the adoption test, the held-out ledger (commit). Checkpoint 2: `dfs weekly` with adopt, reject and rollback, the analyst agent, `/weekly` (commit). Checkpoint 3: `dfs replay` with the hash check (commit).

## Risks

- **Replay hashes drift.** Thread counts and float order are pinned per ADR-021; if a step still differs, replay names it and PROGRESS.md records it.
- **No challenger qualifies by Nov 3.** Expected; the workflow exists and nothing is adopted on noise.
- **Vague proposals from the analyst.** The schema demands a configuration diff and a measurable hypothesis; anything else is dropped.
- **Held-out nights run out.** Families are coarse by design; the ledger shows what each has consumed so the owner sees it coming.
