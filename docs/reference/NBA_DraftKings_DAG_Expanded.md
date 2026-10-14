# DraftKings NBA Scoring DAG and Simulation Blueprint

**Expanded and technically refined from the supplied draft**  
**Prepared:** October 13, 2026  
**Scope:** DraftKings NBA Classic scoring, with notes for Captain formats

## Executive summary

A useful NBA fantasy model should follow the chain from game context and rotation availability to playing time, player opportunities, simulated basketball outcomes, official fantasy scoring, and finally contest-specific lineup decisions.

The supplied draft has a strong starting structure: separate opportunity from outcomes, calculate double- and triple-double bonuses inside each simulation, and apply Captain scoring after the base score. This version keeps that structure and adds several safeguards:

- Treat the diagram as a **prediction dependency graph**, not proof that every arrow is causal.
- Model **minutes and role uncertainty** explicitly. Minutes are the main opportunity multiplier and are affected by rotation changes, foul trouble, blowouts, and return-from-injury limits.
- Simulate connected game outcomes so points, assists, rebounds, and teammate production remain coherent. Independent player-level draws can create impossible or unlikely game states.
- Use the exact scoring rules for the contest, then optimize for the contest's payout and field. A high mean projection alone does not define the best lineup.
- Shrink noisy recent rates toward longer-term and role-based priors; a trailing 10-game average is a feature, not a reliable forecast by itself.
- Add rule, data, calibration, and lineup-validity checks before treating a projection as production-ready.

## 1. Forecasting and decision architecture

The graph below describes which model outputs depend on which inputs. An arrow means “feeds the forecast,” not “a controlled intervention has proven this causal effect.”

~~~mermaid
graph TD
    C["Slate and matchup context"] --> G["Team possessions and game state"]
    A["Availability and rotation news"] --> M["Minutes and player role"]
    G --> O["Player opportunities"]
    M --> O
    R["Player skill and role rates"] --> X["Simulated play outcomes"]
    O --> X
    G --> X
    X --> S["Box-score stat line"]
    S --> D["Versioned DraftKings scoring adapter"]
    D --> F["Player fantasy-point distributions"]
    F --> L["Lineup and portfolio simulation"]
    P["Contest field and payout structure"] --> L
~~~

### Model layers

| Layer | Inputs and outputs | Modeling purpose |
|---|---|---|
| Context | Game total, spread, implied team totals, pace, rest, venue, and matchup | Set priors for scoring environment, possessions, and game-state risk. Treat betting lines as information, not as direct causes. |
| Availability | Confirmed starters, injuries, restrictions, depth chart, rotation patterns | Determine who is available and define plausible minutes and role scenarios. |
| Team game state | Possessions, team scoring, shot mix, opponent misses, blowout and overtime states | Supply shared context so teammates and opponents are simulated together. |
| Player opportunity | Minutes, field-goal attempts, 3-point attempts, free throws, potential assists, rebound chances, defensive events, and turnover chances | Estimate how many chances a player receives before converting those chances into stats. |
| Skill and conversion | Shooting, finishing, passing, rebounding, turnover, steal, and block rates | Estimate how opportunities turn into outcomes, with uncertainty and sample-size controls. |
| Stat simulation | Joint player and team box scores | Generate plausible game-level outcomes rather than only one point estimate per player. |
| Scoring adapter | Official contest scoring and roster rules | Convert each simulated stat line into fantasy points without hand-coded rule drift. |
| Contest decision | Simulated lineups, ownership, field behavior, entry limits, payout structure | Select for the target contest objective: cash probability, expected payout, top-end equity, or portfolio robustness. |

## 2. DraftKings NBA scoring layer

The currently published DraftKings NBA Classic rules list the following fantasy-point values. Recheck the rules for the exact contest and slate before production use; formats and contest rules can differ.

| Stat or bonus | Fantasy points |
|---|---:|
| Point | +1.0 |
| Made 3-point shot | +0.5 additional |
| Rebound | +1.25 |
| Assist | +1.5 |
| Steal | +2.0 |
| Block | +2.0 |
| Turnover | -0.5 |
| Double-double | +1.5 |
| Triple-double | +3.0 |

Let PTS, 3PM, REB, AST, STL, BLK, and TO be the simulated box-score stats. Let I_DD and I_TD be the double- and triple-double indicators.

~~~text
Base fantasy points =
    PTS
  + 0.5 × 3PM
  + 1.25 × REB
  + 1.5 × AST
  + 2.0 × STL
  + 2.0 × BLK
  - 0.5 × TO
  + 1.5 × I_DD
  + 3.0 × I_TD
~~~

The points total already includes the three points from each made three; the 0.5 term is the extra three-point-shot bonus. A player qualifies for the listed milestone categories using points, rebounds, assists, blocks, and steals. The official rules cap each listed milestone at one award per player. Because the published table lists double- and triple-double bonuses separately, the scoring adapter should explicitly encode and regression-test how overlapping milestones are handled for the specific contest rather than leave that behavior implicit.

