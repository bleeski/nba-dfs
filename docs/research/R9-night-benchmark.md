# R9. One synthetic NBA night on this laptop: runtime, memory, and whether the two goals conflict

**Date:** 2026-10-13. **Status:** throwaway benchmark spike for the design session. Synthetic data only.
**Code:** `spikes/night/night_spike.py` (the pipeline) and `spikes/night/summarize_night.py` (turns raw output into the tables below).
**Raw output (all in `spikes/night/out/`):**

| Label used below | File | What it is |
|---|---|---|
| 8G-30k | `20261013-1904_night8_be1_S30000.json` | 8-game night, belief-error layer on, S = 30,000, timed, late news |
| 8G-10k | `20261013-1913_night8_be1_S10000.json` | same at S = 10,000, timed, late news |
| 8G-30k-noBE | `20261013-1917_night8_be0_S30000.json` | 8-game night, belief-error layer off |
| 8G-30k-BEx2 | `20261013-1938_night8_be1x2_S30000.json` | 8-game night, belief errors doubled (sensitivity) |
| 2G-30k | `20261013-1924_night2_be1_S30000.json` | 2-game night, belief-error layer on |
| 2G-30k-noBE | `20261013-1932_night2_be0_S30000.json` | 2-game night, belief-error layer off |
| Summary | `20261013-1945_night_summary.txt` | every table in this memo, generated from the files above |

Each JSON has a matching `.txt` console log with the same stem.

Labels: **VERIFIED** means measured here, with the file cited. **BET** means an assumption or a synthetic parameter that real slates must confirm. Every number about player outcomes, fields and edges is synthetic, so every such number is a BET about the real world even when the measurement itself is VERIFIED.

## The answer

1. **The laptop is fast enough.** A full first build of the medium night (one 8-game Classic slate, three Showdown games on it, 118 entries in 11 contests) takes **211 seconds at S = 30,000 scenarios** and **86 seconds at S = 10,000**. Peak memory is **1.66 GB** including 8 solver worker processes, well under the 3 GB cap. VERIFIED (8G-30k, 8G-10k).
2. **Late news fits the 3-minute target.** Ruling one questionable star out 30 minutes before tip, then re-simulating his game, rebuilding the affected fields, thresholds, candidates and selection, takes **103 seconds at S = 30,000** and **44 seconds at S = 10,000**. VERIFIED (8G-30k, 8G-10k).
3. **The cost lives in one step.** Computing the field's top-1% and min-cash lines in every scenario is **72% of the build** (152 of 211 seconds). Lineup solving is cheap: 6,500 MILP solves take about 10 seconds on 8 workers. VERIFIED (8G-30k).
4. **At the user's planned volume, the two goals do not conflict, because washout essentially never happens.** With 118 entries the chance of zero cashes on the night was **0 in 30,000 held-out scenarios** (below 0.01% at 95% confidence). That held with the belief-error layer on, with it off, and with it doubled. At 50 entries washout was at most 1 scenario in 30,000. VERIFIED, but BET for the real world because the synthetic lineups have a large edge over the synthetic field (point 7).
5. **Where washout does exist (about 25 entries), the hunch holds clearly.** Constrained swaps remove **65% to 94% of the washout risk** for a mean loss of **0.1% to 3.5% of top-1% odds**, depending on the night. On the 8-game night with the belief-error layer, washout fell from 0.51% to 0.063% at a 5% budget. Concentrating every contest on one narrow thesis did the opposite: it cut top-1% odds by 4% to 20% and usually raised washout. VERIFIED (8G-30k, 8G-30k-noBE, 2G-30k, 2G-30k-noBE).
6. **The per-contest guarantee leaks out of sample.** The search enforces "each contest keeps at least (1 - epsilon) of its top-1% odds" on a validation set of 15,000 scenarios. On fresh scenarios, single contests sometimes lost 8% to 14% at a 2% to 5% budget, which is more than the budget allowed. The engine needs a safety margin on that constraint. VERIFIED (8G-30k).
7. **The synthetic edge is too generous, which flatters both goals.** A single synthetic entry cashes 31% to 44% of the time against 22% of the field paid. The user's real per-entry cash rate was 13% (R8). So treat every washout number here as optimistic, and every top-1% number as inflated. BET.

## Terms used

