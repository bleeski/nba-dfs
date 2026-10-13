# S1. First-principles sketch (draft 1, before repo review)

**Status:** working draft written from the brief, the four attached files, and the research memos R1 to R7. It was written before opening any of the user's prior repos, on purpose. S2 records what the repo review changed.

## Part A. The two goals as math

### A1. Notation

- A **night** is a set of contests. Each contest `c` belongs to one **slate** (DraftKings calls it a draft group): the Classic main slate, an early or late Classic slate, or one Showdown game.
- `N_c` is the contest's field size at lock. `n_c` is how many entries we hold in it. `N'_c = N_c - n_c` is the number of opponent entries.
- `k_c` is the number of top-1% places: `k_c = max(1, floor(0.01 x N_c))`. In a field under 200 entries this is 1, so "top 1%" means first place there. (The brief says first place for fields under 100. Fields of 100 to 199 also round down to one place; the formula makes that explicit.)
- `m_c` is the number of paid places (from the payout table).
- A **scenario** `s` is one joint simulated outcome of every game that night: every player's box score and DraftKings points, at UTIL and at Captain. We draw `S` scenarios (10,000 to 20,000). Classic and Showdown contests that share a game read the same simulated game, which is how cross-contest correlation enters.
- `X_L(s)` is the DraftKings score of lineup `L` in scenario `s`.
- The **field model** for contest `c` is a probability distribution over opponent lineups. Given scenario `s`, one random opponent's score has distribution function `F_{c,s}(x)`, the probability that an opponent scores `x` or less. We estimate `F_{c,s}` by scoring a large weighted sample of field lineups in every scenario.
- `B_c(s)` is the score of our best lineup in contest `c` in scenario `s`: `B_c(s) = max over L in E_c of X_L(s)`, where `E_c` is our set of entries in `c`.

### A2. Goal 1: probability of a top-1% finish in each contest

Our best entry is top 1% when fewer than `k_c` opponents beat it. If opponents' lineups are independent draws from the field model (given the scenario), the number of opponents who beat score `x` is binomial with `N'_c` trials and success probability `1 - F_{c,s}(x)`. So:

```
P(top 1% in c | s) = BinomCDF( k_c - 1 ;  N'_c ,  1 - F_{c,s}( B_c(s) ) )

G1_c = average over scenarios s of  P(top 1% in c | s) x share_c(s)
```

- When `k_c = 1` this is `F_{c,s}(B_c(s))` raised to the power `N'_c`: the chance we beat every opponent.
- One formula covers single-entry, 3-max, 20-max, and 150-max contests, and fields of any size. For multi-entry contests it is exactly "the probability at least one of our entries is top 1%", because only our best entry matters for that event.
- **Duplication.** `share_c(s)` is the fraction of the prize we would keep after ties. If opponents also hold our exact lineup, DraftKings pools the prizes for the tied places and splits them evenly. A five-way tie for first in a top-heavy contest keeps roughly a fifth of first-place money, so it counts as about 0.2 of a top-1% finish. A tie deep in the top 1%, where neighboring prizes are nearly equal, keeps nearly everything, so it counts as nearly 1. `share_c` uses the contest's payout table and the field model's estimate of how many opponents hold the same lineup. We report both the raw `P(top 1%)` and the duplication-adjusted `G1_c`, and we optimize the adjusted one.
  - *Why penalize at all:* the point of a top-1% finish is the prize. Without a penalty, the optimizer would favor the chalkiest version of a good lineup in Showdown, where exact duplicates are common, and the user would win titles that pay a fraction of first place.
  - *Why not a flat 1/(1+D) penalty:* it overcharges ties deep in the top 1%, where a tie barely changes the payout, and would push the optimizer away from good lineups for no money.

### A3. Goal 2: probability of a total washout across the night

A washout means no entry cashes anywhere. Our best entry in a contest cashes when fewer than `m_c` opponents beat it, so:

```
P(no cash in c | s) = 1 - BinomCDF( m_c - 1 ;  N'_c ,  1 - F_{c,s}( B_c(s) ) )

P(W) = average over scenarios s of  product over contests c of  P(no cash in c | s)
```

- The product is taken inside each scenario. Contests are treated as independent only after we condition on the simulated night, which keeps the dependence that matters: one game going badly hurts every Classic and Showdown entry that leaned on it, in the same scenario.
- For large fields the binomial is nearly a step, so `P(no cash in c | s)` is close to 1 when `B_c(s)` falls below the min-cash line and 0 when it is above. For small fields it stays smooth.