For a Captain contest, apply the contest's Captain multiplier to the player's correctly calculated fantasy score. DraftKings' NBA Captain-format rules describe a 1.5× scoring multiplier; the Captain salary treatment and roster structure should also be read from the contest's rules. Do not assume that a Captain rule applies to Classic.

### Scoring tests to keep

- A made three contributes 3.5 points total before other stats: 3 points under PTS plus 0.5 additional.
- A turnover subtracts 0.5 points.
- Double- and triple-double thresholds are evaluated from each simulated stat line, not from projected averages.
- Stats at 9 and 10 are tested around every milestone threshold.
- The scoring adapter is checked against official platform scoring examples or completed-entry results.
- Captain multiplier tests apply to the full eligible fantasy score, including bonuses, if that is how the contest rules specify it.
- Classic and Captain lineups are validated with separate salary, roster, and eligibility rules.

## 3. Building the player outcome distributions

### 3.1 Minutes and role come first

Minutes are not a fixed input. Represent them with a distribution or scenario set that reflects:

- Starting status and expected rotation role
- Recent coach rotation changes and teammate availability
- Return-from-injury restrictions
- Foul risk and role-specific substitution patterns
- Blowout risk and late-game rotation changes
- Overtime probability

Minutes should be reconciled across the full team rotation. A regulation game supplies 240 player-minutes per team; overtime adds more. This is a useful coherence check, not a reason to force every player's minutes to a single point estimate.

Role should also be scenario-aware. A teammate scratch may change a player's minutes, touches, usage, assist chances, and shot mix together. Increasing one rate independently can miss those connected changes.

### 3.2 Separate opportunity from conversion

For each player, estimate opportunities such as:

- Field-goal attempts and 3-point attempts
- Free-throw attempts
- Potential assists and passes that lead to shots
- Rebound chances, conditioned on team and opponent misses
- Steal chances, deflections, and block chances
- Touches or possessions with turnover risk

Then estimate conversion rates for those opportunities. Examples include shooting percentage, assist conversion, rebound conversion, and turnover rate. These rates should be informed by season-long and role-specific data, with recent form included carefully.

A trailing 10-game rate can respond to real changes, but it is noisy. Blend recent results with longer windows and a player or role prior; give recent data more weight when there is evidence of a real role change. Record the effective sample size and avoid treating tracking measures as precise when coverage is sparse.

### 3.3 Simulate a coherent game

Independent Poisson or negative-binomial draws can be useful baselines, but choosing a distribution family does not by itself capture the relationships among stats. Prefer a game-level simulation that shares the same possessions, team state, and event outcomes across players.

A practical sequence is:

1. Sample availability, minutes, rotation, and game-state scenarios.
2. Sample team possessions and the distribution of team scoring opportunities.
3. Allocate player-level attempts, drives, and playmaking chances according to role and lineup context.
4. Resolve shot outcomes, free throws, assists, turnovers, rebounds, steals, and blocks with dependencies represented.
5. Build complete stat lines for both teams.
6. Apply the exact DraftKings scoring adapter to each stat line.

This creates meaningful relationships: a made field goal can have an assist; a rebound requires a miss; teammate scoring can convert a potential assist; an opponent shot miss creates rebound chances; and pace changes opportunity for both teams. The simulator need not reproduce every detail of a basketball possession at first, but it should not routinely create contradictory box scores.

### 3.4 Preserve uncertainty

For each player, retain a distribution, not just a mean. Useful summaries include:

- Mean and median fantasy points
- 10th, 25th, 75th, and 90th percentiles
- Probability of reaching a target score or value threshold
- Probability of key stat milestones and scoring bonuses
- Sensitivity to minutes, role, and game-state assumptions

Separate **outcome variance** from **forecast uncertainty**. A stable starter can have volatile game outcomes but a relatively confident minutes projection; a newly promoted reserve may have uncertainty in both minutes and per-minute production.

## 4. Dependencies that matter to lineup decisions

### Within-player dependencies

- More minutes create more chances across most categories.
- More usage often increases points and turnovers together.
- Made shots can produce assists for teammates.
- Rebounds depend on missed shots and player positioning.
- Steals and blocks are valuable but relatively sparse and volatile.

### Between-player and game dependencies

- Teammates can be positively related through pace, team scoring, and assist-to-scorer outcomes.
- Teammates can compete for the same shots, touches, or rebounds.
- Opposing players can benefit from a fast, high-scoring game, while a blowout can reduce late minutes for starters.
- A teammate scratch may raise one player's usage and another's minutes, but not necessarily by the same amount.
- A lineup should retain its game-level correlation structure through simulation and portfolio construction.

Do not convert these relationships into blanket rules. High usage is not automatically good at any price; low usage is not automatically safe; and a player with a high steal or block rate is not automatically a strong floor play.

## 5. From fantasy points to contest strategy

The scoring model ends at player fantasy-point distributions. The contest model starts after that.