- **Scenario:** one simulated version of the whole night, covering every player's box score and DraftKings (DK) points. **S** is the number of scenarios.
- **Goal 1 (G1):** for one contest, the probability that at least one of our entries finishes in the top 1%. **G1\*** is the best G1 we found for that contest alone.
- **Washout, P(W):** the probability that no entry cashes anywhere on the night.
- **Insurance budget (epsilon):** the most G1 we will give up in each contest to lower P(W) (S1 Part A5).
- **Selection set A, validation set V, test set B:** three independent scenario sets. A builds candidate lineups and the pure-G1 portfolio. V is where the swap search measures G1 and P(W). B is used only to report results, so the search cannot flatter them. At "S = 30,000", A and V have 15,000 scenarios each (30,000 simulated for the engine) and B has 30,000 (spike only).
- **Field:** the simulated opponents. **Optimizer-like** opponents solve a lineup problem on noisy projections. **Casual** opponents pick players in proportion to ownership.
- **Top-1% line and min-cash line:** in each scenario, the score our best entry must reach to finish in the top 1%, or to cash.
- **MILP (mixed-integer linear program):** the lineup-building optimization. **GLPK** is the free solver used. The **Hall formulation** uses one yes/no variable per player plus position rows, and was about 5x faster than one variable per player and slot (R2).
- **Bitset:** a packed yes/no record of which scenarios a lineup clears a line in. 30,000 scenarios fit in 3.75 KB per lineup.
- **Greedy:** pick entries one at a time, each time adding the lineup that covers the most new top-1% scenarios.
- **Swap search:** start from the greedy portfolio, then repeatedly make the single lineup swap, in any contest, that most lowers washout on V while every contest keeps G1 at least (1 - epsilon) x G1\* on V. Stop when no swap helps.
- **Belief-error layer:** per-scenario shocks that represent our projections being wrong (sizes below).
- **Ownership shock:** a per-scenario change in which players the field actually played. It is shared by every contest on the same slate, so their lines move together.
- **Standard error (SE):** the Monte Carlo uncertainty of a number. **Paired SE** is the uncertainty of a difference between two portfolios scored on the same scenarios, which is much smaller.
- **Rule of three:** if an event happened 0 times in n trials, its probability is below 3/n at 95% confidence.

## Setup

**The night (BET, synthetic).**
- 8 games, 16 teams, 13 rostered players each (208 players). About 10 are rotation players and 3 are deep bench.
- Positions use DK eligibility, including dual positions.
- Salaries run $3,000 to $11,500 Classic and $1,000 to $16,000 Showdown, priced from projection plus noise.
- Each game has a spread and a total.
- Four starters (two on the 2-game night) are questionable at a 50% chance of playing, each with a named beneficiary. The first is a star in game 0, which is also a Showdown game.
- The 2-game night uses the same generator with 2 games and 52 players.

**Contests.**
- Classic: single-entry with N = 150; single-entry with N = 2,000; 3-max (N = 500, 3 entries); 20-max (N = 3,000, 20 entries); 150-max (N = 8,000, 60 entries).
- Each Showdown game: single-entry (N = 50) and 20-max (N = 1,200, 10 entries).
- 22% of each field is paid. Top-1% places k = max(1, floor(0.01 N)), as in S1.
- The total is **118 entries in 11 contests**, not the "about 106" in the brief. The 2-game night has 107 entries in 9 contests.

**Simulator (R3 section 4, simplified).**
- **Game level.** Per game and scenario: a pace factor, a scoring-environment factor, a margin drawn around the spread (SD 12), and overtime (more likely when close).
- **Team scoring.** Team points follow from total and margin. Players then split their team's made threes, twos, free throws, rebounds and assists by a Dirichlet-multinomial draw: shares are random but sum to the team total. That zero-sum split is what produces the slight negative correlation between teammates.
- **Minutes.** Minutes get noise, early exits and a blowout trim, and are reconciled to 240 (plus 25 per overtime).
- **Questionable players.** When one is out, half his minutes go to the beneficiary and half to same-position teammates, with a usage boost.
- **Player factor.** A gamma "big night" multiplier per player is shared across all of that player's stats.
- **Scoring.** DK scoring is exact, including +1.5 for a double-double and +3 more for a triple-double. Captain = 1.5x.
- **Not modeled.** A first version drew player counts independently. It gave a game-margin SD of 27 points instead of about 12, so I replaced it with the zero-sum split. That earlier version produced no cited numbers.

**Belief-error layer (BET sizes, the design lead's example values).**
- Per scenario, each team's DK points get a lognormal multiplier with SD 0.08.
- Each player's DK points get a lognormal multiplier with SD 0.12 (starters) or 0.18 (bench).
- One ownership shock per slate per scenario: every field lineup's weight is multiplied by exp(sum of its players' shocks), shock SD 0.25. This moves all contests on that slate together.
- All multipliers keep the mean unchanged.
- A slate-wide scoring shift was left out on purpose. Multiplying every lineup by the same factor cannot change any rank, so it cannot change G1 or P(W).

**Field (R3 section 7, simplified).**
- **Classic.** 2,000 optimizer-like lineups from GLPK on projections with 15% noise, plus 20,000 casual lineups from an ownership-weighted slot sampler with a $48,000 salary floor (12.5% of draws accepted).
- **Showdown.** All legal lineups enumerated: about 1.35 million per game in 0.2 seconds. 50,000 casual lineups are drawn in proportion to the product of player ownership weights, with a $46,000 floor (BET). 2,000 optimizer-like lineups are the best lineup under noisy projections.
- **Mixture.** Each contest mixes the two kinds with its own optimizer share, 30% to 45% (BET).

**Lines and estimators.**
- Lines are computed in chunks of 512 scenarios. The field's scores are never all held in memory.
- **Quantile estimator.** The top-1% line is the median of the k-th best opponent score. Technically, it is the field score with exceedance (k - 1/3) / N'. The cash line uses the paid places m the same way.
- **Binomial estimator (S1 A2 and A3).** A stored 72-point tail of each scenario's opponent-score distribution is used to compute the probability that fewer than k (or m) opponents beat us.

