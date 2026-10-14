# C16: Adversarial suite, field family, edge uncertainty, Showdown audit

**State:** Optimizer (milestone M4). **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C13. **Parallel with:** C14.

## Goal, and why it sits here

Make the numbers survive deliberate attempts to fool them, and show how much they move when the opponents differ from what the model assumes. Four pieces: the adversarial test suite of tiny, countable examples from ADR-027; the field family (three settings bundles, one ownership shock per slate, and the shared-field sensitivity) reported for Goal 2; the edge-uncertainty layer, which admits in reporting that our private edge may be smaller than modeled or negative; and the Showdown screening coverage audit. It follows C13 because its results are recorded in the store.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 7, 8, 9, 10 (`CandidatePool`, `enumerate_showdown`, `screen`), 14 (`fixtures/tiny/`), 15 (`[field]`, `[select]`, `[scenarios]`).
2. `docs/ARCHITECTURE.md` section 2 "Three kinds of uncertainty in every scenario", "Goal 2: probability of a severe-drawdown night"; section 5 "Two views of the night", "Who the simulated opponents are", "Cold start, qualification and calibration (ADJUDICATION entry 6)"; section 11 "Model tests".
3. `docs/adr/ADR-027-spike-is-a-mechanics-benchmark-only.md` in full; `docs/adr/ADR-008-field-model-from-a-public-view.md` (its revision note).
4. `docs/review/ADJUDICATION.md` entries 2, 6, 23 and 25 only.
5. `docs/build/chunks/C08-field-model-and-settlement.md` "Scope" (the three bundles and the shared-field hook that already exist).

## Scope

**Build:**

- `tests/adversarial/` with fixtures under `fixtures/tiny/adversarial/`, each with hand-counted expected values, run as `pytest -m adversarial`: exchangeable entrants (our entries drawn from the same generator as the field, so expected prize per entry equals pool over field size: zero edge); a stronger field plus a shared error against our preferred players (Goal 1 falls and Goal 2 rises by the counted amounts); the same lineup and the same opponents repeated across contests (the independence product for Goal 2 is wrong by the counted amount and the shared-field number is right); ties at a payout boundary with more tied entries than paid places; two same-team scratches and a failed upload across a lock; a concentrated Showdown pool where the cap is infeasible. The last three reuse the C08, C09 and C10 fixtures and are collected here.
- `field/family.py`: in the reporting step, build the field under the three C08 bundles (default, stronger field, concentrated chalk) and settle; the brief shows Goal 2 under all three (about a minute extra).
- `field/shock.py`: one ownership shock per slate per reporting scenario, a common multiplicative shift applied to the public view's popularity before the field is scored, with spread `field.ownership_shock_sd` (setting, default 0.10; a judgment call); Goal 2 with the shock is shown beside the unshocked number.
- Shared-field sensitivity: the C08 hook (the same user sample in every contest on a slate) switched on in reporting; Goal 2 under it sits beside the conditional-independence number, labeled.
- `sim/edge.py`: the edge-uncertainty layer. The edge is our projection minus the public view per player. In reporting only, scale it by a weight drawn once per simulated night (one draw per reporting scenario, shared by every player, game and contest) from a normal distribution with `edge.weight_mean` (setting, default 0.5) and `edge.weight_sd` (setting, default 0.5), so the weight can fall below zero. Goal 1 and Goal 2 under this layer are reported beside the plain numbers; selection never sees it (a static test).
- `select/showdown_audit.py`: on each saved Showdown slate, enumerate every legal lineup, score the full set on a fresh scenario draw, and record how many of the top `audit.showdown_top_k` (setting, default 100) by marginal Goal 1 were absent from the screened shortlist (`select.showdown_keep`); the coverage rate per slate goes to DuckDB and the weekly scorecard; no lineup is promoted from the audit.
- `dfs audit showdown --slate <key>`, and the brief's sensitivity block in its own module (`brief/sensitivity.py`) so C14's labels do not collide.

**Out of scope:** fitting the bundles or the shock to standings (C19 challengers), the calibration gates (C14), any change to selection.

## Contracts

- **Consumes:** `PublicView`, `FieldSample`, `FieldScores`, `build_field`, `score_field`, `settle`, `night_goal2` (C08); `ScenarioSet` reporting (C07); `CandidatePool`, `enumerate_showdown`, `screen` (C09); the DuckDB store (C13); `fixtures/tiny/` (C01).
- **Produces:** `Goal2Sensitivity(p_sd_default, p_sd_stronger, p_sd_concentrated, p_sd_shocked, p_sd_shared_field, p_sd_edge_uncertain, g1_edge_uncertain_by_contest)`, `ShowdownAuditResult(slate_key, keep, top_k, missed, coverage_rate, seed)`, the adversarial fixture set, `dfs audit showdown`. Both models go into CONTRACTS.md section 9 in the same commit.

## Definition of done

- Every adversarial example passes against its hand-counted values, including zero edge in the exchangeable case and, in the repeated-lineup case, the independence product wrong but the shared-field number right.
- The three bundles run in the reporting step; the extra time is recorded (about a minute expected); the brief shows three Goal 2 numbers plus the shocked and shared-field numbers, each labeled.
- The edge weight is constant across players within a scenario (a test), can be negative, and a static test proves no selection or validation module imports `sim/edge.py`.
- The Showdown audit on the saved Oct 15 and Oct 16 Showdown slates prints a coverage rate and stores it; running it leaves the portfolio unchanged.
- `pytest -m adversarial` under 60 seconds; the full suite under 5 minutes.

## What I check

On the saved Oct 16 files:

```bash
uv run pytest -m adversarial
uv run dfs audit showdown --slate sd_<AWAY>-<HOME>
```

Expected: every adversarial test passes, and the audit prints something like "screened 5,000 of 41,000 legal lineups; 94 of the top 100 on fresh scenarios were kept". Then `uv run dfs night` on the same files: the brief's Goal 2 line now shows the default number with a range under "stronger field" and "concentrated chalk", a shocked number, a shared-field number, and an "if our edge is uncertain" line.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: the adversarial suite with its fixtures (commit). Checkpoint 2: the field family, the shock, the shared-field sensitivity, the edge layer, the brief block (commit). Checkpoint 3: the Showdown audit and `dfs audit showdown` (commit).

## Risks

- **A hand-counted example disagrees with the engine.** That is the point; fix the engine or the count, never the tolerance, and record which in PROGRESS.md.
- **Three extra field draws cost more than a minute on 12 games.** Run the family at a reduced reporting size (setting `field.family_S`, default 10,000) and label it.
- **The shock and edge defaults are guesses.** They are settings labeled "BET" in the brief; the scorecards give the real ownership error to replace them.
- **Full Showdown enumeration is slow for large pools.** Run it in the morning step; cap at `audit.max_lineups` (setting, default 200,000) with a note.
