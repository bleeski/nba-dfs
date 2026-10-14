# NBA DFS Engine Brief: Adversarial Critique

**Review date:** October 13, 2026. **Reviewer:** Codex.

**Material reviewed:** the brief in this conversation; all four named attachments; and the existing version 3 design in this workspace, including its relevant decision records, research memos, and selected saved benchmark/scoring evidence. The workspace was clean at commit `9f9a44ab47912c1d520911e881be34e805af6e5c`. The reviewed [ARCHITECTURE.md](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md) has SHA-256 `7999d1a73ae3e7abea327564c73aaed3a96b7d883d1311325572a106923b4bd6`.

**Reading key:** confidence rates the support for each finding, not the probability of a forecast. Document statements and web observations are evidence; worked examples are hypothetical; consequences and proposed fixes are reviewer judgments. No finding asserts that the live engine has already failed, because it has not been built.

**Evidence limits:** this is a critique, not a new architecture or an execution of the brief. I inspected the design's saved evidence; I did not rerun its benchmarks, access your DraftKings account, or independently audit the five prior engines. Their historical results are claims in the supplied research, not independently established facts in this review. Web checks below distinguish readable documentation from a working data feed on your laptop. Current NBA salary/entries exports, a live upload round trip, and a complete current-season source chain remain unverified by this review.

## Verdict

The brief can produce a functioning lineup tool by October 20, but it does not establish that the tool will improve either goal against real opponents. The supplied design turns guessed contest facts, an unrealistically weak synthetic field, and uncalibrated model confidence into precise-looking probability claims. It also changes the meaning of Goal 1 through a defective duplication score and can launch without the control required to pursue Goal 2. Its opening-week schedule leaves critical behavior untested until after the last dress rehearsal, while assigning you substantial manual work. Fix the measurement contract, restrict the launch to a rehearsed capability, and require evidence of improvement before treating sophistication as an edge.

## Top five

1. **I-01: Tonight's payout facts cannot come from yesterday's history**
2. **I-02: The simulated edge manufactures confidence in both goals**
3. **I-03: Opening night can ship without the promised product**
4. **I-04: Both goals can improve while your financial results deteriorate**
5. **I-05: The duplication adjustment is neither a probability nor expected money**

## Issues

### I-01: Tonight's payout facts cannot come from yesterday's history

**Severity:** Blocker · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§2, 3, 10; R8-user-nba-history.md

**What it is.** The brief correctly identifies missing contest details but does not make their acquisition a prerequisite for claiming to optimize its goals. The design fills the gap with entry history, contest names, and family defaults. Its own [history memo](C:/Users/benja/Documents/Claude/nba-dfs/docs/research/R8-user-nba-history.md) says that entry history supplies exact facts **after the contest**. That cannot establish tonight's new contest's field size, paid places, or complete payout ladder. A familiar contest name and advertised prize pool do not uniquely identify those facts.

The [Goal 2 definition](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:74) permits an approximately 23% paid share. R8 reports a 0.4% to 27.8% range between the 10th and 90th percentiles of historical Classic paid shares. Some of that range is from other contest types, which reinforces the need to classify them rather than average them together.

**Why it's worth solving.** **Judgment:** A portfolio can appear protected from washout because the model invented a cash line far below the real one. Field capacity, actual filled entries, and the number of opponents are also different quantities. Using a post-contest field count in a historical pre-lock test leaks future information.

**Recommended solution and why.** Require a small, manual, contest-specific facts capture before optimization. Historical templates can prefill the form, but cannot mark it verified. Before lock, use the observed entry count and capacity with explicit fill assumptions; after settlement, use actual counts and prizes to grade outcomes. Cash, ticket awards, refunds, and cancellations need separate treatment.

Replace the brief's contest-details requirement with:

> For each current contest, record its entry fee, entry limit, field capacity, observed entries with timestamp, and exact payout schedule or verified paid cutoff. Historical contest families supply estimates only. Missing facts do not prevent a legal fallback file, but they prevent claims of measured cash probability, washout protection, or payout-aware optimization for that contest. Never infer cashing from finishing percentile alone.

### I-02: The simulated edge manufactures confidence in both goals

**Severity:** Blocker · **Affects:** Both goals · **Confidence:** High · **Applies to:** ARCHITECTURE.md §§1, 2, 5; R9-night-benchmark.md; ADR-001