**Candidates.**
- Classic: 3,200 MILP solves on single scenarios' points plus 1,300 on perturbed means with an ownership penalty. That gave about 4,490 unique lineups, all validated, 0 invalid.
- Showdown: the enumeration screened to the top 20,000 per game by mean plus 0.5, 1.5 or 2.5 standard deviations.

**Selection.**
- Greedy for G1 per contest on set A.
- Then the swap search on set V. Epsilon 0 starts from the greedy portfolio, and each larger epsilon starts from the previous result. That keeps the frontier monotone. The default 5% setting was also timed starting from the greedy portfolio.
- This replaced the first design, a weighted greedy with a lambda sweep, at the design lead's request. On the 118-entry night that design showed P(W) = 0 at every lambda, and its G1 ratio was not monotone in lambda.

**Load.** Each timed run started only after three quiet 5-second windows. System CPU before the runs was 14% to 19%, with no other busy Python process. A parallel solver benchmark by another agent had finished by then. VERIFIED (`meta.load_before` in every JSON).

## Timing

8-game night with the belief-error layer. Cells show wall seconds and, in brackets, the average number of CPU cores busy. Production steps are the ones a nightly run would execute. VERIFIED (8G-10k, 8G-30k; Summary).

| Step | S = 10,000 | S = 30,000 |
|---|---|---|
| Night setup, 6,000-scenario pilot for projections and salaries | 1.1 (1.0) | 1.1 (0.9) |
| Simulate sets A and V (one process) | 1.9 (0.9) | 7.0 (0.8) |
| Start 8 solver workers | 0.6 (3.9) | 0.6 (4.0) |
| Classic field: 2,000 MILP solves | 3.6 (6.6) | 3.8 (6.2) |
| Classic field: 20,000 casual lineups | 2.4 (1.1) | 2.4 (1.1) |
| Showdown fields: enumerate and sample 3 games | 3.1 (1.1) | 3.3 (1.1) |
| Lines on A and V: Classic, 5 contests | 19.0 (1.6) | 53.2 (1.7) |
| Lines on A and V: Showdown, 6 contests | 35.5 (1.9) | 98.9 (1.8) |
| Classic candidates: 4,500 MILP solves | 6.7 (6.6) | 6.7 (6.3) |
| Showdown candidates: screen 3 x 20,000 | 1.3 (1.1) | 1.3 (1.2) |
| Hit bitsets on A (top-1% only) | 3.9 (2.1) | 11.4 (2.1) |
| Greedy G1 portfolio, all contests | 0.2 (0.8) | 0.3 (1.0) |
| Hit bitsets on V (top-1% and cash) | 6.3 (1.6) | 19.3 (1.7) |
| Swap search at the default 5% budget | 0.4 (0.8) | 1.2 (0.9) |
| **First full build (sum of the rows above)** | **86** | **211** |
| *Spike only:* full epsilon frontier, 118 entries / 25 entries | 2.5 / 0.9 | 7.4 / 8.7 |
| *Spike only:* duplication-adjusted greedy | 1.4 | 3.9 |
| *Spike only:* test set B: simulate, lines, scoring | 1.9, 55.9, 3.2 | 6.6, 160.7, 6.6 |

Other measured points (VERIFIED):
- **Without the belief-error layer**, the S = 30,000 build is **150 s**: lines are 35 s (Classic) plus 63 s (Showdown), so the ownership shock makes lines about 1.5x slower (8G-30k-noBE).
- **The 2-game night** builds in **150 s** (2G-30k).
- **Simulating the whole night** takes 1.9 s for 10,000 scenarios and 6.7 s for 30,000 (8G-30k, `sim_timing_s_by_S`).
- **MILP speed.** GLPK on the 208-player Classic pool takes a median of 10.1 ms per field solve (95th percentile 33 ms) and 6.4 ms per candidate solve, with 0 invalid lineups in 6,500. On the 52-player 2-game pool: 1.6 ms and 0.8 ms (8G-30k, 2G-30k).
- **Cores.** The MILP steps keep 6 to 7 of 8 cores busy. The numpy steps (lines, bitsets) use 1.6 to 2.1 cores. Selection runs on one core.

**Late news.** At S = 30,000 the late-news re-run took **103 s** total. VERIFIED (8G-30k, `late_news`).

| Step | Seconds |
|---|---|
| Re-simulate game 0 on A and V | 1.0 |
| Restart workers | 0.6 |
| Rebuild Classic field | 6.2 |
| Rebuild Showdown field for game 0 | 1.1 |
| **Recompute lines for the 7 affected contests on A and V** | **73.1** |
| Drop and replace Classic candidates (1,202 dropped, 1,456 added) | 2.4 |
| Re-screen Showdown candidates | 0.5 |
| Bitsets and greedy on A | 5.7 |
| Bitsets on V | 8.6 |
| Swap search at 5% | 1.2 |

The same re-run took 44 s at S = 10,000, 76 s without the belief layer, and 90 s on the 2-game night. The beneficiary's projection moved from 26.7 to 34.5 DK points.

## Memory

