# NBA DFS Engine: Round 2 Review (Codex)

**Date:** October 14, 2026. **Reviewed revision:** `25982950de0cb32ce4254076128d021cff2ef8a8`, branch `master`. A live `git ls-remote` check returned the same revision as the clean local checkout.

**Review basis:** README, CLAUDE.md, the living brief, the complete adjudication register, architecture v4, the active decision records and supersession notices, BUILD_PLAN, CONTRACTS, PROGRESS, all 22 chunk files, the command file, advisor log, mock brief, reference materials, and the research/spike evidence relevant to the findings. The four reference files match the four originals reviewed in round 1 byte for byte. Historical research was checked for prior coverage and for its October 14 corrections; its old conclusions are not treated as new evidence. No engine code was built and no DraftKings account action was taken.

**Evidence key:** “Fact” identifies repository text or a check performed during this review. “Judgment” identifies the consequence or recommendation. Confidence concerns the finding, not a claim of future profitability. Numerical counterexamples are deliberately small hypothetical contests. The current-season injury feed, future owner exports, and actual platform acceptance were not verified here; no finding depends on pretending they were.

## Verdict

**No-go for C01 as written.** The Floor-only fallback cannot pass the build protocol's dependency checks, and C01 would freeze interfaces that miscompute the revised money objectives. The advertised emergency repair is also blocked by the shared eight-minute export rule. The most likely operational failure is a slipped model build followed by a fallback session that stops on C09's unmet dependency. Fix the four stop-line items, then build the rehearsed Floor while the remaining dated fixes land in their owning chunks.

## Stop the line

- **R2-I-01: The Floor-only build route cannot run**
- **R2-I-02: Goal 2 thresholds expected winnings instead of possible winnings**
- **R2-I-03: Tied prizes are divided twice**
- **R2-I-05: The field interface discards the information settlement needs**

## What I understood

- Goal 1 maximizes each contest's expected dollars from top-1% places after ties, divided by that contest's top-1% prize pool; all our entries count.
- Goal 2 minimizes the chance that total nightly winnings fall below 25% of total nightly entry fees.
- The insurance control may sacrifice a bounded amount of each contest's estimated Goal 1 to improve Goal 2; it ships after opening night.
- Floor generates and validates simple projection-based lineups, with honest labels and an early confirmed upload.
- Baseline adds simulation, opponents, settlement, selection, news reruns, and open-slot swaps; its upload mechanics share the Floor's path.
- Optimizer adds insurance, results, learning, watcher, uncertainty experiments, and QA after opening night.
- The owner supplies DraftKings files and performs uploads; news can be entered manually with `out`, `in`, and `start`.
- C01 defines contracts; C02–C04 produce the Floor; C05–C09 the Baseline model; C10–C11 complete its operating workflow.
- October 15 and 16 are the accepted live rehearsal windows; saved-night drills follow, then the October 19 build and October 20 game-day refresh.
- The accepted data posture and round-one decisions stand; this review tests their execution and the new chunk interfaces.

## Top five

1. **R2-I-01: The Floor-only build route cannot run**
2. **R2-I-02: Goal 2 thresholds expected winnings instead of possible winnings**
3. **R2-I-03: Tied prizes are divided twice**
4. **R2-I-04: The emergency repair disappears inside eight minutes**
5. **R2-I-05: The field interface discards the information settlement needs**

## New issues

### R2-I-01: The Floor-only build route cannot run

**Severity:** Blocker · **Affects:** Opening night · **Lands by:** Before C01 · **Confidence:** High · **Applies to:** BUILD_PLAN “Build usage budget”; C10/C11 dependencies; CLAUDE.md build protocol; run-chunk command

**Nearest decided item:** ADJUDICATION 36, X-05, with entries 3 and 38. The Floor-only fallback is accepted; the new dependency graph makes that accepted fallback impossible to execute.

**What it is.** **Fact:** [BUILD_PLAN](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/BUILD_PLAN.md:124) says that after the usage trigger, C05–C09 move after opening night and C10/C11 are built “in Floor mode only.” But C10 requires C09; C11 requires C09 and C10. CLAUDE.md and [run-chunk](C:/Users/benja/Documents/Claude/nba-dfs/.claude/commands/run-chunk.md) require those dependencies to be done and instruct the session to stop otherwise. Neither chunk specifies an alternate Floor scope and alternate consumed contracts.