### A4. Why the two goals mostly agree (the hunch, stated as math)

Both goals are functions of the same object: the per-contest best-score vector `B_c(s)` across scenarios.

- Goal 1 rewards pushing `B_c(s)` above the **top-1% line** of contest `c` in as many scenarios as possible. In a multi-entry contest the only way to do that is to make different entries win in different scenarios. That is coverage of ways the night can unfold.
- Goal 2 rewards having, in **every** scenario, at least one contest where `B_c(s)` clears the much lower **min-cash line**. That is also coverage of ways the night can unfold.

They disagree in three specific places:

1. **Target height.** The top-1% line sits far above the min-cash line (roughly the 99th and the 75th to 80th percentiles of the field). A lineup built for a ceiling gives up some floor. In a single-entry contest, where we hold one lineup, any floor we buy costs ceiling directly.
2. **Cross-contest concentration.** Goal 1 scores each contest alone, so it is indifferent to whether every contest leans on the same game or the same star. Goal 2 is not. The pure-Goal-1 portfolio tends to reuse the same best thesis everywhere, which creates the correlated failure that causes washouts.
3. **Night composition.** Showdown contests depend on one game each. A night heavy in Showdown has more scenarios where several contests fail together.

The hunch therefore predicts something testable: near the Goal-1 optimum, many different theses score almost the same, so spreading theses across contests buys a large washout reduction for a small Goal-1 cost. If the optimum is sharp instead (one thesis clearly best), insurance is expensive. We measure the slope of the tradeoff every night (A6) and publish it in the slate brief.

### A5. The control: the insurance budget

One setting, `insurance_budget` (call it epsilon), between 0% and 25%.

```
For each contest c, let G1*_c be the best Goal-1 value we can find for c alone.
Choose the night's portfolio that minimizes P(W)
subject to G1_c >= (1 - epsilon) x G1*_c for every contest c.
```

- In words: "I'm willing to give up at most epsilon of my top-1% odds, in every contest, to lower the chance of a night with zero cashes." At 0% the engine maximizes top-1% odds and uses washout only to break ties. At 25% it buys as much washout protection as a quarter of the top-1% odds can pay for.
- Each contest keeps its own guarantee, so Goal 1 stays "within each contest" and no contest is quietly sacrificed for another. The control also needs no weighting between contests of different sizes or fees.
- The setting means the same thing every night, regardless of how many contests or entries the night has. A fixed washout target ("at most 2%") would be impossible on some nights and meaningless on others.
- Proposed default: 5% (a bet, revisited after the first 20 nights of measured frontiers).

### A6. How each goal is estimated, and how precise it is

- **Monte Carlo.** We simulate `S` scenarios of the night, score all candidate and field lineups in each scenario, and average. With 20,000 scenarios, a 1% probability carries a standard error of about 0.07 percentage points, and a 5% washout probability about 0.15 points.
- **Common random numbers.** Every comparison (portfolio A against B, before QA against after) uses the same scenarios, so the difference is far more precise than either number alone.
- **The frontier.** Each night the engine reports Goal 1 per contest and `P(W)` at epsilon = 0%, 2%, 5%, 10%, and 20%. The slate brief shows what each step buys.
- **Honesty about model error.** Monte Carlo precision is not accuracy. If player distributions are too narrow, or correlation is too weak, `P(W)` will be too low. The learning loop checks this with fast signals: predicted cash probability per entry against realized cashes (50 to 200 entries a night), and predicted top-1% and min-cash scores against the actual lines in each standings file.

## Part B. What the engine is, from first principles

### B1. The problem in one paragraph

Each night the user holds entries in about 10 contests across 3 to 5 DraftKings slates (one Classic main slate, sometimes an early or late Classic slate, and 2 to 4 Showdown games that are also on the main slate). The engine must turn uncertain information (injury news, roles, betting lines, ownership) into a joint picture of how the night could unfold, then choose lineups for every entry so that each contest has the best chance of a top-1% finish and the night as a whole rarely ends with zero cashes. It must deliver valid upload files every time, react to news 30 minutes before tip, run on a laptop, and fit inside a Pro-sized Claude budget.

### B2. Design principles that follow from the goals