VERIFIED (memory block in each JSON). Peak is this process plus all workers, sampled every 50 ms.

| Run | Peak total | Of which 8 workers |
|---|---|---|
| 8G-30k | 1,664 MB | 285 MB |
| 8G-10k | 1,182 MB | 287 MB |
| 8G-30k-noBE | 1,458 MB | 286 MB |
| 2G-30k | 1,219 MB | 281 MB |

- The largest single object is the V bitsets: 511 MB at 15,000 scenarios for 11 contests.
- Line computation uses about 300 MB of temporary arrays per chunk.
- The biggest score in any field lineup and scenario was 533 points. The doubled-error run reached 712, which overflowed the first version's 16-bit sort key. The key now adapts its resolution when a score passes 650.
- **Reproducibility.** The five main runs (8G-30k, 8G-10k, 8G-30k-noBE, 2G-30k, 2G-30k-noBE) ran before that change, and only 8G-30k-BEx2 ran after it. The change is behavior-identical below 650 points, and the highest score in the five main runs was 533. So the current script reproduces them.

## Is the simulator sane?

8G-30k, set A. VERIFIED as output; BET as a description of the NBA.

| Player | Mean DK | SD | 99th pct | Notes |
|---|---|---|---|---|
| Star (PF/C, 34.5 min) | 53.1 | 17.9 (16.0 without belief layer) | 103.7 (96.0) | Double-double 72%, triple-double 5.8% |
| Role player (starting C, 27 min) | 24.7 | 9.9 | 53.3 | |
| Beneficiary, questionable star plays | 18.5 | | 43.3 | |
| Beneficiary, questionable star sits | 34.6 | | 73.8 | |

- **Correlations.**
  - Without the belief layer: teammates -0.019, opponents +0.023.
  - With it: teammates +0.022, opponents +0.020. The team shock adds a shared component.
  - Questionable star vs beneficiary: -0.53. Overtime rate: 3.6%.
- **Game environment.** Simulated means sit within 1.4 points of every total. Over rates are 48% to 51%, and margins track the spread with SD 12.7 to 12.9.
- **Lines.**
  - Classic top-1% line: mean 338 (10th to 90th percentile 312 to 367).
  - Classic min-cash line: about 280 (261 to 301).
  - Showdown top-1% line: 241 to 251. Showdown cash line: 212 to 219.
- **Variance is a little wide.** A real star's DK SD is closer to 0.22 to 0.25 of the mean than to 0.30 to 0.34 here, so tails are conservative.

**Field realism (BET).**
- The top Classic player's implied ownership is only 22%, which is flatter than real NBA chalk.
- Showdown is concentrated: the top captain is at 22% to 39%, the most common 20-max lineup is expected 5 to 15 times in 1,200 entries, and 8% to 19% of each 20-max field sits in lineups with at least 2 expected copies.
- All 22,000 Classic field lineups were unique.

## The two estimators

These compare the pure-G1 greedy portfolio on test set B (8G-30k, 118 entries). VERIFIED.

| Contest | G1, quantile line | G1, binomial | Cash, quantile | Cash, binomial |
|---|---|---|---|---|
| 150-max, N = 8,000 (large) | 72.13% | 72.00% | 100.0% | 100.0% |
| 20-max, N = 3,000 | 42.42% | 42.41% | 99.8% | 99.8% |
| Single-entry, N = 150 (small, first place) | 2.34% | 3.02% | 43.1% | 43.0% |
| Showdown single-entry, N = 50, game 2 | 3.75% | 5.16% | 40.7% | 40.6% |

- **Large contests and cash lines:** the two estimators agree within 0.2 points.
- **First-place contests (k = 1):** the quantile line understates G1 by 7% to 38% relative, because it treats a near-miss of the best opponent as a miss.
- **Washout:** P(W) agrees closely (0.513% quantile vs 0.508% binomial at 25 entries).
- **Recommendation:** select on quantile-line bitsets, which are fast, and report G1 for small fields with the binomial.

## Washout with and without the belief-error layer

P(W) of the pure-G1 greedy portfolio on test set B (30,000 scenarios). "0" means 0 washout scenarios, so P(W) < 0.010% at 95%. Caps for 25 entries (8-game): 150-max 10, 20-max 3, 3-max 1, each Showdown 20-max 2, single-entry 1. For 50 entries: 24, 8, 1, 4. For 200 entries: 115, 20, 3, 19. VERIFIED (Summary).

| Night | 25 entries | 50 entries | 118 (2-game: 107) | 200 |
|---|---|---|---|---|
| 8-game, belief layer on | 0.513% (SE 0.041) | 0.003% (1 scenario) | 0 | 0 |
| 8-game, belief layer off | 0.530% (SE 0.042) | 0 | 0 | 0 |
| 8-game, belief errors doubled | 0.493% (SE 0.040) | 0.003% (1 scenario) | 0 | 0 |
| 2-game, belief layer on | 0.997% (SE 0.057) | 0 (49 entries) | 0 | 0 |
| 2-game, belief layer off | 0.643% (SE 0.046) | 0 (49 entries) | 0 | 0 |