**What it is.** The design repeatedly concludes that washout barely matters at 50 or more entries. Its [benchmark](C:/Users/benja/Documents/Claude/nba-dfs/docs/research/R9-night-benchmark.md) explicitly says the synthetic opponents are too weak: synthetic single entries cash about 31% to 44% against 22% paid, and Classic ownership is unusually dispersed. The later uncertainty experiment still gives the engine a favorable relationship to truth. The architecture acknowledges that the more adversarial error layer failed its acceptance bar and [excludes it from Phase 1 selection](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:93).

Zero washouts in 30,000 draws limits sampling uncertainty **inside that invented world**. It does not bound real washout risk. Calling synthetic washout a “lower bound” is also unjustified without a mathematical relationship showing that every relevant real-world alternative has greater risk.

**Why it's worth solving.** **Judgment:** The model can disable your insurance control precisely when it is most overconfident. More simulations then make a wrong answer look more settled. Shared minutes mistakes, correlated late-news misses, stronger opponent projections, and failed uploads can defeat a large portfolio together.

**Recommended solution and why.** Keep the runtime result; discard the strategic reassurance. Before selection relies on these probabilities, require tests against several plausible opponent and error settings, including no edge, a stronger field, concentrated news-driven chalk, and mistakes shared across every contest. Compare portfolios under all of them. Treat unresolved washout as unknown or assumption-sensitive.

Replacement text:

> Simulation count controls numerical noise, not truth. Synthetic tests may establish speed and arithmetic only. Do not use them to claim real washout bounds, establish the insurance default, or declare the two goals compatible. Report the sensitivity of both goals to plausible field strength and shared forecast errors, and preserve the uncertainty in selection.

### I-03: Opening night can ship without the promised product

**Severity:** Blocker · **Affects:** Feasibility · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§8, 13; ADR-019; ADR-022

**What it is.** The brief allows models to mature but still requires sensible portfolios, late-news handling, and one functioning tradeoff control. The [build plan](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:1010) permits Tier A alone to launch, although that tier does not optimize the two goals. The insurance search can arrive after opening night. Stored replacements and the watcher are Tier C, even though Tier A already advertises the command that applies them.

The Friday dress rehearsal precedes weekend work on the remaining selection logic, Claude integration, and insurance. The researcher's first live run is Monday evening. Thus Friday's success cannot certify Tuesday's materially changed product.