1. **One simulated night, shared by every contest.** Both goals are functions of per-contest best scores across the same scenarios (Part A). Separate simulations per contest would make washout look rarer than it is.
2. **Arithmetic belongs to code; judgment belongs to the LLM; the boundary is a schema.** The LLM reads news and writes structured, evidence-backed records (availability, minutes ranges, usage shifts). Code turns those into distributions, lineups, and probabilities. The LLM never writes a lineup or a number into an upload file.
3. **Valid output first, better output second.** A valid fallback portfolio exists within minutes of ingest. Every later stage may only replace it with something that also passes the validator.
4. **Every layer is scored on its own.** Projections before and after LLM overrides, portfolios before and after QA, ownership predicted and actual. Learning happens per layer, where the signal is dense.
5. **Manual where the terms require it.** DraftKings' terms bar automated access to its site, so every DraftKings file enters through the user's hands. Third-party data follows the posture the user chooses.
6. **Claude runs only when the user types a command.** Background polling for news is plain Python that alerts; it never invokes Claude.

### B3. Components (deterministic Python unless marked LLM)

| # | Component | Job | Output |
|---|---|---|---|
| 1 | Inbox and ingest | Parse the user's DraftKings files (one DKEntries per slate, optional DKSalaries for `Status`, pasted payout tables, next-day standings, entry history). Identify each slate from its embedded player list. Fail closed with plain-language errors. | Slate and contest records |
| 2 | Source adapters | Pull schedule, injury report, lines, props, history, and news under the chosen data posture, rate limited, every response snapshotted with a timestamp and hash. | Raw snapshots |
| 3 | Identity map | Link DraftKings IDs to NBA person IDs and names (accent folding, team, position). | Player map, unresolved list |
| 4 | Priors and rates | Per-possession rates with shrinkage and per-stat recency decay; aging; rookie priors; early-season variance inflation. | Rate distributions |
| 5 | Availability | Official status to probability of playing, plus overrides; questionable players stay random inside the simulation. | P(active) per player |
| 6 | Minutes and usage | Minutes distributions by role; redistribution when teammates sit; usage shares that sum to 100%. | Minutes and share parameters |
| 7 | Market anchor | Game lines give team totals and pace; props (when available) pull player stat means toward the market. | Adjusted means |
| 8 | Override store (LLM-fed) | Validate and blend LLM and user overrides by precision weighting; keep the before and after. | Blended parameters, override log |
| 9 | Night simulator | Stat-level joint simulation with game, team, and player factors; blowouts, overtime, and availability drawn per scenario. | X[scenario, player] |
| 10 | Scoring adapter | Versioned DraftKings scoring (triple-double +4.5; Captain 1.5x of the bonus-inclusive total). | DK points |
| 11 | Ownership and field | Simulated opponents (noisy optimizers, ownership-weighted casuals, chalk duplicators) per contest archetype; ownership is read off the field. | Field samples, ownership, duplicate counts |
| 12 | Contest model | Payout table (exact or estimated), top-1% and min-cash places, per-scenario thresholds. | T1 and Tc per contest and scenario |
| 13 | Candidate generator | Classic: MILP on scenario points and leverage-adjusted means. Showdown: full enumeration, screened. | Candidate pools |
| 14 | Portfolio selector | Greedy coverage per contest, insurance-budget control across the night, guardrails, late-swap-friendly slot assignment. | Portfolio plus frontier |
| 15 | Validator and exporter | DraftKings rule checks from R6; the only writer of upload files; re-parses its own output. | Upload CSVs |
| 16 | Late swap | Pin locked players, condition on finished games, re-optimize open slots, apply precomputed contingency swaps. | Swap upload CSVs |
| 17 | Brief | Two-minute slate brief: thesis, assumptions, exposures, risks, what news would change the build, what was skipped. | Markdown |
| 18 | Run store and replay | Manifest per run: inputs, snapshots, versions, seeds, decision records, outputs. | Replayable runs |
| 19 | Learning | Standings and box-score ingest, per-layer scorecards, challenger models in shadow, adoption workflow. | Scorecards, proposals |
| 20 | LLM: news researcher | Reads a deterministic news diff, searches sparingly, files override records with evidence. | Override JSON |
| 21 | LLM: QA adversary | Independent review of the portfolio; files typed change proposals with evidence; code scores them. | Proposal JSON |

### B4. The LLM and solver boundary

The LLM sets beliefs; the solver sets lineups.