**Why 118 entries never washes out here.** The 60-entry 150-max cashed in every one of 30,000 scenarios, and the 20-max in 99.8%. The other contests then do not matter: single entries miss cash 56% to 65% of the time, the 3-max 30%, and the Showdown 20-max 1% to 11% (8G-30k).

**The belief-error layer at these sizes barely moves washout.** It hits our lineups and the field alike and is centered on our projections, so it widens outcomes without making us systematically wrong. The real washout risk is systematic error, where we are confidently wrong about the players we lean on. This spike does not model that. BET.

## Frontier: the 118-entry and 107-entry nights

On both nights every row is identical to the greedy portfolio. The swap search found nothing to improve, because P(W) is already 0 on V. The washout-minimizing end is the same portfolio. VERIFIED (8G-30k, 2G-30k).

Shape of the 8-game greedy portfolio (8G-30k):
- Two lineups in the 150-max share on average 1.32 of 8 players.
- Lineups in different Classic contests share 1.81 players.
- A Showdown single-entry lineup and that game's 20-max lineups share 3.53 of 6 players.
- 66 distinct lineups fill the 85 Classic entries.
- Share of entries touching each game, games 0 to 7: 68%, 51%, 53%, 42%, 55%, 48%, 50%, 39%.

## Frontier: 25-entry nights (where washout exists)

P(W) and G1 are measured on test set B. "G1 loss" is relative to the greedy portfolio's G1 in each contest, averaged over contests (mean) or taken at the worst contest (max). Epsilon 10%, 20% and unconstrained gave the same portfolio as 5%, because P(W) on V was already 0. VERIFIED (Summary; files as labeled).

**8-game night, belief layer on (8G-30k)**

| Portfolio | Swaps | P(W) on V | P(W) on B (SE) | Change vs greedy (paired SE) | Mean G1 loss | Max G1 loss (contest) |
|---|---|---|---|---|---|---|
| Greedy, pure goal 1 | 0 | 0.593% | 0.513% (0.041) | | 0% | 0% |
| epsilon 0 | 12 | 0.120% | 0.157% (0.023) | -0.357 pp (0.042) | 3.4% | 14.4% (single-entry N = 150) |
| epsilon 2% | +2 | 0.027% | 0.087% (0.017) | -0.427 pp | 3.5% | 14.4% |
| epsilon 5% (10%, 20%, unconstrained) | +2 | 0.000% | 0.063% (0.015) | -0.450 pp (0.042) | 2.7% | 10.4% (3-max) |
| One thesis: game 0 over | | | 0.583% (0.044) | +0.070 pp (0.053) | 7.8% | 18.8% |
| One thesis: games 0 to 2 all over | | | 1.417% (0.068) | +0.903 pp (0.077) | 11.7% | 28.5% |

Each contest's G1 relative to G1\* on test set B, plus or minus the paired SE. G1\* is the greedy portfolio's G1 in that contest. Contest names: C = Classic, SE = single entry, SD0 to SD2 = Showdown games 0 to 2. Entries per contest in this 25-entry profile: C_150max 10, C_20max 3, SD 20-max 2 each, all others 1. VERIFIED (8G-30k; Summary).

| Contest | Greedy | eps 0 | eps 2% | eps 5% | One thesis: games 0 to 2 over |
|---|---|---|---|---|---|
| C_SE150 | 1.000 | 0.856 ± 0.050 | 0.856 ± 0.050 | 0.974 ± 0.051 | 0.865 ± 0.050 |
| C_SE2000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.813 ± 0.033 |
| C_3max500 | 1.000 | 0.896 ± 0.034 | 0.896 ± 0.034 | 0.896 ± 0.034 | 0.811 ± 0.035 |
| C_20max3000 | 1.000 | 0.926 ± 0.019 | 0.933 ± 0.019 | 0.933 ± 0.019 | 0.715 ± 0.020 |
| C_150max8000 | 1.000 | 0.972 ± 0.006 | 0.952 ± 0.008 | 0.919 ± 0.008 | 0.752 ± 0.011 |
| SD0_SE50 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| SD0_20max1200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.985 ± 0.009 |
| SD1_SE50 | 1.000 | 1.011 ± 0.019 | 1.011 ± 0.019 | 1.011 ± 0.019 | 0.921 ± 0.024 |
| SD1_20max1200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.948 ± 0.016 |
| SD2_SE50 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| SD2_20max1200 | 1.000 | 0.966 ± 0.027 | 0.966 ± 0.027 | 0.966 ± 0.027 | 0.904 ± 0.036 |

A ratio of exactly 1.000 with no SE means the contest kept the same lineups. The 150-max at 5% (0.919 ± 0.008) shows the guarantee leak: it lost about 8% against a 5% budget, which is 4 standard errors beyond the budget. On the 118-entry and 107-entry nights, every frontier row (greedy, epsilon 0 to 20%, unconstrained) is 1.000 in every contest. The same per-contest table for the other three nights is in the Summary file.

**The other three nights**

