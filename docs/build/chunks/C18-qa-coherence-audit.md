# C18: QA coherence audit

**State:** Optimizer (milestone M5; runs from week 2). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C11, C13. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Give the LLM the one job it does better than code before lock: noticing. The QA audit is a single pass by a separate subagent with no web access that reads a small fact packet and files at most 8 proposals of two kinds: a missed-news challenge with a cited, fetched source, or a lineup-coherence flag naming player pairs whose on-court roles exclude each other. Code judges both. The same chunk moves the statistical splits (back-to-back, rest, home and away) the old QA design asked the LLM for into the deterministic priors module behind an evidence bar. It depends on C11 for the agent and hook pattern and on C13 because the flashback scores the pre-QA portfolio. ADJUDICATION entry 18's Change line names this chunk (C18).

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.2 (`acts` and `evidence`), 4.5, 5 (`Rates`), 9, 10 (`select_contest`, `Portfolio`), 12 (`RunManifest.llm_usage`), 15 (`[llm]`).
2. `docs/ARCHITECTURE.md` section 7 "Agents, inputs and outputs", "The QA audit (one pass, from week 2; ADR-028)", "Guardrails", "The LLM budget"; section 4 "Rates and early-season priors".
3. `docs/adr/ADR-028-qa-as-one-pass-coherence-audit.md` in full; `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (the Subagents and Hooks bullets); `docs/adr/ADR-016-early-season-priors.md` (the Decision bullets).
4. `docs/review/ADJUDICATION.md` entry 18 only.
5. `.claude/agents/news-researcher.md` and the `SubagentStop` hook from C11 (the pattern to copy).

## Scope

**Build:**

- `llm/qa_packet.py`: `build_qa_packet(night_portfolio, news_digest, facts) -> QAPacket`: the top 15 players by portfolio exposure, the top 5 Showdown Captains, the raw news digest with its fetched sources (paths to saved pages), each contest's facts status, and nothing else.
- `.claude/agents/qa-audit.md`: `model: sonnet`, tools limited to reading the packet directory, no WebSearch or fetch; the prompt states the two proposal types, their required fields (quote and source for a challenge, pair and reason for a flag) and the 8-proposal limit; one JSON output at `runs/<run_id>/llm/qa_proposals.json`, checked against the schema by the `SubagentStop` hook; anything else is rejected.
- `llm/qa_judge.py`: `judge(proposals, packet, night_inputs, settings) -> list[QAVerdict]`. A missed-news challenge must pass the researcher's quote and publish-time checks (the quote is in the saved page; `published_at` known and within 24 hours), then materiality (it changes a rostered player's `p_active`, minutes or role) and regret: under the old beliefs no contest may lose more than `qa.regret_max` (default 0.02) of its Goal 1; an accepted challenge becomes a `FactRecord` with `source.kind = "llm"` and runs the re-solve. A lineup-coherence flag is tested by re-selecting the affected contests with the pair excluded; accepted only if neither Goal 1 nor Goal 2 worsens by more than noise on the validation set (`qa.noise_se_multiplier`, setting, default 2 paired standard errors).
- Limits in code: one iteration; `qa.max_minutes` (default 3), after which the hook ignores output; `qa.max_proposals` (default 8); skipped with a brief line when any affected slate locks within `qa.lock_guard_minutes` (default 45), and on Pro-only nights past the weekly usage threshold in `[llm]`.
- The pre-QA portfolio is saved as `runs/<run_id>/portfolio_pre_qa.json` before any accepted change; C13's flashback reads it.
- `/night` (C11) invokes the audit after the main build when `capabilities.qa_audit.enabled`; `dfs qa judge <proposals.json>` runs the judge alone; the brief gains a QA block (each proposal, its verdict, reason and citation); any accepted change can be vetoed with `dfs fact veto`.
- `history/splits.py`: back-to-back, rest-day and home-away splits per player and role from `player_box.parquet`, computed only where at least 20 games or 300 minutes exist, the effect survives shrinkage toward zero, and it holds on a held-out half of seasons; output `SplitAdjustment` rows that C05's `build_rates` applies; never a QA proposal.

**Out of scope:** pairwise leverage swaps (C09's deterministic local-improvement step), the weekly analyst (C19), any proposal type beyond the two.

## Contracts

- **Consumes:** `NightPortfolio`, `select_contest` (C09); `NewsDigest`, the `FactRecord` checks, `dfs fact veto` (C06, C11); `settle` (C08); `ScenarioSet` validation (C07); `resolve` (C10); `Rates`, `player_box.parquet` (C05); capability flags and the hook pattern (C11).
- **Produces:** `QAPacket`, `QAProposal(kind: "missed_news"|"coherence", player_or_pair, quote, source_path, published_at, reason)`, `QAVerdict(proposal_id, accepted, reason, regret_by_contest, goal_deltas)`, `SplitAdjustment(person_key, split, multiplier, games, minutes, held_out_pass)`, the agent file, `dfs qa judge`, the brief block. The four models go into CONTRACTS.md (a new section 4.7 and section 5) in the same commit.

## Definition of done

- Packet test: exactly 15 players by exposure, 5 Captains, the digest, the facts status, and nothing else (a schema test).
- Schema test: a ninth proposal, an unknown kind, or a challenge without a source path is rejected by the hook.
- Challenge judging: a quote absent from the saved page is rejected; a source older than 24 hours is rejected; a passing challenge that costs a contest 2.5% of Goal 1 under old beliefs is rejected on regret; one at 1% becomes a fact and the re-solve runs.
- Coherence flag: re-selection with the pair excluded; accepted only when both goals hold within the noise setting; the tests cover an accept and a reject.
- Time and lock guards: output after 3 minutes is ignored; a slate locking in 44 minutes skips the audit with the brief line; 46 minutes runs it.
- `portfolio_pre_qa.json` exists before any change and the flashback scores it.
- Splits: a player with 19 games gets no split; 20 games with a held-out pass gets one; the effect is shrunk; `build_rates` applies it.

## What I check

From week 2, in Claude Code on a real evening, run `/night`. Expected: the brief ends with a QA block like "QA audit: 3 proposals in 2 min 10 s; 1 challenge accepted (quote and source shown), 1 rejected on regret, 1 coherence flag rejected (goals unchanged)" or "QA audit skipped: lock within 45 minutes". Then, with Claude closed:

```bash
uv run dfs qa judge fixtures/qa/sample_proposals.json
```

Expected: a verdict per proposal with the reason; nothing under `out/uploads/` changes.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the packet, the agent file, the hook schema check (commit). Checkpoint 2: the judge with both proposal types, the limits, the brief block (commit). Checkpoint 3: the splits module (commit).

## Risks

- **The subagent fishes for statistics anyway.** Only two kinds pass the schema; everything else is rejected before judging.
- **It overruns 3 minutes.** The hook ignores late output; the night proceeds on the pre-QA portfolio.
- **Usage budget.** One short Sonnet run; skipped when the weekly figure is past the `[llm]` threshold.
- **Few splits qualify in October.** Expected; the bar is the point; the module reports how many qualify.
