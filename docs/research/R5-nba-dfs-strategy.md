# R5: NBA DFS strategy for DraftKings Classic and Showdown

Status: research memo, design phase only (no engine code).
Date: Tuesday Oct 13, 2026 (go-live is Tuesday Oct 20, 2026).
Scope: what expert writing, vendor studies, and academic papers say about winning DraftKings (DK) NBA tournaments, with numbers wherever they exist, and what that means for an engine that targets (1) top-1% finishes per contest and (2) avoiding a night with zero cashing entries.

## Bottom line

1. **The public evidence base is thin and old (VERIFIED as a finding of this search).** Most published NBA DFS numbers come from 2015 to 2021, were written by vendors who sell tools, and often sit behind paywalls or inside chart images. Treat every number below as a starting prior that our own data agents must re-measure, not as ground truth.
2. **The user's hunch is mostly right, with one real exception (VERIFIED theory, BET for our setting).** Both goals get better when our entries are *less correlated with each other* (they cover different ways the night can go). Academic work (Hunter, Vielma and Zaman; Haugh and Singal) shows this formally for "at least one entry wins." A simple model in Section 7 shows the same lever also cuts washout risk sharply. The exception is *inside* a single lineup: buying leverage (low-owned players, salary left unspent to avoid duplicates) usually costs some projected points, which lowers that lineup's own chance to cash. So the true tradeoff is "how many projected points do we give up for uniqueness," not "floor versus ceiling."
3. **"Floor" lineups are not automatically the anti-washout answer.** Haugh and Singal's rule is about the spread of *our score minus the cash line*. When that gap is expected to be negative (our expected score sits below the cash line), the way to raise the chance of clearing it is to *add* spread, not cut it. The cash line is set by field lineups that share our players, so only variance that makes us *different from the field* helps; stacking the same volatile game everyone stacks barely moves the gap. DK tournaments pay only about the top 20% to 27%, so most lineups face this situation. VERIFIED (theory), BET (that it holds for our lineups until measured). This makes the same lever (differentiation) serve both goals.
4. **Washout is driven by common-mode failure more than by entry count (model illustration, BET).** If our entries all lean on the same player or the same game, a single dud sinks everything. In the Section 7 model, 150 entries with high mutual correlation still wash out about 15% of the time, while 20 nearly independent entries wash out about 1%. Cross-format overlap (Classic and Showdown on the same game) is likely the biggest hidden source of this correlation.
5. **NBA correlation runs through the game, not the passer (BET synthesis of SUPPORTED sources).** Teammates fight over the same possessions, rebounds, and minutes (negative correlation), but they share the same pace, total, closeness of game, and overtime (positive correlation). The engine should simulate both channels and let stacking rules emerge rather than hard-coding them.
6. **Showdown is where duplication bites (VERIFIED arithmetic, SUPPORTED practice).** A 20-player pool allows only 232,560 Captain-plus-five combinations before salary rules, and fields cluster on a small set of those. A RotoGrinders analyst won a $1M NBA Finals Showdown partly by leaving salary unspent to avoid splitting. Measured NBA duplication rates do not exist in public writing; this must come from contest standings data.
7. **Late news is a structural edge in NBA (VERIFIED rules, SUPPORTED tactics).** The league's injury report rules create predictable news windows, and lineups built with late-game flexibility can pivot after the field has locked. The cost is giving up some early-game value, and it adds nightly workload near tip.
8. **Opening night is a special case.** Recent NBA opening nights have been two-game national TV doubleheaders (BET: verify the 2026-27 schedule). On a two-game night, Classic and Showdown share the same games, duplication rises, and washout correlation peaks. Plan for it as a separate scenario.

## How to read this memo

Labels:
- **VERIFIED**: I read the primary source and it reports measured data. Caveats on age and sample size are noted inline.
- **SUPPORTED**: credible expert or vendor claim, or a number I only saw in a search-engine summary because the page itself would not load. Pages that would not load are marked "(page not loaded)."
- **BET**: judgment, folklore, or my own inference with no data behind it.