| Night | Greedy P(W) | eps 0: P(W) / mean G1 loss | eps 2% | eps 5% (same as unconstrained unless noted) | Thesis "game 0 over" | Thesis "all Showdown games over" |
|---|---|---|---|---|---|---|
| 8-game, belief off (8G-30k-noBE) | 0.530% | 0.180% / 0.4% | 0.157% / 0.4% | 0.107% / 2.0% (max 12.8%); unconstrained 0.100% / 3.1% | 1.187% / 8.9% | 0.983% / 20.4% |
| 2-game, belief on (2G-30k) | 0.997% | 0.200% / 0.6% | 0.080% / 1.0% | 0.063% / 1.2% (max 8.1%) | 1.047% / 10.7% | 0.823% / 8.3% |
| 2-game, belief off (2G-30k-noBE) | 0.643% | 0.113% / 0.2% | 0.070% / 0.6% | 0.057% / 0.7% (max 4.7%) | 0.873% / 9.5% | 1.753% / 3.8% |

SEs on these P(W) values are 0.014 to 0.057 points. The doubled-error sensitivity (8G-30k-BEx2) went from 0.493% (greedy) to 0.157% at epsilon 0 and 0.120% at 5%, for mean G1 losses of 0.1% and 0.6%.

The pattern holds across nights. The 2-game night has more overlap (3.3 shared players between 150-max lineups) and more washout (0.64% to 1.00%, against 0.51% to 0.53% on 8 games). The search buys diversity: at epsilon 5% on 8-game, distinct Classic lineups rose from 10 to 16 of 16, and 150-max overlap fell from 2.2 to 1.5 players.

## The hypothesis verdict

The user's hunch: "the two goals conflict less than they look, since both reward covering different ways the night can unfold."

**(a) Pure goal 1 vs the washout-minimizing extreme.**
- At 118 entries both are 0 in 30,000 scenarios. There is nothing to trade.
- At 25 entries the extreme cuts washout from 0.51% to 0.063% on the 8-game night (-88%), and from 1.00% to 0.063% on the 2-game night (-94%). That costs 1.2% to 2.7% of mean G1. VERIFIED.

**(b) Price of insurance, measured from the pure-G1 portfolio.**

| Night | Budget | Washout cut | Mean G1 given up |
|---|---|---|---|
| 8-game, belief on | 2% | 83% | 3.5% |
| 8-game, belief on | 5% | 88% | 2.7% |
| 8-game, belief off | 2% | 70% | 0.4% |
| 8-game, belief off | 5% | 80% | 2.0% |
| 2-game, belief on | 2% | 92% | 1.0% |
| 2-game, belief on | 5% | 94% | 1.2% |
| 2-game, belief off | 2% | 89% | 0.6% |
| 2-game, belief off | 5% | 91% | 0.7% |

- Per 1% of mean G1 given up, that is roughly 25% to 175% relative washout reduction. The ratio is unstable because the denominators are near the noise level: the SE of a mean G1 loss is about 0.7 points, ignoring correlation between contests.
- Most of the gain comes at epsilon 0. Those swaps are tie-breaks among lineups with equal G1 on V. VERIFIED.

**(c) One thesis everywhere.**
- At 118 entries, building every contest only for "game 0 goes over" or "games 0 to 2 all go over" still never washed out, but it cut mean G1 by 6.5% and 11.1% (worst contest -19% and -27%).
- At 25 entries on the 8-game night it raised washout to 0.58% and 1.42% (vs 0.51%) while cutting G1 8% to 12%.
- On the 2-game night the effect on washout was mixed. With the belief layer, one thesis raised washout slightly (1.05% vs 1.00%) and the other lowered it (0.82%). Without it, both raised it (0.87% and 1.75% vs 0.64%). G1 always fell.
- Concentration never helped goal 1 and usually hurt goal 2. VERIFIED.

**(d) 2-game night.** Same picture with more washout to remove at 25 entries (0.64% to 1.00%). At the planned 107 entries it also had 0 washout scenarios in 30,000. So on a 2-game opening night the insurance budget matters only if the user enters thinly, around 25 entries or fewer. VERIFIED.

**Verdict: the hunch holds on this synthetic night.** Where washout exists, most of it disappears for a few percent of top-1% odds, mostly through tie-breaking and spreading theses. Betting on one thesis everywhere hurts both goals. At the planned 118-entry volume the question is moot, because washout is about 0 under this model.

**Caveat in large type: the synthetic numbers are a BET until real slates.** The synthetic edge is large, and the model has no systematic (one-directional) projection error. Real washout at 118 entries is surely above 0, and the frontier must be re-measured on real nights.

## What the numbers mean for the architecture

1. **Runtime budget.**
   - Plan about 3.5 minutes for a first full build at S = 30,000 and about 1.5 minutes at S = 10,000, on this laptop with 8 workers.
   - Plan under 2 minutes for a late-news re-run when one Classic slate and one Showdown are affected. Add about 33 seconds for each further affected Showdown game.
   - VERIFIED for synthetic sizes; BET for real pools, which are similar in size.
2. **Where to optimize, if needed.** The field lines step is 72% of the build. Options, all BET:
   - Fewer field lineups per slate.
   - Caching each slate's sorted scores across contests (already done in part).
   - Computing lines only for the slates the news touched (already done).
   - A compiled sort.
   - Solvers are not a bottleneck.