- **LLM may:** assess availability of questionable players (probability with evidence), express role changes as minutes and usage ranges (the R3 override schema), flag stale or conflicting data, propose player-pool exclusions with a reason, propose QA changes of fixed types, and write the thesis paragraph of the brief.
- **LLM may not:** pick players for lineups, set exposures by feel, edit projections directly, write upload files, or touch DraftKings.
- **Why:** the objective is a probability over thousands of scenarios and opponents. No reader, human or model, can compare thousands of candidate lineups on that objective; code can. Keeping the LLM's contribution as structured beliefs also makes it measurable, because every override has a model-only twin to score against.

### B5. Late news and late swap

- **Questionable players are random in the simulation.** Each scenario draws whether they play and redistributes minutes accordingly, so lineups are judged across both branches before the news.
- **Contingency swaps are precomputed.** For every entry holding a questionable player, the engine stores the best legal replacement in the same slot at equal or lower salary, under both branches. When news lands, applying the swap map takes seconds and needs no LLM.
- **Re-run path.** News triggers a narrow re-run: refresh availability for the affected team, re-simulate that game, rebuild candidates only for affected slates, re-select, validate, export. The full night is not rebuilt.
- **Lock waves.** After each lock, the user re-downloads the entries file. The engine pins locked players, treats finished or in-progress games as known, and re-optimizes only open slots against the post-lock field, where late pivots are low-owned.
- **Swap flexibility is bought, not assumed.** Slot assignment places late-game players in UTIL, G, and F where eligibility allows, at no cost. Beyond that, the selector values flexibility through the simulation, so the engine pays for flexibility on uncertain nights and not on quiet ones.

### B6. Showdown

- Captain and UTIL are different DraftKings IDs with a 1.5x salary; the engine pairs them by name and team, never by ID arithmetic, and reads slot labels from the file header.
- Every legal lineup can be enumerated (about 440,000 for a 22-player pool in 0.015 seconds, R2), so Showdown needs no solver.
- Captain and UTIL ownership are modeled separately; the field model generates Showdown fields large enough to count exact duplicates.
- The duplication-adjusted Goal 1 matters most here: chalky Captain builds tie often, and ties split prizes.

### B7. Ownership and the field

- **Ownership is an output of a simulated field, not a separate guess.** Opponents are a mixture of noisy optimizers, ownership-weighted casuals, and chalk duplicators, weighted by contest archetype (stake, size, entry limit). Ownership falls out of how often each player appears. Late news flows through automatically: when a starter sits, the simulated optimizers pick up the cheap replacement, which is how real "new chalk" forms.
- **Cold start:** the field's few knobs (noise, casual share, salary floor, share of stale lineups that never update after news) start from published rules of thumb and are fitted to the user's own standings files from night 2.
- **Uncertainty:** several field realizations per contest (Dirichlet draws around the ownership), so one wrong ownership guess cannot make thresholds look certain.

### B8. Learning

- **Fast signals (per player, nightly):** minutes and points error, distribution calibration (PIT, coverage, CRPS), ownership error, field realism (salary left, duplicates, top-1% and min-cash lines against prediction), override value, QA value.
- **Slow signals (per contest):** cash rate against paid share, top-1% rate, washout nights. Mostly noise for months; reported with intervals and never used alone to change the model.
- **Adoption:** challengers run in shadow, are compared night by night on held-out nights with a paired test, and need the user's sign-off before becoming the default. Every model and config is versioned.

### B9. Where this departs from the user's vision (first pass)

1. **Inputs:** one DKEntries file per slate replaces "the salary file plus the entries file", because each entries file already contains its slate's player list with IDs (R6). Payout tables come from an optional paste or a default by contest class.
2. **Order:** a valid fallback portfolio is built before any LLM step, then improved.
3. **LLM role:** the LLM files structured beliefs; the solver assigns players to lineups.
4. **QA:** proposals are typed and scored by re-simulation; an argument alone never changes the portfolio.
5. **Ownership:** produced by the field simulation rather than projected separately, so it reacts to news by construction.
6. **New steps:** contingency swaps for questionable players, lock-wave late swap, the night-level washout control and frontier, and a morning-after results step that feeds every layer's scorecard.

### B10. Open items before the repo review

- Data posture (strict or personal-use) is the user's call; the source layer must make it a configuration switch.
- Runtime and memory budgets wait on the R9 night benchmark.
- Opening night (Oct 20) appears to lock at 2:00 pm CT (DraftKings lobby, R6), before the user's usual 1 to 4 pm build window.
- The Team seat may be the user's employer's; personal use needs the user's confirmation.