A lineup optimizer should account for:

- Salary cap, roster slots, positions, team and game eligibility
- Contest type, entry count, payout curve, and number of entries
- Player ownership estimates and uncertainty in those estimates
- Lineup duplication and common roster constructions
- Correlation among players in the lineup and across the portfolio

The objective should match the contest. For a cash contest, emphasize the probability of beating the relevant field threshold and lineup robustness. For a large-field tournament, evaluate upper-tail lineup outcomes, payout-weighted return, and ownership leverage. For a multi-entry portfolio, manage shared failure modes and concentration across lineups. A lineup with the highest sum of mean projections is not automatically best for any of these objectives.

Use simulated field lineups and payout results where practical. Ownership is a probability distribution or range, not an unquestioned point estimate. Track projected duplication and how frequently a portfolio relies on the same fragile game or player assumption.

## 6. Validation and operating checklist

### Data and rule checks

- [ ] Save a timestamped snapshot of salaries, positions, injury status, projected lineups, game context, and source provenance.
- [ ] Confirm slate and contest format, including late-swap status and exact scoring rules.
- [ ] Flag missing, stale, conflicting, or implausible inputs instead of silently treating them as zero.
- [ ] Check team-minute totals against regulation minutes, while allowing overtime scenarios.
- [ ] Check that simulated attempts, makes, assists, rebounds, and turnovers are internally plausible.
- [ ] Keep scoring rules versioned by platform, sport, and contest format.

### Projection checks

- [ ] Compare minutes, opportunities, and fantasy-point forecasts against simple baselines.
- [ ] Backtest on chronological holdout slates; do not tune and evaluate on the same games.
- [ ] Measure minutes error, fantasy-point bias and error, interval coverage, and calibration of threshold probabilities.
- [ ] Review performance by role, salary tier, starter status, injury replacement status, and contest format.
- [ ] Test whether simulation results stabilize at the tail thresholds used by the optimizer. A fixed 10,000 draws is not automatically sufficient.
- [ ] Record model version, random seed, data timestamps, and assumptions for each run.

### Lineup checks

- [ ] Verify salary, roster slots, positions, player uniqueness, game eligibility, and platform upload format.
- [ ] Recalculate fantasy scores from the final simulated stat lines through the versioned rules adapter.
- [ ] Inspect exposure, correlation, duplication risk, and shared assumptions across the portfolio.
- [ ] Generate and validate a usable fallback lineup before optional research or optimization steps consume the remaining time.

## 7. Improvements to the original draft

1. **Do not use the trailing 10-game window as the sole rate estimate.** It is responsive but often too noisy. Use longer-term priors and role-aware shrinkage, then adjust quickly when evidence supports a true role change.
2. **Do not assume marginal distributions preserve covariance.** Independent Poisson or negative-binomial samples can miss the connections among attempts, makes, assists, rebounds, and teammate scoring. Simulate shared game states or explicitly model the dependencies.
3. **Do not infer double-double probability from rebound average alone.** The relevant quantity is the joint distribution of eligible stat categories, especially distance from thresholds and covariance between categories.
4. **Treat steals and blocks as upside sources, not automatic floors.** Their scoring weights are high, but the events are infrequent and noisy.
5. **Use the turnover example as arithmetic, not a strategy rule.** In the supplied example, 20 points, 8 assists, and 5 turnovers score 29.5 points from those categories. Whether that player is valuable still depends on salary, minutes, role, other stats, and the field.
6. **Make contest payout and opponents part of the last layer.** A player projection does not encode ownership, roster duplication, or the contest's payout curve.
7. **Add an operational fallback.** The system should preserve a valid lineup even if optional data feeds, simulations, or advanced optimization fail.

## 8. Recommended implementation order

1. Build and test a versioned DraftKings scoring adapter.
2. Establish a timestamped player, salary, position, injury, and game-context data contract.
3. Improve minutes and role distributions, including injury and rotation scenarios.
4. Add opportunity and rate models with uncertainty and sample-size controls.
5. Build coherent game-level simulation and validate its statistical behavior.
6. Connect player distributions to contest-aware lineup and portfolio optimization.
7. Backtest, monitor calibration, and add safe fallback behavior before expanding complexity.

## Sources and rule notes

- [DraftKings NBA Classic Rules & Scoring](https://www.draftkings.com/help/rules/4/70) — scoring values, milestone categories, salary cap, and eight-player Classic roster.
- [DraftKings NBA Series Rules & Scoring](https://www.draftkings.com/help/rules/4/137) — Captain multiplier and six-player Captain-format information.
- [DraftKings Showdown overview](https://support.draftkings.com/dk/en-us/game-style-showdowns-overview?id=kb_article_view&sysparm_article=KB0010694) — overview of the single-game Showdown format.

Rules were checked on October 13, 2026. Recheck the live rules page for the slate and contest being modeled, especially where scoring bonuses overlap or format-specific rules differ.