Jargon used throughout:
- **GPP** (guaranteed prize pool): a tournament with top-heavy prizes. **Cash** or **min-cash**: finishing inside the paid places. **Cash line**: the lowest score that pays.
- **Ownership**: the share of the field's lineups that roster a player. **Chalk**: heavily owned players. **Leverage**: being over or under the field on a player relative to his chance of a big game.
- **Dupe** (duplicate): an identical lineup entered by someone else. Tied finishes split the combined prizes for those places.
- **Stack**: two or more players from the same team. **Game stack**: players from both teams in one game. **Bring-back** (or run-back): adding an opponent to a team stack.
- **Punt**: a minimum or near-minimum salary player. **Value play**: a cheap player projected well above his price, usually because an injury opened minutes.
- **SE**: single-entry contest. **MME** (mass multi-entry): playing 150 lineups in a 150-max contest.
- **Late swap**: replacing players whose games have not started yet. **Lock**: when a player's game starts and he can no longer be swapped.
- **CPT**: Showdown Captain (1.5x points and 1.5x salary). **UTIL**: utility slot.
- **Hindsight-optimal lineup**: the best possible lineup after the fact. It is not the same as the lineup that actually won.
- **Pace**: possessions per game. **Total**: the betting market's expected combined points. **Spread**: the expected margin.
- **Plus/Minus** (FantasyLabs metric): actual DK points minus the points a player's salary implies.
- **Exposure**: the share of *our own* lineups that include a player (compare with ownership, which is the field's share).
- **Usage**: the share of a team's possessions a player finishes with a shot, free throws, or a turnover while he is on the floor.
- **Variance**: how widely a score can swing around its expected value. **Floor**: a likely low-end outcome. **Ceiling**: a likely high-end outcome.
- **ROI** (return on investment): winnings minus entry fees, divided by entry fees.
- **R-squared**: the share of variation in one number explained by another (0 means none, 1 means all).
- **Garbage time**: late minutes of a lopsided game, usually played by bench players.

## 1. Correlation and stacking

### Findings

| Claim | Label | Source |
|---|---|---|
| NBA correlation matters less than in NFL or MLB because scoring piles up in small increments rather than big single events like touchdowns. | SUPPORTED | Dinkmeyer, Establish The Run (ETR), Oct 2024; Mears, FantasyLabs, Nov 2015 |
| Starting teammates were "fairly strongly correlated," more than the author expected; his explanation was that the game's total matters more than teammates stealing each other's stats. Coefficients were in charts, not text. | SUPPORTED | Mears, FantasyLabs, Dec 29, 2016 |
| Same-team big men tend to be negatively correlated (example: DeAndre Jordan and Blake Griffin about -0.40), mostly because one played more when the other sat. | SUPPORTED (page not loaded) | FantasyLabs, 2017 |
| Same-team players were generally negatively correlated; team PG total vs team SG total was -0.38; opposing players were "less significant." FanDuel scoring, 2012-13 to 2015-16. | VERIFIED (old, FanDuel scoring, one coefficient in text) | Whitestone, ianwhitestone.work |
| How well guards do against a matchup tracks pace (PG 0.57, SG 0.43); centers barely do (0.12). Across only 30 teams. | VERIFIED (tiny sample, 2016) | Mears, FantasyLabs, Jan 13, 2016 |
| The cleanest positive teammate link is assist to made basket (one event credits both players); usage inside a team is "close to zero-sum." | SUPPORTED (vendor, no coefficient) | Stokastic stacking article, Jul 2026 |
| Overtime happened in 6.2% to 6.4% of games (2013-14 to 2015-16, over 4,400 games); overtime games averaged 221.0 total points vs 201.2 (+19.8, about +10%); only 17% of overtime games went past one overtime. | VERIFIED (2013 to 2017 data) | Lem, RotoGrinders, Feb 2017 |
| About 5% to 7% of games go to overtime; game stacks probably add some value but not enough to use everywhere; they fit mid-size (4 to 6 game) slates best; prioritize spreads over totals; pricey teammates (example LeBron James and Anthony Davis) cannibalize, so their stack nearly needs overtime. | SUPPORTED | Dinkmeyer, ETR, Oct 2024 |
| Totals are the field's most common research starting point, so high-total games draw ownership and are often already priced into salaries. | SUPPORTED | Dinkmeyer, ETR, Oct 2024 |
| A big spread empties benches in the fourth quarter; tight projected games are preferred for stacks. | SUPPORTED (no data) | Stokastic stacking article, Jul 2026 |
| Don't optimize for game stacks the way you would in NFL or MLB. | SUPPORTED (vendor opinion) | Baker, Stokastic strategy guide, Jul 2026 |

**Synthesis (BET, but principled).** The apparent contradiction (starters "positively correlated" vs "teammates negatively correlated") resolves once you separate two channels. A shared game-level shock (fast pace, high scoring, a close game that keeps starters in, overtime) lifts everyone in that game. A zero-sum split of possessions, rebounds, and minutes inside one team pushes teammates apart, most strongly for players who share a position or a backup and starter at the same spot. Which effect wins depends on the pair.

**Blowouts vs shootouts (BET with support).** Blowout risk hurts starters on both sides and helps bench players. ETR notes that a likely blowout can make the *bench* the right stack. Close games help starters and raise overtime odds. No source I found measured how many minutes starters lose by spread size; that is an open question for the game-log agent.

### Recommendations

- **Model correlation as two layers: game-level shocks (pace, scoring, final margin, overtime about 6%) plus a within-team allocation of minutes and usage that sums to a fixed total.** Results: correlation signs come out right for every pair, including negative starter/backup pairs; cost: more modeling work up front, but no hand-tuned stacking rules later.
- **Do not hard-code stacking or bring-back rules for Classic.** Results: avoids forcing a weak NFL habit onto NBA; the simulation decides when a stack is worth it; workload: none nightly.
- **Feed the simulation an explicit blowout and overtime process.** Results: bench-heavy and overtime-dependent builds get credit only when the game script supports them; cost: needs a margin model from spreads, which a data agent must calibrate.

## 2. Classic GPP construction norms

### Findings

| Claim | Label | Source |
|---|---|---|
| Of 2017-18 DK NBA GPP winners: over 61% used the full $50,000, 86.25% used at least $49,900, average $49,923. Sample size not stated. | VERIFIED (vendor study, one season) | LaMarca, FantasyLabs, Oct 12, 2018 |
| Winners' highest-owned player averaged 42.75%; winners averaged 2.5 players under 10% owned; 55% had at least three under 10%; more than four under 10% was "rare" (wording ambiguous); lowest-owned player averaged 4.78%; 30% had at least one player at 2.5% or less. | VERIFIED (same caveats) | LaMarca, FantasyLabs, 2018 |
| Winners paid about $10,100 for their priciest player and $3,900 for their cheapest; only 30% had no player at $9,000 or more. | VERIFIED (same caveats) | LaMarca, FantasyLabs, 2018 |
| Players priced $4,000 or less and projected for at least 28 minutes averaged +3.97 Plus/Minus (+5.21 when also at least 0.70 fantasy points per minute). This is the "injury-created value" effect: DK salaries lag sudden role changes. | VERIFIED (vendor data, 2017-18) | LaMarca, FantasyLabs, 2018 |
| A backup PG at $4,200 who inherits a starter's role is "worth" about $1,500 to $2,000 more than his price; the worked example puts such a chalk value play at 45% projected ownership. | SUPPORTED (vendor example) | Baker, Stokastic, Jul 2026 |
| Target the top 20% of lineups by projection while beating about 30% of the field on ownership. | BET (vendor rule of thumb, no data) | Baker, Stokastic, Jul 2026 |
| Single-entry builds should sit between cash-game and MME risk; NBA's lower variance makes the single-entry approach friendlier than in NFL. | SUPPORTED | RotoGrinders single-entry articles; FantasyPros, 2020 |
| On large main slates, gross lineup shapes look similar across field sizes; small contests favor the strongest lineup, large fields justify calculated risks. | SUPPORTED (vendor opinion) | Baker, Stokastic, Jul 2026 |
| MME default: cap each player around 3 to 4 times his projected ownership, then hand-tune; on three-game slates, heavier chalk exposure is acceptable because the field is stuck with it too. | BET (vendor heuristic) | Stokastic multi-entry article, Jul 2026 |
| With two-game slates, ownership concentrates and tied scores become much more frequent. | SUPPORTED (page not loaded) | RotoWire cheat sheet |
| On big main slates, dupes usually don't move the needle; they matter most in Showdown and two-game slates. | SUPPORTED (vendor) | Stokastic sims article, Jul 2026 |

**Not found:** how many games winning Classic lineups typically span, and typical player-pool sizes. These are open questions for the contest-results agent.

**Reading the chalk numbers (BET).** The 2017-18 winners typically held one heavily owned anchor (around 40%), about five players between 10% and 40%, and two or three under 10%. That is a "mostly right, a little different" profile, not a contrarian one. Whether it still holds in 2026 is unknown.

### Recommendations

- **Let contest size drive the leverage dial, not a fixed rule.** Results: SE and small fields get near-optimal lineups with one or two leverage spots; 150-max gets broader coverage; workload: the contest type becomes an input, not a manual choice.
- **Treat injury-created value plays as the main source of Classic edge and of chalk risk at the same time.** Results: the engine plays them when they are underpriced but caps how many of our lineups depend on one cheap player; cost: needs reliable late injury data.
- **Do not enforce a salary floor in Classic; let the simulation decide.** Results: the cap is used when it pays, and salary is left only when dupes are a real threat (two-game slates); workload: none.

## 3. Showdown (Captain Mode)

### Findings

| Claim | Label | Source |
|---|---|---|
| CPT costs 1.5x and scores 1.5x, so a player's points per dollar are unchanged at CPT; the real question is whether his extra half-score beats what the higher salary forces you to give up elsewhere. | VERIFIED (arithmetic) | OnlyDFS, Sep 2026; Edgerton, RotoWire, May 2021 |
| Actual winners, 19 DK NBA Showdown slates (late May 2019, playoff-heavy): 17 of 19 paid at least $11,400 at CPT; average CPT just under $14,800; average salary used over $49,400; all but one at least $48,700; 52.6% used a player at $2,000 or less; most were 3-3 or 4-2; only one was 5-1. | VERIFIED (small, playoff-heavy sample) | LaMarca, FantasyLabs, May 30, 2019 |
| Hindsight-optimal lineups, 124 DK NBA Showdown slates (January 2022): average CPT just over $13,500; 22.6% had a CPT at $17,100 or more; average salary just under $47,900; full cap in only 7 slates; over $49,500 in 42 (33.9%). The article has internal arithmetic errors (it says 11 of 124 is 11.3%, and that 50% were under $49,000 though its own counts imply about 44%). | VERIFIED (optimal, not winners; arithmetic issues) | LaMarca, FantasyLabs, Jun 4, 2023 |
| Over 350 NBA Showdown slates: over 80% of optimal lineups paid at least $10,000 at CPT; 3-3 and 4-2 were the most successful splits; over 80% of optimal lineups had at least one bench player; about 15% had a bench player at CPT. | SUPPORTED (page not loaded) | DFS Karma |
| "The majority of winning lineups" are 3-3; stacking one team is "ill-advised." No data shown. | SUPPORTED | Edgerton, RotoWire, May 2021 |
| A 5-1 build (Kevin Durant as the lone Warrior) won the DK $1M NBA Finals Showdown, deliberately leaving salary ($49,100 used) to cut duplication. | VERIFIED (one first-person result) | Cole, RotoGrinders, Jun 2018 |
| An NBA Showdown ($800K, about 44,777 entries) ended in a 19-way tie for first at 271.13 points with a 1.8%-owned CPT (Daniel Theis) and $49,500 salary. | SUPPORTED (page not loaded) | Awesemo/Stokastic review, 2020 |
| An optimizer put Damian Lillard at CPT in 19% of optimal lineups while the author expected 25%+ CPT ownership: the field over-captains the obvious star. One slate. | SUPPORTED | Dinkmeyer, ETR, Aug 2020 |
| In NBA, production relative to expectation is tighter than NFL, so overall construction matters more than CPT choice. | SUPPORTED (opinion) | Dinkmeyer, ETR, Aug 2020 |
| Players who share minutes (backup and starter at the same spot) rarely appear together in winning lineups, except after a blowout or foul trouble. | SUPPORTED | Dinkmeyer, ETR, Aug 2020 |
| CPT choice is one of the biggest drivers of duplication; leaving salary unspent reduces dupes. | SUPPORTED | Baker, Stokastic, 2026; LaMarca, FantasyLabs, 2023 |
| NFL Showdown data: lineups at or under $49,500 averaged 4.86 dupes vs 23.68 above $49,500; salary used vs dupe count had R-squared of only 0.16 and was nonlinear. | VERIFIED for NFL; transfer to NBA is BET | Main, ETR, Sep 2021 and ETR Showdown pages |
| NFL Showdown: a lineup built about 500 times turned a $500,000 first prize into about $1,559 each, and it won only 0.08% of simulations. | VERIFIED for NFL; transfer is BET | RotoGrinders NFL Showdown tips |
| In small fields (example: 20 entries), being contrarian is "just being wrong slightly more often." | BET (vendor opinion) | OnlyDFS, Sep 2026 |

**Both-teams rule.** DK requires at least one player from each team, so 5-1 is the most lopsided legal split. In a blowout, this forces at least one player from the losing side, which pushes builds toward that side's bench or garbage-time minutes (BET).

**Why Showdown dupes are common (VERIFIED arithmetic).** With 20 players there are 232,560 CPT-plus-five combinations before salary and team rules; with 24 players, 807,576. Real fields cluster on a tiny fraction of those, so a 40,000-entry contest will contain many identical lineups. Public writing has no measured NBA dupe rate.

**Game script (BET).** Close games and overtime (about 6%) reward stars at CPT. Blowouts move fourth-quarter minutes to benches on both teams, which is when cheap bench players and lopsided splits win. Note the gap between winners (salary over $49,400) and hindsight-optimal lineups (about $47,900): the best lineup often leaves money because a cheap player beat expectations, while the field crowds the cap.

### Recommendations

- **Price duplication directly into payouts in the simulation (tied lineups split the prize) rather than using a salary rule.** Results: the engine leaves salary or picks an off-beat CPT only when the split risk outweighs the lost points; cost: needs a field model that predicts how often each lineup gets built.
- **Let CPT choice, team split, and punt use emerge from simulation.** Results: avoids baking in 2019-era playoff patterns; workload: none nightly.
- **Model blowout and overtime per game for every Showdown.** Results: bench players get correct upside in lopsided scripts; cost: depends on the same margin model as Classic.

## 4. Winning scores, top-1% lines, cash lines, and payouts

### Findings

| Claim | Label | Source |
|---|---|---|
| DK GPP cash line (top 20% at the time) needed about 5.48 points per $1,000, which is about 274 points on a $50,000 cap. Contests with at least $10K prize pools and 100+ entrants. Bigger contests had higher winning scores. | VERIFIED (2016 data; league pace was lower then) | Hourigan, RotoGrinders, Mar 2016 |
| Same study: the score needed to cash *fell* as contest size grew, which the author suspected came from many overly contrarian "dead" lineups in big fields. Relevant to goal 2: big fields may be easier to min-cash. | SUPPORTED (search summary; the chart values were images I could not read) | Hourigan, RotoGrinders, Mar 2016 |
| 2020 to 2021 DK NBA GPP winners: 349.5, 360, 364.25, 369.25, 376.5 (39,215-entry and similar contests), 350.75 on a four-game slate, 389.25 on a nine-game slate; hindsight-optimal lineups reached 411.75 to 432.25. | SUPPORTED (page not loaded) | Stokastic/Awesemo lineup rewinds, Dec 2020 to Mar 2021 |
| One February 2021 GPP: 58,823 entries from 20,434 players; only 3,163 players (15.5%) made a profit. | SUPPORTED (page not loaded) | Stokastic lineup rewind, 2021 |
| One NBA Showdown winning score: 271.13 (see Section 3). | SUPPORTED (page not loaded) | Awesemo review, 2020 |
| DK GPP listings showed 20% to 27% of entries paid, min-cash about 1.5x to 2x the entry fee, and rake (the site's cut) of about 10% to 12%. Flagship Millionaire Maker example: 22% paid, 33.3% of the prize pool to first; a flatter contest paid 26.1% with 8% to first. These listings were NFL contests, but DK uses similar templates across sports (BET). | VERIFIED for those NFL listings | 4for4 "Best GPPs" listings, 2017 and 2021 |
| Rake is "often around 10% to 15%." | SUPPORTED | Smith, Stokastic contest selection, Jul 2026 |

**What I could not find:** any current table of NBA top-1% thresholds by slate size or contest size, for Classic or Showdown. I did not interpolate one. The contest-results agent should compute: winning score, top-1% score, and min-cash score by number of games on the slate, entry count, and contest type, plus each one's gap above the field's median score.

**What the payout structure implies for washout (VERIFIED arithmetic).** If about 20% of entries cash, one lineup fails to cash about 80% of the time. Three fully independent lineups all miss about 51% of the time; ten all miss about 11%. Real lineups are not independent, so these are best-case numbers (see Section 7).

### Recommendations

- **Treat score thresholds as data, re-measured weekly, not as constants.** Results: the simulation's top-1% and cash lines stay calibrated as scoring and pace drift; cost: a recurring data job.
- **Model each contest's actual payout table, including rake and the split rule for ties.** Results: the engine optimizes the real prize and cash structure, not a generic one; workload: payout tables must be captured per contest each night.

## 5. Late news and late swap

### Findings

| Claim | Label | Source |
|---|---|---|
| NBA teams must post a participation status by 5 p.m. local time the day before a game (1 p.m. local on game day for the second night of a back-to-back), file a game-day report between 11 a.m. and 1 p.m. local (8 to 10 a.m. for tips at 5 p.m. or earlier), and update continually. These are the 2025-26 rules; confirm for 2026-27. | VERIFIED | official.nba.com injury report page |
| The league fines inaccurate reports (Orlando $25,000 in April 2026; Philadelphia $100,000 in 2024 over Joel Embiid). | SUPPORTED | AP/Fox and Bay News 9 reports |
| Questionable players suit up "about half the time"; assume they play, or build separate "in" and "out" lineups. | BET (no data cited) | Baker, Stokastic, Jul 2026 |
| Keep at least three roster spots in later games so you can react to news; the cost is passing on stronger early-game plays when news never comes. | SUPPORTED | Baker, Stokastic, Jul 2026 |
| On injury-heavy slates, cut early-game exposure (example: one player from about 70% to 23%) so late spots stay open. A post-lock pivot (Blake Wesley after Tre Jones was ruled out) finished only 11% owned because the field had no room left; a pre-lock value darling finished 32.1% owned with -51.4% ROI. One slate. | SUPPORTED (vendor, one example) | Engleman, Stokastic, Jul 2026 |
| Upload a full pool 30 minutes before lock, then make one surgical swap if a starter is ruled out. | SUPPORTED | Stokastic multi-entry article, Jul 2026 |
| Put game-time decisions in flexible slots (UTIL, then G or F) so any position can replace them. | SUPPORTED | FantasyPros, Jul 2020 |
| Starting lineups typically post 30 to 60 minutes before tip. | BET (vendor claim) | OnlyDFS, Sep 2026 |
| DK has experimented with tournaments that turn late swap off. | SUPPORTED | Stokastic, Jul 2026 |
| Only players whose games have not tipped can be swapped. Showdown covers one game, so every slot locks at that tip (my corollary). | SUPPORTED (vendor description of DK rule) | Baker, Stokastic, Jul 2026 |

**How ownership shifts ("new chalk") (BET with one example).** News before the first lock creates a crowd on the cheap replacement (the 45% backup PG in Baker's example). News after the first lock produces low-owned pivots, because many field lineups have already locked their flexible slots. That asymmetry is the late-swap edge.

### Recommendations

- **Represent each questionable player as an explicit in/out scenario with a probability, and keep lineups for both branches.** Results: no lineup dies on a scratch, and the "out" branch captures the cheap-replacement value; cost: needs measured play rates by designation (open question).
- **Score late-game roster flexibility as a value inside the simulation instead of a fixed "three late spots" rule.** Results: flexibility is bought only on nights with real uncertainty; workload: the user's near-tip re-run becomes a planned step.
- **Build a re-run that touches only unlocked slots and re-optimizes for the post-news field.** Results: the engine exploits post-lock pivots the field cannot make; workload: the user must be available near late tips, as they already expect.

## 6. Situational effects

### Findings

| Claim | Label | Source |
|---|---|---|
| Back-to-backs (2014-15 season, starters only): league-wide minutes dropped only about 0.2 per game on the second night; players averaging 33 minutes lost about 1, those at 36 lost about 2; the top 40 fantasy players scored about 7% (about 3 DK points) less. Players under 25 minutes saw negligible effects. | VERIFIED (one season) | Rikleen, RotoWire, Dec 2016 |
| Over 20,000 games: second-night teams play slower, shoot worse, get fewer offensive rebounds, and allow better shooting; effects about 0.5% to 2%, statistically significant. | SUPPORTED (author's blog summary of a Cureus paper; paper not read) | Bailey and Aicardi, Cureus, 2026 |
| Teams win about 44% on the second night of a back-to-back vs 51% with normal rest. | SUPPORTED (page not loaded) | SportsBettingDime, 2026 |
| The Player Participation Policy (since 2023-24) fines teams $100,000, then $250,000, then $1M more per repeat violation for resting healthy stars (All-Star or All-NBA in the prior three seasons) in national TV and NBA Cup games, and requires at least one star available each game. | SUPPORTED | CBS Sports, Sep 2023 |
| Stars missed roughly 15% fewer games in the policy's first season. Back-to-backs where a star played one night but not the other: 30% (2022-23), 22%, then 24% (2024-25). | SUPPORTED (page not loaded) | Silver press conference via news; Sportico, 2025 |
| Home teams won 54.4% of 2024-25 regular-season games; home edge has declined for decades. | SUPPORTED (page not loaded) | Neil Paine, 2025; The Ringer, 2021 |
| Teams favored by 10+ (2015-16) showed mixed player Plus/Minus by team; no clear blowout penalty. Small sample. | VERIFIED (weak) | Monighetti, FantasyLabs, Feb 2016 |
| Don't try to game blowouts across 150 lineups; they even out. | BET (vendor opinion) | Stokastic multi-entry article, Jul 2026 |
| Early season: pricing is "more forgiving" since salaries anchor to last season; bench and rookie minutes are hard to project; role changes the market hasn't priced yet create value. One writer argues week one has the *least* variance (clear injury picture, starters play heavy minutes). | BET (conflicting opinions) | Razzball 2022; LineStar newsletter; RotoWire Yahoo pieces |
| Favorable game environments are often already priced into DK salaries; betting props are the market's projection. | SUPPORTED | Dinkmeyer, ETR, 2024; Baker, Stokastic, 2026 |

**How much is priced in (BET).** DK salaries move slowly and react to role changes with a lag (the +3.97 Plus/Minus for cheap high-minute players suggests the lag is real). Betting markets move fast. The working assumption: player props and game lines already price rest, back-to-backs, and travel; DK salaries do not fully. Edge comes from projecting minutes better than the salary does, not from re-discovering effects the betting market already knows.

**Travel.** I found no usable NBA DFS-specific travel data in this pass. Treat travel as a small effect that the betting lines already capture (BET).

### Recommendations

- **Anchor projections to betting markets (props and game lines), then adjust minutes for news.** Results: situational effects are priced once, by the most efficient source; cost: depends on an odds feed owned by another agent.
- **Widen projection uncertainty for the first two to three weeks rather than adding early-season rules.** Results: the simulation naturally favors players whose minutes are secure and spreads exposure on uncertain roles; workload: one tunable "early-season" variance setting.
- **Raise rest-risk probabilities for stars on the second night of back-to-backs in games that are not national TV.** Results: fewer lineups built on a star who sits; cost: needs the national TV schedule.

## 7. The two-goal tradeoff (and the user's hunch)

### What the formal work says

- **Hunter, Vielma and Zaman (MIT, 2016), VERIFIED for DK hockey.** The objective is literally "maximize the probability that at least one of our entries wins." The math (a submodular objective) means a greedy one-lineup-at-a-time build gets at least about 63% of the best possible result. Each lineup should have a high mean and high variance, and lineups should overlap little. They capped shared players between lineups (best values 4 to 7, depending on the number of games), and aggressive stacking beat no stacking. Over 38 DK hockey contests in late 2015 they finished top ten multiple times. Applying these settings to NBA is BET.
- **Haugh and Singal (Management Science, 2021), VERIFIED for FanDuel NFL 2017.**
  - For a cash-style contest (double-up), they argue (as intuitively clear outside "pathological cases," not as a proof) that the best portfolio is the single best lineup entered N times.
  - For a single lineup trying to clear a threshold, the quantity that matters is *our score minus the threshold*, where the threshold itself depends on the field. If that gap is expected to be positive, cut its variance. If it is expected to be negative, *add* variance. Because field lineups share our players, only variance that differs from the field's moves this gap.
  - For top-heavy contests: build a diversified set of lineups, each with high mean and variance, that don't compete with each other. They model opponents' lineups statistically (a Dirichlet-multinomial model) to estimate the field.
  - Results: over 350% ROI across 17 weeks at $50 a week with 50 entries, but "very high variance." In their collusion table, their model put the average weekly probability of a *losing* week at about 49% even for the strong portfolio. That is a model estimate, not a count of real losing weeks, and a losing week means net loss, not zero cashes.

### A simple washout model (VERIFIED arithmetic; the model itself is BET)

Assume every entry has the same chance to cash (20%) and entries share a common correlation (rho) through a single "how did the night go" factor. Probability that **no entry cashes**:

| Entries | rho 0 | rho 0.2 | rho 0.4 | rho 0.6 | rho 0.8 |
|---|---|---|---|---|---|
| 3 | 51% | 55% | 59% | 63% | 69% |
| 10 | 11% | 22% | 33% | 44% | 57% |
| 20 | 1.2% | 9.6% | 21% | 34% | 50% |
| 40 | 0.01% | 3.3% | 13% | 26% | 45% |
| 150 | about 0% | 0.3% | 4.2% | 15% | 35% |

Same model, probability that **at least one entry finishes top 1%** (each entry 1% on its own):

| Entries | rho 0 | rho 0.2 | rho 0.4 | rho 0.6 | rho 0.8 |
|---|---|---|---|---|---|
| 3 | 3.0% | 2.9% | 2.8% | 2.5% | 2.1% |
| 20 | 18% | 15% | 12% | 8.8% | 5.4% |
| 150 | 78% | 52% | 35% | 21% | 11% |

Holding each lineup's own odds fixed, lowering the correlation between our lineups improves *both* goals at once. Entry count matters a lot when correlation is low, but once correlation is high, adding entries buys little. We do not yet know what correlation real NBA portfolios show (see Open questions), so read the table as direction, not level.

### Practitioner wisdom

- Clumped, similar lineups raise volatility and make you compete against yourself for the top spots (SUPPORTED, Stokastic diversification article).
- Don't use the same lineup for cash games and tournaments; cash builds chase floor, tournaments chase ceiling and leverage (SUPPORTED, Baker, Stokastic, 2026).
- "80/20" cash/GPP bankroll splits are common (4for4, Razzball); these are folklore with no published risk-of-ruin math (BET). One 4for4 writer notes cash games carry their own correlated risk: a bad week loses all of them.
- Leverage builds "win big fields" but "lose most nights" (BET, OnlyDFS opinion).

### Evidence on the hunch

**For (the goals conflict less than they look):**
1. Lower correlation between our entries improves both goals (Hunter; Haugh and Singal; table above).
2. With roughly 20% to 27% of the field paid, most lineups' expected scores sit below the cash line, so even the cash goal rewards variance that sets us apart from the field (Haugh and Singal's rule). Variance shared with the field (the popular stack) does not help. So floor-chasing does not automatically lower washout, and "maximize lineup variance" is not a safe anti-washout rule either: differentiation is the lever. VERIFIED theory, BET until measured on our lineups.
3. Washout comes from shared failures (one player, one game, one late scratch in every lineup). Coverage removes exactly those.

**Against (where the goals truly trade off):**
1. Inside a lineup, leverage and anti-duplication usually cost projected points (low-owned players, a cheaper CPT, salary left unused). That lowers that lineup's own cash odds a bit.
2. On low-volume nights (only SE and a few 3-max entries), washout is common no matter what: five independent entries at 20% each still all miss about 33% of the time.
3. Even the strong academic portfolio had a modeled chance of a losing week of about 49%. Diversification spreads results; it does not make top-heavy contests safe.

**Net (BET).** The hunch holds on the portfolio level and partly fails inside individual lineups. The real dial is "how much projected mean do we trade for uniqueness and coverage."

### Recommendations

- **Make "correlation between our own entries" a first-class quantity the simulation measures and reports for each contest and for the whole night.** Results: both goals get a shared, visible lever; workload: one extra number in the nightly report.
- **Optimize goal 1 per contest, then use goal 2 as a portfolio-level check that may override only when the cost to top-1% probability is small.** Results: washout protection without quietly giving up tournament equity; cost: the user must choose an exchange rate (see Open questions).

## 8. Cross-contest correlation (Classic and Showdown sharing games)

**What exists publicly.** Almost nothing. I found no article that explicitly manages exposure to the same game across Classic and Showdown (gap, BET). SaberSim's podcast notes mention a "Portfolio Sim EV" metric, so some tools at least evaluate a whole portfolio (SUPPORTED, show notes only).

**What follows from the mechanics (BET).**
- A Showdown entry on Game X is 100% exposed to Game X's shocks (pace, final margin, overtime, a star's early exit). Classic lineups that lean on Game X share those shocks.
- A dud game (blowout with a slow pace, or a star hurt in the first quarter) can then sink the Showdown entries *and* the Classic entries that leaned on it. That is the exact common-mode failure that drives washout.
- On small nights the overlap is unavoidable. On a two-game night every Classic lineup must use both games, and the Showdowns are those same games.

### Recommendations

- **Simulate the whole night jointly, using the same game outcomes for every contest.** Results: cross-format correlation is measured, not guessed; cost: one shared simulation layer instead of separate per-contest runs.
- **Track and report "share of our total entries exposed to each game" across formats, with an optional soft cap as a hypothesis to test.** Results: the user sees concentration risk before lock; workload: one table in the nightly report.
- **On big Showdown nights, consider using Classic to cover the other games rather than doubling down on the Showdown game, but only if the per-contest cost is small.** Results: likely lower washout probability; cost: possible small loss of Classic top-1% odds, which the simulation must quantify.

## Open questions

Each question lists who should answer it.

1. **Current top-1%, winning, and min-cash scores** for DK NBA Classic by number of games and entry count, and for Showdown by entry count; the gap above field median. Owner: contest-results / ResultsDB agent.
2. **Measured NBA Showdown duplication.** How often is the winning lineup duplicated, how are dupe counts distributed, and how do they relate to salary used and CPT ownership? Owner: contest-standings agent.
3. **Team splits (5-1, 4-2, 3-3) and CPT salary among NBA Showdown top-1% lineups** in recent regular seasons, not playoffs. Owner: contest-standings agent.
4. **CPT ownership vs how often each player is the optimal CPT.** Is the obvious star over-captained as a rule? Owner: contest-standings agent.
5. **Play rates by injury designation** (probable, questionable, doubtful) and when news typically lands relative to tip. Owner: injury-report data agent.
6. **Minutes lost by starters by closing spread and actual margin;** current overtime rate. Owner: NBA game-log agent.
7. **A current DK-scoring correlation matrix** for teammates and opponents by role (starter/bench, position) and by game environment. Owner: NBA game-log agent.
8. **Games spanned and player-pool size of winning Classic lineups** by slate size. Owner: contest-results agent.
9. **Early-season projection error** (weeks 1 to 3 vs later) for minutes and points. Owner: projections/backtest agent.
10. **Exact payout tables and rake** for the contests the user actually enters, and whether any of them disable late swap. Owner: DK lobby agent.
11. **What between-entry correlation do real portfolios show?** The Section 7 washout table can't be read at a real level until we know whether typical 20-max or 150-max portfolios sit near 0.2 or near 0.6, and how correlated a night's Classic and Showdown entries are. Owner: backtest agent (replay past slates with simulated portfolios).
12. **Exchange rate between goals** (how much top-1% probability the user will give up for a given cut in washout probability). Owner: the user, as a product decision.
13. **The 2026-27 opening-week schedule** (is opening night again a two-game doubleheader?). Owner: schedule agent.

## Implications for the architecture

1. **The simulation must be joint and game-centric.** It should draw one set of game outcomes (pace, scoring, final margin, overtime, injuries during the game), then split minutes and usage within each team, then score every contest's lineups from the same draws. This one design choice delivers correct NBA correlation, cross-format washout measurement, and Showdown game-script effects.
2. **A field (opponent) model is required, not optional.** Top-1% probability, cash lines, and prize splits from duplicates all depend on what the rest of the field builds. Haugh and Singal's statistical opponent model is a reasonable starting template.
3. **Payout evaluation must use each contest's real table, including ties.** Duplication is a payout effect, so it belongs in the scorer, not in heuristics.
4. **Portfolio construction can follow the proven greedy recipe:** add one lineup at a time, choosing the lineup that most increases the contest objective given lineups already chosen. The approximation guarantee (at least about 63% of the best possible) makes this a safe default.
5. **Late news needs a scenario layer** (in/out branches with probabilities) and a re-run mode that only touches unlocked slots.
6. **Thresholds and correlations are data products,** refreshed on a schedule by data agents, not constants in code.

### Strategy rules worth encoding as constraints

These are DK rules, mechanical facts, or guardrails against catastrophic failure:
- DK roster rules: Classic positions, $50,000 cap, at least two games; Showdown one CPT plus five UTIL, both teams required, CPT at 1.5x salary and points.
- Lock and late-swap feasibility: never change a locked slot; Showdown locks entirely at tip.
- Never roster a player ruled out; questionable players only through explicit in/out scenarios.
- Never enter the same lineup twice in one tournament (it can only split with yourself).
- A guardrail on maximum overlap between our own lineups in one contest (start loose, informed by Hunter et al., then tune from simulation).
- A guardrail on the share of the night's entries depending on any single player, and (as a tested hypothesis) on any single game across formats.

### Things the simulation should discover on its own

- Whether and when to stack teammates, add bring-backs, or game-stack.
- Showdown CPT choice, team split (3-3, 4-2, 5-1), and punt usage.
- Salary left unused (Classic and Showdown).
- How many chalk players and how many low-owned players each lineup carries, by contest size.
- How much leverage to take in SE vs 3 to 20-max vs 150-max, and in fields under 100 (first place only).
- Exposure caps per player (the "3 to 4 times ownership" heuristic is a prior to test, not a rule).
- How much to pay for late-swap flexibility on a given night.
- Blowout and overtime handling.
- How much to shade toward cash-friendly builds on low-volume nights to control washout.

## Sources

Academic
- Hunter, Vielma, Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming," arXiv 1604.01455 (2016): https://arxiv.org/abs/1604.01455v3 and https://ar5iv.arxiv.org/html/1604.01455
- Haugh and Singal, "How to Play Fantasy Sports Strategically (and Win)," Management Science (2021), DOI 10.1287/mnsc.2019.3528: https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.2019.3528 ; slides read in full: https://cfe.columbia.edu/sites/default/files/content/slides/How%20to%20Play%20Fantasy%20Sports%20Strategically%20(and%20Win).pdf ; SSRN: https://papers.ssrn.com/abstract=3393127
- Bailey and Aicardi, "Running on Empty: How Back-to-Backs Impact Pace and the Four Factors of Basketball Success," Cureus (2026), via author blog: https://economistwritingeveryday.com/tag/max-aicardi/ ; paper: https://www.cureusjournals.com/articles/12833-running-on-empty-how-back-to-backs-impact-pace-and-the-four-factors-of-basketball-success
- Getty, Li, Yano, Gao, Hosoi, "Luck and the Law," SIAM Review (2018) (background only): https://dspace.mit.edu/handle/1721.1/119466

League
- NBA official injury report rules (2025-26): https://official.nba.com/nba-injury-report-2025-26/
- Player Participation Policy: https://www.cbssports.com/nba/news/nba-load-management-board-approves-rules-that-fine-teams-if-star-players-sit-certain-games
- Sportico load management data (page not loaded): https://www.sportico.com/leagues/basketball/2025/nba-injuries-load-management-data-participation-1234849899/
- Injury report fines: https://baynews9.com/fl/tampa/sports/2026/04/09/nba-fines-magic--25-000-for-injury-report-listing-violation-monday-on-black ; https://fox29.com/sports/nba-fines-76ers-100000-for-violating-injury-reporting-rules-in-the-game-embiid-returned
- Home court: https://neilpaine.substack.com/p/whats-a-home-playoff-game-worth-now ; https://www.theringer.com/2021/06/01/nba/what-happened-to-home-court-advantage

FantasyLabs
- LaMarca, "What Can We Learn from Winning NBA DFS Lineups on DraftKings?" (Oct 2018): https://www.fantasylabs.com/articles/2018-nba-dfs-draftkings-fanduel-gpp-tournament-strategy/
- LaMarca, "5 Tips to Dominate the DraftKings NBA Showdown Format" (May 2019): https://www.fantasylabs.com/articles/nba-dfs-tips-picks-analysis-draftkings-showdown-format-strategy/
- LaMarca, "NBA DFS: 5 Rules for Attacking the DraftKings NBA Showdown Format" (Jun 2023): https://www.fantasylabs.com/articles/nba-dfs-5-rules-attacking-draftkings-nba-showdown-format-fantasy-basketball/
- Mears, "Rethinking Stacking and Correlations in NBA DFS" (Nov 2015): https://fantasylabs.com/?p=4795
- Mears, "Daily Fantasy NBA Player Correlations" (Dec 2016): https://www.fantasylabs.com/articles/daily-fantasy-nba-player-correlations/
- FantasyLabs correlation post with Jordan/Griffin example (page not loaded): https://fantasylabs.com/?p=40334
- Mears, "What's More Important in NBA DFS: Matchup or Pace?" (Jan 2016): https://www.fantasylabs.com/articles/whats-more-important-in-nba-dfs-matchup-or-pace/
- Monighetti, "NBA Trend of the Day: Games With Double-Digit Spreads" (Feb 2016): https://www.fantasylabs.com/articles/dfs-trend-of-the-day-2316/

Establish The Run
- Dinkmeyer, "How and When to Game Stack in NBA DFS" (Oct 2024): https://establishtherun.com/game-stacking-in-nba-dfs/
- Dinkmeyer, "DFS NBA Top Plays: August 15th Showdown" (Aug 2020): https://establishtherun.com/?p=279319
- Main, "How to Create Unique Showdown Lineups" (NFL, Sep 2021): https://establishtherun.com/how-to-create-unique-showdown-lineups/
- ETR NFL Showdown breakdown pages with dupe statistics, for example: https://establishtherun.com/showdown-breakdown-cowboys-at-ravens/

RotoGrinders
- Hourigan, "What it Really Takes to Win an NBA GPP" (Mar 2016): https://rotogrinders.com/articles/what-it-really-takes-to-win-an-nba-gpp-1210935
- Lem, "Banking On Overtime" (Feb 2017): https://rotogrinders.com/articles/banking-on-overtime-1710010
- Cole, "Maximizing NBA Finals DraftKings Showdown Winnings" (Jun 2018): https://rotogrinders.com/articles/maximizing-nba-finals-draftkings-showdown-winnings-2556869
- NFL Showdown tips (dupes example): https://rotogrinders.com/articles/nfl-dfs-showdown-strategy-tips-for-building-expert-showdown-lineups-3800741
- Single-entry approach: https://rotogrinders.com/articles/building-gpp-lineups-the-single-entry-approach-1024957

Stokastic (vendor content with promo codes; commercial interest noted)
- Stacking strategy (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-stacking-strategy
- Strategy guide, Baker (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-strategy-guide
- How to win DraftKings DFS, Baker (Jul 2026): https://www.stokastic.com/articles/dfs-strategy/how-to-win-draftkings-dfs
- Lineup flexibility, Engleman (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-lineup-flexibility
- Without late swap (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-without-late-swap
- Multi-entry strategy (Jul 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-multi-entry-strategy
- Sims guide (Jul 2026): https://www.stokastic.com/articles/nba-dfs/how-to-use-nba-dfs-sims
- Contest selection, Smith (Jul 2026): https://www.stokastic.com/articles/dfs-strategy/dfs-contest-selection
- Diversification: https://www.stokastic.com/articles/dfs-strategy/dfs-diversification-strategy
- Showdown review, Heat vs Celtics Game 5 (page not loaded): https://www.stokastic.com/nba/nba-dfs-draftkings-showdown-review-heat-vs-celtics-game-5/
- 2020 to 2021 lineup rewinds (pages not loaded), for example: https://www.stokastic.com/nba/nba-daily-fantasy-lineup-rewind-draftkings-fanduel-2-10-21/ and https://www.stokastic.com/nba/nba-dfs-lineup-rewind-draftkings-12-26-2020-main-slate-gpp-review/

Other
- Edgerton, "DFS NBA: Showdown and Single-Game Strategy," RotoWire (May 2021): https://www.rotowire.com/basketball/article/dfs-nba-showdown-and-single-game-strategy-57179
- Rikleen, "Numbers Game: Investigating Back-to-Backs," RotoWire (Dec 2016): https://www.rotowire.com/basketball/article.php?id=30997
- RotoWire two-game slate note (page not loaded): https://www.rotowire.com/basketball/article/draftkings-nba-sunday-cheat-sheet-49315
- Whitestone, NBA DFS analysis (FanDuel scoring, 2012 to 2016): https://ianwhitestone.work/nba-dfs/
- DFS Karma, Showdown strategies NBA vs NFL (page not loaded): https://www.dfskarma.com/dfs-101/showdown-strategies-nba-vs-nfl/
- OnlyDFS, NBA Showdown strategy (Sep 2026, vendor): https://onlydfs.com/blog/nba-dfs-showdown-strategy.html
- FantasyPros, late swap tips (Jul 2020): https://www.fantasypros.com/2020/07/dfs-strategy-tips-advice-late-swap/amp/
- FantasyPros, single-entry vs multi-entry (Jul 2020): https://www.fantasypros.com/2020/07/dfs-strategy-tips-advice-single-entry-vs-multi-entry-tournaments/amp/
- 4for4 DK GPP listings (payout percentages, rake): https://www.4for4.com/2021/w15/best-nfl-dfs-gpps-play-week-15 and https://4for4.com/node/116992
- Grantland, back-to-backs (2012): https://grantland.com/the-triangle/the-effects-of-the-compressed-schedule-examining-back-to-backs/
- SportsBettingDime back-to-back record (page not loaded): https://www.sportsbettingdime.com/?p=840685
- Razzball opening night (2022): https://basketball.razzball.com/nba-dfs-opening-night-10-22/
- SaberSim DFS Q&A episode notes: https://sabersim.castos.com/episodes/dfs-qa-best-practices-for-correlation-and-sim-diversity-in-nba