3. **Memory.** 1.7 GB at S = 30,000 leaves room on a laptop with about 6 GB free. Doubling S would push the bitsets toward 1 GB. VERIFIED / BET.
4. **The insurance control needs two fixes.**
   - The per-contest guarantee must carry a safety margin. Enforce it on validation with epsilon minus about 2 standard errors, or use a larger validation set. Out of sample, contests lost up to 14% at a 2% budget.
   - "Epsilon 0 = tie-breaks only" is not free on finite scenarios: those swaps cost 0.2% to 3.4% of mean G1 out of sample.
   - VERIFIED (8G-30k).
5. **Report G1 for first-place contests with the binomial estimator.** The quantile line understates it by up to 38% relative. VERIFIED.
6. **Duplication changes Showdown picks a lot.** This is the design lead's item 3. Scoring each scenario by the best hitting entry times E[1/(1+D)], where D is Binomial(N', q) for that lineup's field frequency q:
   - In the three Showdown 20-max contests, the duplication-adjusted greedy kept only 4, 1 and 0 of the raw greedy's 10 lineups.
   - Mean expected copies per entry fell from 0.50 / 1.13 / 2.16 to 0.09 / 0.07 / 0.10.
   - Raw G1 fell slightly: 0.329 to 0.322, 0.302 to 0.281, 0.216 to 0.181.
   - Duplication-adjusted G1 rose: 0.293 to 0.314, 0.218 to 0.273, 0.106 to 0.172.
   - Showdown single-entry picks did not change.
   - On the 8-game Classic slate duplication is negligible: 0.04% of candidates appear in the field sample.
   - On the 2-game Classic slate it is not: our 150-max lineups average 0.76 to 1.22 expected copies (up to 6 to 7), and duplication-adjusted G1 is 0.64 vs 0.72 to 0.77 raw. The engine should apply the adjustment to small Classic slates too. This spike did not optimize for it there.
   - VERIFIED (8G-30k, 2G-30k, 2G-30k-noBE). S1 A2's point stands: a flat 1/(1+D) overcharges ties deep in the top 1%, so the real share should come from the payout table. BET.
7. **Washout at real volume is a model-error question.** The learning loop should compare predicted with realized washout and per-entry cash rates from night one, as S1 A6 says. BET.

## Caveats

- **Synthetic everything.** Rates, minutes, salaries, ownership, field mix and optimizer noise are all invented and tuned only for plausibility. One night was drawn, with one seed per scenario set. BET.
- **Edge too large.**
  - Synthetic single entries cash 31% to 44% against 22% paid.
  - G1 for the N = 150 single entry is 2.3% to 3.0%, about 4x the 0.67% an average lineup gets.
  - The user's real cash rate was 13% (R8).
  - So synthetic washout is a lower bound and synthetic G1 an upper bound. BET.
