# R3: NBA player projection, minutes, usage, correlation, ownership, and field modeling

Author: research subagent R3 (design-only session). Date: Tuesday Oct 13, 2026. Go-live: Tuesday Oct 20, 2026.
Spike output cited below: `spikes/modeling/out/20261013-1644_sim_shape_and_mc_error.txt` (script `spikes/modeling/sim_shape_and_mc_error.py`).

Evidence labels used throughout:
- **VERIFIED**: I read it in the primary source (or ran it myself) and cite the place.
- **SUPPORTED**: a credible secondary source says it (cited), or I saw only a summary of the primary source.
- **BET**: my judgment, or a number I could not find in any source. Treat as a starting value to be measured.

### Plain-English glossary (terms used before they are explained)
- **DFS, GPP, cash line**: daily fantasy sports; a GPP is a large tournament with top-heavy prizes; the cash line (min-cash) is the lowest score that wins any prize.
- **Classic, Showdown, Captain (CPT), UTIL**: DK Classic is an 8-player lineup from a multi-game slate. Showdown is a single game, 6 players: 1 Captain (1.5x points, 1.5x salary) plus 5 UTIL (flex) players.
- **Ownership, chalk, leverage**: ownership is the share of entries that roster a player; chalk is the most-owned players; leverage is being different from the field where it pays.
- **Usage (usage rate)**: the share of a team's possessions a player ends (with a shot, free throws, or a turnover) while on the floor. It averages 20% because five players share the ball.
- **WOWY (with-or-without-you), on/off**: comparing a player's stats in games or minutes when a teammate plays versus sits.
- **Shrinkage, empirical Bayes**: pulling a noisy small-sample rate toward a sensible average, by an amount set by how much data exists.
- **Stabilization point**: the sample size at which a stat is half signal and half noise.
- **Negative binomial (gamma-Poisson)**: a count distribution like Poisson but with extra game-to-game spread.
- **Dirichlet, Dirichlet-multinomial, softmax**: ways to model shares that must add up to 100% (for example ownership or usage) with uncertainty.
- **Common random numbers**: scoring every lineup and contest against the same set of simulated games, so comparisons are not distorted by luck in the draws.
- **CRPS, pinball loss, Brier score, log loss**: scores for how good a probability forecast was (lower is better). CRPS is for full distributions, pinball for single percentiles, Brier and log loss for yes-or-no events.
- **PIT (probability integral transform)**: where the real outcome fell inside the predicted distribution, from 0 to 1. A well-calibrated model produces evenly spread PIT values.
- **Logit**: a transform that stretches a 0-to-1 quantity onto an unbounded scale, so averages behave sensibly.

---

## Summary of answers

1. **Minutes are the single biggest driver, and they should be a per-simulation random draw, not a number.** Model each player's minutes as: will he play (yes or no), what role (starter or bench), then a "core" minutes distribution plus three tail events that the game simulation itself produces: early exit (injury, ejection), blowout (from the simulated score margin), and overtime. Then force each team's minutes to add up to 240 (plus 25 per overtime period) inside every simulation. No published minutes accuracy figure was found; plan on measuring it from night 1. (Mix of VERIFIED practitioner methods and BET.) *Means for results:* the engine stops treating a starter who might exit early or sit in a blowout as a "safe" floor.
2. **For usage when a teammate sits, use a "share" model with a sum-to-100% constraint and a position/role prior, then let with-or-without data move it only as fast as its sample size allows.** Raising one player's usage then automatically lowers someone else's, and a small efficiency penalty applies (published estimates: 0.6 to 1.25 points per 100 possessions lost per extra 1% usage, SUPPORTED). No published "where vacated usage goes" percentages were found. *Means for results:* injury-driven value plays, the most common NBA DFS edge, get honest upside and uncertainty instead of a guess.
3. **For per-minute rates, use per-possession rates with empirical Bayes shrinkage and per-stat recency decay, seeded on opening night from last season plus a free prior (DARKO).** DARKO's method (per-stat exponential decay, Kalman filter, per-stat aging, rookie prior from age, draft slot and height) is VERIFIED from its About page and is the best free prior found. Three-point percentage needs about 750 attempts to stabilize (SUPPORTED); most counting stats stabilize far faster. *Means for your workload:* opening night runs on priors with no manual rate entry, and the model shifts to current-season data on its own.
4. **Simulate at the stat level with shared random factors, not possession by possession.** My spike shows the direction of the effects (VERIFIED by spike): a normal (bell-curve) fantasy-point model thins the upper tail, and fixed-minutes independent draws understate spread. The sizes (for example SD 7.7 vs 13.1 at the same mean) come from parameters I assumed, so they are BET until re-measured on real box scores. Possession-level simulation is a later upgrade, not an Oct 20 need. Use 10,000 simulations for screening and 30,000 for the final portfolio, with the same random draws for every lineup and contest. *Means for build cost:* days of work instead of weeks, with nightly simulation time in seconds to minutes.
5. **NBA correlations are small.** Teammates are slightly negative to slightly positive, opponents slightly positive, and the largest shared effects are pace, overtime, and blowouts. A public open-source simulator hard-codes same-team correlations of about -0.04 to -0.13 and opponent correlations of about 0 to +0.02 (VERIFIED in code; their origin is undocumented). Let correlations emerge from shared factors and check them against measured values, rather than typing in a matrix. *Means for results:* stacking teammates is a weak lever in the NBA; the engine will not force stacks.
6. **Ownership (the share of entries that pick a player) has no published accuracy benchmark.** Start with a "field optimizer" model: many simulated opponents each optimize a noisy copy of a public projection. Learn a proper model from real contest results after 3 to 6 weeks. Ownership must obey hard sums: 800% across players in Classic, and 100% Captain plus 500% UTIL in Showdown. *Means for your workload:* from week 2 the engine needs the post-contest standings file for each contest you enter.
7. **Model the field as a mixture of opponent types**, calibrated to measurable targets: ownership, salary left over, duplicate rates, and winning and top-1% scores. Three types: optimizer-like "pros", ownership-weighted "casuals", and chalk duplicators. Haugh and Singal (Management Science 2021) is the academic anchor; their opponent model is a Dirichlet-multinomial (SUPPORTED). *Means for results:* the top-1% and cash lines are only as good as this simulated field, so it gets its own calibration checks.
8. **Estimate the top-1% line and the min-cash line inside each simulation, not as one fixed number.** A lineup's chance of a top-1% finish is the share of simulations in which its score beats that simulation's own 99th-percentile field score. The same applies to cash lines, which the zero-cash portfolio goal needs. *Means for results:* both of your goals become directly measurable numbers rather than proxies.
9. **Evaluate each layer with proper scoring rules** (CRPS, pinball loss, PIT histograms, interval coverage, Brier and log loss), comparing nights as paired blocks. Contest results alone cannot show a real improvement within one season: detecting a top-1% rate rising from 1.0% to 1.5% needs about 7,700 independent entries per arm (VERIFIED arithmetic). Scoring every field lineup in each real contest helps the engine check its ranking of lineups. Those lineups all share one slate outcome, though, so each night still counts as roughly one observation and must be compared night by night. *Means for your workload:* improvements are judged mostly on the upstream layers, which give answers in weeks rather than seasons.
10. **The LLM "role override" should be a structured, probabilistic, expiring record that is blended with the model, not a replacement value.** The engine scores every override afterward so the user gets a measured answer to "is the LLM helping?" Full schema in Section 10. *Means for your workload:* you never type numbers; you can skim a nightly override list, or ignore it.

---

## 1. Minutes and role

### Answer
Build minutes as a three-stage draw in every simulation: (a) availability, (b) role scenario, (c) minutes given role. Then reconcile to team totals. The tails (early exit, blowout, overtime) should come from the game simulation, not from fixed haircuts.

