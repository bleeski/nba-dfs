# R1: How the leading DFS platforms create their NBA edge

- Date: Tuesday, October 13, 2026 (NBA preseason; go-live is opening night, Tuesday, October 20, 2026)
- Author: research subagent (design-only session, no engine code)
- Scope: public help centers, methodology pages, vendor articles, podcast show notes and two academic papers. Product pages were read; no data endpoints were called; nothing was logged into.
- Builds on: the user's report `DFS_Platforms_Competitive_Edge_Report_2026-10-13.md`. This memo does not repeat its platform summaries. It adds mechanism-level detail, NBA and Showdown specifics, the academic methods behind portfolio selection, and a ranked, free-only build list tied to the two goals.

---

## 1. The answer first

(Jargon used below is defined in plain English in Section 2. Labels in parentheses say how strong the evidence is.)

1. **The NBA moat is minutes and late news, not the optimizer.** DARKO, a respected public NBA projection system, reports that it beat DFS sites on every box-score stat it tested except one: "The only stat where DARKO lost was in minutes projections." Every serious vendor builds projections as minutes times a per-minute scoring rate and treats injury and starting-lineup news as the main driver of change. (VERIFIED [S64], [S29], [S66b], [S67a])
2. **Simulation-first vendors build lineups from the same correlated game draws they later use to grade them.** SaberSim optimizes each lineup against a sample of its play-by-play game simulations (down to a single simulation at the most diverse setting), then ranks lineups by simulated return on investment (ROI: profit divided by entry fees) inside a rebuilt copy of each contest (real entry limit, size and payout), repeated "tens of thousands of times." (VERIFIED [S2], [S6])
3. **The opponent field is modeled by stake level and contest size, not by one ownership number.** SaberSim uses four stake buckets and "13 contest types" of ownership; Stokastic uses Low Stakes, High Stakes and Marquee archetypes plus a pool size set to "mimic the real field." Stokastic's counterintuitive point: high-stakes fields are sharper but more alike, so they are more concentrated. (VERIFIED [S5], [S24], [S28], [S30])
4. **Duplication is modeled, and it is driven by the product of ownerships, not the sum.** SaberSim shows a "Dupes" estimate per lineup; DFS Hero splits each prize across expected copies; ETR found a .43 r-squared (a 0 to 1 measure of how well one number predicts another) between product ownership (the ownership percentages of a lineup's players multiplied together) and duplicate count in NFL Showdown, the strongest single variable it tracks. (VERIFIED [S23], [S66a], [S62])
5. **The best portfolio selectors pick lineups that win in different simulated worlds.** SaberSim's default "Portfolio Diversifier picks lineups that depend on different game outcomes," which its backtests say beat minimum-uniques and global exposure caps. The academic version (Hunter, Vielma and Zaman; Haugh and Singal) proves why: "the probability of at least one entry winning" is a submodular objective (each added lineup helps less than the one before), so greedy one-at-a-time selection is provably close to the best possible. (VERIFIED [S13], [S76], [S77])
6. **No vendor publicly measures a night-level washout risk (goal 2).** Every metric found is per contest: Sim ROI, win rate, cash rate, Top 1%, min ROI by uniques. Nothing reviewed computes "probability that zero of tonight's entries cash across all contests." (BET, based on absence across every doc reviewed) The mechanism to compute it is visible, though: SaberSim's custom contests run on "the same game simulations and field lineups as everything else." (VERIFIED [S5])
7. **Showdown Captain versus UTIL ownership is a documentation gap across the whole industry.** No vendor page reviewed explains how Captain ownership is projected separately. What is documented: Captain costs and scores 1.5 times, winners spend nearly the full cap, most winning NBA lineups split 3-3 or 4-2 by team, and lineup rules should center on teammates whose playing time affects each other. (VERIFIED [S66b], [S54], [S61]; negative correlation of minutes-sharing teammates SUPPORTED [S73]; the gap is BET by absence)
8. **Late swap is mechanical and copyable for free.** Lock players by game start, treat an unknown start time as locked, set finished games to their final scores with zero variance, use actual ownership of already-locked players, and re-solve only the open slots. (VERIFIED [S19], [S36], [S66c])
9. **The free analog of the vendors' best calibration feature exists.** SaberSim Contest Flashback re-runs finished DK contests against every real lineup entered, and Stokastic's Post-Contest Simulator "grades every lineup you enter against the field." DraftKings has historically offered an "Export Lineups to CSV" on contest standings with every lineup and player ownership. The user can download these by hand nightly, which would let us calibrate ownership and field models on real fields at zero cost. (VERIFIED for vendors [S21], [S42]; DK export SUPPORTED by a 2016 article [S75], current availability is an open question for the DK-data agent)
10. **Opening night is the hardest night of the season for every model.** DARKO "has no NCAA, summer league, or preseason data in it," and Stokastic warns early-season pace is noisy. Rotations, minutes and ownership habits are least known on October 20. (VERIFIED [S64]; SUPPORTED [S34])

---

## 2. How to read this memo

### Evidence labels

- **VERIFIED**: I directly observed the claim on the primary source (usually the vendor's own page) and give a short verbatim quote or exact description. For vendor pages, VERIFIED means "the vendor says this," not "this is true."
- **SUPPORTED**: a credible secondary source says it, or I saw it on the vendor page but only have a paraphrase.
- **BET**: my judgment or inference, or an unverified marketing claim.

Method note: the web-fetch tool returns a model's paraphrase of a page, so every VERIFIED quote below came from a second fetch that asked for verbatim text. A helper agent fetched the long-tail tools (DFS Hero, Daily Fantasy Fuel, LineStar, Basketball Monster, FantasyCruncher, SpikeWeek, Fantasy Points, ResultsDB) under the same rules; I re-fetched and confirmed the DFS Hero simulator, DFS Hero NBA guide and Daily Fantasy Fuel injuries pages myself.

### Jargon, defined once

- **DFS**: daily fantasy sports. **DK**: DraftKings.
- **Classic**: the standard 8-player DK NBA lineup across many games. **Showdown (Captain Mode)**: a single-game, 6-player lineup with one Captain (CPT) slot that scores and costs 1.5 times, plus five UTIL (utility) slots.
- **GPP**: guaranteed prize pool tournament, usually top-heavy (most money near the top). **Cash line**: the lowest score that wins any prize. **Single-entry, 3-max, 20-max, 150-max**: the most entries one user may submit.
- **Projection, median, ceiling**: projection is the expected (average) fantasy score; median is the middle outcome; ceiling is a high-end outcome (vendors use the 85th to 99th percentile).
- **Ownership**: the percent of the field's lineups that include a player. **Chalk**: heavily owned players. **Leverage**: your exposure (or a player's optimal rate) minus field ownership.
- **Exposure**: the percent of *your* lineups that include a player.
- **Optimal % (Opto%)**: how often a player appears in the single best possible lineup across simulations.
- **Field**: the opponents' lineups in a contest. **Field model**: our simulated stand-in for that field.
- **Dupes (duplicates)**: identical lineups entered by different users; a duplicated winner splits the prize.
- **Uniques (min uniques)**: the minimum number of players by which any two of your lineups must differ.
- **Late swap**: on DK, changing players whose games have not started after the slate's first game locks.
- **Sim / simulation draw**: one random, internally consistent version of how tonight's games go. Thousands of draws make a distribution.
- **Submodular**: a property of "coverage" objectives where each added lineup helps less than the last; it makes greedy selection provably close to the best possible.
- **Greedy selection**: pick the single best lineup, then the lineup that adds the most on top of it, and so on, one at a time.
- **Washout**: a night where zero of our entries cash in any contest (goal 2).
- **ROI**: return on investment, (prizes minus entry fees) divided by entry fees. **Sim ROI**: average ROI across simulated contests. **EV**: expected value, the long-run average result.
- **FPPM**: fantasy points per minute.
- **Product ownership**: multiply the ownership percentages of every player in a lineup; a tiny product means few opponents are likely to have built the same lineup.
- **r-squared**: a 0 to 1 measure of how much of the variation in one number another number explains (0 is none, 1 is all).
- **Kalman filter**: a standard method for estimating a true value from noisy measurements, updating a little after each new observation.
- **Gradient-boosted tree**: a common machine-learning model that adds up many small decision rules.
- **Dirichlet distribution**: a way to draw random percentages that add up to 100%; used to simulate how a field's ownership could differ from the projection.
- **Order statistics**: the math of ranked values (for example, the 99th-percentile score in a field), which lets us estimate the top-1% line without simulating every opponent.

---

## 3. Platform findings

Each platform section only covers topics with public evidence. "Not found" means I looked and the public material is silent.

### 3.1 SaberSim (simulation-first, the most transparent help center)

**Projections**
- Projections come from play-by-play simulation: "Every SaberSim projection comes from play-by-play game simulations." The projection is the average of simulated scores. (VERIFIED [S4])
- It publishes distributions, not just a number: the 25th percentile is the floor, the 50th the median, and "the 85th to 99th is their ceiling." (VERIFIED [S4], [S23])
- Correlation is built in because "every player's score comes from the same simulated game." (VERIFIED [S4])
- Late news: "projections update within minutes of an injury or lineup change." (VERIFIED [S4]; the speed itself is a vendor claim, BET)
- Users can move a team total rather than individual players: "Changing a team total shifts the whole game script," and the simulations decide who benefits. (VERIFIED [S12]) This is a useful lever for a non-engineer: change one number, the whole game reprices.
- How NBA minutes are set is not documented in writing. A January 2024 podcast episode lists the question "How is SaberSim calculating the projected minutes for NBA?" but the show notes contain no answer. (VERIFIED that notes are empty of method [S27])

**Ownership**
- Field ownership is "how often SaberSim expects the field to roster a player," and Ultimate users can switch sets "that model different contest sizes and stakes." (VERIFIED [S8])
- The Starter plan has "Live-updating Flagship ownership"; Ultimate has "Auto-updating ownership for 13 contest types." (VERIFIED [S24])
- "Adj Own" adjusts ownership for simulated performance; above "My Own" means over-owned. (VERIFIED [S23])
- Contest sims do not read ownership numbers directly. They use "field lineups, which are full sets of simulated opponent lineups," and editing an ownership number "on its own" changes nothing until you generate a new field from it. (VERIFIED [S10], [S11]) This is an important design hint: ownership is an *input to field generation*, and the field is the real object.
- Method of building ownership: not documented. A December 2025 episode lists the question "Base model that regresses to market?" with no written answer. (VERIFIED that the question exists, method unknown [S27])
- Accuracy: an episode is titled "How accurate are SaberSim's ownership projections?" with no figures in the notes. (VERIFIED [S27])

**Simulation and contest modeling**
- Contest Sims rebuild each contest in your DK entries file with its real entry limit, size and payout, fill it with "simulated opponent lineups," score one game simulation per game, pay prizes, and repeat "tens of thousands of times." (VERIFIED [S2])
- Metrics: Sim ROI, "how often it wins, how often it cashes," and "how much its results swing." (VERIFIED [S2]) Glossary adds "Dupes": "The number of times a lineup is expected to be duplicated." (VERIFIED [S23])
- Saber Score is the same idea against a generic GPP and internal field; Sim ROI uses your actual contests. (VERIFIED [S3], [S23])
- Custom contests: "choose the stakes bucket closest to the entry fee" for field lineups (Low Stakes $4 and under, Flagship $4.01 to $30, Med Stakes $30.01 to $99.99, High Stakes $100 and up), a payout (copy one, or set entries, percent to first, percent of field cashing), and "User Entries," which puts your own lineups in the sim to avoid lineups that "cannibalize the EV of other lineups you play." (VERIFIED [S5]) EV means expected value.
- Custom contests "run with the same game simulations and field lineups as everything else." (VERIFIED [S5]) That shared-draw design is exactly what a night-level washout metric needs.

**Portfolio construction**
- Lineup generation: "SaberSim selects a sample of our simulations to use for that lineup" and builds "the best possible lineup for those sims." The Sim Diversity slider sets the sample size: at 10, "it's a single simulation"; at 0, "it's using every simulation" (that is, average projections). Defaults per sport and slate size were chosen by backtesting. (VERIFIED [S6])
- A Correlation slider adds extra pull toward positively correlated pairs on top of what the sims already contain. Defaults are backtested. (VERIFIED [S7])
- Selection: lineups are "graded and ranked by either Saber Score (on Starter) or Sim ROI (on Ultimate)," and the system "spreads your entries across different outcomes." (VERIFIED [S16])
- Diversification: "The Portfolio Diversifier picks lineups that depend on different game outcomes." SaberSim says backtests showed it "produced better ROI with less downside" than Min Uniques or global caps. (VERIFIED [S13]; performance is a vendor claim, BET)
- Exposure guidance is leverage-based, not a fixed number: "Work from the leverage column rather than a target percentage," and any manual exposure change will "decrease your Sim ROI or Saber Score somewhat." Set exposures after building. (VERIFIED [S14], [S15])
- Lineup-level limits can combine ownership by "sum, average, product, or geometric mean." (VERIFIED [S25])
- Contest assignment: one lineup group per contest; if a group has fewer lineups than entries, lineups are duplicated to fill. (VERIFIED [S17])

**Late swap**
- Quick Swap "removes out players and replaces them while keeping the rest of your lineup intact." Full Swap "rebuilds every open slot in your lineups from new simulations." "NBA is where this matters most, since one injury can flip the slate." (VERIFIED [S18])
- In Full Swap, "Players whose games have started are locked in place," and Contest Sims and the Portfolio Diversifier re-run after the swap build. A "Delta Exposure" column shows exposure change versus the pre-lock build. (VERIFIED [S19], [S20], [S23])
- Alerts: mobile notifications for out players and Discord lineup-alert channels; a "significant projection change" sim is the cue for Full Swap. (VERIFIED [S18], [S26])
- "Live Sims" for NBA with staggered start times are discussed in an October 2025 episode, but not documented in writing. (VERIFIED that the topic exists [S27])

**Post-contest calibration (Contest Flashback)**
- The day after a DK contest, "SaberSim collects every real lineup," then "runs the slate 100,000 times" and pays out each real lineup to get Flashback ROI. DK only. The gap between Sim ROI and Flashback ROI is how far the projected field diverged from the real one. (VERIFIED [S21], [S22])

**Showdown**: no written Showdown-specific method. Episodes cover "first-half minutes," late swap with custom projections and a live Showdown build demo. (VERIFIED topic list only [S27])

**Price**: Starter $97/month, Ultimate $297/month; Contest Sims are Ultimate-only. (VERIFIED [S24])

### 3.2 Stokastic (Awesemo lineage; contest-field simulation plus a data hub)

Note: most Stokastic articles found are dated June to August 2026 and several are bylined "Stokastic Staff." They read like search-optimized marketing. Several NBA pages (ownership, Showdown ownership, older NBA Sims guide, a user case study) are JavaScript-rendered and came back as a title only; I make no claims about their contents. (VERIFIED render failure [S44])

**Projections**
- "Projected fantasy points are just minutes multiplied by scoring rate." (VERIFIED [S29])
- Process advice: minutes first, then adjust usage, rebounding and assist rates for absent teammates (with on/off tools), then pace and Vegas total. The worked example is James Harden's usage rising toward nearly 50% with Russell Westbrook out. Early season: lean on league-average pace. (SUPPORTED, paraphrase of [S34])
- Alex Baker's method article: "Convert the game total and spread into implied team totals," then distribute each team total across the roster, and "trust team totals and moneylines more than props." (VERIFIED [S40]) He also says "Proven projections are cheap and the edge has moved into lineup construction," naming "ownership, correlation, leverage, and late swap." (VERIFIED [S40])
- Update speed: updates begin "early in the day," refresh "on real events" such as "a starter ruled out, a confirmed lineup," a late rest call, or a moving game total. Pages show a "last updated" stamp. (VERIFIED [S37])
- Columns include minutes, FPPM (fantasy points per minute), standard deviation, Boom Score, Bust Score, ceiling and floor ("The high and low end of the player's realistic range"). (VERIFIED [S29]; a first paraphrase of the same page described ceiling differently, which is a reminder that only verbatim quotes count)

**Ownership**
- Target contest: "how often a player will land in lineups in the night's largest-field contest," updated "through the day as injury and rest news lands." (VERIFIED [S41])
- "in NBA, ownership projections keep updating after the early games lock." (VERIFIED [S37]) That post-lock update is what makes their late swap work.
- Method: not published. A search snippet claimed a fixed two-hour cadence and a 1:00 PM ET first post, but the ownership page did not render, so this stays unverified. (BET)
- Leverage is defined as "The gap between a player's projected ownership and his optimal rate," where Optimal is "How often, across our simulations, the player lands in the single highest-scoring lineup." (VERIFIED [S29])
- Starting-lineup news example: a backup "climbs to about 45% projected ownership," while the wing who moves into the starting five "often goes underowned." (VERIFIED [S38])

**Simulation and field modeling (Contest Generator)**
- The Contest Generator "builds a realistic field of opponents," and the Sims grade your lineups against it. (VERIFIED [S28])
- Pool size: "Set pool size to mimic the real field, because realism beats raw size"; staff run about 500 for a few-hundred-entry high-stakes contest and bigger presets for "huge cheap fields." (VERIFIED [S28])
- Archetypes: "Low Stakes builds a softer, chalkier field; High Stakes builds a sharper one." High-stakes regulars "play a lot more similar to each other," so "A sharper field is a more concentrated field." (VERIFIED [S30])
- Percent to first (a payout-shape dial for ranking, not for the field): "first-place prize ÷ total prize pool," and a higher value "ranks the more contrarian, ceiling-chasing lineups higher." (VERIFIED [S30])
- Re-run discipline: "If the input that feeds the field changed, you re-run." If you only changed your own preferences after the field was built, "you don't." (VERIFIED [S28]) This is a clean caching rule for our architecture.
- Number of sims: not stated for NBA. (Not found)

**Portfolio construction**
- Workflow: build in Contest Sims, simulate, favorite the top lineups by simulated ROI with a uniques setting from 0 to 8, apply per-player ROI boosts and stack filters, re-favorite. Results are "a ranking, not a promise." (SUPPORTED, paraphrase of [S32])
- Uniques: "two to four is the everyday range," more on bigger slates, fewer on two-game slates where forcing uniques "drags in bad rosters." "a setting can crater your min ROI while the average barely moves." (VERIFIED [S31])
- Portfolio Overview shows "min and average ROI at each uniques count." (VERIFIED [S28])
- Entry Manager reads the DK contest file and "matches your saved Sims lineups to your registered entries." (VERIFIED [S33])

**Late swap**
- Re-simulates submitted lineups "against the live contest pool," which "folds in the actual ownership of players who have already locked." For finished games, set the projection to the final score and variance to 0. (VERIFIED [S36])
- Late scratch: swap to "a high-upside, position-eligible replacement in a still-locking game." (VERIFIED [S38])
- Some DK tournaments turn late swap off: "DraftKings has experimented with tournaments that turn late swap off," and then "once you submit, you are frozen." Advice: pre-load beneficiaries of a questionable star and trim the risky star. (VERIFIED [S39]) Our engine must read a per-contest late-swap flag.

**Post-contest**: "The NBA DFS Post-Contest Simulator grades every lineup you enter against the field," scored "on Sim ROI, ownership, and dupes." (VERIFIED, 2023 to 2024 package page [S42])

### 3.3 RotoGrinders and FantasyLabs (one product family; treat SimLabs as one technique)

RotoGrinders and FantasyLabs appear to share a parent company (Better Collective). A RotoGrinders page, whose web address names it a FantasyLabs contests dashboard now live on RotoGrinders, says "The sophisticated Contests Dashboard will replace the previous ResultsDB interface." (VERIFIED via helper [S50]; the shared corporate ownership itself is BET because the press release returned 403.) FantasyLabs' help center returned HTTP 403 on every attempt, so I could not observe its SimLabs or ownership articles. (VERIFIED block [S55])

**Projections**
- RotoGrinders' long-running NBA lesson by Derek Farnsworth ("Notorious") gives explicit weights: minutes 20 to 25%, turnover-adjusted usage 15 to 20%, team totals 10 to 14%, pace 5 to 10%, defense versus position 5 to 10%, and a blowout factor from the Vegas line. "Minutes are king in daily fantasy basketball." (VERIFIED [S47], updated April 2024) His paid course covers "How to adjust minutes and FP/min projections for injuries." (VERIFIED title only; paywalled [S48])
- LineupHQ lets NBA users edit projected minutes and upload and "aggregate all your projection sources," and shows an "Opto%" metric. (VERIFIED [S46])
- FantasyLabs Models are "fully customizable," with a Trends tool that queries pricing and ownership history. (VERIFIED [S51])

**Ownership**
- FantasyLabs launched NBA ownership in October 2016; the base model was built by Colin Davy, targets the main mid-stakes GPP ("Crossover and Slam"), and updates on role changes and Vegas moves. (SUPPORTED, paraphrase of [S52]; old)
- A FantasyLabs writer: "Projecting ownership is much more of a knowledge-based art than a formula-driven science." (VERIFIED [S53], 2017, about NFL)
- No accuracy figures published. (Not found)

**Simulation, field and portfolio (SimLabs)**
- "We simulate the games thousands of times." Three fields: Large Field ("The most diverse field of lineups"), Small Field ("evaluates 5000 of the best lineups"), Single Entry ("evaluates 2000 of the best lineups"). (VERIFIED [S45])
- Lineups get a 0 to 99 SimLabs Rating from five user weights (Simulation, Projection, Ownership, Upside, Correlation); metrics include Top 100 and ITM (in the money). "You can't currently ask SimLabs for a set amount of any given player"; a Results Range control spreads outputs. (VERIFIED [S45]) BET: a weighted blend of five scores is less principled than SaberSim's or Stokastic's direct simulated-contest ranking, but easier to explain.
- LineupHQ is the rule-heavy optimizer: min and max exposure, groups, stack builder, randomness and "Range of Outcomes," and NBA late swap editing. (VERIFIED [S46])

**ResultsDB / Contests Dashboard**: sections include Exposures, Duplicates, Leaderboard and "Full ROI" for contest participants across NBA and other sports; paid. (VERIFIED via helper [S50])

### 3.4 Ship It Nation (process and community)

- NBA plans list DK and FanDuel projections, separate Showdown projections, ownership, The Stone and "The Stone 2.0 (w/Handbuilder)," GPP and cash core reports, slate stations, an education course and Discord. The NBA + Optimizer plan builds "Up To 100 Lineups" and includes "Quick Swap." Contest sims, ROI and rank metrics, portfolio diversification and custom-data upload sit only in higher all-sports tiers. NBA is $29/month, NBA + Optimizer $49/month. (SUPPORTED: seen on the vendor page, but only short phrases were captured verbatim [S57])
- No public methodology for projections, ownership or sims. (Not found)
- BET: the edge is curated judgment (core plays, player pools) delivered on a fixed nightly rhythm, which is exactly the part a non-engineer needs from our engine's "slate brief."

### 3.5 Establish The Run (ETR)

- Nightly NBA cadence: "BASE TEMPLATE PROJECTIONS AND OWNERSHIP PROJECTIONS BY 12 P.M. ET," a "first run" from "the minutes team the night before," "FINALIZED DFS PROJECTIONS BY 5 P.M. ET," and projections "update continuously on news" through the final lock. A live show runs two hours before lock. (VERIFIED [S58])
- BET (strong): ETR runs a dedicated minutes team, which matches finding 1 that minutes are where the work is.
- Ownership targets "the largest-field tournaments on DraftKings and FanDuel." (VERIFIED, Showdown projections page [S60]) The page is paywalled, so I could not see whether CPT and FLEX ownership are separate. (VERIFIED paywall [S60])
- NBA Showdown advice (August 2020, Drew Dinkmeyer): DK's "dynamic captain pricing is more sophisticated, less likely to get monstrous duplicates"; "I'll often try to take more spread approaches at my captain exposure"; and the "majority of rules should focus on players that impact each other's playing time." (VERIFIED [S61])
- NFL Showdown 101 (September 2026, Cody Main), built from "a database of every lineup entered in the DraftKings flagship GPP": "The .43 r-squared between product ownership and the number of duplicates"; "minimal correlation between CPT ownership and the number of duplicates"; lower salary spent correlates with fewer dupes. (VERIFIED [S62]; NFL, so for NBA this is a transferable technique, not a transferable number)
- ETR's site menu lists "The Solver" (and FantasyLabs) under Optimizers, and shows no NBA sims, late swap or Showdown tools of its own. (VERIFIED menu only [S63]) BET: ETR's NBA edge is projections and ownership, with optimization handled by partner tools.

### 3.6 DARKO (projection method, not a DFS tool)

- Each past game is weighted by a per-stat exponential decay (older games count less; the page says starting role fades within about a game, while three-point shooting persists for seasons), a modified Kalman filter (a standard method for estimating a true value from noisy measurements) updates estimates faster when a player changes teams, and a gradient-boosted tree (a machine-learning model that combines many small decision rules) merges the two. Adjusts for rest, travel, home court, opponent, aging, seasonality. (SUPPORTED, paraphrase of [S64])
- Minutes: "Minutes are the hardest thing any projection system forecasts," and in DARKO's own test against DFS sites, "The only stat where DARKO lost was in minutes projections." (VERIFIED [S64])
- Rookies start from "age, draft slot and height"; no college, summer league or preseason data. (VERIFIED [S64])
- CSV downloads exist on many pages; no license or terms of use stated. (SUPPORTED [S64], [S65]) Reuse permission is an open question.
- BET: DARKO is a strong free prior for per-minute rates and stat-level means, while minutes must come from news-driven logic or a DFS-oriented source.

### 3.7 DFS Hero (newer; unusually explicit field and late-swap docs)

- Projections: "It plays every game 10,000 times before lock" (home page; the simulator article says "thousands of times"). NBA: "DFS Hero recomputes My Proj as minutes times FPPM," and "A projection built on 34 minutes is only as good as the minutes." (VERIFIED [S66a], [S66b])
- Field: "Exclude a chalk player from your pool and the field still owns him." "Chalk lineups appear more than once, the way they do in a real contest." "Players on the same team move together." (VERIFIED [S66a])
- ROI: expected ROI is "the average prize per play, shared with the expected copies" of that lineup. It records finishes "inside the Top 0.1%, Top 1%, and Top 5%, and inside the paid places." "A stated 2% is not a guarantee of 2%." (VERIFIED [S66a])
- Showdown: CPT and MVP slots "score 1.5 times the player's points and cost 1.5 times the salary"; $50,000 cap on DK. Nothing on CPT ownership. (VERIFIED [S66b])
- Late swap: "re-solves the unlocked slots in every entry with the locked players pinned"; "A player whose start time is unknown counts as locked"; "Next lock is your deadline for the whole sheet"; it "never changes your entries on DraftKings or FanDuel by itself." NBA late swap listed for "Classic slates on both sites." (VERIFIED via helper [S66c], and [S66b])
- Replay runs "up to 20 past slates in one run"; Analyzer lets you "read the whole field" of a finished contest. (VERIFIED via helper [S66d])
- Price: $79.95 and $149.95 per month; no free tier. (VERIFIED via helper [S66e])

### 3.8 Daily Fantasy Fuel (DFF), LineStar, Basketball Monster, FantasyCruncher, SpikeWeek, Fantasy Points

- **DFF (the best free projection source found)**: "projections can be downloaded in CSV format for free," for Classic and Showdown; baseline uses "historical performance, usage, minutes, and fantasy points per minute"; "50+ updates in just the final 30 minutes before slate start." (VERIFIED via helper [S67a]) Injuries page: "The official updates are posted at 1:30pm ET, 5:30pm ET, and 8:30pm ET," and "we will adjust projections for players that we anticipate will pick up minutes." One OUT list applies "across our suite of tools." (VERIFIED, my own fetch [S67b]) The Showdown table shows one ownership column, no CPT and UTIL split. (SUPPORTED [S67a]) The terms of service page has no clause on automated access or scraping. (VERIFIED absence, last updated June 7, 2026 [S67c]) Premium is $29.99/month.
- **LineStar**: free view of only "the past week"; current slates need Premium ($39.99/month). Offers a consensus projection column and a projected versus actual ownership "Diff" view where "Actual ownership is pulled from the contest you choose." Phone push notifications. (VERIFIED via helper [S68])
- **Basketball Monster**: projections "update instantly as news breaks"; lineups page distinguishes "Projected Lineup" vs "Verified Lineup"; Custom Daily Minutes for members. (VERIFIED via helper [S69]) Its paid membership page does not mention DK DFS projections. (VERIFIED via helper [S69])
- **FantasyCruncher**: injured players are set to zero and "Back-up players who are expected to get a start will see an increased projection"; it checks whether update time is after the news time; randomness uses "standard deviations and normal or log normal distribution"; FC Pro ownership is "Ownership Projections from Stokastic"; Lineup Rewind shows historical projections versus actual scores. Late Swaptimizer tutorial did not render. No free trial. (VERIFIED via helper [S70])
- **SpikeWeek**: Best Ball focus; an ownership visualizer with "Show Captain Ownership" and "Upload Contest CSV," apparently NFL. No NBA DFS product found. (VERIFIED via helper [S71])
- **Fantasy Points**: every page returned HTTP 402 Payment Required. No claims. (VERIFIED block [S72])

### 3.9 Cross-platform comparison

| Topic | SaberSim | Stokastic | RG / FantasyLabs | DFS Hero | Free analog for us |
|---|---|---|---|---|---|
| Projection core | Play-by-play sim | Minutes x FPPM, team totals | Minutes-weighted model, editable minutes | Sim; minutes x FPPM | Minutes x per-minute rates, Vegas-anchored, DARKO prior, DFF consensus |
| Distributions shown | 25th / 50th / 85th to 99th | Std dev, boom, bust, ceiling, floor | Range of outcomes | Sim percentiles | Our sims |
| Ownership by contest type | 4 stake buckets, 13 contest types | 3 archetypes plus pool size | Mid-stakes GPP (2016) | Tournament field | Model calibrated on DK exports by stake and size |
| Field model | Simulated opponent lineups | Contest Generator | 2,000 to 5,000 "best lineups" | Chalk dupes, field owns your excluded players | Ownership-driven sampler, dupes modeled |
| Ranking metric | Sim ROI, win, cash, swing, dupes | Sim ROI; min and avg ROI by uniques | 0 to 99 rating, Top 100, ITM | ROI, Win, Top 0.1/1/5%, Cash | P(top 1%), P(first), cash rate, ROI, dupes |
| Diversity | Portfolio Diversifier (different outcomes) | Uniques 0 to 8 | Results Range | Not documented | Greedy coverage on shared draws |
| Night-level washout | Not found | Not found | Not found | Not found | Build it (shared draws across contests) |
| Late swap | Quick and Full Swap, alerts | Live pool with actual ownership | LineupHQ edit | Pin locked, unknown start = locked | Same, with file export |
| Post-contest | Flashback (100,000 sims on real field) | Post-Contest Simulator | Contests Dashboard | Analyzer, Replay | Re-sim on DK standings exports |

---

## 4. What the academic work adds (the actual algorithms behind the marketing)

### 4.1 Hunter, Vielma and Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming" (arXiv 1604.01455, revised 2019)

- The objective is literally goal 1 for winner-take-all contests: "the probability of at least one entry winning," which they show is submodular. (VERIFIED [S76])
- Construction is greedy and sequential: each new entry maximizes mean score subject to a minimum variance and a maximum overlap (shared players) with earlier entries. For baseball they set "the maximum overlap parameter γ to six." Stacking raises lineup variance. (VERIFIED [S76])
- Result: top-ten finishes "multiple times in hockey and baseball contests with thousands of competing entries." (VERIFIED [S76]) No opponent model. (VERIFIED, per Haugh and Singal's summary [S77])

### 4.2 Haugh and Singal, "How to Play Fantasy Sports Strategically (and Win)" (Management Science, 2021; I read their 2019 workshop slides, the paper itself is paywalled or blocked)

- Opponent model: each position's ownership vector is drawn from a Dirichlet distribution whose parameters come from a regression on player features ("Dirichlet regression"), then opponent lineups are sampled. A results chart compares realized QB ownership with the model's 95% prediction interval (I could read the chart labels, not the plotted values). (VERIFIED [S77]) BET: this is the most defensible free recipe for a field model, and it naturally produces dupes and ownership uncertainty.
- Payout-aware objective: for one entry, maximize the chance of beating a "stochastic benchmark" (the field score at the payout cutoff), approximated by a mean-variance search over binary quadratic programs. (VERIFIED [S77])
- Many entries in top-heavy contests: greedy selection, justified because the top-heavy objective is "monotone submodular," so greedy "achieves ≥63% of true unknown optimal" (the classic Nemhauser bound), plus a diversification constraint after each pick. (VERIFIED [S77])
- For double-up (cash-style) contests, the opposite holds: the best N-entry portfolio is usually the best single entry repeated N times. (VERIFIED [S77]) BET: this is the mathematical reason goal 1 and goal 2 pull in different directions within a contest, and why goal 2 is better served by spreading cash chances *across contests and game outcomes* than by duplicating safe lineups.
- Compute shortcut: generating every opponent lineup is expensive for big fields, so they simulate the field's score distribution and read the needed percentile directly ("order statistics"). (VERIFIED [S77]) BET: on a laptop with about 6 GB free, this is how we evaluate 150,000-entry fields without holding 150,000 lineups per draw.
- Result: "ROI of Over 350% in Just 17 Weeks!" on FanDuel NFL with 50 entries and $50 per week, with a slide titled "But a Very High Variance!" (VERIFIED [S77]) Small stakes, one season: treat as proof of concept, not a performance estimate.

### 4.3 Decary, Bergman, Cardonha, Imbrogno and Lodi, "The Madness of Multiple Entries in March Madness" (arXiv 2407.13438, 2024)

- Multi-entry pools: maximize "the expected score of the best-performing entry"; the best 100-entry solution "had a 2.2% likelihood of winning a $1 million prize." (VERIFIED, abstract only [S78]) BET: confirms the "best-of-N" framing generalizes beyond DFS.

---

## 5. Cross-cutting findings that go beyond the source report

1. **Two goals, one math object.** Goal 1 (at least one entry in the top 1%, or first in small fields) and goal 2 (at least one cash somewhere tonight) are both "coverage" problems over the same simulation draws: pick entries so that as many draws as possible contain at least one success. Both are monotone submodular, so the same greedy selector can serve both, with goal 2 as a constraint or tie-breaker. (BET, built on VERIFIED math in [S76], [S77])
2. **Washout risk is correlated through shared games.** Showdown games are usually games that are also on the Classic slate, so one bad game script can sink both. A night-level metric must score every contest on the *same* draws. SaberSim already shares draws across contests [S5]; no vendor reports the night-level number. (BET for the gap; VERIFIED for shared draws)
3. **Field realism depends on stake and size more than on any single ownership number.** Low-stakes fields are softer and chalkier; high-stakes are sharper but more concentrated. Pool size should match the real contest. (VERIFIED [S28], [S30]) Our field generator needs a contest archetype input, and the user's contest mix (single-entry, 3 to 20-max, 150-max) means several archetypes per night.
4. **Under the user's stated goal 1, duplication does not reduce the probability of a top-1% finish; it only reduces the money.** A tied duplicate still finishes in the top 1%. Vendors rank by ROI, which penalizes dupes [S23], [S66a]. (BET, logic) We should report both, and the user should decide whether goal 1 stays pure probability or becomes dupe-adjusted. This is the most important open product decision in this memo.
5. **Ownership modeling is the weakest public link.** No vendor publishes its method or accuracy; FantasyLabs calls it art over science [S53]; SaberSim's own podcast lists the open question "Base model that regresses to market?" [S27]. The free path is calibration on actual DK contest ownership, which LineStar and SaberSim both surface post-contest [S68], [S21]. (BET for the conclusion; VERIFIED for each cited fact)
6. **The late-news rhythm is predictable and should drive the nightly schedule.** Official NBA injury reports at 1:30, 5:30 and 8:30 PM ET [S67b]; ETR posts by noon and finalizes by 5 PM [S58]; DFF does 50+ updates in the last 30 minutes [S67a]. (VERIFIED) Our engine should rebuild at fixed checkpoints plus on news, and always keep a valid fallback file.
7. **Opening night (Oct 20) breaks history-based models.** No preseason data in DARKO [S64]; noisy early pace [S34]; ownership habits calibrated on last season. (VERIFIED for DARKO, SUPPORTED for pace; BET implication) Widen minutes uncertainty, anchor more on Vegas team totals, and avoid tuning anything on night one.

---

## 6. Synthesis: ranked techniques for the two goals

Ranking is by expected contribution to goal 1 and goal 2 given the free-only constraint and an October 20 go-live. Difficulty is for Claude Code building it, not for the user operating it.

| Rank | Technique | Goal | Free? | Free inputs needed | Difficulty | What it means for results, cost or workload |
|---|---|---|---|---|---|---|
| 1 | **Minutes-first projections with news-driven redistribution** (minutes x per-minute rates; set OUT players to zero and push their minutes and usage to named beneficiaries; widen uncertainty early season) | 1 and 2 | Yes | Box scores and game logs, official injury reports (1:30 / 5:30 / 8:30 PM ET), confirmed starting lineups, Vegas team totals; optional DARKO prior and DFF free CSV as a consensus check | High to do well, medium for a good-enough first version | This is where every vendor says NBA slates are decided, so it moves both goals more than any optimizer feature; the user's job is confirming a short list of "who absorbs the minutes" calls. |
| 2 | **Correlated slate simulation with game scripts** (one shared set of draws per night: team totals and pace drive game environment; blowouts cut starter minutes; teammates competing for minutes negatively correlated) | 1 and 2 | Yes | Rank 1 outputs, spreads and totals, historical variance by player | High | Without correlated draws, "top 1%" and "washout" cannot be measured at all; 10,000 to 50,000 draws is the vendor norm and fits the laptop. |
| 3 | **Greedy portfolio selection on shared draws** (pick each next lineup by its marginal gain in "draws where at least one entry is top 1%"; overlap cap or min uniques as guardrails; self-cannibalization counted) | 1 | Yes | Candidate lineup pool, rank 2 draws, rank 4 field thresholds | Medium | Directly optimizes goal 1 with a proven near-optimal method; replaces hand-tuned exposure rules, so less nightly fiddling for the user. |
| 4 | **Contest-aware field model with duplication** (Dirichlet-style ownership sampling by contest archetype and size; chalk dupes; field percentiles via the order-statistics shortcut for big fields; full field for under-100 contests) | 1 | Partially | Ownership projections (rank 5), DK contest size, entry limit and payout table from the user's DK entry files | High | Turns "good lineup" into "good lineup against this field"; quality is capped by ownership accuracy. |
| 5 | **Ownership model calibrated on real DK contests** (inputs: salary, projection, value, team total, news recency, positional scarcity, slate size; separate CPT and UTIL in Showdown; separate by stake level) | 1 | Partially | DK contest standings exports the user downloads by hand after contests; our own projections; salary files | Medium to high | Ownership is the input vendors guard most and document least; even a rough calibrated model beats guessing, and it improves every night the user saves an export. |
| 6 | **Night-level washout control** (score every contest on the same draws; report P(zero cashes tonight); enforce a ceiling on it by steering some entries in flatter or softer contests toward higher cash rates and spreading entries across different games and scripts) | 2 | Yes | Ranks 2 to 4, every contest's cash line | Medium once 2 to 4 exist | The only goal-2 tool anywhere; gives the user one number per night and a dial to trade a little goal-1 upside for washout protection. |
| 7 | **Showdown module** (CPT at 1.5x points and salary; separate CPT ownership; dupes driven by product ownership; team-split and salary-usage priors; spread captain exposure; minutes-linked teammate rules) | 1 and 2 | Yes | Rank 1 to 5 outputs per game; DK Showdown salary files | Medium | Showdown is a large share of volume and has small fields where first place matters; the CPT ownership gap is a chance to be better than documented vendor practice. |
| 8 | **Late swap engine** (pin locked players; unknown start time counts as locked; finished games fixed at final score with zero variance; actual ownership for locked players; Quick Swap for OUT players always, Full Swap after major news; next-lock clock; per-contest late-swap flag) | 1 and 2 | Yes | DK entries file the user downloads after first lock, live results, rank 1 updates | Medium | Removes zero-point lineups, which SaberSim calls more damaging "than almost anything else" (BET that this is a leading avoidable washout cause), and lets the user re-upload one file per lock wave. |
| 9 | **Post-contest flashback and calibration loop** (re-simulate real fields; projected vs actual ownership "Diff"; separate projection error, field error and luck) | 1 and 2 over time | Yes, if the user exports standings | DK standings CSVs, box scores | Medium | The only honest way to know whether the engine is improving; costs the user a few manual downloads per night. |
| 10 | **Backtested defaults for every knob** (sample size per lineup, correlation pull, uniques, overlap cap, washout ceiling) by slate size and contest type | 1 and 2 | Yes | Rank 9 history | Low to medium, but needs weeks of data | Keeps the user out of settings; defaults will be weak in week one and improve as history accumulates. |
| 11 | **Nightly workflow layer** (slate brief with the night's key minutes calls and chalk; one OUT list respected everywhere; timestamped inputs with "updated after news" checks; push or desktop alerts on OUT players; entry-file matching to DK contest entries; always-valid fallback file) | Supports both | Yes | All of the above | Low | Makes a 30 to 60 minute nightly routine realistic for a non-engineer and protects against shipping stale lineups. |

---

## 7. Open questions

1. **Goal 1 definition and duplicates.** Should "top-1% finish" count a tied duplicate as a full success (pure probability), or should we optimize a dupe-adjusted version? Pure probability can favor chalky lineups that make money poorly. Decision for the user.
2. **Goal 2 trade-off rate.** How much goal-1 probability is the user willing to give up to cut washout probability, for example from 10% to 5%? The engine needs either a ceiling or an exchange rate.
3. **DK standings export today.** Does DK still offer "Export Lineups to CSV" with every lineup and ownership, for which contests (only ones the user entered?), and does it split Showdown CPT and UTIL ownership? (For the DK-data agent; my only evidence is a 2016 article [S75] and SaberSim's Flashback collecting "every real lineup" [S21].)
4. **Which DK contests have late swap turned off, and how is that shown in the lobby or entry file?** [S39]
5. **Showdown CPT ownership.** No vendor documents it. Do DK exports and salary files list CPT and UTIL as separate player IDs and separate ownership? (BET: yes; needs the DK-data agent.)
6. **Free projection sources and terms.** DFF's free CSV and DARKO's CSV downloads have no stated scraping or license terms [S67c], [S64]. Can the engine fetch them nightly, or should the user download them by hand? (For the data-sourcing agent and the user.)
7. **Minutes source on opening night.** With no regular-season data, do we start from last season's minutes plus preseason rotations, Vegas totals and a consensus check, and how wide should the uncertainty be?
8. **Accuracy of any vendor ownership.** None publish it. If the user ever has a vendor trial, a one-week projected-versus-actual comparison would give us a benchmark.
9. **ETR NBA product details** (CPT and FLEX ownership, ceiling columns) are paywalled [S60]; not needed for a free build, but useful as a benchmark if the user has access.

---

## 8. Implications for the architecture

1. **One shared simulation store per night.** Generate correlated draws once per rebuild checkpoint for all of tonight's games; every Classic and Showdown contest reads the same draws. This single decision enables goal 2, the night-level washout metric, and keeps compute bounded. Store player scores per draw as compact arrays (for example 300 players x 20,000 draws in 32-bit floats is about 24 MB). The expensive object is not the player table but candidate lineups x draws per contest (20,000 candidates x 20,000 draws in 32-bit floats is about 1.6 GB, and there are several contests a night), so score lineups on the fly from player draws in chunks, cap candidate pools per contest, and keep only what selection needs (for example per-draw hit flags for "top 1%" and "cashed" as bits). What it means: the whole night fits in the roughly 6 GB of free memory on the laptop, at the cost of slightly longer scoring runs.
2. **Separate the layers the way Stokastic's re-run rule implies.** Inputs (projections, minutes, news) feed draws; draws plus ownership feed fields; fields plus payouts feed contest scoring; selection sits on top. Only re-generate a layer when its inputs change; selection-only changes (exposures, uniques, washout dial) never re-run sims. [S28] What it means: the user's late tweaks return in seconds instead of forcing a full rebuild near lock.
3. **Minutes are a first-class, editable object.** Each player has a minutes distribution, a role, and a list of "if X is out, who gains" rules with timestamps. Late news edits minutes; everything downstream recomputes. A user-visible minutes table is the main override surface, like LineupHQ and DFS Hero. [S46], [S66b] What it means: the user's highest-value nightly action is a short list of minutes calls, not dozens of settings.
4. **Field model per contest archetype.** Inputs: stake level, field size, entry limit, payout table, ownership set. Small fields (under about 100) get full simulated opponent lineups; big fields use sampled fields plus the order-statistics shortcut to get the top-1% line and cash line per draw. Duplicates are generated, not bolted on. [S5], [S28], [S77] What it means: top-1% and first-place odds are measured against a field that looks like the real contest, which matters most in the small single-entry and 3-max fields where the user's goal is first place.
5. **Selection as greedy coverage with guardrails.** Candidate pool built by sampling draws (SaberSim's Sim Diversity idea), then greedy picks by marginal gain in the contest's success event, with overlap caps, self-cannibalization counted, and a night-level washout constraint checked after each contest's picks. Report per contest: P(at least one top 1%), P(first) for small fields, cash rate, ROI, dupes. [S6], [S13], [S76], [S77] What it means: the engine optimizes the user's actual goals directly, and the user reviews a few numbers per contest instead of hand-setting exposures.
6. **Showdown is its own module, not a Classic setting.** Separate CPT and UTIL ownership, product-ownership dupe model, minutes-linked teammate rules, and full-field simulation for small Showdown contests. [S54], [S61], [S62] What it means: more build work up front, but Showdown is a large share of the user's volume and the one area where no vendor documents a method to copy.
7. **Late swap is a scheduled mode.** After each lock wave: pin locked players, treat unknown starts as locked, fix finished games at final scores, swap OUT players first, then optionally re-solve open slots, and write a DK upload file. Respect a per-contest late-swap flag. [S19], [S36], [S39], [S66c] What it means: one download and one upload per lock wave for the user, and no zero-point lineups from late scratches in contests that allow swaps.
8. **Calibration store from day one.** Save every night's inputs, draws seed, fields, selections and exported files; ingest DK standings exports when the user provides them; compute projected-versus-actual minutes and ownership and a Flashback-style re-sim. Tune defaults only on held-out nights. [S21], [S68] What it means: a few minutes of manual exports per night buys the only honest measure of whether the engine is improving.
9. **Opening-night safety.** Default to wider minutes uncertainty, more weight on Vegas team totals, conservative washout ceiling, and a deadline-safe fallback file that is always valid even if the advanced layers fail. What it means: opening night trades some upside for a lower chance of a broken or stale submission.
10. **Explain every night in plain English.** A slate brief lists the key minutes calls, chalk and pivots, each contest's portfolio intent, tonight's washout estimate, and what changed since the last build, with a timestamp on every input. What it means: the user can approve or override a build in minutes without reading code or raw tables.

---

## Sources

Accessed October 13, 2026. "via helper" means fetched by the helper agent under the same evidence rules.

**SaberSim (help center and podcast)**
- [S1] Help Center home: https://support.sabersim.com/en/
- [S2] How do Contest Sims work?: https://support.sabersim.com/en/articles/17506264-how-do-contest-sims-work
- [S3] Saber Score vs Sim ROI: https://support.sabersim.com/en/articles/17506349-what-s-the-difference-between-saber-score-and-sim-roi
- [S4] Where do your projections come from?: https://support.sabersim.com/en/articles/17506644-where-do-your-projections-come-from
- [S5] How do I set up a custom Contest Sim?: https://support.sabersim.com/en/articles/17506298-how-do-i-set-up-a-custom-contest-sim
- [S6] Sim Diversity slider: https://support.sabersim.com/en/articles/17506457-what-does-the-sim-diversity-slider-do
- [S7] Correlation slider: https://support.sabersim.com/en/articles/17506464-what-does-the-correlation-slider-do
- [S8] Adj Own vs My Own: https://support.sabersim.com/en/articles/17506767-what-is-the-difference-between-adj-own-and-my-own
- [S9] Which ownership set?: https://support.sabersim.com/en/articles/17506865-which-ownership-set-am-i-supposed-to-use
- [S10] What happens when I change ownership?: https://support.sabersim.com/en/articles/17506780-what-happens-when-i-change-ownership
- [S11] How do I use my own ownership?: https://support.sabersim.com/en/articles/17506876-how-do-i-use-my-own-ownership
- [S12] What happens when I change projections?: https://support.sabersim.com/en/articles/17506741-what-happens-when-i-change-projections
- [S13] How do I make my lineups more diverse?: https://support.sabersim.com/en/articles/17507295-how-do-i-make-my-lineups-more-diverse
- [S14] How much exposure should I have?: https://support.sabersim.com/en/articles/17507375-how-much-exposure-should-i-have-to-a-player
- [S15] Exposures before or after building?: https://support.sabersim.com/en/articles/17507370-should-i-set-my-exposures-before-or-after-i-build
- [S16] How do I build lineups on SaberSim?: https://support.sabersim.com/en/articles/17506516-how-do-i-build-lineups-on-sabersim
- [S17] Build lineups for a specific contest: https://support.sabersim.com/en/articles/17506489-how-do-i-build-lineups-for-a-specific-contest
- [S18] Quick Swap vs Full Swap: https://support.sabersim.com/en/articles/17507052-when-should-i-use-quick-swap-vs-full-swap
- [S19] How do I Full Swap?: https://support.sabersim.com/en/articles/17507029-how-do-i-full-swap
- [S20] Delta Exposure for locked players: https://support.sabersim.com/en/articles/17507061-why-does-delta-exposure-show-a-number-for-a-locked-player
- [S21] How does Contest Flashback work?: https://support.sabersim.com/en/articles/17506355-how-does-contest-flashback-work
- [S22] Flashback ROI vs Sim ROI: https://support.sabersim.com/en/articles/17506386-why-is-my-flashback-roi-different-from-my-sim-roi
- [S23] Glossary: https://support.sabersim.com/en/articles/17507063-glossary
- [S24] Plans: https://support.sabersim.com/en/articles/17507079-plans
- [S25] Limits on lineup projection or ownership: https://support.sabersim.com/en/articles/17506976-how-do-i-set-limits-on-lineup-projection-or-lineup-ownership
- [S26] Late Swap collection (includes mobile notifications article title): https://support.sabersim.com/en/collections/19779220-late-swap
- [S27] DFS Office Hours show notes (topic lists only, no transcripts): https://sabersim.castos.com/episodes/dfs-qa-how-is-sabersim-calculating-the-projected-minutes-for-nba ; https://sabersim.castos.com/episodes/dfs-qa-how-does-sabersim-generate-ownership ; https://sabersim.castos.com/episodes/dfs-qa-how-accurate-are-sabersims-ownership-projections ; https://sabersim.castos.com/episodes/dfs-qa-how-does-sabersim-determine-ownership-differences-across-stake-levels ; https://sabersim.castos.com/episodes/dfs-qa-how-do-live-sims-impact-nba-lineups ; https://sabersim.castos.com/episodes/dfs-qa-how-andrew-builds-winning-nba-showdown-lineups

**Stokastic**
- [S28] Contest Generator (Jake Hari, July 13, 2026): https://www.stokastic.com/articles/dfs-strategy/stokastic-contest-generator
- [S29] NBA DataHub explained (Josh Engleman, August 1, 2026): https://www.stokastic.com/articles/nba-dfs/how-to-use-nba-dfs-data
- [S30] Contest Archetype and Percent To First (Jake Hari, August 1, 2026): https://www.stokastic.com/articles/dfs-strategy/stokastic-sims-contest-archetype-percent-to-first
- [S31] How Many Uniques (Jake Hari, July 19, 2026): https://www.stokastic.com/articles/dfs-strategy/how-many-uniques-dfs
- [S32] Build winning lineups in Stokastic Sims: https://www.stokastic.com/articles/dfs-strategy/build-winning-dfs-lineups-stokastic-sims
- [S33] NBA Sims Portfolio Manager: https://www.stokastic.com/articles/dfs-strategy/how-to-manage-dfs-lineups
- [S34] NBA DFS Research: minutes, usage and pace: https://www.stokastic.com/articles/nba-dfs/nba-dfs-research
- [S35] How to use NBA DFS projections: https://www.stokastic.com/articles/nba-dfs/how-to-use-nba-dfs-projections
- [S36] NBA DFS Late Swap (Staff, July 15, 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-late-swap
- [S37] When do NBA DFS projections update? (Jake Hari, July 19, 2026): https://www.stokastic.com/articles/dfs-strategy/when-do-nba-dfs-projections-update
- [S38] NBA starting lineups leverage (Josh Engleman, June 17, 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-starting-lineups-leverage
- [S39] NBA DFS without late swap (Staff, July 15, 2026): https://www.stokastic.com/articles/nba-dfs/nba-dfs-without-late-swap
- [S40] How To Make DFS Projections (Alex Baker, July 15, 2026): https://www.stokastic.com/articles/dfs-strategy/how-to-make-dfs-projections
- [S41] How to use NBA DFS ownership projections (Staff, July 15, 2026): https://www.stokastic.com/articles/nba-dfs/how-to-use-nba-dfs-ownership-projections
- [S42] 2023-24 NBA DFS packages: https://www.stokastic.com/news/2023-24-nba-dfs-packages-how-stokastic-experts-are-raking-in-the-winnings-with-contest-sims-late-swap-tool-more/
- [S43] Best DFS Tools 2026 (vendor comparison, Staff, July 16, 2026): https://www.stokastic.com/articles/dfs-strategy/best-dfs-tools
- [S44] Did not render (title only, no claims made): https://www.stokastic.com/nba/nba-ownership-projections-draftkings/ ; https://stokastic.com/nba/nba-dfs-showdown-single-ownership-projections/ ; https://stokastic.com/nba/how-to-use-nba-dfs-sims-expert-strategy-guide-tips-advice-ac11 ; https://www.stokastic.com/nba/nba-dfs-tools-how-to-turn-4-into-1000-w-stokastic-ac14

**RotoGrinders and FantasyLabs**
- [S45] SimLabs FAQ (created October 3, 2023; updated September 15, 2026): https://rotogrinders.com/articles/dfs-sims-faq-3952660
- [S46] LineupHQ: https://rotogrinders.com/lineuphq
- [S47] Key Inputs in an NBA Projections System (Derek Farnsworth, updated April 9, 2024): https://rotogrinders.com/lessons/key-inputs-in-an-nba-projections-system-1144825
- [S48] Predicting Minutes, Adjusting for Injuries (paywalled course, topic list only): https://rotogrinders.com/lessons/predicting-minutes-adjusting-for-injuries-updating-projections-2843200
- [S49] Late swap lesson (preview only, 2016): https://rotogrinders.com/lessons/how-do-i-manage-all-of-these-teams-late-swap-1418021
- [S50] RotoGrinders Contests Dashboard announcement (via helper; updated February 3, 2022): https://rotogrinders.com/pages/fantasylabs-contests-dashboard-now-live-on-rotogrinders-3751657
- [S51] FantasyLabs Tools: https://www.fantasylabs.com/tools/
- [S52] Announcing FantasyLabs NBA Ownership Projections (Jonathan Bales, October 25, 2016): https://www.fantasylabs.com/?p=30693
- [S53] Bitcoin, Projections, and Rankings (Matthew Freedman, December 1, 2017): https://www.fantasylabs.com/?p=76532
- [S54] 5 Tips to Dominate the DraftKings NBA Showdown Format (Matt LaMarca, May 30, 2019): https://www.fantasylabs.com/?p=109841
- [S55] FantasyLabs Support (HTTP 403, not observed): https://support.fantasylabs.com/hc/en-us/articles/20710673521293-What-is-the-Difference-Between-SimLabs-and-an-Optimizer ; https://support.fantasylabs.com/hc/en-us/articles/20710246632077-How-Does-SimLabs-Work ; https://support.fantasylabs.com/hc/en-us/articles/360037582352-Ownership-Projections

**Ship It Nation**
- [S57] Product and pricing page: https://shipitnation.com/

**Establish The Run**
- [S58] NBA Daily Content Schedule: https://establishtherun.com/nba-daily-content-schedule/
- [S59] NBA DFS Projections page: https://establishtherun.com/draftkings-nba-projections/
- [S60] Showdown and Single Game Projections (paywalled): https://establishtherun.com/draftkings-showdown-and-fanduel-single-game-projections/
- [S61] DFS NBA Top Plays: August 15th Showdown (Drew Dinkmeyer, 2020): https://establishtherun.com/dfs-nba-top-plays-august-15th-showdown/
- [S62] How to Beat DFS: NFL Showdown 101 (Cody Main, September 5, 2026): https://establishtherun.com/nfl-showdown-101/
- [S63] Home page (menu only): https://establishtherun.com/

**DARKO**
- [S64] About and methodology: https://www.darko.app/about
- [S65] Home: https://www.darko.app/

**Long-tail tools**
- [S66a] DFS Hero simulator: https://dfshero.com/help/simulate/how-the-simulator-works ; home: https://dfshero.com/
- [S66b] DFS Hero NBA guide: https://dfshero.com/help/sports/nba
- [S66c] DFS Hero late swap (via helper): https://dfshero.com/help/late-swap/what-late-swap-does
- [S66d] DFS Hero tools (via helper): https://dfshero.com/tools
- [S66e] DFS Hero pricing (via helper): https://dfshero.com/pricing
- [S67a] Daily Fantasy Fuel NBA projections, NBA home, Showdown projections, premium (via helper): https://www.dailyfantasyfuel.com/nba/projections/ ; https://www.dailyfantasyfuel.com/nba/ ; https://www.dailyfantasyfuel.com/nba/showdown-single-game-projections/ ; https://www.dailyfantasyfuel.com/premium/
- [S67b] Daily Fantasy Fuel NBA injuries: https://www.dailyfantasyfuel.com/nba/injuries/
- [S67c] Daily Fantasy Fuel terms of service (updated June 7, 2026): https://www.dailyfantasyfuel.com/terms-of-service
- [S68] LineStar (via helper): https://www.linestarapp.com/ ; https://www.linestarapp.com/Projections/Sport/NBA ; https://www.linestarapp.com/Ownership/Sport/NBA/Site/DraftKings
- [S69] Basketball Monster (via helper): https://basketballmonster.com/dailyprojections.aspx ; https://basketballmonster.com/nbalineups.aspx ; https://basketballmonster.com/Help.aspx ; https://basketballmonster.com/questionsanswered.aspx ; https://basketballmonster.com/membership.aspx
- [S70] FantasyCruncher (via helper): https://www.fantasycruncher.com/help/faqs ; https://www.fantasycruncher.com/fc-pro ; https://www.fantasycruncher.com/help/tutorials
- [S71] SpikeWeek (via helper): https://spikeweek.com/draftiq-help/ ; https://spikeweek.com/dfs-ownership-visualizer/
- [S72] Fantasy Points (HTTP 402, not observed): https://www.fantasypoints.com/nba

**RotoWire**
- [S73] DFS NBA: Showdown and Single-Game Strategy (Jeff Edgerton, May 18, 2021): https://www.rotowire.com/basketball/article/dfs-nba-showdown-and-single-game-strategy-57179
- [S74] NBA Projected Minutes Explained (Mark Strotman, updated December 10, 2025): https://www.rotowire.com/basketball/article/nba-projected-minutes-explained-fantasy-basketball-97473
- [S75] DFS Football 101, Round 4 (Michael Rathburn, 2016; describes DK "Export Lineups to CSV"): https://www.rotowire.com/football/article/dfs-football-101-important-tips-for-new-players-round-4-29758

**Academic**
- [S76] Hunter, Vielma, Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming," arXiv 1604.01455 (v3, January 23, 2019): https://arxiv.org/abs/1604.01455 (PDF read: https://arxiv.org/pdf/1604.01455)
- [S77] Haugh and Singal, "How to Play Strategically in Fantasy Sports (and Win)," workshop slides, May 17, 2019: https://cfe.columbia.edu/sites/default/files/content/slides/How%20to%20Play%20Fantasy%20Sports%20Strategically%20(and%20Win).pdf . Journal version: Management Science 67(1), 2021, doi 10.1287/mnsc.2019.3528 (not read; SSRN abstract page returned 403 and the Columbia repository blocked automated access).
- [S78] Decary, Bergman, Cardonha, Imbrogno, Lodi, "The Madness of Multiple Entries in March Madness," arXiv 2407.13438 (July 18, 2024): https://arxiv.org/abs/2407.13438