- **No systematic model error.** The belief-error layer is symmetric noise that we "know about". A world where our beliefs are wrong in one direction (the truth differs from our projections, and the field's errors differ from ours) is not simulated. It is the most likely real cause of washouts and the next spike to run. BET.
- **Field too flat in Classic.** The top implied ownership is 22%, against real NBA chalk that often reaches 40% or more. That makes field lines lower and duplication rarer than real. BET.
- **Swap search is local and data-hungry.** It stops as soon as V shows zero washout, so the "unconstrained" end is limited by V's size (15,000 scenarios). Per-contest G1 on V carries 1% to 5% relative noise, which the search exploits. VERIFIED.
- **Timing and load.** Timings are for this laptop on AC power at 14% to 19% background CPU. They will vary by a few seconds between runs. VERIFIED.

## Edge uncertainty (added after review, time-boxed run)

**Question.** Does washout appear, and does the hunch survive, when our private disagreements with the public are only partly right, and the size of that "partly" is shared by every contest on the night?

**Setup.** All values BET. Raw output: `spikes/night/out/20261013-1957_edge8_be1_edge0.1mix_S30000.json`, called EDGE-30k. 8-game night, S = 30,000 (A and V 15,000 each, test set B 30,000).
- **Public view.** The previous projections. The field and DK salaries use it.
- **Engine view.** Public mean x d, with d ~ lognormal(0, 0.10) per player, drawn once for the night. The realized spread of log d was 0.091, and d ranged from 0.79 to 1.22. Our mean-based and Showdown candidates use the engine view.
- **Truth in each scenario.** Every player's points are multiplied by 1 + w x (d - 1), with w ~ Beta(2, 3) drawn once per scenario and shared by every player and contest. Outcome noise and the symmetric belief-error layer stay on top.
- **Scenario sets.** The selection, validation and test sets all draw w this way, so the engine knows its edge is uncertain.
- **Safety margin.** The swap search was run with and without it. With it, each contest must keep G1 at least (1 - epsilon + 2 x SE) x G1\*, where SE is that contest's relative Monte Carlo error on V.

**(1) Per-entry cash rate: not a modest edge.** VERIFIED (EDGE-30k).
- Our entries cash 35.8% of the time across all 118 entries, and 41.6% in single-entry contests, against 22% paid. Before this layer it was 31% to 44%.
- The reason is the construction. w lies between 0 and 1 in every scenario, so the truth always sits partway toward our view. Our private deviations are never wrong-way; they are only partly right. That adds edge instead of removing it: G1 for the N = 150 single entry rose to 3.7%.
- Reducing our disagreement would not bring the cash rate below 30%, because most of the edge comes from the weak synthetic field, not from d.
- To get a modest edge, the next run should either let w go below 0 (for example w = 1.5 x Beta(2, 3) - 0.3, so on some nights the public was right and we were wrong), or strengthen the field. BET.

**(2) Washout of the pure-G1 portfolio, test set B.** VERIFIED (EDGE-30k).

| Entries | P(W) | SE | Washout scenarios of 30,000 | P(W), binomial estimator |
|---|---|---|---|---|
| 25 | 0.753% | 0.050 | 226 | 0.701% |
| 50 | 0.003% | 0.003 | 1 | 0.004% |
| 118 | 0 (below 0.010% at 95%) | | 0 | 0 |

At 25 entries washout rose from 0.513% to 0.753%, about +47%. At 118 entries it stayed at 0: the 60-entry 150-max still cashed in every scenario. The shared w makes our failures move together, but not enough to sink 60 entries at this edge.

**(3) Frontier, test set B.** VERIFIED (EDGE-30k).

At 118 entries every row, with or without the margin, equals the greedy portfolio (P(W) = 0). At 25 entries:

| Portfolio | Swaps | P(W) on V | P(W) on B (SE) | Change vs greedy (paired SE) | Mean G1 loss | Max G1 loss |
|---|---|---|---|---|---|---|
| Greedy, pure goal 1 | 0 | 0.673% | 0.753% (0.050) | | 0% | 0% |
| eps 0, with 2-SE margin | 0 | 0.673% | 0.753% (0.050) | 0 | 0% | 0% |
| eps 2%, with margin | 6 | 0.160% | 0.243% (0.028) | -0.510 pp (0.047) | 0.2% | 2.0% (150-max, 0.980 ± 0.007) |
| eps 5%, with margin | +4 | 0.100% | 0.193% (0.025) | -0.560 pp (0.048) | 0.4% | 4.7% (150-max, 0.953 ± 0.008) |
| Unconstrained | +5 (via eps 10% and 20%) | 0.000% | 0.113% (0.019) | -0.640 pp (0.050) | 2.5% | 16.3% (150-max) |
| *No margin, for comparison:* eps 0 | 8 | 0.120% | 0.243% (0.028) | -0.510 pp | 0.4% | 2.2% |
| *No margin:* eps 5% | +5 | 0.007% | 0.130% (0.021) | -0.623 pp | 2.5% | 7.7% (3-max, 0.923 ± 0.025) |
| One thesis: games 0 to 2 all over | | | 1.113% (0.061) | +0.360 pp (0.072) | 15.3% | 36.9% |

**What the margin does.**
- It removes the guarantee leak. With it, the worst contest lost 2.0% at a 2% budget and 4.7% at 5%, both inside the budget on fresh scenarios. Without it, the worst loss at 5% was 7.7%.
- It also correctly blocks the "free" epsilon-0 tie-break swaps.
- The price is small. At 5%, washout is 0.193% with the margin against 0.130% without it, while the mean G1 loss falls from 2.5% to 0.4%.

**(4) Does the hunch hold?** Yes, and more clearly than before.
- With one-directional, night-wide edge uncertainty, a 2% budget with the safety margin removed 68% of the washout at 25 entries (0.753% to 0.243%) for a 0.2% mean loss of top-1% odds. A 5% budget removed 74% for 0.4%.
- Betting every contest on one thesis raised washout by about half (0.753% to 1.113%) and cut top-1% odds by 15%.
- At 118 entries there is still nothing to trade, because P(W) is 0 in 30,000 scenarios.

**Overconfident engine (contrast run).** VERIFIED; raw output `spikes/night/out/20261013-2004_edge8_be1_edge0.1one_S10000.json` (S = 10,000).
- Same layer, but the engine's own selection and validation scenarios assume its view is the truth (w = 1). Only the test set draws w ~ Beta(2, 3).
- **Washout as the engine sees it vs the truth:**

  | Entries | Engine believes (V) | Truth (B) |
  |---|---|---|
  | 25 | 0.22% | 1.91% (SE 0.14) |
  | 50 | 0 | 0.05% (5 of 10,000) |
  | 118 | 0 | 0 |

- At 25 entries the engine underestimates washout about 9x.
- The swap search, run on its own overconfident validation set, still halved the true washout (1.91% to 0.96%) at a 2% budget with the margin, and lost no top-1% odds on the test set.
- Lesson for the architecture: the engine's simulation must carry its own edge uncertainty (a night-wide w), or its washout numbers will be far too low. BET for size; VERIFIED for direction in this synthetic world.
- A third variant (disagreement SD 0.20) was stopped unfinished at the time box and is not reported.

**Caveat.** This layer, as specified, gives us a real edge on every night, so it cannot produce the "we were simply wrong" nights that drive real washouts. Those need w below 0 or a stronger field. The 118-entry result therefore remains an optimistic bound. BET.