The calendar-slip branch has the same gap: “skip C10's open-slot swap” does not explain which remaining C10/C11 checkpoints can run without the Baseline objects.

**Why it's worth solving.** **Judgment:** this failure occurs when the project already has the least time or usage left. A fresh session must either obey the protocol and stop, or invent a new plan. The fallback then depends on precisely the improvisation the chunk plan was intended to remove.

**Recommended solution and why.** Give C10 and C11 explicit mode-specific scopes, dependencies, acceptance tests, and tracker states. Floor-mode completion must not mean that their Baseline functionality is done.

Exact edit:

> C10-F depends on C04 and provides the Floor news-command wiring, legal-repair routing, and Floor-mode swap behavior. C11-F depends on C10-F and provides the no-Claude launcher, essential guards, capability reporting, and Floor opening-night drill. C10-B and C11-B retain the current Baseline dependencies and remain pending until built. The tracker and /run-chunk resolve dependencies by mode.

An even smaller implementation is to finish all required Floor operations in C04 and give C11's independent launcher/guard work its own dependency path. Either way, verify the route by setting C05–C09 to deferred and walking the actual session protocol before C01 starts.

### R2-I-02: Goal 2 thresholds expected winnings instead of possible winnings

**Severity:** Blocker · **Affects:** Goal 2 · **Lands by:** Before C01 · **Confidence:** High · **Applies to:** CONTRACTS §9; C08 settlement/night; C12 insurance; ADR-025

**Nearest decided item:** ADJUDICATION 9, B-I-02. The severe-drawdown goal stands; the new Settlement interface loses the payout randomness required to calculate that goal.

**What it is.** **Fact:** [CONTRACTS](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:199) defines prize_all as the **expected** prize for an entry in each basketball scenario. C08 integrates over uncertain opponent ranks and copies. night_goal2 then receives those expected prizes, without their payout distributions, and computes the chance total winnings fall below the threshold.

These operations do not commute. In a fixed basketball scenario, suppose our entry wins $100 with probability 10% and $0 otherwise. Fees are $10, so the drawdown threshold is $2.50. Expected winnings are $10: thresholding that expectation reports no drawdown. The correct drawdown probability is 90%.

**Why it's worth solving.** **Judgment:** Goal 1 can use expected dollars. Goal 2 needs the distribution of dollars. Replacing that distribution with its mean can erase the risk the new goal was introduced to measure, even with perfect player projections.

**Recommended solution and why.** Separate expected-prize outputs from jointly realized payout samples. For each basketball scenario, either draw complete opponent fields and settle all our entries together, or integrate the conditional distribution of total winnings. Preserve dependence among our entries in the same contest; drawing each entry's rank independently is not a joint settlement.

Exact contract addition:

> Settlement exposes expected_prize_* for Goal 1 and a separate joint payout-outcome representation for Goal 2. Each payout sample identifies its basketball scenario and opponent-field realization. night_goal2 applies the fee threshold to total realized winnings in each joint outcome, then averages the indicators. It never applies the threshold to conditional expected prizes.

Put the 10%/$100 example, plus two correlated entries, in C01's hand-counted fixtures and C08's acceptance tests.

### R2-I-03: Tied prizes are divided twice

**Severity:** Blocker · **Affects:** Both goals · **Lands by:** Before C01 · **Confidence:** High · **Applies to:** CONTRACTS §9; C08; ARCHITECTURE §2; ADR-024

**Nearest decided item:** ADJUDICATION 5, A-I-05/B-I-01/B-I-07. Rank-aware dollar settlement and the goal change stand; a new arithmetic check shows that the formula carrying them out is wrong.

**What it is.** **Fact:** [C08](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/chunks/C08-field-model-and-settlement.md:24) explicitly requires `mean(W(r..r+D)) / (1+D)`. Taking the mean already divides by the number of tied entries.

For two entries tied across prizes of $100 and $60, the correct payment is ($100 + $60)/2 = $80 each. The specified formula pays $40 each. For five tied entries it reduces the correct payment by another factor of five. I ran these arithmetic checks locally; they reproduce the extra division.

