# C21: Market-implied minutes from props; value-of-information digest

**State:** Optimizer. **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C06, C10, C11, C13 (the re-solve and the researcher's search caps). **Parallel with:** none.

## Goal, and why it sits here

Let the betting market tell us minutes, and spend research where it changes lineups. Bookmakers' player-prop ladders (alternate over/under lines at several thresholds) encode a distribution for each player's points; back-solving that into expected minutes gives a cheap second opinion on our depth chart. This chunk fetches ladders from The Odds API (free tier, per event, largest slates first), converts them to market-implied minutes, blends them with the model at a stated weight, and flags any player where the market and our depth chart disagree by 4 or more minutes. It also adds value-of-information ordering v2 to the news digest: a quick two-state re-solve for the top few unresolved facts that says whether the portfolio changes materially if a fact resolves, plus a late-news search reserve.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 4.5, 5 (`Rates`), 6, 11.4, 15 (`[llm]`, `[redistribution]`).
2. `docs/ARCHITECTURE.md` section 4 "Minutes and role come first", "Rates and early-season priors", "The projection graph, as implemented" (the market-anchor paragraph); section 7 "Agents, inputs and outputs" (the news digest ordering and the reserve); section 10 "Sources table" (the props row).
3. `docs/adr/ADR-016-early-season-priors.md` (with its revision note); `docs/adr/ADR-005-data-posture-and-source-layer.md` (the allowlist and credit rule).
4. `docs/review/ADJUDICATION.md` entries 21 and 31 only, and item V12 in its "Verification log".
5. `docs/research/R4-data-sources.md`: The Odds API subsection only (endpoints, markets, credit costs).
6. The C06 chunk file in `docs/build/chunks/`, "Scope" (the `anchor` signature and the lines adapter).

## Scope

**Build:**

- `ingest/props.py`: fetch per-event player prop markets from The Odds API through the posture allowlist, largest slates first, stopping at `props.daily_credit_budget` (setting, default the key's free allowance); snapshot every response; parse ladders into `PropLadder(person_key, stat, lines: [(threshold, over_price, under_price)], book, fetched_at)`. Players with fewer than `props.min_ladder_lines` (setting, default 2) lines are skipped.
- `projections/implied_minutes.py`: per ladder, remove the vig (the bookmaker's margin) by normalizing each over/under pair to sum to one (`props.vig_method`, default `multiplicative`); build the survival function (the probability the stat exceeds each threshold); integrate it across thresholds with a tail beyond the last line to get the expected stat; divide by the player's shrunk per-minute rate from C05's `Rates` for implied minutes; reconcile per team to 240 expected minutes (players without ladders keep model minutes and absorb the remainder, bounded by `redistribution.max_teammate_shift`).
- The blend inside `anchor` (C06): `minutes.q50 = w x implied + (1 - w) x model` with `w = props.blend_weight` (default 0.5 when a ladder exists, 0 otherwise); q10 and q90 shift by the same amount; `minutes_source = "blend:props"` (added to the CONTRACTS 6 enum); facts keep precedence (out stays zero; hard caps bind).
- The disagreement flag: `|implied - model| >= props.disagreement_minutes` (default 4) adds `market_minutes`, `model_minutes` and `disagreement = true` to the player's `NewsDigest` item, and the researcher is told to check flagged players first.
- Value of information v2 in `llm/digest.py`: for the top `digest.voi_top_n` (setting, default 3) unresolved facts by the existing order, run a two-state re-solve (the player out, the player in) at `digest.voi_S` (setting, default 5,000) within `digest.voi_budget_s` (setting, default 120) and add `changes_materially`: true when more than `digest.voi_material_share` (setting, default 0.10) of affected entries differ between the two states, with the entry count. The late-news reserve: `llm.reserve_searches` (setting, default 3) and `llm.reserve_fetches` (setting, default 2) are held back from `max_searches` and `max_fetches` until 60 minutes before the first lock.
- The minutes scorecard (C13) gains two rows, market-implied alone and the blend, each against the model, so C19 can propose the weight as a challenger.

**Out of scope:** ESPN or any other ladder source outside the posture; props for stats other than points, rebounds and assists; auto-tuning the weight.

## Contracts

- **Consumes:** `Rates` (C05); `ProjectionTable`, `anchor`, the lines adapter, `NewsDigest` (C06); `resolve` (C10); `ScorecardRow` (C13); the posture allowlist (C11); `config/secrets.toml` (C01).
- **Produces:** `PropLadder`, `ImpliedMinutes(person_key, stat, expected_stat, rate_per_minute, implied_minutes, reconciled_minutes, n_lines)`, the `"blend:props"` source value, the `NewsDigest` v2 fields (`market_minutes`, `model_minutes`, `disagreement`, `changes_materially`, `entries_affected`), the `[props]` and `[digest]` settings. CONTRACTS.md sections 4.5, 6 and 15 change in the same commit.

## Definition of done

- Vig removal: a pair priced at -110 and -110 normalizes to 0.5 and 0.5; a skewed pair sums to one.
- Survival integration on a hand-made three-line ladder reproduces a known expected points value; implied minutes equal that value divided by the rate; the team reconciles to 240.
- Blend: with `w = 0.5` the q50 is the midpoint; a player without a ladder is unchanged except for reconciliation; an out player stays at zero.
- Disagreement: a 4.0-minute gap flags, 3.9 does not; flagged items carry both numbers.
- VOI: on the saved Oct 16 files with a scripted questionable star, the two-state re-solve runs within budget and reports `changes_materially` with the entry count; an unexposed bench player reports false without a re-solve.
- Reserve: with `max_searches = 12` the researcher stops at 9 before the last hour and has 3 left after.
- Credits: fetch order by slate size, stopping at the budget; every response snapshotted; a missing key means `props = None` and the anchor runs unchanged.

## What I check

On an evening with the key in place:

```bash
uv run dfs night
```

Expected: the brief's news digest gains lines like "market implies 29 minutes, our depth chart says 23 (flag)" for a few players, and for the top unresolved facts a line "if X is ruled out the portfolio changes materially: yes (41 entries)". `uv run dfs status` shows the props credits used today.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the props fetch, snapshots, ladder parsing, the credit order (commit). Checkpoint 2: implied minutes, reconciliation, the blend, the flag, the scorecard rows (commit). Checkpoint 3: the two-state VOI and the reserve (commit).

## Risks

- **Free-tier credits run out mid-week.** When the budget is gone the anchor runs without props and the brief says "props: not fetched".
- **Ladders are thin early in the season.** Players with fewer than two lines are skipped; the blend applies only where a ladder exists.
- **Early-season per-minute rates mis-scale minutes.** The weight is a setting; the scorecard rows show whether the blend beats the model, and C19 adjusts it through a challenger, never on one night.
- **The two-state re-solve eats the evening.** It is capped by `digest.voi_budget_s` and runs for the top three facts only; past the cap the digest says "not computed".
