# C15: Economic diagnostics, ramp-gate readout, hunch report

**State:** Optimizer (milestones M4 and M5). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C13, C12. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Put the money next to the goals, and decide the ramp on evidence. Both goals can improve while the bank account shrinks (ADJUDICATION entry 4), so the brief and the results page always show total fees, expected net return, the chance of recovering fees, the severe-loss probability, the chance of a prize worth at least 10x its fee, and the fraction of entries cashing, with volume changes reported separately from skill changes. The same chunk builds the Nov 3 readout, which computes the volume-ramp gate of Decision D9 from the scorecards and the flashback, and the hunch report, which scores the three insurance variants on real fields and gives a verdict after 20 nights or says "undecided". It needs C13's store and C12's variants, which is why it follows both.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 9, 10 (`NightPortfolio`), 11.1 (`Ledger.states`), 12, 15 (`[goal2]`).
2. `docs/ARCHITECTURE.md` section 2 "Economic diagnostics beside the goals (ADJUDICATION entry 4)", "How the goals trade off, and the hunch test"; section 9 "What gets measured" (the flashback paragraph and the readouts), "Guardrails against chasing variance (ADJUDICATION entry 13)"; section 14 "Decisions for you" (D9 only).
3. `docs/adr/ADR-015-learning-and-model-adoption.md` (the revision note and Decision), `docs/adr/ADR-025-goal-2-severe-drawdown-and-insurance-control.md` (the Wording and hunch-test bullets).
4. `docs/review/ADJUDICATION.md` entries 4 and 13 only.
5. `docs/build/chunks/C13-results-scorecards-flashback.md` "Contracts" (the store and flashback rows this chunk reads).

## Scope

**Build:**

- `settle/diagnostics.py`: `economic_diagnostics(settlements, fees, alpha, settings) -> EconomicDiagnostics` on the reporting set: total fees `F`; expected net return `E[winnings] - F`; `p_recover_fees`; the severe-loss probability (winnings under `goal2.alpha` of fees, the same arithmetic as Goal 2 at the default 0.25, shown as a diagnostic so the two never disagree); `p_meaningful_prize` (any entry winning at least 10x its fee); quantiles of the fraction of entries cashing. Realized versions in `dfs results` use entry-history winnings. Each number carries the worst `facts_status` behind it.
- Volume separately from skill: per-dollar versions of every figure (prize equity and net return per fee dollar), and a night-over-night line that splits the change in expected net return into the part from entries and fees changing and the part from per-dollar figures changing.
- `learn/ramp_gate.py`: the Nov 3 readout per D9 over a window (default the nights since Oct 20): (1) delivery failures, which must be zero, counted from ledgers and manifests as any entry still `pending` at its lock, any latest file invalid at a lock, or any DraftKings rejection recorded at `dfs uploaded`; (2) minutes and ownership accuracy against the section 9 baselines (75% season plus 25% last five games; the previous field version, or the pure ownership sampler while no previous version exists) as the average nightly difference with a block bootstrap by night (resampling whole nights), passing when the interval excludes zero in the right direction; (3) flashback prize equity of the final portfolio against the control and the random benchmark, same test; the diagnostics shown beside them. Realized finishing percentile is shown but is not the gate. Output: pass, fail or "insufficient nights", with the night count and every interval.
- `learn/hunch.py`: from C13's flashback rows for the 0%, 20% and lowest-drawdown variants, the average nightly difference against 0% in prize equity won, winnings as a share of fees and fraction cashing, each with a block-bootstrap interval; a verdict after 20 nights, "undecided" when fewer than 20 nights exist or an interval includes zero.
- `dfs readout [--as-of <date>]`: prints the diagnostics for the latest night, the ramp gate and the hunch report; writes `runs/<run_id>/readout.md`. The brief gains the diagnostics block beside the goals; `dfs results` gains the realized block.

**Out of scope:** the challenger and adoption workflow (C19), the sensitivity range under field settings (C16), any change to what the control does (C12).

## Contracts

- **Consumes:** `Settlement`, `Goal2`, `night_goal2` (C08); `NightPortfolio`, `Brief` (C09); `Ledger`, `RunManifest` (C03); `ScorecardRow`, `FlashbackRow`, the DuckDB store (C13); `InsuranceVariants` (C12); the entry-history rows (C04).
- **Produces:** `EconomicDiagnostics(fees_total, net_return_mean, p_recover_fees, p_severe_loss, p_meaningful_prize, cashing_fraction_quantiles, per_dollar, facts_status_worst)`, `RampGateReadout(window, nights, delivery_failures, minutes, ownership, flashback_vs_control, flashback_vs_random, diagnostics, percentile_shown, verdict)`, `HunchVerdict(nights, comparisons, verdict)`; `dfs readout`; the brief block. All three go into CONTRACTS.md section 12 in the same commit.

## Definition of done

- Diagnostics on `fixtures/tiny/tiny_10_entries_3_paid.json` match hand-computed values for every figure; `p_severe_loss` equals `Goal2.p_sd` at `alpha = 0.25` on the same settlements (a test asserts equality); a prize of exactly 10x the fee counts as meaningful.
- Volume test: the same lineups entered twice double fees and expected return, leave every per-dollar figure unchanged, and the split line attributes the whole change to volume.
- Ramp gate on a synthetic 14-night fixture: a pending entry at lock counts as one failure and fails the gate; intervals come from the block bootstrap by night; "insufficient nights" below `ramp.min_nights` (setting, default 10); the percentile line is present and excluded from the verdict.
- Hunch on a synthetic 20-night fixture gives a verdict with intervals; 19 nights, or an interval including zero, gives "undecided".
- `dfs readout` runs from the store in under a minute with Claude closed.

## What I check

Any morning after `dfs results`:

```bash
uv run dfs readout
```

Expected: a diagnostics block for last night (fees, expected net return, chance of recovering fees, severe-loss probability, chance of a 10x prize, share of entries cashing), then three gate rows each marked pass, fail or insufficient nights with their intervals and the night count, then "hunch: undecided (n of 20 nights)" until twenty real nights exist. By Nov 3 the page should exist with real numbers in every row.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the diagnostics with the tiny-fixture tests and the brief block (commit). Checkpoint 2: the ramp gate with the delivery-failure count and the intervals (commit). Checkpoint 3: the hunch report and `dfs readout` (commit).

## Risks

- **Fewer than ten nights by Nov 3.** The readout prints "insufficient nights" rather than a pass; the owner does not scale on it.
- **"Delivery failure" is read differently later.** The definition is printed on the readout page itself, next to the count.
- **Baselines were not stored at decision time.** C13 stores predictions and baselines nightly; a night that lacks them is excluded from the gate and named.
- **The 10x diagnostic depends on default payout curves.** Each figure carries its facts status; the readout flags any night built on defaults.