### What strong public projectors do
- **Simple blends of season and recent minutes.** A RotoGrinders lesson (Derek Farnsworth, updated Apr 2024) uses 75% season average plus 25% last-five-games average as the baseline. It names three main rotation drivers: injuries, role changes, and blowouts. It cuts projected minutes 1.5% per point of spread above 7 points (VERIFIED, [RotoGrinders](https://rotogrinders.com/fantasy/lessons/accurately-predicting-minutes-nba-dfs)). Its 240-minutes-per-team check matches the blueprint.
- **Blend of rolling minutes and depth charts.** FiveThirtyEight's 2022-23 NBA forecast reportedly weighted a rolling average of recent minutes 60% and a depth-chart projection 40% (SUPPORTED: search summary only, because the FiveThirtyEight URL now redirects to ABC News, which I observed directly).
- **DARKO** forecasts minutes per game "based on recent playing time and role" and updates after every game (VERIFIED, [darko.app/about](https://www.darko.app/about)).
- **On/off and game-log reading** is the common practitioner method for role changes. Stokastic warns that a player's average can hide a wide minutes range, giving 14 to 28 minutes depending on foul trouble for one center (VERIFIED, [Stokastic, Jul 2026](https://www.stokastic.com/articles/nba-dfs/nba-dfs-research)).

### Specific factors
| Factor | Evidence | Recommended treatment |
|---|---|---|
| Starter vs bench | Universal practice (VERIFIED in sources above) | Role is a discrete scenario with probability `p_start`; minutes distribution is conditional on role. |
| Rotation size | Coach-specific (BET) | Per-team "rotation depth" parameter from last 10 games, shrunk to the coach's prior-season habit. |
| Blowout | Farnsworth sliding scale (VERIFIED). FantasyPros (Jul 2020) found six stars averaged 1.7 to 10.0 points below season average in blowout wins of 20+ (SUPPORTED, small sample, [FantasyPros](https://www.fantasypros.com/2020/07/how-should-potential-blowout-games-influence-dfs-lineups-fantasy-basketball/amp/)). | Draw the final margin each simulation from the spread (margin SD about 12 points around the spread, SUPPORTED weakly by a [Wayne Winston blog post](https://www.goodreads.com/author_blog_posts/16483561-why-is-standard-deviation-of-nba-scores-about-point-spread-12-points)). Starters lose fourth-quarter minutes as a function of that simulation's margin. Bench players gain them. |
| Overtime | About 6.2% to 6.4% of games in three seasons around 2016 (SUPPORTED, [RotoGrinders "Banking on Overtime"](https://rotogrinders.com/articles/banking-on-overtime-1710010)). | In each simulation, OT probability rises when the simulated margin is close. Each OT adds 25 team minutes, mostly to starters. Re-measure the rate on recent seasons. |
| Foul trouble | Practitioner anecdote only (VERIFIED as anecdote, Stokastic) | Widen the core distribution for foul-prone bigs (player-specific SD, shrunk to position SD). |
| Early exit (injury, ejection) | No rate found (BET: 2% to 4% of starter games) | Mixture component: with small probability, minutes are drawn from a low range. His teammates get the leftover minutes in the same simulation. That creates the realistic negative correlation. |
| Return-from-injury restriction | Practitioner practice (BET) | A hard cap (truncation) plus wider uncertainty, not just a lower mean. Restrictions are often stated as a range, which fits the override schema in Section 10. |
| Back-to-backs, load management | NBER WP 35803 (Sep 2026): workload causally raises injury risk; "coaches rest players in response to injury risk shocks" (VERIFIED, [NBER abstract](https://www.nber.org/papers/w35803)). The 2023 Player Participation Policy limits resting more than one star per game and requires stars for national TV and in-season tournament games, with exceptions for players 35+ or with heavy career workloads (SUPPORTED, [ESPN 2023](https://www.espn.com/nba/story/_/id/38386013)). | Model back-to-backs mainly as a higher *rest probability* (availability), with a small minutes-mean cut for older stars. Use the policy as a prior: on the second night of a back-to-back, the non-national-TV game is the likelier rest game. Check whether the policy changed since 2023. |
| Injury report timing | Day-before report by 5 p.m. local; game-day report 11 a.m. to 1 p.m. local; continuous updates (SUPPORTED, [official.nba.com](https://official.nba.com/nba-injury-report-2025-26/), via search summary) | Availability probabilities must be re-estimated at each report time, and the engine re-run before lock. |

### Distribution shape
- **Recommended:** a mixture. A truncated normal "core" (mean and SD from the role model, bounded 0 to 48), plus an early-exit component, plus blowout and overtime adjustments that come from the simulated game state. (BET, illustrated by the spike.)
- In my spike, an illustrative 32-minute starter with this mixture has a minutes SD of 5.9 and a left-skewed fantasy distribution (skew -0.30). The 1st percentile falls to 10 points, while fixed minutes put it at 26. The direction is VERIFIED by the spike; the sizes are BET because the mixture inputs are assumed.
- *Means for results:* the downside tail (a starter who exits at 14 minutes) is exactly what sinks lineups. Modeling it stops the optimizer overrating "safe" high-minute players.

### How accurate are minutes projections?
- **Not found in any primary source.** I searched for published minutes RMSE (root mean squared error, the typical size of a miss with big misses penalized more) and MAE (mean absolute error) and found none for nightly NBA projections.
- BET: once starting lineups are confirmed, expect MAE of about 3.5 to 4.5 minutes and RMSE of about 5 to 6 minutes for rotation players. RMSE is inflated by early exits and surprise DNPs (did not play). Errors are much larger before news settles.
- Treat these as targets to measure in the first two weeks, broken out by role and by "news changed today" status.

### Opening night (no current-season data)
- Seed from last season's minutes in the same role, adjusted for offseason roster moves and the current depth chart, plus LLM overrides from beat-writer news.
- Preseason minutes are weak evidence. The Ringer argues preseason has little predictive power for individual players (SUPPORTED, [The Ringer 2019](https://www.theringer.com/2019/10/18/nba/nba-preseason-2019-20-regular-season)). Give preseason starting assignments some weight, but not preseason minute totals (BET).
- Shift weight toward current-season minutes fast: by games 3 to 5, current-season minutes in the current role should dominate (BET; fit the decay on past seasons' openers).
- *Means for your workload:* on opening night, role is mostly known from news rather than data. That is the night LLM overrides matter most, and the night you may want to glance at the override list.

---

## 2. Usage and minutes redistribution when a player sits

### Answer
Use a constrained **share model**. Each team's on-court "possessions used" are a fixed pool, and each player's share is his base usage times any multipliers, renormalized so the shares add to 100%. When a player sits, his share and his minutes are redistributed by a prior based on position and role similarity. That prior is updated by with-or-without-you (WOWY) evidence in proportion to how many minutes of "without" data exist. Uncertainty enters as random multipliers drawn in each simulation.

### Evidence
- **Usage is zero-sum on the floor.** League-average usage is 20% by construction, because five players share possessions (SUPPORTED, [Bruin Sports Analytics](https://www.bruinsportsanalytics.com/post/star-usage-analysis), via search summary).
- **Efficiency falls as usage rises, modestly.**
  - Dean Oliver (2005) estimated a loss of 0.6 points per 100 possessions per 1% usage.
  - Eli Witus (2008, using lineup data) estimated 1.25 points per 100 possessions per 1%.
  - Both are reported by Neil Paine ([Apr 2010](https://neilpaine.substack.com/p/optimizing-the-95-rockets)). I verified Paine's quotes, so the label is SUPPORTED for the underlying studies.
  - Later analyses dispute any cliff ([Liberty Ballers 2019](https://www.libertyballers.com/2019/1/29/18199824/is-there-an-efficiency-cliff), SUPPORTED via search summary).
- **On/off tools are the practitioner standard.** Stokastic cites a teammate's usage reaching "nearly 50%" with the star off the floor (VERIFIED as an anecdote).
- **Teammate absence raises workload.** NBER WP 35803 uses teammate absence as an instrument for a player's workload, which only works if absence moves workload materially (VERIFIED abstract; no effect size on the abstract page).
- **No published, quantified "where does vacated usage go" study was found** (searched several phrasings). DARKO publishes a "WOWY RAPM" page, but that measures impact (team point differential), not usage (VERIFIED that the page exists).

### Methods compared
| Method | Strength | Weakness | Use |
|---|---|---|---|
| WOWY, game-level (teammate's stats in games with vs without X) | Simple; captures coach behavior | Few "without" games; confounded by opponent, schedule, other absences | Evidence term, heavily shrunk |
| On/off, stint-level (lineup possession data, for example pbpstats) | Far more possessions | Confounded by which units play together (bench units, garbage time) | Better evidence for usage shares once data exists |
| Position-based redistribution | Works with zero data | Ignores coach quirks and true role | Prior on opening night |
| Bayesian hierarchical | Combines the above with honest uncertainty | More engineering | Target design (below) |

### Recommended model (BET, designed from the above)
For team *t* in one simulation, let the set of active players be *A*. Each active player *i* has base usage share `u_i` (from the rates model), simulated minutes `m_i`, and a per-simulation multiplier `k_i`. Then:

```
raw_i   = u_i * k_i * m_i
share_i = raw_i / sum_{j in A} raw_j          # possession-weighted, sums to 1
FGA_i, FTA_i, TOV_i drawn from team possessions * share_i * player shot-mix
```

When player X is out, his share does not vanish. The renormalization spreads it to teammates in proportion to `u_j * k_j * m_j`. To make it role-aware, multiply each teammate's `k_j` by a redistribution weight:

```
k_j = exp( beta_pos * sim(pos_j, pos_X) + beta_wowy_j + noise_j )
beta_wowy_j ~ Normal( observed_log_lift_j * n_without_j/(n_without_j + M_wowy), prior_sd^2 * M_wowy/(n_without_j + M_wowy) )
```

- `sim(pos_j, pos_X)` is position similarity, so a guard's absence lifts guards most.
- `n_without_j` is minutes played without X. `M_wowy` is a shrinkage constant (BET: start near 300 minutes and fit it).
- The efficiency penalty applies to shooting percentage: about 1 point per 100 possessions per 1% usage gained (BET midpoint of Oliver and Witus).
- Minutes redistribution is a separate step (Section 1 reconciliation): X's minutes go first to his listed backup, then spread by position.
- *Means for results:* the most common NBA DFS edge, a cheap player stepping into a starter's role, is captured with honest uncertainty instead of an all-or-nothing guess.
- *Means for build cost:* roughly a day of work on top of the share model, and it works on opening night with the position prior alone.

### Typical effect sizes
- Not found in primary sources.
- BET to verify on last season's box scores: when a 28%+ usage star sits, the next one or two teammates commonly gain 3 to 6 usage points, and part of the vacated share is absorbed by better efficiency and pace changes rather than fully reassigned.
- I deliberately do not cite the "60% of usage redistributed" heuristic that appears in an unreviewed document online.

---

## 3. Per-minute rates, shrinkage, and early-season priors

### Answer
- Model each counting stat as a rate per possession, then convert to per-game expectations with the simulated minutes and simulated team pace (possessions).
- Estimate rates by empirical Bayes shrinkage toward a role and position prior, with a separate recency decay for each stat.
- On opening night, seed rates from last season (adjusted for age, team change, and role change) and, if the data agent confirms access, from DARKO's free per-stat forecasts.

### Evidence and method
- **DARKO's method** (VERIFIED, [darko.app/about](https://www.darko.app/about)):
  - Weighs every past game by a decay of the form beta to the power of t, where t is days since the game, with "The value of β differs for each stat", fitted by differential evolution.
  - Combines that with a modified Kalman filter (a running estimate that updates as each game arrives), merged by a gradient-boosted tree.
  - Uses "an independent aging curve for every stat it projects".
  - Builds rookie priors from age, draft slot, and height.
  - Adjusts for rest, travel, home court, and opponent.
  - Its Fantasy Lab page says DARKO "projects every box-score stat per 100 possessions", and it converts to per-game values with projected minutes and pace (VERIFIED, [darko.app/projections](https://www.darko.app/projections)). That page showed values "as of Jul 26, 2026", so whether it refreshes before Oct 20 is for the data agent to confirm.
  - The About page states no license or terms of use (VERIFIED). See Open questions.
- **Empirical Bayes shrinkage formula.** The regressed rate is (league rate x M + successes) / (M + trials). M is the "stabilization point", where true-talent variance equals random variance; a player with M trials is regressed 50% to the mean (VERIFIED, Staude, [FanGraphs 2013](https://blogs.fangraphs.com/randomness-stabilization-regression)). For NBA, use a role or position prior instead of a league-wide one.
- **Stabilization points:**
  - Three-point percentage takes roughly 750 attempts (Blackport 2014, quoted in Daly-Grafstein and Bornn, Section 1, [arXiv 1808.04871](https://ar5iv.labs.arxiv.org/html/1808.04871); SUPPORTED). The same paper's empirical Bayes example adds about 10 league-average shots as a Beta prior and tunes it for error (VERIFIED).
  - "Some stats like blocks stabilize much faster than 3PT%" (VERIFIED quote, [BBall Index Aug 2025](https://www.bball-index.com/creating-more-predictive-stats/)). No numbers given.
  - No NBA table for rebounds, assists, steals, turnovers, or usage was found.
  - BET ordering, to be measured once by split-half reliability on three past seasons: usage, rebound rate and assist rate stabilize in a few hundred minutes; blocks fast for bigs; steals slower; shooting percentages slowest.
- **Aging.** Blocks and rebounding tend to decline with age, while assists hold up or improve (SUPPORTED, [Harvard Sports Analysis 2017](https://harvardsportsanalysis.org/2017/11/what-happens-to-nba-players-when-they-age/) and [arXiv 2402.12400](https://arxiv.org/pdf/2402.12400), via search summaries). Per-stat curves are best taken from DARKO or fitted ourselves.
- **Scorekeeper bias.** Home-arena scorekeepers vary in how generously they award assists and blocks, both DK-scored stats (VERIFIED abstract, van Bommel and Bornn, [arXiv 1602.08754](https://arxiv.org/abs/1602.08754)). An arena factor for assists and blocks, heavily shrunk, is a cheap later addition.

### Free public priors, ranked for DFS use
1. **DARKO** (free): per-stat box-score and minutes forecasts. Directly usable. Highest value. Data access to be confirmed by the data agent.
2. **Our own last-season per-100 rates** from free box scores, with aging and shrinkage. Always available. This is the fallback.
3. **LEBRON (BBall Index), EPM (Dunks and Threes)**: single-number impact metrics, partly paywalled (BET on current paywall status). They add little for fantasy points, which are box-score stats.
4. **RAPTOR**: discontinued. The FiveThirtyEight URL now redirects to ABC News (VERIFIED redirect); I assume RAPTOR is not maintained (BET).

### Recent-form weighting
- Use per-stat exponential decay fitted on two past seasons. Do not use a fixed 10-game window.
- Speed up the decay temporarily when a role change is flagged (new starter, teammate out), because the old data describes a different role (BET).
- *Means for results:* avoids chasing hot streaks in shooting, which is mostly noise, while reacting quickly to genuine role changes, which are mostly real.

### Early-season plan
- **Night 1:** prior = last season (or DARKO) rates in the new role.
- **Rookies:** draft-slot, age and height prior as DARKO does, plus college or international per-minute stats discounted heavily (BET).
- **Team changes:** move through the usage share model rather than editing raw rates.
- **Coaching changes:** pace prior shrunk toward league average (Stokastic also recommends leaning on league-average pace early, VERIFIED).
- Recompute each night. The shrinkage formula makes the transition automatic as minutes accumulate.

---

## 4. Fantasy-point distributions and simulation design

### Answer
- Simulate box-score stats with **shared random factors** at game, team and player level, using overdispersed counts (gamma-Poisson, also called negative binomial).
- Compute DK points, double-doubles and triple-doubles from each simulated stat line.
- Do not draw fantasy points from a normal distribution. Do not build a possession-level simulator for Oct 20.

### What the distribution looks like
- Given minutes, a player's DK total is a sum of many counts, so it is close to symmetric with mild right skew. Points are "very symmetric", while blocks and steals are right-skewed and spiky (VERIFIED, [RotoGrinders "NBA Stat Variance"](https://rotogrinders.com/lessons/nba-stat-variance-209254), 2012-13 data, 167 players at 25+ minutes).
- Without conditioning on minutes, the distribution has a heavy left tail from early exits and blowouts, and a right tail from overtime and big role nights.
- NBA game-to-game variation is much lower than NFL's, relative to the mean (SUPPORTED, [Footballguys](https://www.footballguys.com/article/14johnlee_DFS4Dummies_Part2)).

Spike results (VERIFIED as output, illustrative inputs for a 32-minute starting big; DK scoring; triple-double assumed to also earn the double-double bonus, which is unverified):

| Design | Mean | SD | Skew | p01 | p50 | p90 | p99 | P(double-double) | P(triple-double) |
|---|---|---|---|---|---|---|---|---|---|
| A: fixed 32 min, independent Poisson | 42.9 | 7.7 | +0.14 | 26.0 | 42.8 | 52.8 | 61.5 | 0.642 | 0.0005 |
| B: minutes mixture, Poisson given minutes | 41.4 | 11.0 | -0.30 | 10.0 | 41.8 | 54.8 | 66.0 | 0.587 | 0.0008 |
| C: B + shared game factor + overdispersion | 41.3 | 13.1 | +0.15 | 9.5 | 41.0 | 58.0 | 74.2 | 0.536 | 0.0020 |
| D: normal matched to C's mean and SD | 41.3 | 13.1 | 0 | 10.8 | 41.3 | 58.1 | 71.6 | n/a | n/a |

What this shows. The directions are VERIFIED by the spike. The sizes depend on parameters I assumed (shared game factor with coefficient of variation 0.12, stat overdispersion 0.20, 4% early-exit rate), so every magnitude below is BET until the factors are fitted to real box scores and the table is re-run:
- **Minutes uncertainty and shared factors widen the spread** (about 70% wider at the same mean in this toy, A vs C).
- **A normal distribution thins the 99th-percentile tail** (about 2.6 points lower in this toy, D vs C). Tournaments are decided in that tail, which is why the public open-source simulator I read, which uses a multivariate normal, is the wrong template (Section 5).
- **Double-double and triple-double odds move with the joint distribution** (in this toy, 0.64 to 0.54 for double-doubles and about four times higher for triple-doubles). This supports the blueprint's point 3: compute bonuses from each simulated line, never from averages.

### Simulation designs compared
| Design | Tail realism | Calibration burden | Compute | Verdict |
|---|---|---|---|---|
| Possession-level game simulation (SaberSim describes its approach as play-by-play simulation, SUPPORTED via podcast summaries) | Potentially best | Very high: shot mix, rebound chances, substitution logic, foul logic; every step can drift | Highest | Upgrade later, if ever |
| **Stat-level counts with shared latent factors** (recommended) | Good, when the factors include minutes, pace, team efficiency and per-player role | Moderate: about 10 parameter groups, each checkable against box scores | Low: seconds per 10,000 simulations for a full slate in numpy (BET) | **Build for Oct 20** |
| Fantasy points as multivariate normal with a correlation matrix (as in [chanzer0/NBA-DFS-Tools](https://github.com/chanzer0/NBA-DFS-Tools) `nba_gpp_simulator.py`, VERIFIED) | Poor: symmetric, thin upper tail, no double-double logic | Low | Lowest | Use only as a fallback |

### Recommended stat-level simulator (per simulation *s*)
1. **Game:** draw a pace factor (shared by both teams) and the final margin, centered on the spread with SD about 12. Draw overtime given a close margin.
2. **Team:** draw an offensive efficiency factor for each team. Its mean comes from the implied team total in the betting market, and its spread is fitted.
3. **Availability and minutes:** for each player, apply Section 1, including blowout trims from this simulation's margin, then reconcile minutes to the team total.
4. **Player role factor:** a gamma multiplier `g_i` with mean 1 shared across a player's stats, giving "big night" correlation. Then add stat-specific overdispersion.
5. **Usage-driven stats:** draw field-goal attempts, free-throw attempts and turnovers from team possessions times usage share (Section 2). Draw makes as binomial given attempts and shrunk percentages. Points follow from makes.
6. **Rebounds:** team rebound chances follow from simulated misses by both teams. Allocate them among active players by rebound-share weights (Dirichlet-multinomial). This produces the negative correlation between same-team bigs that practitioners observe.
7. **Assists:** a share of the team's made field goals, allocated by assist-share weights. This gives a mild positive link between a passer and team scoring without simulating every pass.
8. **Steals and blocks:** gamma-Poisson draws on opponent possessions and opponent attempts.
9. **Scoring:** apply the versioned DK scoring adapter. Captain points equal 1.5 times the same simulation's DK points.

*Means for build cost:* this is days of work rather than weeks, and every parameter can be checked against free box scores. *Means for nightly run time:* the simulation step should be a small part of the night.

### How many simulations
Monte Carlo standard error of an estimated probability p from n simulations is sqrt(p(1-p)/n) (VERIFIED arithmetic, spike Part 1):

| True p | n = 5,000 | n = 10,000 | n = 30,000 | n = 100,000 |
|---|---|---|---|---|
| 1% (single lineup top-1%) | 14% relative error | 10% | 5.7% | 3.1% |
| 2% | 9.9% | 7.0% | 4.0% | 2.2% |
| 25% (portfolio "at least one top-1%") | 2.4% | 1.7% | 1.0% | 0.5% |

Recommendations:
- Use 10,000 simulations to screen candidate lineups and 30,000 for the final portfolio and the zero-cash estimate (BET).
- Always use **common random numbers**: every lineup and every contest is scored on the same simulated slates.
- In my toy test, common random numbers cut the variance of a lineup-versus-lineup comparison by 1.6 times (VERIFIED, spike Part 1b). The gain grows with player overlap.
- Common random numbers are also what makes the cross-contest zero-cash probability computable at all.
- *Means for nightly run time:* 30,000 simulations x about 300 players is roughly 36 MB of fantasy points in float32, trivial for the laptop. The cost lives in the field and portfolio steps (Section 8).

---

## 5. Correlation in NBA DFS

### Answer
NBA correlations are small, mostly negative within a team and slightly positive across opponents. The shared drivers are pace, game total, overtime and blowouts. Represent them through the shared factors in Section 4, then validate the correlations the simulator produces against correlations measured from real box scores.

### Evidence
- "starting teammates are often fairly strongly correlated" (VERIFIED quote, Bryan Mears, [FantasyLabs Jan 2017](https://www.fantasylabs.com/?p=40730)). His explanation is that high-scoring games lift everyone.
- Same-team big men are usually negatively correlated, because they share rebounds (SUPPORTED, FantasyLabs, via search summary).
- His Dec 2016 correlation study used players with 5+ games and 15+ minutes per game, but the numbers lived in embedded graphics I could not read (VERIFIED method only, [FantasyLabs](https://fantasylabs.com/?p=40334)).
- Assists made up about 32% of one star point guard's DK value, so "passer plus scorer" stacking is weaker than quarterback-receiver stacking in the NFL (SUPPORTED, FantasyLabs 2015, via search summary).
- **Open-source defaults** (VERIFIED in `nba_gpp_simulator.py`):
  - Same-team correlation is -0.067 between guards and other positions, -0.044 to -0.082 involving centers, and -0.08 to -0.13 for the same position.
  - Opponent correlation is +0.015 to +0.021 for most pairs, and -0.07 center versus opposing center.
  - These are entered as fixed numbers with no stated source, and applied to a multivariate normal.
- **Other sports for contrast:**
  - NHL same-line linemates are much more correlated than other teammates (SUPPORTED, Hunter, Vielma and Zaman, [arXiv 1604.01455](https://arxiv.org/abs/1604.01455v3)).
  - NFL opposing quarterbacks are positively correlated through game scoring (SUPPORTED, [arXiv 2112.07002](https://arxiv.org/abs/2112.07002)).
  - NBA differs because minutes and usage are fixed resources that teammates split. Production is spread across many possessions, so no single play links two players' outcomes the way a touchdown pass does.

### Representation (recommended)
- **Positive, game-wide:** the pace factor and overtime.
- **Positive, within team:** the team efficiency factor.
- **Negative, within team:** fixed usage shares, rebound allocation, and redistribution of minutes after an early exit or blowout.
- **Negative, starters vs bench:** blowouts move minutes from starters to the bench.
- **Validation target:** a table of residual correlations by role pair (starter guard and starter center, same team; same position; opponents; starter vs bench) measured from last season's box scores against projections. The simulator's output correlations should land within sampling error of it. The fallback multivariate-normal model can borrow the same measured table (BET).
- *Means for results:* stacking teammates is a weak lever in the NBA. The correlation that matters is shared downside (blowouts, injuries) and shared game environment, and getting it wrong mostly misprices game stacks in Showdown.

---

## 6. Ownership projection without a paid feed

### Answer
1. **For Oct 20:** project ownership by building a simulated field of opponents who each optimize a noisy copy of a public-style projection, then reading off how often each player appears. Add rule-based nudges for news timing and name value.
2. **Within 3 to 6 weeks:** replace it with a learned model trained on real ownership from contest results, using a softmax regression constrained to the slot totals. A gradient-boosted model is the alternative if data volume allows.
3. **Always:** carry ownership as a distribution, not a point.

### Evidence
- **Haugh and Singal** model opponents' picks with a Dirichlet-multinomial whose parameters come from "Dirichlet regressions" (SUPPORTED, [Management Science 2021, DOI 10.1287/mnsc.2019.3528](https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.2019.3528), via search summary). Features include "cost, expected points, momentum" (SUPPORTED, [ODSC summary](https://opendatascience.com/how-to-play-fantasy-sports-strategically-and-win/)). Their NFL 2017 test reported more than 350% return over 17 weeks at $50 per week (SUPPORTED; small sample).
- **Practitioner factors** (VERIFIED list, Chris Gimino, [RotoGrinders](https://rotogrinders.com/articles/dfs-strategy-predicting-ownership-1360237)): expert projections, perceived role, Vegas totals, perceived matchup, salary versus value, positional scarcity, opportunity cost, recency bias, and the consensus of industry experts.
- **Stokastic** describes a baseline of counting how often a player appears in the top 1,000 optimal lineups, refined with other variables (SUPPORTED, via search summary).
- **A FantasyLabs analyst** calls ownership "much more of a knowledge-based art than a formula-driven science" (VERIFIED quote, [FantasyLabs 2017](https://www.fantasylabs.com/?p=76532)).
- **Accuracy:** no published ownership MAE (average miss in percentage points) was found. One vendor reports r-squared and RMSE instead, and its own example miss was 22.4% projected by the industry versus 42.4% actual on one golfer (SUPPORTED, FTN via search summary).
- BET: a good model on large NBA main slates misses by about 3 to 6 percentage points on average among players above 5% ownership, with the biggest misses on late-news value plays. Measure ours from week 1.

### Model specification (BET, designed)
- **Hard constraints:**
  - In Classic, ownership across all players sums to 800%, because every lineup has 8 slots. Each position-eligibility group must also be feasible.
  - In Showdown, Captain ownership sums to 100% and UTIL to 500%, and Captain and UTIL are separate entries for the same player.
  - Enforce these with a softmax over players per slot type, with a temperature (concentration) parameter (VERIFIED arithmetic for the sums).
- **Features:**
  - Salary, and projection from public-facing sources. DK's own salary file shows each player's average points per game, which casual players see (BET: the data agent should confirm the column exists).
  - Value (projection per $1,000), and value rank within position.
  - Starter flag and "promoted today" flag.
  - Hours between the news and lock (late news gives a partial ownership spike, because many lineups were already built).
  - Game total and implied team total.
  - Name value (proxy: All-Star or All-NBA in the last 3 seasons, salary tier).
  - Slate size (more games means flatter ownership).
  - Contest type (buy-in, max entries).
- **Captain vs UTIL in Showdown:** Captain ownership concentrates on the top-projected stars. Writers note the public tends to captain the highest projected scorer (SUPPORTED, [RotoWire](https://www.rotowire.com/basketball/article/dfs-nba-showdown-and-single-game-strategy-57179) and others). Model Captain share as a sharper softmax (lower temperature) over projection than the UTIL share (BET).
- **Uncertainty:** treat the predicted vector as the mean of a Dirichlet distribution whose concentration is fitted from past misses, and draw several field realizations from it (Section 7).
- **Bootstrapping with no history:** the field-optimizer model needs no history. Calibrate its two or three knobs (noise level, share of casual entries, salary floor) to rules of thumb on night 1, then to real contest results from night 2.
- *Means for your workload:* from week 2 the engine needs the post-contest standings file for each contest you enter, which lists every lineup. Downloading it may be a manual step each morning unless the data agent finds an automated route.
- *Means for results:* ownership errors directly corrupt the leverage math. Expect noisy ownership for the first 2 to 3 weeks and a measurable improvement after.

---

## 7. Field modeling

### Answer
Generate opponents as a mixture of three types, with weights set per contest:
1. **Optimizer-like entrants** (pros): each solves for the best lineup under a noisy projection.
2. **Ownership-weighted samplers** (casuals): they pick players in proportion to ownership, subject to a salary window.
3. **Chalk duplicators:** a small number of very common lineups, which matter most in Showdown.

Calibrate the mixture to targets measured from real contest results, not to ownership alone.

### Evidence and methods
- **Haugh and Singal:** opponents' selections follow a Dirichlet-multinomial process (SUPPORTED). Their opponent model is an ownership sampler with budget and team constraints. The "insider information" analysis in that paper shows how valuable knowing the field is (SUPPORTED).
- **Open-source ownership sampler** (VERIFIED, chanzer0 `generate_lineups`):
  - Fills slots in sequence, choosing among eligible players with probability proportional to projected ownership.
  - Enforces a minimum and maximum lineup salary (default floor 48,000).
  - Boosts the last pick's probability by (salary / cap) squared so lineups use their salary.
  - It is a reasonable "casual" component but produces too few optimizer-style lineups.
- **Contest archetypes:** Stokastic's field generator asks for a contest archetype ("high stakes" for $1,500 buy-ins, "low stakes" for 50-cent entries) and a pool size matched to the contest (SUPPORTED, via search summary of Stokastic pages).
- **Duplication data** (VERIFIED, [RotoGrinders 2016 golf Milly Maker](https://rotogrinders.com/articles/draftkings-milly-maker-masters-lineup-analysis-1258937)):
  - 205,732 entries contained 149,657 unique lineups (72.7%).
  - Lineups using all salary were unique only 65.5% of the time.
  - Leaving $500 to $1,000 unused raised uniqueness to 89% to 98%.
  - This is golf, not NBA, but it shows that the salary-left distribution is a primary calibration target.
- No NBA Showdown duplicate rate was found. Showdown has 6 slots and a small player pool, so duplication there is far higher than in Classic (BET).

### Calibration targets (measured from contest standings files)
- Player ownership, including Captain vs UTIL.
- Co-ownership of the top 20 player pairs.
- Salary-left distribution.
- Share of lineups with 3+ players from one team, and with game stacks.
- Number of unique lineups, and the duplicate count of the top-scoring lineups.
- Winning score, top-1% score, and min-cash score, compared after the fact with the predicted distributions (Section 8).

### Duplication estimation for our lineups
- Showdown: generate a large field sample (100,000 to 1,000,000 lineups, cheap at 6 slots) and count exact matches. Expected duplicates of lineup L = field size x frequency of L.
- Classic: use the field sample for chalky lineups and the ownership product times a fitted correction factor for rare ones (BET).
- *Means for results:* duplicates split top-1% payouts, but they do not change whether a lineup *finishes* top 1%. Under your stated goal, duplication matters mainly for portfolio diversity and as a field-realism check.

---

## 8. Estimating the top-1% and min-cash score thresholds

### Answer
Compute thresholds **inside each simulation** from the simulated field:
- P(lineup L finishes top 1%) = average over simulations of 1[score_L(s) >= q99_field(s)].
- The same works for min-cash, using the cash percentile of the payout table.
- For fields under 100 entries, use the field maximum (first place).
- The portfolio's "at least one top-1%" and the night's "zero cashes anywhere" are then just counts over the same simulations.

### Why per-simulation thresholds matter
- On a high-scoring night (fast pace, overtime), the threshold rises together with your lineup's score.
- A fixed threshold ignores that, which overrates high-variance lineups and misstates the zero-cash risk.
- Haugh and Singal build on Monte Carlo samples of opponents' scores and "order statistics" (the k-th highest score) (SUPPORTED, ODSC summary).

### Estimators and sample sizes
- **Large GPPs:** sample M field lineups (BET: M = 20,000 to 50,000, or the full field if smaller). Compute q99 and the cash quantile per simulation. About 1% of M lineups sit above q99 (200 to 500 lineups), which gives a stable quantile (BET).
- **Small fields (under 100):** simulate the full field N-1 times in each simulation, using several field realizations drawn from the ownership uncertainty.
- **Ownership uncertainty:** use K field realizations (BET: K = 5 to 10), each with its own Dirichlet draw of ownership, and assign simulations across them in rotation. This stops one wrong ownership guess from making the threshold look too certain.
- **Pre-slate prior (later):** a regression of realized top-1% and min-cash scores on slate features (games on slate, sum of top projected values, field size, contest type) from past contest results. Use it as a sanity check on the simulated threshold distribution.
- **Calibration check:** each morning, find where the realized top-1% score fell within the predicted per-contest distribution (its PIT value, Section 9). Over many contests these values should be spread evenly from 0 to 1.

### Memory budget (6 GB free)
- 50,000 field lineups x 30,000 simulations in float32 would be 6 GB, too much.
- Process simulations in chunks of about 1,000: lineup-player incidence matrix times a player-score chunk, about 200 MB per chunk. Keep only the per-simulation quantiles.
- Candidate lineups: store top-1% and cash hits as bits. For example, 20,000 candidates x 30,000 simulations is 75 MB per threshold.
- (VERIFIED arithmetic; run times are BET.)
- *Means for results:* "probability of a top-1% finish" and "probability of zero cashes tonight" become numbers the engine can compute and later check against reality.
- *Means for the laptop:* the field step fits in memory as long as it is chunked.

---

## 9. Calibration and evaluation

### Answer
Score each layer separately with proper scoring rules, compare challenger models against the current model night by night as paired blocks, and use the thousands of field lineups in each real contest for contest-level calibration. Do not wait for your own wins to tell you anything.

### Per-layer metrics
| Layer | Point metric | Distribution metric | Calibration check | Baseline to beat |
|---|---|---|---|---|
| Availability | n/a | Brier, log loss | Reliability diagram (predicted vs actual play rate) | Injury-report status mapped to fixed rates |
| Minutes | MAE, RMSE by role | Pinball loss (quantile loss) at 10/50/90 | 80% interval coverage; PIT histogram | 75% season + 25% last-5 (Farnsworth) |
| Per-stat counts | MAE | CRPS (continuous ranked probability score: average distance between predicted distribution and outcome) | PIT; double-double Brier | Last-season per-minute x projected minutes |
| DK points | MAE, bias by salary tier | CRPS; log score | 80% coverage; PIT; P(over X) reliability | DK average-points field; DARKO-derived DK points |
| Ownership | MAE (pct points), weighted MAE | Log loss of the ownership vector (cross-entropy) | Predicted vs actual by ownership bucket | Field-optimizer ownership v1 |
| Field model | Salary-left distance, duplicate-rate error | Kolmogorov-Smirnov distance (largest gap between two distributions) on field score distributions | Top-pair co-ownership | Pure ownership sampler |
| Thresholds | Absolute error of median vs realized | CRPS of threshold distribution | PIT of realized top-1% and min-cash | Slate-feature regression |
| Lineup P(top-1%) | n/a | Brier and log loss over all field lineups in each contest | Reliability diagram over predicted-probability buckets | Same with normal-distribution simulator |
| Overrides | Minutes MAE with vs without | CRPS with vs without | Coverage of stated intervals | Model without override |

References for the scoring rules:
- Gneiting and Raftery (2007), "Strictly Proper Scoring Rules, Prediction, and Estimation", JASA, DOI 10.1198/016214506000001437 (SUPPORTED, standard reference, not re-read today).
- Gneiting, Balabdaoui and Raftery (2007), JRSS-B, for the "sharpness subject to calibration" principle and PIT histograms (SUPPORTED).
- A PIT (probability integral transform) value is where the actual outcome fell inside the predicted distribution, from 0 to 1. A well-calibrated model produces a flat histogram of these values.

### What a significant improvement looks like
- **Unit of evidence:** the night, not the player-game. Players on the same night share news and game environments.
- **Test:** for each night, compute the average score difference (for example CRPS of challenger minus incumbent) over all player-games. Then run a paired test over nights: a block bootstrap by night, or a Diebold-Mariano test with autocorrelation-robust errors (Diebold and Mariano 1995, SUPPORTED standard reference).
- **Decision rule:** adopt the challenger when the 95% interval of the average nightly difference excludes zero and the effect holds in at least two of three subgroups (starters, bench, news-affected) (BET).
- **Expected time:** about 2 to 4 weeks for distribution-level changes, given roughly 5 to 7 game nights a week (BET) with hundreds of player-games each. Ownership changes are similar.
- **Why contest results alone do not work:** to detect a top-1% rate improving from 1.0% to 1.5% with 80% power at 5% significance needs about 7,700 independent entries per arm (VERIFIED arithmetic: (1.96+0.84)^2 x (0.0099+0.0148) / 0.005^2). Correlated entries need more. That is more than a season.
- **Using every field lineup helps, with a caveat.** Score predicted P(top-1%) for every lineup in each real contest's standings (thousands per contest) with Brier and log loss. That tests *discrimination*: given what happened, did the model rank lineups correctly? It is far more informative than your own entries alone. But every lineup in a contest shares one slate outcome, and lineups built on the same game rise and fall together. So the effective sample is still about one per contest-night, and it does not test calibration across different slate outcomes. Run it as a per-night paired comparison like the other tests, and pair it with the threshold PIT check (Section 8) for calibration.
- *Means for your workload:* challengers can run in shadow mode each night at no extra effort to you. A weekly scorecard would tell you which layer is improving.

---

## 10. The LLM role-override interface

### Design principles
1. **An override is evidence, not a value.** It carries a distribution and a stated confidence. The engine blends it with the model.
2. **It can be conditional.** Most news is "if Y sits, X starts". The simulator already draws Y's availability in each simulation, so a conditional override applies only in simulations where its condition holds.
3. **It expires and is attributed.** It records who said it, when, from what evidence, and when it stops applying.
4. **Team totals still hold.** After overrides apply, minutes and usage are renormalized to team totals.
5. **It is scored afterward.** Every override is logged with what the model would have predicted without it, so the engine can measure whether overrides help.

### Schema (JSON; example for "Player X starts, expect 32 to 36 minutes, usage up")
```json
{
  "override_id": "2026-10-20-LAL-0001",
  "created_at": "2026-10-20T17:42:00-04:00",
  "expires_at": "lock",
  "source": {
    "kind": "llm",
    "model": "<model id>",
    "confidence": "medium",
    "evidence": [
      {"url": "<beat writer post>", "quote": "<under 15 words>", "published_at": "2026-10-20T17:30:00-04:00"}
    ]
  },
  "game_id": "<engine game id>",
  "player": {"dk_player_id": 12345, "nba_person_id": 1630000, "name": "Player X"},
  "condition": [
    {"dk_player_id": 67890, "status": "OUT"}
  ],
  "availability": {"p_active": 0.97},
  "role": {"p_start": 0.90},
  "minutes": {"q10": 30.0, "q50": 34.0, "q90": 36.5, "hard_cap": null},
  "usage_multiplier": {"q10": 1.00, "q50": 1.10, "q90": 1.22},
  "stat_multipliers": {"ast": {"q10": 0.95, "q50": 1.05, "q90": 1.15}},
  "redistribution_hint": [
    {"dk_player_id": 11111, "minutes_weight": 0.6},
    {"dk_player_id": 22222, "minutes_weight": 0.4}
  ],
  "rationale": "Coach said X will start in Y's place; X played 34 min in last start."
}
```

### Semantics
- All quantities are conditional on the `condition` list holding and the player being active.
- Omitted fields mean "no opinion", so the model value stands.
- `q10/q50/q90` are the source's 10th, 50th and 90th percentiles. The engine fits a smooth distribution through them: skewed normal for minutes on a 0 to 48 scale, lognormal for multipliers.
- `hard_cap` truncates minutes (for restrictions). It is not a mean.
- `usage_multiplier` multiplies `k_i` in the Section 2 share model before renormalization, so teammates' shares fall automatically.
- `redistribution_hint` biases where freed minutes go. Without it, the position prior applies.

### Combining with the model (BET; parameters fitted from the override log)
- **Transform first.** Work with minutes as logit(minutes / 48) and multipliers as log(multiplier).
- **Precision-weighted blend.** posterior mean = (model mean / model var + override mean / override var) / (1 / model var + 1 / override var).
- **Inflate the override's variance before blending.** override var = (stated var) x c_source^2, where c_source is a coverage factor per source and confidence level. It starts at 1.5 for LLM "medium" and 1.2 for user overrides. It is updated weekly so that stated 80% intervals actually cover 80% of outcomes.
- **Discrete fields** (`p_active`, `p_start`) blend by averaging log-odds with source weights. They start at 0.5 for LLM and 0.8 for user, refit weekly.
- **Precedence:** official injury designations OUT and inactive lists override everything. A user override beats an LLM override. A newer override replaces an older one from the same source for the same field.
- **Validation (reject with a logged reason):** unknown player or game; game already locked; quantiles not in order; minutes outside 0 to 48; multipliers outside 0.5 to 2.0; evidence missing for an LLM override; expired.

### Scoring the overrides
For each override, store model-only and blended predictions for minutes, DK points and P(active). After the game, compute:
- Minutes MAE and CRPS, with vs without.
- Coverage of the stated 80% interval.
- Brier score for `p_active`.

The weekly report answers three questions: did overrides improve CRPS, are the LLM's intervals honest, and which kinds of news it handles well.
- *Means for your workload:* you never type a number. The LLM files structured records with evidence, you can skim a nightly list, and the engine tells you within weeks whether the LLM deserves more or less trust.

---

## Critique of the attached DAG blueprint

**What it gets right** (keep all of these):
- Separates opportunity from conversion.
- Computes double-doubles and triple-doubles from each simulated line.
- Applies Captain after base scoring.
- Versions the scoring adapter.
- Uses chronological backtests.
- Records seeds and timestamps.
- Keeps a fallback lineup.
- Warns that 10,000 draws is not automatically enough.
- Insists that ownership is a distribution.
- Its warning against a trailing 10-game rate matches DARKO's per-stat decay approach.

**Structural problems in the graph:**
1. **Missing arrow from game state to minutes.** In the mermaid graph, minutes (M) is fed only by availability (A). Blowouts, overtime and foul trouble all come from game state (G), and back-to-backs come from context (C). Without G to M, a simulator built from this graph would draw minutes independently of the score margin. That would erase the most important NBA correlation, starters losing minutes in blowouts.
2. **The contest and field side is one box with no inputs.** "Contest field and payout structure" has no parents. In reality ownership depends on salary, public projections, Vegas lines and news timing. The field depends on ownership and contest type. Thresholds depend on the field and the simulated slate. This is the second most important model in the system, and it needs its own sub-graph: Section 6 (ownership), Section 7 (field), Section 8 (thresholds).
3. **Availability is drawn as an input, not a random variable.** Questionable players and "if Y sits, X starts" need availability sampled in each simulation, with conditional role scenarios. There is also no node for news or overrides (Section 10), and no notion of when news arrives relative to lock.
4. **No prior or time dimension.** "Player skill and role rates" has no parent for last season, aging, rookies or DARKO. Opening night has zero current-season data, so this node is what the model runs on for the first weeks.
5. **No opponent or matchup input into rates.** Opponent pace is covered through G, but opponent rebounding and opponent turnover tendencies should modestly adjust rates. Defense-versus-position data is noisy and should be heavily shrunk ([FantasyLabs, "Why DvP Data is Misleading"](https://www.fantasylabs.com/articles/why-dvp-data-is-misleading/)).
6. **Two different objectives are missing.** The blueprint lists generic objectives (cash probability, expected payout, top-end equity). Your goals are specific: top-1% probability per contest, and zero-cash probability across all contests on the night. That requires per-simulation top-1% and cash thresholds for every contest, computed on shared simulations. The graph should show all contests reading from one slate simulation.

**Modeling choices I would change:**
- **Possession-level simulation as the preferred design (Section 3.3).** For DFS, the dependencies that matter (minutes, pace, team efficiency, usage competition, rebound competition) are captured by stat-level shared factors at a fraction of the calibration cost. The blueprint's examples ("a made field goal can have an assist") matter little in NBA DFS, where assists are about a third of even a star point guard's value (SUPPORTED). Keep possession-level as a later upgrade.
- **"Teammates can be positively related"** is stated without noting that the net effect is small and usually negative (Section 5). A builder who reads it as "stack teammates" will overweight stacks.
- **"Treat steals and blocks as upside sources"** is right. The spike also shows that independent fixed-minutes draws understate triple-double probability, which supports its point 3. The "about fourfold" size in my toy is BET, because it depends on assumed parameters.

**Scoring and rules items to verify** (owned by the scoring and data agents):
- Whether a triple-double also earns the double-double bonus on DK (4.5 bonus total vs 3). Sources conflict: a 2015 RotoWire article says both bonuses apply; 2021 Rotoballer pages say only one (SUPPORTED, via search summary). The blueprint rightly flags this. The answer can be settled from one completed contest containing a triple-double.
- Whether the Captain multiplier applies to bonuses.
- The blueprint cites "NBA Series Rules" (rules/4/137) for the Captain multiplier. That page may describe a different product than Showdown Captain Mode, so the scoring agent should confirm the right page. Captain is 1.5x points and 1.5x salary (SUPPORTED, RotoWire 2021).

**Validation checklist gaps:**
- It names "interval coverage" and "calibration" but no proper scoring rule, no PIT, and no significance test (Section 9).
- It has no override log.
- It has no field-model checks (salary left, duplication, threshold PIT).
- "Compare against simple baselines" should name them (Section 9 table).

---

## Open questions

1. **DK triple-double bonus stacking** (3 vs 4.5 total). Needs one real completed contest. Owner: scoring agent.
2. **DARKO access and terms.** Is DARKO's per-stat projection data reachable for free, and is automated nightly use acceptable? The About page states no terms. Owner: data agent; possibly ask the site owner.
3. **Contest standings files.** Can the engine get the full standings file (every lineup, every player's ownership) for each contest the user enters, ideally automatically? Without it, ownership and field calibration stay at "rules of thumb" for longer.
4. **Free public ownership projections.** Do any free sites publish NBA ownership projections usable as an extra feature? Owner: data agent.
5. **Starting lineup confirmation timing.** When are starting lineups reliably known (commonly cited as about 30 minutes before tip; not verified)? This decides when the final re-run happens.
6. **Opening night slate shape.** How many games are on Oct 20, and which contest types are offered? A 2-game night is effectively Showdown-like, with heavy ownership concentration and duplication.
7. **Which contests the user enters** (sizes, buy-ins, max entries). This sets field archetype weights.
8. **How the two goals trade off.** Maximizing top-1% probability and minimizing zero-cash probability can conflict: high-variance lineups help the first and hurt the second. The portfolio agent needs a rule (lexicographic, constraint, or weighted).
9. **Is the 2023 Player Participation Policy still in force for 2026-27** in the same form?
10. **How much nightly review the user wants.** Should the user approve overrides, or only see the list?

---

## Implications for the architecture

1. **One shared slate simulation per run** (common random numbers), at 10,000 simulations for screening and 30,000 for final. Every contest (Classic and Showdown) and the cross-contest zero-cash metric are scored on the same simulations. Showdown Captain uses 1.5 times the same simulation's points.
   - *Means for results:* this is what makes the zero-cash goal computable at all.
2. **Separate, testable modules** with versioned outputs:
   - priors builder (last season plus DARKO)
   - availability model
   - minutes model
   - rates model (shrinkage plus decay)
   - usage share and redistribution
   - override ingestion and validation
   - stat-level simulator
   - DK scoring adapter
   - ownership model
   - field generator (mixture)
   - threshold estimator
   - portfolio optimizer
   - evaluation store
   - *Means for results:* each layer can be scored and swapped on its own, so a bad ownership model cannot hide inside a good projection.
3. **Data flow per run:** snapshot inputs, apply the override log, simulate players (about 300 x 30,000), generate K field realizations per contest, compute per-simulation thresholds in chunks, score candidates as bitsets, select the portfolio, then write predictions to the evaluation store.
   - *Means for reproducibility:* any night can be replayed exactly from its snapshot.
4. **Memory:** never hold a full field x simulations matrix. Chunk by simulation (about 1,000 at a time) and keep only per-simulation quantiles and candidate hit bitsets. This keeps peak memory near 1 GB, within the 6 GB free (BET, from Section 8 arithmetic).
   - *Means for the laptop:* the engine can run alongside normal use without exhausting memory.
5. **Compute:** the simulation step takes seconds to a minute in numpy (BET). Field generation with optimizer opponents is the costliest step: each lineup optimization takes tens of milliseconds with a mixed-integer solver such as HiGHS (BET), so use a few thousand optimizer lineups plus cheap ownership samples. Parallelize across the 8 cores by contest or by field realization.
   - *Means for nightly run time:* a full run should take minutes, not hours (BET until measured).
6. **Late news re-runs:** the engine must re-run quickly after injury reports and confirmed lineups, before each game's lock. Only availability, minutes, overrides and ownership change, so cache priors and rates.
   - *Means for results:* late scratches, where most NBA edge appears, can be acted on before lock.
7. **Evaluation from day 1:** every run writes its predicted quantiles, P(active), P(double-double), ownership vectors, and threshold distributions with a run id, so the Section 9 scorecard can be computed the next morning.
   - *Means for your workload:* a weekly scorecard instead of guessing whether changes helped.
8. **Fallbacks, in order:** full model; then multivariate-normal fantasy points with measured correlations; then mean-projection optimizer with exposure caps. Each produces a valid lineup set before optional steps run.
   - *Means for results:* a data outage costs some edge, never a missed contest.
9. **Configuration, not code, for tunables:** decay rates, shrinkage constants, override coverage factors, field mixture weights, and simulation counts should live in versioned config, so challengers can run in shadow mode.
   - *Means for build cost:* tuning becomes a config change and a scorecard check rather than a code change.

---

## Sources

Primary or near-primary (read directly):
- DARKO About page (methodology): https://www.darko.app/about
- DARKO Fantasy Lab (per-100 projection statement): https://www.darko.app/projections
- DARKO home (page list including WOWY RAPM): https://www.darko.app/
- Daly-Grafstein and Bornn, "Rao-Blackwellizing Field Goal Percentage", arXiv 1808.04871 (Blackport 750-attempt citation, empirical Bayes Section 4.1): https://ar5iv.labs.arxiv.org/html/1808.04871
- van Bommel and Bornn, "Adjusting for Scorekeeper Bias in NBA Box Scores", arXiv 1602.08754: https://arxiv.org/abs/1602.08754
- Hunter, Vielma and Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming", arXiv 1604.01455: https://arxiv.org/abs/1604.01455v3
- Bergman et al., "Optimizing the expected maximum of two linear functions defined on a multivariate Gaussian distribution", arXiv 2112.07002: https://arxiv.org/abs/2112.07002
- Musco, Sviridenko and Thaler, "Determining Tournament Payout Structures for Daily Fantasy Sports", arXiv 1601.04203: https://arxiv.org/abs/1601.04203
- Krishna, Lychagin and McLean, "Injury, Workload, and the Strategic Response of Coaches in the NBA", NBER WP 35803 (Sep 2026): https://www.nber.org/papers/w35803
- chanzer0/NBA-DFS-Tools, `src/nba_gpp_simulator.py` (field sampler, correlation defaults, multivariate normal): https://github.com/chanzer0/NBA-DFS-Tools
- Staude, "Randomness, Stabilization, & Regression", FanGraphs (May 2013): https://blogs.fangraphs.com/randomness-stabilization-regression
- Neil Paine, "Optimizing the '95 Rockets" (Apr 2010; Oliver and Witus usage-efficiency figures): https://neilpaine.substack.com/p/optimizing-the-95-rockets
- Derek Farnsworth, "Accurately Predicting Minutes in NBA DFS", RotoGrinders (Apr 2024): https://rotogrinders.com/fantasy/lessons/accurately-predicting-minutes-nba-dfs
- Stokastic Staff, "NBA DFS Research: How To Project Minutes, Usage & Pace" (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-research
- Bryan Mears, "NBA Breakdown: Monday 1/2", FantasyLabs (Jan 2017): https://www.fantasylabs.com/?p=40730
- Bryan Mears, "Daily Fantasy NBA Player Correlations", FantasyLabs (Dec 2016): https://fantasylabs.com/?p=40334
- Bryan Mears, "Rethinking Stacking and Correlations in NBA DFS", FantasyLabs (Nov 2015): https://fantasylabs.com/?p=4795
- Chris Gimino, "DFS Strategy: Predicting Ownership", RotoGrinders: https://rotogrinders.com/articles/dfs-strategy-predicting-ownership-1360237
- Matthew Freedman, FantasyLabs (Dec 2017): https://www.fantasylabs.com/?p=76532
- Nick St. Pierre, "DraftKings Milly Maker: Masters Lineup Analysis", RotoGrinders (Apr 2016): https://rotogrinders.com/articles/draftkings-milly-maker-masters-lineup-analysis-1258937
- BriPC23, "NBA Stat Variance", RotoGrinders: https://rotogrinders.com/lessons/nba-stat-variance-209254
- Zachary Hanshew, "How Should Potential Blowout Games Influence DFS Lineups?", FantasyPros (Jul 2020): https://www.fantasypros.com/2020/07/how-should-potential-blowout-games-influence-dfs-lineups-fantasy-basketball/amp/
- Jeff Edgerton, "DFS NBA: Showdown and Single-Game Strategy", RotoWire (May 2021): https://www.rotowire.com/basketball/article/dfs-nba-showdown-and-single-game-strategy-57179
- ODSC summary of Haugh's talk: https://opendatascience.com/how-to-play-fantasy-sports-strategically-and-win/
- Taylor Wyman, "Creating More Predictive Stats", BBall Index (Aug 2025): https://www.bball-index.com/creating-more-predictive-stats/
- Evangelista, Cal Poly thesis on evaluating NBA DFS projections (abstract only): https://digitalcommons.calpoly.edu/theses/2025

Secondary or seen only through search summaries (SUPPORTED at most):
- Haugh and Singal, "How to Play Fantasy Sports Strategically (and Win)", Management Science 67(1) 2021, DOI 10.1287/mnsc.2019.3528: https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.2019.3528 (SSRN: https://papers.ssrn.com/abstract=3393127)
- RotoGrinders, "Banking On Overtime": https://rotogrinders.com/articles/banking-on-overtime-1710010
- NBA official injury report rules 2025-26: https://official.nba.com/nba-injury-report-2025-26/
- ESPN on the 2023 Player Participation Policy: https://www.espn.com/nba/story/_/id/38386013
- The Ringer on preseason predictiveness (2019): https://www.theringer.com/2019/10/18/nba/nba-preseason-2019-20-regular-season
- Liberty Ballers, "Is there an efficiency cliff" (2019): https://www.libertyballers.com/2019/1/29/18199824/is-there-an-efficiency-cliff
- Bruin Sports Analytics, star usage: https://www.bruinsportsanalytics.com/post/star-usage-analysis
- Harvard Sports Analysis, aging (2017): https://harvardsportsanalysis.org/2017/11/what-happens-to-nba-players-when-they-age/
- arXiv 2402.12400 (age-conditioned load management): https://arxiv.org/pdf/2402.12400
- Wayne Winston on NBA margin SD about 12 points: https://www.goodreads.com/author_blog_posts/16483561-why-is-standard-deviation-of-nba-scores-about-point-spread-12-points
- Footballguys on NBA vs NFL variance: https://www.footballguys.com/article/14johnlee_DFS4Dummies_Part2
- FantasyLabs, "Why DvP Data is Misleading": https://www.fantasylabs.com/articles/why-dvp-data-is-misleading/
- SaberSim podcast episode pages (play-by-play simulation claim): https://sabersim.castos.com/episodes/dfs-qa-what-do-the-correlation-and-sim-diversity-sliders-do
- Gneiting and Raftery (2007), JASA, DOI 10.1198/016214506000001437; Gneiting, Balabdaoui and Raftery (2007), JRSS-B; Diebold and Mariano (1995), JBES (standard references, not re-read today)

Spike (run today):
- `spikes/modeling/sim_shape_and_mc_error.py`, output `spikes/modeling/out/20261013-1644_sim_shape_and_mc_error.txt`