The NBA confirms October 20 and a 3 p.m. Eastern opening tip, or 2 p.m. Central. [NBA schedule announcement](https://www.nba.com/news/nba-schedule-season-opener-2026-27).

**Why it's worth solving.** **Judgment:** “Valid file” becomes a substitute for the product promised. Meanwhile [30 to 45 minutes of manual work plus an evening on call](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:758) is a substantial operating commitment. Projecting that workload from a few small rehearsals does not test simultaneous alerts, several uploads, or a stalled confirmation.

**Recommended solution and why.** Define two honest release states: an operational baseline that submits sensible entries, and a model that has earned probability-based selection. A baseline can launch without pretending to satisfy the full optimization promise. Require a replay and operator drill after the final substantive change. Include a measured recovery path for news affecting an unlocked player or beneficiary.

Replace the MVP language with:

> Opening-night acceptance requires a complete, frozen workflow that Ben has rehearsed, including an initial confirmed upload, one late-news update, and recovery with Claude unavailable. A baseline launch may defer the probability optimizer and insurance control, but must label those capabilities unavailable. Upload and confirm the baseline early; replace it only after an improved file passes checks. An unrehearsed feature stays off.

Do not leave the baseline unuploaded until the full build “looks at risk,” as the current runbook proposes. Early confirmation removes a preventable deadline gamble.

### I-04: Both goals can improve while your financial results deteriorate

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§2, 9, 14

**What it is.** Top 1% is a rank event, not a large-prize event. In a 20,000-entry field it includes places 1 through 200, despite potentially enormous payout differences. “At least one” ignores how many other entries win and the total returned. Washout treats a tiny cash as full success even if nearly the entire night's entry fees are lost.

For example, spending $100 and returning $1 is a non-washout. A method that raises that outcome's frequency can improve Goal 2 without meaningful downside protection. Adding inexpensive entries can also reduce washout mechanically, without improving lineup skill.

**Why it's worth solving.** **Judgment:** A 150-entry portfolio can chase broad coverage of marginal top-1% outcomes at the expense of first-place value. Conversely, washout protection can buy frequent small cashes at a large cost to exceptional outcomes. Neither behavior is necessarily wrong under your stated preferences, but neither means “better financial results.”

The [volume-ramp recommendation](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:1088) compounds this by proposing increased volume after beating median finish and a control portfolio. Median finish does not establish favorable returns after entry fees.

**Recommended solution and why.** Preserve your two fixed objectives. Add economic diagnostics and constrain comparisons to the same contests, entry counts, and total fees. Expected value means average net dollars across outcomes; ROI means net return divided by entry fees. Neither should be advertised as calibrated before the model earns that claim.

Replacement text:

> Always report the two objectives alongside total fees, expected net return under stated assumptions, probability of recovering the night's fees, severe-loss probability, and probability of a meaningful prize. A non-washout is not a profitable night. Changes in volume are reported separately from changes in skill. Better median rank alone never justifies scaling spend.

### I-05: The duplication adjustment is neither a probability nor expected money

**Severity:** Major · **Affects:** Goal 1 · **Confidence:** High · **Applies to:** ARCHITECTURE.md §2; ADR-009-duplication-as-prize-share.md

**What it is.** [ADR-009](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-009-duplication-as-prize-share.md) scores each simulated contest using the best of our entries' top-1% probability multiplied by its retained prize fraction. That changes the literal goal, and it does not calculate expected payout.

Consider one hypothetical scenario in which both alternatives finish in the top 1%. A lineup shares a $10,000 first prize and receives $1,000 after settlement, a retained fraction of 0.10. Another wins $100 uniquely, a retained fraction of 1.00. The proposed score prefers the $100 outcome. Both fulfill the rank goal equally; the first delivers ten times more money. With multiple entries, taking a maximum also discards the money earned by the other entries.

Exact duplicate lineups are not the only ties. Different NBA lineups can finish with identical scores. [DraftKings' tie rules](https://support.draftkings.com/dk/en-us/what-happens-when-i-tie-with-others-in-a-fantasy-sports-contest?id=kb_article_view&sysparm_article=KB0010633) pool the prizes across tied positions and divide them among the tied entries.

**Why it's worth solving.** **Judgment:** The design appears payout-aware while systematically rewarding retained percentage rather than the amount retained. Showdown is where this distinction is most consequential.

**Recommended solution and why.** Keep raw top-1% probability intact. Evaluate dollars with a separate contest settlement calculation covering all our entries, all equal-score ties, and their occupied ranks. If payout is a tie-breaker or an explicit tradeoff, name it that way. Do not describe prize-weighted utility as a probability.

Replacement text:

> Duplication never changes the definition of a top-1% finish. Report raw Goal 1 separately from expected settled winnings. Any duplication-aware preference must use actual dollars after all score ties, rather than a normalized prize-retention fraction, and must disclose any sacrifice in raw Goal 1.

### I-06: The field can be wrong in ways ownership accuracy will not reveal

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§2, 5; ADR-008

**What it is.** The design derives ownership, duplicate counts, and score thresholds from one guessed opponent generator. If they agree, that is internal consistency, not three independent confirmations. Matching player ownership does not establish that the generator combines players correctly or represents strong opponents.

Calling one free projection feed the “public view” is particularly weak when your opponents use different paid projections. Labeling an inference private does not make it unique to you. Other players can independently infer the same rotation change.

There is also an unresolved mathematical assumption: [Goal 2 multiplies contest failure probabilities](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:113), asserting independence after conditioning on the simulated night. Common player outcomes and one ownership shock do not automatically capture the same opponents, copied builds, vendor-driven chalk, and late-swap behavior across contests. The user-clustered field in §5 is not reconciled with §2's independent-opponent binomial calculation.

**Why it's worth solving.** **Judgment:** A field that is too weak or combines its chalk incorrectly will overstate top-end chances. Unmodeled dependence between contest cash lines can understate night-wide washout. Collecting thousands of lineups from one game does not establish performance on a different news regime.

**Recommended solution and why.** Demand separate checks of marginal ownership, player combinations, salary usage, Captain combinations, exact duplicates, entrant portfolios, and realized score cutoffs. Use several opponent archetypes and projection disagreements while evidence is thin. For washout, carry shared opponent behavior across contests or show a sensitivity range for that missing dependence. Define switch-on tolerances before seeing results; “about five files” is not a calibration standard.

Replacement text:

> Treat the field as a family of plausible opponent behaviors. Ownership fit alone cannot qualify it. Qualify thresholds and duplication separately, using held-out games and news conditions; explicitly test dependence across contests. Private inference is a hypothesis about informational advantage, not evidence that opponents lack it.

### I-07: The selection guarantee does not cover the proposed constraints

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** ARCHITECTURE.md §6; ADR-001; ADR-007

**What it is.** The design claims greedy selection is at least about 63% as good as the best portfolio from its candidate pool. That result applies to a fixed, diminishing-returns objective with a simple entry-count constraint. The paper establishes those conditions, not an unrestricted guarantee for arbitrary exposure constraints. [Hunter, Vielma, and Zaman](https://arxiv.org/html/1604.01455).

The design then adds a [60% player cap across the whole night](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:498), while first calculating each contest's supposedly independent best portfolio. Those best portfolios need not be jointly feasible. If two single-entry contests favor the same player, using him in both creates 100% exposure. Even one single-entry night cannot satisfy a literal 60% maximum.

For a Showdown pool of nine players, six roster slots require average exposure of 66.7%. A universal 60% cap is impossible on that pool. With a larger salary pool but only nine credible rotation players, it pressures the engine toward players with little playing time.

**Why it's worth solving.** **Judgment:** The fallback choice becomes breaking the cap, sacrificing more Goal 1 than the insurance budget allows, or failing to fill entries. The math currently promises all three away. Enumeration also does not make Showdown selection exact after the [screening stage](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:484) discards candidates.

**Recommended solution and why.** Treat exposure limits as explicit, feasibility-tested preferences, with necessary exceptions for small portfolios and concentrated slates. Define the baseline under the actual constraints that will apply to the final portfolio. State whether every guarantee concerns an approximate search result, a restricted candidate pool, or a proven optimum.

Replacement text:

> Report search quality separately from model quality. A greedy guarantee applies only where its assumptions hold. Exposure preferences must be feasible for tonight's entry counts and player pools, and cannot silently invalidate a per-contest tradeoff promise. “Best found” does not mean optimal.

### I-08: The insurance safety margin is not a statistical guarantee

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** ARCHITECTURE.md §§2, 6; ADR-001; ADR-022; spikes/night/night_spike.py

**What it is.** The four simulated datasets are an improvement over evaluating on the construction data. But [the “reporting” set also chooses rollbacks](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:173). Once a dataset changes the chosen portfolio, it is no longer untouched reporting data. Repeated swap and QA searches can also exploit the reused validation set. Two standard errors for one comparison do not establish simultaneous protection over many searched changes and contests.

There is an additional evidence mismatch: the architecture specifies a paired standard error of the change, while the [benchmark implementation](C:/Users/benja/Documents/Claude/nba-dfs/spikes/night/night_spike.py:967) computes a margin from the baseline hit rate's relative error. The paired error depends on how often the old and new portfolios disagree in the same scenarios; it is a different calculation.

**Why it's worth solving.** **Judgment:** The user-facing “give up at most 2%” promise is stronger than the evidence supports. These are small claimed improvements chosen from many alternatives, precisely where selection on noise matters. A successful run of a different margin formula does not validate the specified one.

**Recommended solution and why.** Call the setting a model-based target, not a real-world guarantee. Use one clearly specified paired calculation, predefine the acceptance comparisons, and qualify its behavior under repeated searching. Freeze the portfolio after acceptance, then estimate its outcomes on fresh draws. If reporting causes a rollback, evaluate the resulting portfolio afresh or report both candidates without selecting on those reported numbers.

Replacement text:

> The insurance budget is a constraint on estimated performance under stated models. Validate the actual search and margin implementation, including repeated comparisons. Final reporting uses scenarios that neither selected nor repaired the reported portfolio. Report unresolved uncertainty instead of promising a hard probability guarantee.

### I-09: Single-player replacement plans do not solve joint late news

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§6, 8; ADR-011

**What it is.** The design correctly fixes the old “second file undoes the first change” problem. It does not establish that separate replacement plans remain strategically or financially compatible when combined.

If two questionable teammates both sit, the rotation, ball handling, and Captain choice differ from either one-out case. Separate replacements can compete for the same salary or player slot. Two events in different games can also compete for the same Classic roster flexibility. The [acceptance test](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:936) mainly checks that changes do not revert and ruled-out players disappear. Those are necessary conditions, not evidence that the combined portfolio still has sensible projections.

Phase 1 also limits post-lock reruns to removing players ruled out. If you own none of the scratched player but hold the wrong teammates, that policy misses the actionable news.

**Why it's worth solving.** **Judgment:** The engine can react instantly with a valid but obsolete portfolio. A planned pending upload introduces another hazard: once a lock passes, the platform's actual lineup, not an unconfirmed replacement in the ledger, determines what can still change.

**Recommended solution and why.** Require each replacement plan to identify the complete news state it assumes. Compose only compatible plans; otherwise use a bounded rerun on the combined state. Recompute beneficiaries even when the absent player was not rostered. After a lock, reconcile the actual entry file before relying on any pending player as fixed.

Replacement text:

> Late-news acceptance must cover two same-team absences, conflicting pivots, a status reversal, an unrostered scratch that changes our beneficiaries, and a failed upload crossing a lock. Fast replacements require compatible assumptions; otherwise use the bounded rerun. Measure detection-to-confirmed-upload time, including Ben's work, at 30, 10, and 2 minutes before tip. State when there is insufficient time to act.

### I-10: “Only validity blocks” removes the distinction between usable and merely uploadable

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§1, 8; ADR-019; competitive-edge report Phase 1

**What it is.** A legal lineup can contain a player who will not play. The design's [fallback policy](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-019-delivery-first-only-validity-blocks.md) labels missing injury checks but otherwise ships. The promise “never hands me an invalid file” also exceeds what an offline validator can guarantee after the file is produced. Locks advance, the platform can correct its player pool, and uploads can partially fail. Both attached rules files explicitly allow pool corrections that invalidate existing lineups.

The correct fallback depends on what failed. A failed optional field simulation is different from losing player identity, receiving conflicting status evidence, or discovering that the currently uploaded lineup differs from the local ledger.

**Why it's worth solving.** **Judgment:** A label does not restore an absent player's points or make a stale lock assumption safe. Conversely, blocking delivery over a missing advanced model can leave you worse off. The brief needs a narrow failure policy that distinguishes these cases.

**Recommended solution and why.** Preserve a confirmed incumbent and degrade optional improvements. Treat identity, slot IDs, locks, and authoritative exclusions as hard constraints. Track file validity, news state, model status, and confirmed upload separately. If no credible update is possible, show the emergency choice and its concrete known weakness instead of calling it a normal recommendation.

Replacement text:

> Guarantee that exported bytes pass the validator against their identified input snapshot and lock time. Confirm platform acceptance separately. Optional modeling failures preserve the last usable portfolio; identity or lock uncertainty prevents an unsafe edit. Known-out unlocked players must be removed when a legal repair exists. Missing evidence is visible and never relabeled as verified.

### I-11: The LLM's numerical confidence is being treated as statistical evidence

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§4, 7; R3-nba-modeling.md

**What it is.** The design asks the LLM for minutes and usage percentiles, then [precision-weights its estimate with the model](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:338). A player-outcome interval describes how variable the game could be. It is not automatically the uncertainty in the analyst's estimate of the mean. The LLM and model can also rely on the same news and history, so they are not independent witnesses. Inflating the LLM interval by 1.5 does not establish either assumption.

Checking that quoted words appear on a page proves text provenance, not that the quote concerns tonight's game or supports the proposed adjustment. The [override checks](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:596) explicitly allow records with unknown publication time. A truthful old quote can still produce a harmful current override.

**Why it's worth solving.** **Judgment:** A confidently narrow LLM range can dominate the numerical model without a measured forecasting track record. A “starts tonight” fact can quietly become an unsupported 34-minute projection, then drive a large portfolio.

**Recommended solution and why.** Separate extracted facts from inferred quantities. Let the LLM identify a starter announcement, a restriction, or an absence; use a deterministic, historically evaluated rule to translate that fact into a distribution. Keep speculative numeric overrides in shadow until their own calibration is measured. Preserve source date, event date, exact player identity, and whether the evidence has been superseded.

Replacement text:

> An LLM's stated confidence is not a statistical weight. Facts and numerical inferences are separate records. A verified quote supports only what it actually says; unknown or mismatched event time cannot silently authorize an availability change. Numerical override influence must be earned through prospective calibration and must account for shared evidence with the base model.

### I-12: The learning rules still allow premature victories

**Severity:** Major · **Affects:** Both goals · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §§2, 5, 9, 14; ADR-015; ADR-022

**What it is.** The design correctly says [the night is the unit of evidence](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:822). Other promises undermine that restraint: duplicate adjustment is expected after roughly five files, edge uncertainty may be fitted after two weeks of cash rates, and the volume ramp depends on a two-week rank comparison.

Several contests on one Showdown game reveal one basketball outcome. Thousands of field entries help estimate that game's ownership and duplicate frequency, but do not supply thousands of independent tests of the projection model. Cash rates alone also cannot identify whether the problem is minutes, field strength, construction, or shared model error.

The [spike-as-oracle rule](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-022-spike-as-reference-implementation.md) checks whether a rewrite reproduces its predecessor. It cannot establish that either model is right.

**Why it's worth solving.** **Judgment:** The engine may promote an impressive but unrepeatable result. Sequentially trying challengers against the same “held-out” nights eventually turns those nights into training data. Reconstructing an old slate with later news or season-end rates produces further false confidence.

**Recommended solution and why.** Keep the existing night-level paired evaluation, but attach evidence thresholds to each claim. Use player observations to improve minutes and distributions while reserving contest claims for sufficiently varied independent nights. Preserve every prediction as it existed at the actual decision time. Distinguish a fixed pre-lock replay from a late-swap policy replay, which must reproduce when news became available and whether you could act.

Replacement text:

> Calendar time and file count never certify a model. State the independent nights, news regimes, uncertainty interval, and repeated-testing policy for every promotion. Freeze challengers before their evaluation period. Score actual submitted entries separately from hypothetical alternatives, and replace our historical entries rather than adding free extra entries to the field. Reproducing spike output proves regression consistency only.

### I-13: “A complete free stack works” is not supported by the source evidence

**Severity:** Major · **Affects:** Feasibility · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §10; R4-data-sources.md; competitive-edge report

**What it is.** The [data summary](C:/Users/benja/Documents/Claude/nba-dfs/docs/ARCHITECTURE.md:854) says a complete free stack works from the laptop today. Its own table says The Odds API has not been tested with a key, Daily Fantasy Fuel supplied no usable preseason projections, current NBA status/starting columns remain a bet, and the new injury-report format is unknown.

My web checks found:

- The [2025-26 official injury policy](https://official.nba.com/nba-injury-report-2025-26-season/) is readable and describes reporting deadlines and continuing updates. The requested 2026-27 page was inaccessible through the web tool. That does not prove the new feed is absent; it means current-season operation remains unverified.
- [The Odds API](https://the-odds-api.com/) advertises 500 monthly free credits. Its [documentation](https://the-odds-api.com/liveapi/guides/v4/) charges by markets and regions and reserves historical odds for paid plans. I did not test your credentials or local access.
- [Daily Fantasy Fuel's page](https://www.dailyfantasyfuel.com/nba/projections/) returned a current update stamp and download claims, but the retrieved content did not expose populated player projections. Page availability is not evidence of a usable nightly feed.
- A [March 2026 nba_api issue](https://github.com/swar/nba_api/issues/652) documents timeout reports. That supports outage planning, not a claim that your laptop is currently blocked.

**Why it's worth solving.** **Judgment:** The likely free-data disadvantages are news delay, missing historical decision-time inputs, weak ownership priors, and support burden. Reproducing a paid tool's interface or number of simulations does not close them. The attached competitive report itself disclaims independent profitability evidence; [SaberSim's explanation](https://support.sabersim.com/en/articles/12079141-building-lineups) is a vendor description of its method, not proof that copying it creates an edge.

**Recommended solution and why.** Require an end-to-end rehearsal of the actual source chain and a named fallback for each required input. Preserve distinctions among public accessibility, successful parsing, freshness, and permitted use. Do not turn uncertain source rights into an automatic green status. Collect your own pre-lock snapshots immediately; do not promise free retrospective market validation that has not been sourced.

Replacement text:

> “Verified source” means the chosen local path returned the required current data, parsed correctly, and passed freshness checks. Documentation-only and historical probes remain separate labels. A paid platform technique earns implementation effort only through a specific hypothesis and a measurable improvement over our simpler baseline. Free data availability is an operating constraint, not an assumed solved problem.

### I-14: The advisor instruction has no enforceable nightly budget

**Severity:** Major · **Affects:** Cost · **Confidence:** High · **Applies to:** Brief; ARCHITECTURE.md §7; ADR-013; docs/brief/2026-10-13-architecture-brief.md

**What it is.** “You have a question” sends essentially every judgment call to the advisor. That instruction has no materiality threshold, time allowance, or rule for proceeding when the advisor fails. The supplied architecture budgets researchers and QA but contains no Fable consultation budget or advisor-log workflow. Its saved brief also omits the current prompt's advisor section, so the current brief and design are not aligned.

This is not a claim that the feature is imaginary. [Anthropic's current advisor documentation](https://code.claude.com/docs/en/advisor) describes full-conversation context, model-directed calls, inherited advisor configuration in subagents, and additional usage; on some plans Fable uses usage credits. The documentation says there is no setting that caps or forces advisor calls. [Subagents share usage limits](https://code.claude.com/docs/en/sub-agents), and [usage fields can be absent](https://code.claude.com/docs/en/statusline).

**Why it's worth solving.** **Judgment:** Long research sessions and multiple subagents can multiply expensive consultation. A full-context advisor is also not an independent blinded evaluator. The same process that builds the engine can consume the allowance needed to operate it.

**Recommended solution and why.** Separate development review from nightly execution. Use the advisor for a few consequential design decisions and diagnosis outside the deadline window. Nightly operation should not depend on a response. Measure whole-session usage, including subagents and advisor calls; missing telemetry means unknown usage, not zero.

Replacement text:

> Consult the advisor for consequential unresolved decisions, not every judgment call. Give each consultation a named decision and a time/usage budget. Keep a concise log, but do not treat the advisor as independent empirical validation. Disable optional advisor work when the nightly budget or deadline is threatened, and continue through the deterministic fallback.

## Ideas

Ranked by expected impact. These are changes to the brief's priorities and evidence requirements, not a replacement architecture.

### D-01: Define a narrow, testable source of advantage

**Affects:** Both goals · **Effort:** Low · **Confidence:** Medium

**What it is.** Replace “emulate the secret sauce” with two or three specific hypotheses about where this engine can outperform its own baseline.

**Why it's worth solving.** Rebuilding broad commercial capabilities is expensive, while their actual forecasting quality is largely unobservable. Your potential advantages are narrower: consistent execution, better handling of a particular rotation change, targeted contest selection, and reacting correctly when a free source disagrees with the current build. None is an established edge yet.

**Recommended solution and why.** Require each proposed feature to name the mistake it exploits, the available evidence, and the result that would falsify the hypothesis. Add a pre-entry advisory comparison of contest families using current fees, payout concentration, fill uncertainty, field strength, and operating demands. Keep all entry decisions manual. Compare against equal-spend alternatives rather than assuming that more contests or a smaller field is automatically better.

Suggested addition:

> Every claimed edge needs a prospective test against a simple baseline. Prioritize reliable execution and a small number of measurable NBA-specific improvements before commercial-platform feature replication.

### D-02: Spend research and data quota where a decision can change

**Affects:** Both goals; Cost; Workload · **Effort:** Medium · **Confidence:** High

**What it is.** Prioritize information by its potential to alter tonight's portfolio, rather than researching every uncertain player equally.

**Why it's worth solving.** One uncertain replacement starter can change many entries and several slates. Most other news may change none. The scarce resources are often attention, timely information, and quota, rather than lineup-solving time.

**Recommended solution and why.** Before optional research, compare plausible states of an unresolved fact. If every state produces essentially the same decisions, spend little effort there. If the portfolio changes materially, research that fact first and reserve time to act. Include unrostered players whose availability changes teammates. Treat this as an approximate prioritization tool until probabilities are calibrated.

Suggested addition:

> Rank research tasks by the decisions they could change, affected entries and fees, source reliability, and time remaining to upload. Preserve a late-news reserve for both data requests and LLM usage.

### D-03: Value the ability to change a lineup later

**Affects:** Both goals · **Effort:** High · **Confidence:** Medium

**What it is.** Evaluate a lineup together with the future swaps you can actually execute.

**Why it's worth solving.** A lineup with slightly weaker pre-lock projections can be preferable if it preserves affordable pivots after an important status resolves. Conversely, a simulated “if he sits” optimum is useless if it requires changing an earlier locked player. Merely putting later players in UTIL improves flexibility but does not measure its value.

**Recommended solution and why.** Ask the eventual design to compare a small set of feasible decision paths: no timely news, news before the relevant lock, and news too late to act. Before news arrives, all scenarios with the same known information must share the same decision. This prevents the simulator from using future information. Include whether you are available to upload. After games start, evaluate remaining choices using known scores and uncertainty about unfinished games.

Suggested addition:

> Treat late-swap flexibility as an option with an exercise deadline and operator availability. A claimed gain must come from a sequence of feasible decisions using only information available at each decision time.

### D-04: Audit what Showdown screening throws away

**Affects:** Goal 1 · **Effort:** Medium · **Confidence:** High

**What it is.** Use the small Showdown universe to measure candidate-search loss instead of assuming enumeration solves Captain selection.

**Why it's worth solving.** Listing every legal lineup is only the beginning. A shortlist based on mean plus a few standard deviations can eliminate a lineup whose useful tail is driven by a particular rotation state, a less common Captain, or a different duplicate pattern. A 99th-percentile player score is not the probability that his lineup reaches a top-1% contest rank.

**Recommended solution and why.** Compare the shortlist with broader evaluations on saved small slates and preserve candidates across Captain choices and materially different game states. Measure how often an independently evaluated strong candidate was discarded, without promoting hindsight winners into the current model. Keep one shared stat outcome for each person across Classic, UTIL, and Captain. Require exact scoring precision sufficient for Captain eighth-points; the current “quarter-point-exact” wording in [ADR-020](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-020-scoring-adapter.md) is inconsistent with its own 85.875 example.

Suggested addition:

> Showdown acceptance includes a candidate-coverage audit and exact tie-aware scoring. Full enumeration does not justify an optimality claim after screening.

### D-05: Learn from joint failures before waiting for washouts

**Affects:** Goal 2 · **Effort:** Medium · **Confidence:** High

**What it is.** Measure shared forecast mistakes and near-washout outcomes as diagnostics, while keeping literal washout as the goal.

**Why it's worth solving.** Rare washouts are a weak early calibration signal. You can learn sooner whether teammates' minutes miss together, whether several contests rely on the same mistaken role assumption, and whether the model understates how many entries fail on a bad night. Good player-level average error can coexist with badly wrong portfolio risk.

**Recommended solution and why.** Track errors by game and news event, the fraction of entries cashing, best-entry distance from the actual cash line, and returns across the night. Compare their distributions with what was predicted before lock, with uncertainty grouped by night. Attribute failure to a common assumption, not merely to a list of disappointing players. These diagnostics can reject a bad model; they do not certify a tiny washout probability.

Suggested addition:

> Validate dependence and shared downside explicitly. Correct average player projections and ownership totals are insufficient evidence that portfolio washout risk is modeled correctly.

### D-06: Make the model survive deliberate attempts to fool it

**Affects:** Both goals · **Effort:** Medium · **Confidence:** High

**What it is.** Add a small set of deliberately unfavorable, fully understood contest examples before adding more realism.

**Why it's worth solving.** Ordinary synthetic nights show that the machinery runs. Adversarial examples show whether it invents an advantage from assumptions or bookkeeping.

**Recommended solution and why.** Require examples with:

- Exchangeable entrants, where our entries have no information or construction advantage.
- Stronger opponents and a shared error that makes our preferred players worse than forecast.
- The same lineup and opponents repeated across contests, so multiplying independent cash chances gives the wrong answer.
- Different lineups tied at a payout boundary, including more tied entries than paid positions.
- Two same-team scratches and one failed upload spanning a lock.
- A concentrated Showdown pool where the proposed exposure cap is infeasible.

Check arithmetic independently of the production spike. Use tiny examples where every possible outcome can be counted, so disagreements have definite answers. This is a higher-value use of adversarial QA than searching for fresh back-to-back narratives every night.

### D-07: Put a stopping rule on architecture research itself

**Affects:** Feasibility; Cost; Workload · **Effort:** Low · **Confidence:** High

**What it is.** Make research stop when it no longer changes a consequential decision.

**Why it's worth solving.** The brief requests expanded vendor research, newer papers, several tool ecosystems, live source probes, five repository histories, multiple reviews, and repeated advisor consultation within the same week needed to build and rehearse. The supplied design already has 25 components and 22 decision records. More memos can consume the allowance without reducing opening-night risk.

**Recommended solution and why.** Allow an early, brief inventory of proven file-format failures and operational incidents from prior engines, while postponing their architecture and implementation choices. Greenfield should prevent inherited design assumptions, not require rediscovering known upload mistakes. Give each research track a decision to resolve and a time cap. Retain existing vendor summaries unless a specific unresolved choice needs more evidence.

Suggested addition:

> Research ends when it resolves the named decision or reaches its time budget. Established operational failure facts may be consulted before the first-principles sketch; existing architectures do not constrain that sketch. Before opening night, prioritize the next real rehearsal over additional architecture documentation.

## What holds up

- Deterministic code should own scoring, lineup construction, validation, and export; LLMs should supply bounded, inspectable evidence.
- Classic and Showdown must share each person's actual simulated outcome across the whole night.
- Preserve immutable inputs, decision-time snapshots, overrides, and pre-QA baselines so improvements can be measured.
- Keep DraftKings entry and upload actions manual, with an explicit confirmation of what the platform accepted.
- Keep night-level paired comparisons, chronological evaluation, shadow challengers, and Ben's approval for model adoption.
