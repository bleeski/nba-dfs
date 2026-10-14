# C08: Field model and settlement

**State:** Baseline. **Size:** L (one session, about 2 to 3 hours, three checkpoints). **Depends on:** C04, C07. **Parallel with:** nothing.

## Goal, and why it sits here

Build the opponents and the money. The field model simulates each contest's opponents from a public view that never sees our private model, reads ownership and copy rates off it, and scores it in every scenario. The settlement turns scores into dollars: each of our entries' rank, the contest's payout at that rank, tie splits with copies, and from that Goal 1 (top-1% prize equity) and Goal 2 (severe-drawdown probability) exactly as the owner defined them on 2026-10-14. Selection (C09) needs both.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 3.2 (as consumed), 7 (as consumed), 8, 9, 14 (`fixtures/tiny/`), 15 (`[settle]`, `[public_view]`, `[field]`, `[goal2]`).
2. `docs/ARCHITECTURE.md` section 2 in full (the settlement, Goal 1, Goal 2, the diagnostics; skip the insurance subsection); section 5 in full.
3. `docs/adr/ADR-024-goal-1-as-top-1pct-prize-equity.md`, `docs/adr/ADR-025-goal-2-severe-drawdown-and-insurance-control.md` (Goal 2 and settlement paragraphs only), `docs/adr/ADR-008-field-model-from-a-public-view.md` (with its revision note).
4. `docs/research/R2-optimization-methods.md` section 5.2 (Haugh and Singal's opponent model and tie splitting) and `docs/research/R9-night-benchmark.md` "Field" and "Lines" subsections for the mechanics to regression-check (read its correction note first).
5. `docs/review/ADJUDICATION.md` entries 5, 6, 9 only.

## Scope

**Build:**

- `field/public_view.py`: `build_public_view(slate, lines, facts_public, dff_file)`: Daily Fantasy Fuel CSV parser (the download the owner may make in a browser; its format from `spikes/data/out/downloads/projection_pages/`) and the deterministic public formula when the file is absent or empty (salary-implied value, market-implied team share, trailing DraftKings points per minute, weights in settings); public facts applied; **a static test proves this module never imports the engine's `ProjectionTable`**.
- `field/sampler.py`: `build_field(contest_facts, slate, public_view, settings) -> FieldSample`: optimizer-like entrants (GLPK on public projections plus personal noise, near the cap), casual entrants (popularity-weighted picks above a salary floor), chalk duplicators, stale entrants (built before the latest public facts); mixture weights by contest family; sampled as users with multi-entry users sharing cores; Showdown by enumeration frequency; ownership read off the sample with the sum checks (8.0; 1.0 plus 5.0); copy rates per lineup hash (Showdown: frequency; Classic: exact matches for chalky lineups, ownership product with a correction otherwise). Three settings bundles (default, stronger, concentrated) exist from the start for later sensitivity runs.
- `field/scores.py`: `score_field(field_sample, scenario_set) -> FieldScores`: per-scenario score quantile grid of the weighted field sample, chunked over scenarios (memory under 1 GB for 30,000 scenarios and 20,000 lineups).
- `settle/settle.py`: `settle(contest, our_scores, copy_rates, field, mode)`: opponents-above binomial from `F_{c,s}`; the rank window; our entries' joint ranks (exact mode) or independent ranks (additive); copies `D ~ Poisson(N' q)`; the tie split `mean(W(r..r+D)) / (1+D)`; `prize_top1`, `prize_all`, `G1`, `G1_no_dup`, `p_top1_any`, standard errors; `facts_status` carried.
- `settle/night.py`: `night_goal2(settlements, fees_total, alpha, unfilled)`: `P(SD)`, the literal washout, winnings mean, `p_recover_fees`, `p_meaningful_prize`, `calibrated = False` until C14 flips it; the shared-field sensitivity hook (the same user sample reused across contests on a slate) computed when the setting is on.
- `dfs field --slate <key>`: prints ownership by player, the top 20 most common lineups with copy counts, and each contest's top-1% and min-cash lines by scenario quantile.

**Out of scope:** selection (C09), the insurance control (C12), the ownership shock and the field family runs (C16), standings calibration (C14).

## Contracts

- **Consumes:** `ContestFacts` (C04), `ScenarioSet` (C07), `ProjectionTable` only for *our* lineups' scores (never for the public view), the candidate solver interface from C04's Floor (`select/floor.py`'s solver wrapper) for optimizer-like entrants.
- **Produces:** `PublicView`, `FieldSample`, `FieldScores`, `Settlement`, `Goal2`, `settle`, `night_goal2`.

## Definition of done

- Tiny-contest tests from `fixtures/tiny/` match the hand-computed values exactly: 10 entries and 3 paid places; ties at a payout boundary with more tied entries than paid places; two of our entries adjacent in rank (exact differs from additive by the expected amount); a copied lineup at first place splits correctly; the infeasible-cap Showdown case is left for C09.
- Public-view tests, three directions: a public scratch raises the beneficiary's ownership; a private fact leaves it unchanged; a change to our baseline model leaves it unchanged always; the static import test passes.
- Field tests: ownership sums; Showdown copy rates sum consistently; the most-owned Classic player falls in 40% to 60% on the saved Oct 16 slate under the default bundle (adjust the bundle's casual share if not, and record it); multi-entry users share cores.
- Settlement tests: `G1` equals the exact enumeration on a 50-entry field; `G1_no_dup >= G1`; `p_top1_any` matches the binomial formula; Goal 2 at `alpha` near zero equals the literal washout.
- Mechanics regression (ADR-027): on the synthetic night, the top-1% and min-cash lines agree with the spike within Monte Carlo tolerance.
- Runtime: fields and settlement for a 12-game night with 10 contests under 4 minutes at 15,000 scenarios; recorded.

## What I check

Run on the saved Oct 16 files:

```bash
uv run dfs field --slate classic_main
```

Expected: an ownership table whose top player is between about 40% and 60%, a list of the most common lineups with their copy counts, and each contest's top-1% line in DraftKings points. The numbers should look like a real slate: stars and cheap value plays at the top, nobody above 70%.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: public view and the static test (commit). Checkpoint 2: sampler, ownership, copy rates, field scores (commit). Checkpoint 3: settlement, Goal 1, Goal 2, tiny tests, `dfs field` (commit).

## Risks

- **No Daily Fantasy Fuel file exists** (none in preseason). The formula path is the rehearsed path; the brief labels the public view "formula".
- **Memory on 12 games.** Chunk scenarios; store field scores as float16 quantile grids.
- **The settlement is slow in exact mode.** Restrict exact mode to fields under 10,000 and to our entries only; vectorize over scenarios; profile before optimizing.
- **Copy rates are guesses.** They are labeled "unfitted" on every number until C14's tolerances pass; Goal 1 is shown with and without them.