There is a related boundary defect to resolve in the same fixture: Goal 1 is money **from top-1% places**, while Goal 2 uses all paid places. When a tie crosses the top-1% cutoff, crediting the entire settled prize whenever the tie starts above the cutoff imports lower-place money into Goal 1.

**Why it's worth solving.** **Judgment:** this is an unintended extra penalty on popular Showdown lineups, not the duplication policy the owner chose. It biases selection and the drawdown estimate in the same direction.

**Recommended solution and why.** Replace every current formula, including the ADR and the hand-computed fixture instructions, with:

> For a tie group occupying ranks r through r+t-1, each entry receives sum(W(j) over those ranks)/t. t includes opponent copies, different lineups with equal scores, and our own tied entries. For Goal 1, use the same calculation with W_top1(j) = W(j) for j <= k and zero otherwise. For total winnings, use the full W.

For the $100/$60 two-way tie with k = 1, the outputs are $80 total winnings and $50 attributable to the top-1% pool per entry. Check conservation: the sum of all entrants' full payouts equals the paid pool, and the sum of their top-1% allocations equals the top-1% pool. [DraftKings' tie explanation](https://support.draftkings.com/dk/en-us/what-happens-when-i-tie-with-others-in-a-fantasy-sports-contest?id=kb_article_view&sysparm_article=KB0010633) confirms pooling tied positions and dividing once.

### R2-I-04: The emergency repair disappears inside eight minutes

**Severity:** Blocker · **Affects:** Opening night · **Lands by:** Before C03 · **Confidence:** High · **Applies to:** CONTRACTS §11.7; C03 insufficient-time test; C10 drill; ARCHITECTURE §8

**Nearest decided item:** ADJUDICATION 10, A-I-09/B-I-04, with entry 11. The legal-repair fallback stands; the new common export rule prevents it from doing the job assigned to it.

**What it is.** **Fact:** [CONTRACTS §11.7](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:273) tells the exporter to drop any changed row whose game locks within eight minutes. C03 requires a test proving a five-minute change is dropped. Meanwhile the runbook and C10 name repair as the fallback when the re-solve is too slow or news arrives two minutes before tip. Repair uses the same exporter.

Thus the fast repair can finish in one second and still produce no usable changed row. C10's timing drill also assumes a three-minute upload, so the T-2 drill cannot possibly complete that assumed upload, regardless of compute speed.

**Why it's worth solving.** **Judgment:** the operator receives a recovery command that cannot recover the affected entries. Replacing a stale file with an empty or partial update would be especially misleading.

**Recommended solution and why.** Separate the time needed to **start a full re-solve** from the hard prohibition on editing a locked slot. Give repair its own small, explicit upload allowance based on the rehearsal. If that allowance cannot fit, state that no correction was exported and name the still-uploaded incumbent.

Exact edit:

> resolve.min_minutes_to_lock decides whether to attempt the full model path. Repair is allowed while every changed slot remains unlocked and its measured repair-plus-upload allowance fits. The exporter enforces actual locks and valid_until for every path; it does not apply the full-rebuild eight-minute guard to repair. Dropped rows are listed explicitly and never reported as repaired.

Replace the five-minute “must drop” test with separate tests for the full path, a feasible quick repair, and an actually insufficient upload window.

### R2-I-05: The field interface discards the information settlement needs

**Severity:** Major · **Affects:** Both goals · **Lands by:** Before C01 · **Confidence:** High · **Applies to:** CONTRACTS §§8–10; C08 field/scores and Risks; C09 settlement_fn

**Nearest decided item:** ADJUDICATION 5 and 23. Exact equal-score settlement and eighth-point Captain precision stand; the newly specified compressed field representation cannot preserve them.

**What it is.** **Fact:** [FieldScores](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:184) stores only 400 evenly spaced quantiles and obtains the score distribution by interpolation. This does not retain the exact probability mass at a tied score. It also gives only about four grid intervals across the entire top 1%, while Goal 1 now heavily rewards first place. In a 35,000-entry field, the one-opponent tail probability relevant to first place is about 0.000029; grid spacing is about 0.0025.

[C08's memory advice](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/chunks/C08-field-model-and-settlement.md:61) then changes those grids to float16 despite the contract saying float32. A local NumPy check gives:

> float16(300.375) = 300.5; float16(300.5) = 300.5.

Two different legitimate Showdown totals become the same score. Finally, settlement_fn accepts only score arrays even though duplicate rates are keyed by lineup identity. Two different lineups can have the same score array and different copy rates.

**Why it's worth solving.** **Judgment:** the settlement cannot reconstruct discarded ties, tail detail, or lineup identity. A mode called “exact” will not make that information reappear.

**Recommended solution and why.** Amend the contract before C01 types it. Use exact score masses or sorted weighted scores for tie settlement, with lossless eighth-point score storage. A coarse quantile summary can remain a display or screening artifact. If an approximate tail representation is used, define and test its error against the dollar objective.

Exact edit:

> Settlement consumes candidate identities alongside scores, and a field representation exposing P(score > x), P(score = x), and joint field realizations. Stored scores preserve eighth-points exactly. Coarse or float16 quantile grids cannot be the authoritative input for equal-score settlement. “Exact” refers to settlement on the represented field, not to a compressed interpolation.

Test two candidates with identical scores but different lineup hashes, and two scores separated by 0.125 near 300 points.

### R2-I-06: A starter announcement can erase a minutes restriction

**Severity:** Major · **Affects:** Both goals · **Lands by:** Before C06 · **Confidence:** High · **Applies to:** CONTRACTS §4.2; C04 manual facts; C06 projections/facts; C17 report diffs

**Nearest decided item:** ADJUDICATION 12, A-I-11. Newer evidence must supersede obsolete evidence; the implementation expands that rule to unrelated attributes.

**What it is.** **Fact:** [CONTRACTS §4.2](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:122) says a later fact for a player supersedes an earlier fact “of any kind.” A player can simultaneously be available, starting, and limited to 24 minutes. If the restriction is recorded first and the starter announcement second, the rule discards the restriction. An availability update can similarly erase a role or restriction fact that it never addressed.

The same contract also allows any acting source to set OUT, while the architecture gives official OUT precedence. A generic latest-record rule is not a resolution policy for those conflicts.

**Why it's worth solving.** **Judgment:** one harmless update can raise minutes across every lineup, or remove an authoritative exclusion. This defeats the purpose of structured facts without requiring a hallucination.

**Recommended solution and why.** Supersede within an attribute and game, preserving independent facts. Define separate availability, starting-role, and restriction state, each with provenance. A new starter fact should not clear a cap; a new availability fact should not change whether the player starts.

Exact edit:

> Supersession is keyed by (person_key, game_id, attribute), not by person alone. Independent active attributes coexist. Removing a minutes restriction requires an explicit restriction-cleared fact. Conflicts use the documented source-precedence rule and remain visible. An IN update supersedes the relevant availability fact only.

Add a restriction-then-starter test, the reverse order, and an unrelated status update; all must retain the restriction.

### R2-I-07: The parser contract describes a different CSV layout

**Severity:** Major · **Affects:** Opening night · **Lands by:** Before C02 · **Confidence:** High · **Applies to:** CONTRACTS §§2.1/3.1; C02 ingest/entries and ingest/slates

**Nearest decided item:** ADJUDICATION 37, X-06, with entry 19. Real-file testing and optional salaries stand; the new parser instructions contradict the repository's already captured file-layout evidence.

**What it is.** **Fact:** [CONTRACTS §2.1](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:45) and C02 say the player pool comes after a blank line. [R6 §2.3](C:/Users/benja/Documents/Claude/nba-dfs/docs/research/R6-draftkings-mechanics.md:130) says entry rows continue down the left while the pool occupies columns on the right, requiring separation by column position. A long entries list therefore overlaps the pool vertically.

The schema also requires draft_group_id, although R6 explicitly says that ID is absent from the entries file. For post-lock imports, R6 records Game Info variants such as “In Progress” and “Final”; CONTRACTS requires the timestamp-shaped string. The current 2026-27 NBA variant still needs the agreed real-file check.

**Why it's worth solving.** **Judgment:** a fresh C02 session is told to implement two incompatible parsers and populate a missing identifier. A parser that works only on a few test rows can fail when the owner increases entry count or re-downloads after lock.

**Recommended solution and why.** Make R6's two-table layout explicit in the contract. Detect each table's header, read the entry and pool column regions independently, and preserve every entry even where it shares a physical row with pool data.

Exact edit:

> Parse DKEntries as independent entry and player-pool column regions. Do not assume a blank physical row separates them. draft_group_id is optional unless supplied by verified metadata; an internal slate key binds date, format, games, and the pool's role IDs without inventing a DraftKings identifier. A post-lock Game Info marker reuses the last verified schedule for that exact game; an unresolved lock time prevents an edit.

Add a many-entry fixture that overlaps the pool, plus a re-download containing locked markers. Keep the original raw file as the evidence for which NBA format actually occurred.

### R2-I-08: C04 requires features its source and prior chunks do not provide

**Severity:** Major · **Affects:** Build · **Lands by:** Before C04 · **Confidence:** High · **Applies to:** C04 projections/simple; C05 scoring; CONTRACTS §§5–6

**Nearest decided item:** ADJUDICATION 38, X-07, with entry 3. The simple, local Floor is accepted; its new implementation instructions depend on unavailable columns and a later chunk.

**What it is.** **Fact:** [C04](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/chunks/C04-contest-facts-injury-report-floor.md:27) asks for historical DraftKings points per minute and a points-on-salary regression “from the same file.” I read the schema of the actual sportsdataverse parquet in the local spike downloads: 34,883 rows, ordinary basketball stats including points and minutes, but no salary or dk_points column. The reusable DraftKings scoring function is first built in C05, after C04's live rehearsal.

Basketball “points” are not DraftKings fantasy points. The input is sufficient to calculate fantasy points, but the transformation and its owner have not been placed before the Floor needs them.

**Why it's worth solving.** **Judgment:** C04 is already the critical rehearsal-day chunk. It must now invent a scoring implementation, choose an unsupported regression input, or silently substitute the wrong units. The latter can produce legal but badly ranked lineups.

**Recommended solution and why.** Pull the small pure scoring adapter and its discriminating tests forward into C04, with C05 explicitly consuming that function rather than rebuilding it. Specify the source of salary-implied fallback pairs.

Exact edit:

> C04 derives historical dk_points from the parquet's counting stats using the shared scoring adapter. Historical salary is not present. If fitting the fallback, pair current pool salary with the explicitly defined historical fantasy-point target for matched players, and label that cross-sectional rule as a fallback. Otherwise use a documented fixed salary-implied rule. C05 reuses the scorer and adds full history/rates functionality.

Add a schema check against the actual raw parquet and a test where rebounds and assists make the fantasy-point ordering differ from ordinary scoring points.

### R2-I-09: Saved-night drills can overwrite the evidence they rehearse

**Severity:** Major · **Affects:** Build · **Lands by:** Before C03 · **Confidence:** High · **Applies to:** CONTRACTS §1.1/§11; C03 Paths; C11 readiness drills; C19 replay

**Nearest decided item:** ADJUDICATION 32, X-01, and advisor consultation 2's saved-night addition. Rehearsing saved files with a frozen clock stands; the new mode changes input date and clock without separating mutable outputs.

**What it is.** **Fact:** [saved-night mode](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/CONTRACTS.md:39) points at that night's ledger and news state. It does not define an isolated ledger, upload directory, run namespace, or confirmation channel for drills. C11 explicitly rehearses `dfs uploaded` after a dry upload. C03's exporter increments versions, moves older files to stale, and changes pending state.

Following those rules against the actual October 16 night can replace its real confirmation history with fictional drill actions. C19's replay uses the same deterministic steps without an explicit read-only output policy.

**Why it's worth solving.** **Judgment:** the tests can corrupt the historical evidence needed by the learning and delivery-failure gates. A copied file is not enough protection when the mutable ledger still points to the real night.

**Recommended solution and why.** Give drills and replays an explicit execution mode with isolated writes and distinct confirmation semantics.

Exact edit:

> Live, drill, and replay have separate writable roots. A drill reads immutable archived inputs into a fresh drill_id namespace for its news state, ledgers, manifests, and upload-shaped files. Simulated confirmations never update live committed state. Replay writes only to a scratch comparison directory. Frozen time does not select a live ledger for mutation.

Make C03 test that a completed drill, including simulated uploads and failures, leaves every original run artifact and live ledger byte-identical.

### R2-I-10: Active ADR bodies still instruct the reversed behavior

**Severity:** Major · **Affects:** Build · **Lands by:** Before C08 · **Confidence:** High · **Applies to:** ADR-007 Decision; ADR-008 Decision; C08/C09 reading lists

**Nearest decided item:** ADJUDICATION 5 and 14. Both decisions stand; their changelog notes were updated while active decision bullets still say the opposite.

**What it is.** **Fact:** [ADR-007's current Decision](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-007-greedy-coverage-selection.md) says “Each scenario's value is the best of our entries,” despite Goal 1 now summing all our top-1% winnings. [ADR-008's current Decision](C:/Users/benja/Documents/Claude/nba-dfs/docs/adr/ADR-008-field-model-from-a-public-view.md) still permits the public view to use our baseline when consensus is absent. Its new changelog forbids that.

These are active, accepted records in the fresh sessions' mandatory reading lists, not merely superseded ADRs retained for history.

**Why it's worth solving.** **Judgment:** a session can implement the old objective or leak private projections into the field while claiming to follow an accepted decision. Resolving contradictory prose also spends context and advisor usage on already settled matters.

**Recommended solution and why.** Rewrite the active Decision sections to match ADR-024 and the deterministic public formula. Keep old wording in a clearly labeled historical section that is excluded from implementation reading lists.

Exact edit:

> ADR-007: the per-scenario value is the sum of our entries' top-1% prize allocations under the current settlement; no max-over-entries utility is used.
>
> ADR-008: when consensus is absent, use the named public formula; the engine's private baseline is never a fallback. The baseline-change isolation test applies whether or not consensus exists.

Run a narrow consistency check on active decision bullets, chunk instructions, and contracts before their consumer chunks start. Do not ask the next builder to decide which paragraph wins.

### R2-I-11: C14 invents a paid-place cutoff from a file without payouts

**Severity:** Major · **Affects:** Both goals · **Lands by:** Before C14 · **Confidence:** High · **Applies to:** C14 facts/cache; CONTRACTS §2.5; R6 §2.4

**Nearest decided item:** ADJUDICATION 1, A-I-01/X-05. Estimated contest facts and their labels remain allowed; the new cache writer claims an exact paid rank from an input that does not supply one.

**What it is.** **Fact:** [C14](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/chunks/C14-contest-facts-v2-calibration-gates.md:22) says standings supply “places paid from the last paid rank.” The listed standings columns contain rank, score, lineup, ownership, and player points. They contain no winnings, paid flag, or payout ladder. R6 distinguishes that file from the entry-history export and pasted payout table.

The last listed rank is the last entrant, not the last paid entrant.

**Why it's worth solving.** **Judgment:** a cache writer can convert missing payout evidence into a supposedly evidence-backed template. Those wrong facts then persist across nights and steer both dollar objectives.

**Recommended solution and why.** Limit each source to the fields it actually proves.

Exact edit:

> Standings may establish the completed field size and lineup/score facts. They cannot establish places_paid or prizes unless the specific file contains an explicit verified payout field. Obtain those from the entry-history export or a payout paste; otherwise retain the existing template/default and its provenance. Do not derive paid status from rank.

Test that a full standings file with no winnings fields cannot change places_paid in the cache, including when the prior cutoff is unknown.

### R2-I-12: Live-score conditioning loses the stats needed for bonuses

**Severity:** Major · **Affects:** Goal 1 · **Lands by:** Before C22 · **Confidence:** High · **Applies to:** C22 LiveState and simulate_game_partial; CONTRACTS §7 extension

**Nearest decided item:** ADJUDICATION 17 and 28. Live-score conditioning remains scheduled after the MVP, and opponent locked-field conditioning stays in backlog; this concerns the newly specified partial-game scorer.

**What it is.** **Fact:** C22's partial-game input contains fantasy points so far and a fraction of game time remaining. It then adds a newly simulated remainder to those points. That input cannot determine milestone bonuses.

A player with ten points and nine rebounds who gets one more rebound earns the double-double bonus. Simulating one rebound in isolation cannot detect that crossing. If the bonus was already earned, independently scoring the remaining stat line can award it a second time. Total fantasy points do not uniquely identify the underlying points, rebounds, assists, steals, and blocks.

**Why it's worth solving.** **Judgment:** the error is multiplied at Captain and changes the distribution used to decide open-slot swaps. It affects exactly the near-threshold stars for whom this scoring detail matters.

**Recommended solution and why.** Require cumulative box-score categories and compute the final score once.

Exact edit:

> For in-progress games, LiveState carries the cumulative scoring stat line and minutes played per player. Simulate remaining stats conditional on that state, add them to cumulative stats, and apply the scoring adapter once to the completed line. Do not add two independently bonus-scored fantasy totals. If only current fantasy points are available, the partial-game bonus path is unavailable and the brief labels the fallback.

Test a double-double crossed during the remainder, one already earned before the snapshot, and a triple-double transition; include Captain in every case. Finished-game conditioning can ship independently when exact final fantasy points are available.

## New ideas

### R2-D-01: Keep the person stable when the team changes

**Affects:** Both goals · **Lands by:** Before C02 · **Effort:** Medium · **Confidence:** High · **Applies to:** C02 identity; CONTRACTS player keys; C05 historical joins

**Nearest decided item:** ADJUDICATION 11, A-I-10, with entry 14. Identity certainty and the approved history sources stand; neither ruling decides how permanent athlete identity survives a team change.

**What it is.** **Fact:** [C02](C:/Users/benja/Documents/Claude/nba-dfs/docs/build/chunks/C02-draftkings-ingest.md:23) makes person_key a normalized name plus team. The inspected historical parquet already has athlete_id. **Proposal:** separate permanent athlete identity from the team he represents in a particular game.

**Why it's worth solving.** A player traded in the offseason otherwise looks like a new person when current salaries are joined to old-team history. Name normalization also cannot safely resolve two people whose normalized names collide. Opening week is the worst time to throw away the usable history of established players.

**Recommended solution and why.** Give each person a stable internal key and maintain explicit aliases for source IDs, names, and their effective dates. Store team on the game appearance, not in the permanent key. DraftKings role IDs remain specific to a slate; Captain and UTIL map to the same person.

Add fixtures for one traded player, a suffix/accent variant, and two distinct players with similar names. An uncertain match must be exposed for review rather than silently treated as either a rookie or a confirmed match. This changes a join contract before it spreads through projections, facts, hashes, and results.

### R2-D-02: Repair the open positions before declaring a player irreplaceable

**Affects:** Both goals · **Lands by:** Before C03 · **Effort:** Low · **Confidence:** High · **Applies to:** C03 legal repair; CONTRACTS §11.6

**Nearest decided item:** ADJUDICATION 11, A-I-10, with entry 10. Cheap legal repair remains the fallback; this adds a bounded way to find a legal replacement without invoking the full model or precomputed plans.

**What it is.** The repair currently searches for a substitute eligible for the vacated slot. Sometimes a valid substitution exists only after moving an existing unlocked player to that slot.

For example, an OUT player occupies SG, an existing SG-eligible player occupies G, and the available replacement is PG-eligible. The replacement cannot enter SG directly. Moving the existing player from G to SG and placing the replacement at G repairs the lineup, with the other six players unchanged.

**Why it's worth solving.** This converts some otherwise stranded entries into legal entries during the exact emergency when the full re-solve is unavailable. It also avoids forcing an inferior direct substitute when another roster position can accommodate the better available repair.

**Recommended solution and why.** After choosing replacement players, run a tiny player-to-open-slot matching step: assign the existing unlocked players and replacements to eligible unlocked positions. Keep locked cells fixed, enforce salary and duplicate-player rules, and try replacements in the accepted cheap-repair order. This is position assignment within one entry, not the rejected contest-entry assignment optimizer.

Add the SG/G example as a hand-counted test and include it in the existing 150-entry, ten-second repair benchmark. If this small matching step cannot finish within that budget, retain the current direct-slot path.

### R2-D-03: Make rehearsal approval identify the version that passed

**Affects:** Opening night · **Lands by:** Before C11 · **Effort:** Low · **Confidence:** High · **Applies to:** CONTRACTS capabilities; C11 readiness; ADR-023

**Nearest decided item:** ADJUDICATION 3, A-I-03/B-I-03, with entry 32. Rehearsing after substantive changes is already required; a bare date cannot enforce that requirement in the new capability mechanism.

**What it is.** **Fact:** capabilities currently store enabled and rehearsed_on. **Proposal:** also store the tested code/configuration fingerprint and the drill's result artifact.

**Why it's worth solving.** A parser or scorer can change on Monday while the flag still says it was rehearsed on Friday. The guard then admits a version that never passed the rehearsal, despite the accepted rule.

**Recommended solution and why.** Record which version of the capability, its relevant dependencies, runtime lockfile, and method settings passed the drill. A relevant change makes that capability's evidence stale and requires a replay drill; an unrelated document edit does not. Normal new nightly inputs and news do not invalidate the implementation's rehearsal.

Show “passed for this version,” “stale after change,” or “never rehearsed” in status. Keep the independent Floor available when a later capability needs another drill. This makes the existing gate automatic instead of relying on memory.

### R2-D-04: Publish each upload and its ledger record as one recoverable generation

**Affects:** Opening night · **Lands by:** Before C03 · **Effort:** Medium · **Confidence:** High · **Applies to:** C03 exporter/ledger/manifest; CONTRACTS §§11–12

**Nearest decided item:** ADJUDICATION 11 and 19. The separation of pending files from confirmed uploads stands; neither ruling specifies what happens if the process stops between writing the file and recording its state.

**What it is.** **Fact:** C03 writes the CSV, validates it, hashes it, updates two records, and moves older files. Its single-run lock prevents overlapping writers but does not make that sequence indivisible. **Proposal:** publish a complete immutable generation with a recoverable commit record.

**Why it's worth solving.** A laptop restart or interrupted session can leave a visible file with no matching ledger entry, or a ledger naming a file that was never finished. That costs time at lock and makes the “latest file” instruction unreliable.

**Recommended solution and why.** Write the file and metadata into a temporary generation, re-read and validate them, then publish a small committed-generation marker. Only committed generations can appear as actionable files in status. On restart, finish or discard incomplete generations deterministically. Preserve the last confirmed incumbent through the entire operation; exporting a new file never confirms an upload.

Add interrupted-write tests at the file, validation, manifest, ledger, and publication boundaries. These test recoverability of one export, not a new database system.

### R2-D-05: Spend simulation work where the dollar objective is noisy

**Affects:** Both goals · **Lands by:** After opening night · **Effort:** High · **Confidence:** Medium · **Applies to:** C16 uncertainty; scenario/settlement contracts; runtime benchmarks

**Nearest decided item:** ADJUDICATION 8, A-I-08/B-I-02, with entry 2. The paired margin, independent scenario sets, and honest uncertainty labels remain; this proposes a different sampling method to reduce numerical noise within the same model.

**What it is.** Ordinary random simulation spends many samples on common outcomes that pay nothing toward Goal 1. Test stratified sampling, which deliberately covers defined ranges of game and role outcomes, or importance sampling, which oversamples rare outcomes and weights them back to their actual modeled probability. These are established numerical methods; [He and Owen's importance-sampling research](https://arxiv.org/abs/1411.3954) supports the efficiency mechanism, not its benefit for this DFS model.

**Why it's worth solving.** A first-place-heavy dollar objective can depend on a handful of simulated hits. More indiscriminate scenarios can use the entire late-news runtime budget while barely stabilizing a comparison. Better sampling can improve the precision per second of both the upside estimate and the downside estimate.

**Recommended solution and why.** Start as a frozen challenger after the ordinary simulator and settlement pass their exact tiny examples. Keep the independent selection, screening, validation, and reporting sets. Carry explicit sample weights through both goals and all uncertainty calculations; do not treat deliberately oversampled ceiling cases as ordinary equally likely nights.

Accept the method only if it reproduces known expectations on countable fixtures and reduces the paired error of portfolio differences per second on unseen saved slates. It reduces simulation noise, not uncertainty about whether the player and opponent models are right.

## What holds up

- The revised goals distinguish top-end dollars from severe nightly loss and retain expected-return diagnostics.
- An early confirmed Floor remains available while more ambitious capabilities earn their rehearsal.
- One live news-state re-solve replaces the conflicting precomputed replacement store.
- Public opponent inputs stay separate from private projections, and unvalidated numerical LLM inferences remain in shadow.
- One chunk per fresh session, explicit checkpoints, and capability labels give the owner a usable way to track partial progress.
