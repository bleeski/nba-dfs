# RT2. Red team, round 2: attack on ARCHITECTURE.md version 2

**Date:** 2026-10-13. **Reviewer:** an independent critic who did not write the design. Round 2 of at most 2. **Read:** the brief; RT1 (29 findings); `docs/ARCHITECTURE.md` version 2 in full; all 22 ADRs and the ADR index; `docs/SLATE-BRIEF-MOCK.md`; R9 in full; spot checks of R2, R4, R6, R7, R8, RR1 to RR3 and S2. I did not open the user's prior repos or GitHub. The two "TODO-EDGE" markers are treated as open; section 4 says what that benchmark must show.

**Section references** such as "§6" point to ARCHITECTURE.md version 2.

---

## 1. Verdict

Version 2 fixed most of round 1: 19 of 29 findings are fixed, 10 are partly fixed, none are untouched, and the R9 numbers are cited accurately apart from a few small slips. What still threatens the user is concentrated in two places: the new ready-made late-news files (they do not compose when two players are ruled out, Classic files go stale at the first lock, nothing is built for a questionable player who plays, and news cannot be entered without Claude), and the insurance control, which as written is either loosened or inert on every night R9 measured, with a 2% default whose evidence was measured without the safety margin and on nights below the design's own skip line. These are targeted specification changes to sections 2, 6, 8, 13 and 14 and six ADRs, not a new architecture, so the design is ready for the user's approval once the nine must-fix items in section 3A are made, without another full revision or red-team round.

---

## 2. Round-1 scorecard

Status is strict: a fix that is described but would not work as written counts as PARTLY FIXED.

| RT1 rank | Finding (short) | Status | Where version 2 addresses it, and what is left |
|---|---|---|---|
| 1 | Goal 2 is about zero at the user's volume, so the control does nothing | PARTLY FIXED | §2 adds three uncertainty layers, reports P(W) with and without, and skips the search under 1%. R9 showed the symmetric layer does not move washout ("doubling the symmetric errors changed nothing"); the only layer that might is TODO-EDGE. The control is still inert at planned volume (new findings 4 and 5). |
| 2 | Late news does not fit in 30 minutes | PARTLY FIXED | §6 ready-made if-out files, §8 timeline with a 22-minute buffer, Bluesky every 60 s, alert-only entries re-download, narrow re-run defined in 8 steps. Works for one event; fails on two events, after a lock, on a cleared player, and without Claude (new findings 1, 2, 3, 6). |
| 3 | Hunch never tested | PARTLY FIXED | §2 and §9 store 0%, 20% and lowest-washout portfolios and score them on real standings. The test is underpowered and the variants are identical on nights the search is skipped (new finding 12). |
| 4 | Field uses our private model and misses public news | FIXED | §5 public view from consensus, salary value and public-tagged overrides; `visibility` tag; three propagation tests; ADR-008. |
| 5 | Phase 1 cannot be built and rehearsed on schedule | PARTLY FIXED | §13 must-ship list, ADR-022 decides the spike question, March 2026 PDF replays, build-week budget rule. Rehearsal 2 needs code that is built the next day, and there is no cut line (new finding 7). |
| 6 | "No LLM" fallback still runs through Claude | FIXED | Component 22 desktop launcher; §7 guardrails; acceptance criterion 6 run by the user. Weekly usage may not be machine-readable (new finding 18). |
| 7 | Insurance algorithm does not enforce its rule; noise decides | PARTLY FIXED | §2 constrained swap search, separate validation set, 2-SE margin, re-checks after later steps. The margin is worded backwards, "within noise" is undefined, and D3's evidence predates the margin (new finding 4). |
| 8 | Duplication factor breaks the greedy guarantee | FIXED | §2 maximum over entries of probability x share, share averaged over copies, D2 staged; ADR-009. Switch criterion is weak (new finding 15). |
| 9 | Two news events undo each other | PARTLY FIXED | §6 ledger, run lock, merge. The ready-made files, now the main late-news path, bypass the ledger (new finding 1). |
| 10 | Upload guard covers only two tools | FIXED | §7 hooks on Edit, Write, NotebookEdit, Bash and PowerShell; manifest hashes; §11 tests. |
| 11 | Contest facts stay guesses in Phase 1 | FIXED | Component 4; must-ship item 3 on Oct 14; ADR-018 written. |
| 12 | Terms bets and thin opening-night inputs | PARTLY FIXED | §10 states both bets; D1; Odds API key as a dated action; rookie prior replaced. The researcher allowlist adds "major news outlets", which brings back sites whose terms ban automated access (new finding 14). |
| 13 | Contingency swaps change one slot only | FIXED | §6 full Showdown alternates; Classic 2 to 3 slot re-optimization. New problems with these files are new findings 2 and 3. |
| 14 | Misreads why prior engines lost; scales volume with no proof | FIXED | §1 corrected; D9 volume ramp; Nov 3 readout. |
| 15 | Overrides used after schema checks only | FIXED | §7 `dfs research fetch`, quote and 24-hour checks, 8-minute teammate cap, one-command veto. Fetch mechanics need work (new finding 14). |
| 16 | Precision weighting averages two worlds | FIXED | §4 role changes become mixtures. |
| 17 | Estimators disagree; opponents not independent | FIXED | §2 binomial for first-place contests, 8-bit probabilities under about 1,000; §5 opponents sampled as users once standings exist. |
| 18 | Best of 20,000 noisy candidates flatters picks | FIXED | §2 four independent scenario sets; §6 steps 1 to 6. |
| 19 | Opening-night late swap rests on one test | FIXED | §13 test on Oct 14, repeat Oct 15; §8 Phase 1 post-lock rule. |
| 20 | User workload about double the stated figure | PARTLY FIXED | Auto-filing, alert-only re-exports, `/status` next action, criterion 8. The new figure is still low and the test cannot measure it (new finding 11). |
| 21 | DraftKings `Status`/`Starting` wrongly marked verified | FIXED | §10 relabeled BET; Oct 14 export check. One leftover in §1 (new finding 19). |
| 22 | Fallback can include OUT players | FIXED | §8 fallback row; ADR-019. |
| 23 | QA status contradicts itself | FIXED | §1, §7, §8 and §13 now agree: QA from week 2. |
| 24 | Opening night needs an 11:30 am workday start | PARTLY FIXED | §8 Monday-evening build and D7. Tuesday uses the wrong command, and the first chance to fix the new injury-report parser is blocked (new finding 8). |
| 25 | VERIFIED claims rest on missing records | FIXED | R9 written; 22 ADRs; R2 placeholders filled; lobby provenance disclosed. One stale line in ADR-007 (new finding 9). |
| 26 | QA bar can be passed by fishing | FIXED | §7 evidence bar item 4: logged queries, at most 10, held-out half. |
| 27 | Some nights cannot be replayed | FIXED | §10 manifest list (identity map, contest facts, coverage factor, fallback level); canonical sort. |
| 28 | Other users' names can reach Claude | PARTLY FIXED | Hash on parse; Read denied on `inbox/standings/`. Bash and the raw zip in Downloads are still open (new finding 16). |
| 29 | Box scores from one volunteer job | FIXED | §10 shows lag; scoring check falls back to standings FPTS; `nba_api` backup in D1. |

**Counts: 19 FIXED, 10 PARTLY FIXED, 0 NOT FIXED.**

---

## 3. New findings, ranked by impact on the two goals

Axes: (A) the two goals; (B) free-only and terms; (C) the late-news timeline; (D) operability by a non-engineer; (E) contradictions, labels, determinism, privacy.

### 3A. Must fix before approval

#### 1. Critical (C). The ready-made if-out files do not compose, and the ledger cannot see them

**Evidence.**
- §6: "Files are rebuilt whenever a newer upload file is exported, so they always start from the latest exported lineups (the ledger, below)."
- §6 ledger: "the engine refuses (in plain language) to write a row that would revert a newer exported change".
- §8: "When no ready-made file fits (news about a player who was not questionable, or two players out in one game), `/news` ... runs the narrow re-run". Only same-game pairs are covered.
- R6 upload checklist: "Rows the engine did not change are left out of the upload".
- §8 narrow re-run step 8: "Validate, export ..., update the ledger, and rebuild the remaining if-out files", and §6: "Only one engine run happens at a time".

**Why it fails.** Every if-out file is written at the same moment from the same main portfolio, and the revert check runs when a file is written, not when the user uploads it. Take two questionable players, X and Y, in different games on the same Classic slate (the normal case on a 10-game night; R4's March 15 report listed 12 Questionable players). Both are ruled out. Y's file was built from the main portfolio, so its rows for entries that hold both players still contain X: uploading it after X's file puts a ruled-out player back. X's 2 to 3 slot re-optimization can also bring in Y as a replacement, and Y's file never touches that entry, so Y stays in after he is ruled out. The ledger holds two "last exported" lineups for every affected entry (main and if-out, same time) and no rule for which one is live until a re-download. And after any `/news`, rebuilding every remaining file happens inside the run lock at 1 to 2 minutes per player (§8), so during that window the only files on the brief's card are stale ones. Each of these leaves an entry with a zero in one slot, which is the RT1 rank 9 failure on the design's main late-news path.

**Fix.**
1. At build time, store for each questionable player and each affected entry a ranked list of validated replacement sets, not only finished files.
2. When an alert is confirmed (or the user runs `dfs out <player>`, finding 6), a deterministic `dfs apply` step composes every confirmed status change against the ledger's committed state, independent of the order the news arrived, and writes one versioned file per slate in seconds. The alert names that file. The user still does one upload.
3. The ledger marks a file "pending" from the moment the alert names it until the user confirms the upload (one key in the alert, or the next re-download). Later files are built on top of pending changes unless the user says the upload did not happen.
4. On any new export, move every older if-out file to `out/uploads/stale/` at once, so neither the brief nor an alert can name one.
5. Export first and release the run lock; rebuild Showdown alternates afterward in a background queue that `/news` can pre-empt.
6. Test: two outs in different games on one Classic slate, applied in either order, never revert a change and never leave an OUT player in a lineup.

#### 2. High (C). Classic if-out files go stale at the first lock, and nothing expires them

**Evidence.** §6: "Classic: a re-optimization of 2 to 3 slots per affected entry, using only players in games that have not started, preferring later games." R6 §2.5: "Any swap involving a game made after its real-life start (even if it started early) gets the lineup disqualified and refunded." §8 says the engine "never writes a player from a game that has started", but that check runs when a file is written. Files are rebuilt only "whenever a newer upload file is exported", not when a lock passes.

**Why it fails.** At 3:00 pm no game has started, so a file for a 9:00 pm questionable player may swap out a 6:00 pm player as one of its 2 to 3 changed slots. At 8:30 pm that cell is locked. Uploading the file then either gets the row rejected (the entry keeps an OUT player) or, per R6, gets the lineup disqualified. The watcher would still name the file, because nothing ties a file to the clock.

**Fix.** Restrict Classic if-out changes to slots whose current and new players tip at or after the questionable player's game, so the file stays valid until that game locks. Stamp each file with "valid until" (the earliest lock among its changed cells); the watcher and `dfs status` never name an expired file; the brief's card shows the stamp. With finding 1's composition step this is automatic, because the file is written at alert time against the current clock.

#### 3. High (A, C). Nothing is built for the more likely outcome: a questionable player who plays

**Evidence.** §6 and §8: the engine "builds and validates a complete upload file for the 'out' outcome". The mock: "Player C (DET) cleared to play | Nothing; current files already favor that outcome", for a player listed as "Questionable, 55% to play". §6: "Showdown has no late swap". §8: in Phase 1, `/swap` "swaps only players ruled out".

**Why it fails.** At 55% to play, greedy selection deliberately covers both worlds, so part of each Showdown and Classic portfolio is built for "C sits" (for example the beneficiary at Captain). R9 shows how different the worlds are: the beneficiary averages 18.5 points when the star plays and 34.6 when he sits. When C is cleared, those entries carry dead weight and neither a file nor a Phase 1 command removes it. Showdown is "a large share of volume" (brief) and has no late swap, so the Goal 1 loss is locked in on the most common resolution of a Questionable tag.

**Fix.** For each Showdown, build both "if out" and "if in" alternates (enumeration plus greedy is about 1 to 2 seconds per contest, R9). For Classic, store "if in" replacement sets the same way as "if out" (finding 1). The watcher alerts on "available", "will play" and official upgrades too. Correct the mock's "Nothing" line.

#### 4. High (A). The insurance control as written is loosened or inert, and the 2% default rests on nights the design would skip

**Evidence.**
- §2: every contest keeps "at least `(1 - epsilon) x G1*_c` **minus a safety margin of two standard errors**".
- §2: "a budget smaller than two standard errors of a contest's Goal 1 estimate is reported as 'within noise' for that contest".
- §2: "if `P(W)` at 0% is under 1% (with the edge-uncertainty layer), the brief says 'washout risk is negligible tonight' and skips the search."
- D3: "On synthetic 25-entry nights, 2% removed 70% to 92% of washout risk".
- R9 frontier: the pure top-1% portfolio's washout on the four 25-entry nights was 0.513%, 0.530%, 0.997% and 0.643%. R9: "Most of the gain comes at epsilon 0. Those swaps are tie-breaks". R9 per-contest table: the N = 150 single-entry contest kept "0.856 ± 0.050" at both epsilon 0 and 2%.

**Why it fails.**
- (a) Read literally, "(1 - epsilon) x G1* minus a margin" lowers the bar. R9 asked for the opposite ("epsilon minus about 2 standard errors").
- (b) D3's evidence comes from a configuration the rule does not use. Under the layers R9 actually ran, all four nights with any washout sat under the 1% line (the 2-game night at 0.997% is within noise of it), so the rule would have skipped them. Whether layer 3 lifts such nights above 1% is exactly the open TODO-EDGE question, so today D3 has no evidence that applies to the rule as written.
- (c) D3's numbers were measured with no margin, and most of the gain came from tie-break swaps at epsilon 0, which a correct margin forbids and which cost one single-entry contest 14% of its top-1% odds out of sample.
- (d) "Within noise" does not say whether the contest is frozen or unconstrained. With 15,000 validation scenarios, two unpaired standard errors on a 1% to 3% single-entry probability are about 9% to 16% of it, so at 2% nearly every single-entry and small contest is "within noise". If that means unconstrained, the search can sacrifice exactly those contests; if frozen, it can only touch the big multi-entry contests, which almost never wash out (R9: the 150-max "cashed in every one of 30,000 scenarios").

**Fix.** Write the rule as `G1_V(new) >= (1 - epsilon) x G1*_V + 2 x SE_paired`, with both terms on the validation set and the paired standard error of the change against the greedy portfolio. State that a contest whose budget is within noise is frozen. Replace the 1% skip with a noise rule (skip only when the validation set has fewer than about 50 washout scenarios, about 0.33% at 15,000) or make the threshold a setting shown in the brief. Re-run R9's 25- and 50-entry frontiers with the corrected margin and the freeze rule (the spike exists; this is minutes of compute) and quote those numbers in D3. After the search, check each contest on the reporting set and roll back any contest that ends more than two standard errors below its guarantee. Say plainly in §1 and D3 that at 50 or more entries the control will usually do nothing, and that opening week (where the search is a stretch item, §13) has no working control.

#### 5. High (A). The edge-uncertainty layer (TODO-EDGE) changes which lineups are picked, and its Phase 1 status is undefined

**Evidence.** §2 layer 3: "the true expectation for every player is drawn between the public view and our view, with the weight on our view drawn once per scenario ... The weight starts low and wide (BET)". §13 must-ship item 6: "simulator v0 with the model-error layer" (one layer); item 7: "washout reported with and without model error". But §2: "Reported two ways: with and without the edge-uncertainty layer", and the skip rule is judged "with the edge-uncertainty layer". R9: the symmetric layer "barely moves washout".

**Why it fails.** Selection runs on the same scenarios as the washout estimate. With a low weight on our view, simulated truth is mostly the public view, which is also what the field is built from. Greedy then covers "the public is right" scenarios with chalkier lineups: more duplication while D2 keeps selection on raw probability, and less effect from the researcher's private overrides. Whether the insurance search runs at all also depends on this unfitted weight. Phase 1 does not say whether layer 3 ships, or whether it feeds selection or only the reported number.

**Fix.** State that in Phase 1 layer 3 feeds reporting only (P(W) with and without it), unless the TODO-EDGE result meets the bar in section 4. Write that bar and the decision it triggers into §2 before the result arrives, so the result cannot be read to fit.

#### 6. High (C, D). Without Claude, news has no reliable structured input

**Evidence.** Component 18: the watcher, "plain Python, no Claude", "polls ... Bluesky reporter mirrors every 60 seconds ... raises a desktop alert naming the ready-made file". R4: the Bluesky source is "A Shams Charania mirror bot (`shamsbot.bsky.social`)", and "the mirror is unofficial and could stop any day". §8 narrow re-run step 2: "Update the affected players' availability (and roles, if the researcher has time and budget)". §8 offers "`/news` (or `dfs news`)", but no command takes a player name.

**Why it fails.** To name a file from a Bluesky post, plain Python has to turn free text into "Player X OUT", and the design gives no rule. Posts such as "X is out of the starting lineup", "X (ankle) upgraded from out to questionable" or "Y will start with X out" defeat keyword matching, and a false OUT alert leads the user to pull a playing star from every affected lineup. When the user sees news first (the realistic fast path if the bot stops) or Claude is over its limit, `dfs news` has no way to be told who is out, because only the researcher files overrides.

**Fix.** Two alert classes. OFFICIAL (the injury report or a DraftKings `Status` change) names the file. POSSIBLE (Bluesky) shows the post word for word and asks the user to confirm with `dfs out "<name>"`. Add `dfs out` and `dfs in` to the launcher: fuzzy name match against tonight's slates, one confirmation, recorded as a user override (which beats the LLM's), feeding finding 1's composition step or the narrow re-run. Add a negation test set to the suite, and replay recent mirror posts before Oct 20 to count false alerts. Tell the user that their own phone alerts are the primary fast channel and the bot is a bonus.

#### 7. High (D). The Phase 1 schedule contradicts itself, and the only opening-night-shaped rehearsal cannot run the pipeline

**Evidence.** §13: "Thu Oct 15 (2 games ...) | Item 6 | **Rehearsal 2:** full build without LLM on the 2-game slate (Classic plus both Showdowns), opening night's shape". Item 7 (candidates, field v0, thresholds, greedy) is built on "Fri Oct 16 (12 games) | Items 7 to 9", with the dress rehearsal that same evening. The must-ship list is "in build order" with no cut line. D4: "until then everything runs on Pro".

**Why it fails.** A full build needs item 7, which does not exist until Friday. Friday then builds candidates, field, thresholds, selection, if-out files, the watcher and the brief, and dress-rehearses all of them that night. If the Pro weekly window runs low mid-week, nothing says what is dropped.

**Fix.** Pull a minimal item 7 (casual-only field, candidates, greedy) into Thursday by moving slot assignment and the with/without washout report to Saturday; keep items 8 and 9 on Friday. Define tiers inside the must-ship list: tier A (items 1 to 5 plus a brief-lite) is the floor that ships valid files on Oct 20 with nothing else; tier B is items 6 and 7; tier C is items 8 to 10. Record Claude usage after Wednesday's build and project the week; if Wednesday used more than about 20% of the weekly window, build only tiers A and B before Oct 20.

#### 8. Medium (C). The opening-night Tuesday refresh uses a command built for one game's news

**Evidence.** §8: "Tuesday, 12:30 to 12:45 pm CT | Re-download the entries and salary files; run `dfs news` (no LLM needed), which finishes in under 15 minutes." The narrow re-run is defined as "Re-simulate only the affected game". §13: "Mon Oct 19 | Fixes only until noon", while R4 says the 2026-27 injury report naming "cannot be known yet" and the first reports appear Monday.

**Why it fails.** Overnight and game-day reports can change all three games, and contests entered after Monday's download need lineups; neither is what a one-game re-run does, and "under 15 minutes" is unmeasured. Monday evening is the first chance to see the new injury-report format, and the plan forbids fixes after noon.

**Fix.** Tuesday runs `dfs night --no-llm --reuse-overrides` (a full deterministic build that reuses Monday's checked overrides and fills new entries), timed in rehearsal 3. Allow injury-report parser fixes on Monday evening. Ask the user to confirm they can be at the laptop from 12:30 to 2:00 pm CT on a workday; if not, Monday's upload and if-out files stand and the brief says so.

#### 9. Medium (E). The decision records contradict the design on the core control and on workload

**Evidence.**
- ADR-001: "three independent scenario sets: screening (10,000), selection (10,000), reporting and validation (30,000)", with no safety margin, and "each contest's top-1% odds never fall more than epsilon below the best the engine found (on fresh scenarios)", which R9 disproved.
- ADR-002: "a slate-wide scoring shift" (R9: it "cannot change any rank"), "10,000 scenarios to screen, 30,000 to finalize", and no edge-uncertainty layer.
- ADR-007: three sets, no margin, and "(68 to 370 seconds for 150 lineups, R2, indicative)", against ADR-006's GLPK 30.8 s.
- ADR-004: workload "about 2 to 8 minutes a night". ADR-005: `Status` and `Starting` "from the user's salary re-export near lock (manual)", against §8's alert-only re-exports. ADR-011: "about 5 minutes per news alert".

**Why it matters.** The user approves these records and Claude Code builds from them. ADR-001 merges validation and reporting into one set, which is exactly the leak R9 measured.

**Fix.** Rewrite ADR-001, 002, 004, 005, 007 and 011 from the next version of the design, and add a test that checks the scenario-set sizes and the margin rule appear the same way in ARCHITECTURE and ADR-001.

### 3B. Fix during Phase 1

#### 10. Medium (A, C). If-out generation does not fit the build budget on big nights

**Evidence.** §8 build row: "Budget 15 min ... 3.5 min for the core build ... plus about 2.7 min for reporting ... plus about 1 to 2 min per questionable player for if-out files (R9)". R4's March 15 report: "Questionable 12, Probable 2, Doubtful 1" across 15 games. R9's 103-second re-run excludes ingest, export and rebuilding other files; the 5,000-scenario screening set is unmeasured.

**Problem.** About one qualifying player per game means about 10 on a 12-game night: 10 to 20 minutes of if-out work, which breaks the 15-minute budget by itself.

**Fix.** Build files only for players in at least a set share of our entries or whose absence materially moves a beneficiary in our pool. Classic uses stored replacement sets (finding 1); Showdown runs at 10,000 scenarios reusing other games' lines; work in lock order, in the background. Rehearsal 3 measures the budget with the real count of qualifying players.

#### 11. Medium (D). The user-time figure is still optimistic, and its acceptance test cannot measure it

**Evidence.** §8 "Your time, honestly": 15 to 20, 4 to 8, 4 to 5 and 4 to 5 minutes sum to 27 to 38, but the total says "About 25 to 35". §1 step 2 suggests uploading the fallback "as insurance" (four more uploads, not counted). §10: the Daily Fantasy Fuel CSV is "downloaded by you ... about 30 seconds" (not counted). Criterion 8: "Your measured time on the dress rehearsal is under 35 minutes", but the rehearsal is "two or three $0.25 contests". Staying reachable for alerts from about 4:30 pm to last lock is not counted.

**Fix.** Quote 30 to 45 minutes plus an on-call window. Time each action in the rehearsals and project a 4-slate, 10-contest night from those per-action times; make criterion 8 that projection (under 40 minutes). Recommend the fallback upload only when the full build is at risk.

#### 12. Medium (A). The real-field hunch test is too weak to decide anything, and the skip rule starves it

**Evidence.** §2: "Each night the engine stores three portfolios ... After 20 nights the brief gives a verdict with an interval." §9: "Detecting a top-1% rate moving from 1.0% to 1.5% needs about 7,700 independent entries per version". §2's skip rule.

**Problem.** The variants differ by a few lineups and at 50 or more entries almost never wash out, so 20 nights cannot separate them; on nights the search is skipped the three are the same portfolio.

**Fix.** Compute all three variants every night even when production skips the search (about 1 second). Compare them on dense paired measures: each contest's realized best-entry percentile and cash count, paired by contest. State now the interval width expected after 20 nights, and report "undecided" if the interval spans zero.

#### 13. Medium (D). Stale run lock and the watcher's lifecycle are unspecified

**Evidence.** §6: "Only one engine run happens at a time". Component 18 is a long-running watcher; risk 13 mentions "keep-awake during night runs". Nothing says who starts the watcher or what happens to a lock left by a crash.

**Problem.** A crashed run or a sleeping laptop leaves a lock that blocks `/news` at T-20, which is the golf failure (RR3) in a new form. A watcher started from a Claude session dies when the session closes.

**Fix.** A lock file with process ID and heartbeat, cleared automatically after about 2 minutes without a heartbeat, and a plain-language `dfs status` line. The launcher starts the watcher in its own window with keep-awake from the first build to the last lock; `/status` shows each source's last poll time.

#### 14. Medium (B). The researcher's allowlist includes sites that ban automated access, and the quote check may fail on its main sources

**Evidence.** §7: "Permissive posture allowlist: official.nba.com, nba.com team news pages, team and league press releases, `bsky.app` reporter posts, and major news outlets' articles." §10 on ESPN: it "Prohibits access 'using a robot, spider, script, or other automated means' (VERIFIED quote)". §7 checks: "the page was published within the last 24 hours".

**Problem.** "Major news outlets" includes espn.com and paywalled outlets with no-scraping terms, contradicting "uses only sources whose terms do not prohibit this use" (§10). `bsky.app` post pages are rendered in the browser, so a plain fetch may not contain the quoted words. How the publish time is read is unspecified per site, so the 24-hour rule could drop every record.

**Fix.** List the allowlist by domain with each domain's terms status; drop espn.com and paywalled outlets. Fetch Bluesky posts through the public API (post text and `createdAt`). Define the publish-time source per domain, and label (rather than drop) a record whose time cannot be read.

#### 15. Low (A). The duplication switch counts files instead of checking calibration, and ignores small Classic slates

**Evidence.** §2: "Selection switches to the adjusted version after at least five NBA Showdown standings files have fitted the duplicate rate." §6 (from R9): "On the 2-game Classic slate our 150-max lineups averaged about 1 expected copy". Opening night has a 3-game and a 2-game Classic slate.

**Fix.** Switch per format when predicted copy counts, for our own entries and for the field's most common lineups, match observed counts within a stated tolerance; include Classic slates of 3 games or fewer.

#### 16. Low (E, privacy). "Claude cannot read the raw standings files" is not enforced

**Evidence.** §7: "deny Read on `inbox/standings/`"; the Bash and PowerShell hooks block only `out/uploads` and `draftkings.com`; component 1 picks files up from Downloads.

**Fix.** The filer moves (not copies) standings zips out of Downloads to a folder outside the project, parses and hashes them there, and writes only hashed tables into the project. Extend the Bash and PowerShell hook to block commands that name that folder or `contest-standings`, and test it.

#### 17. Low (B). The Odds API plan exceeds the free quota

**Evidence.** R4: "lines for all games in one call cost 3 credits; twice a day for a month is 180 credits ... Props for 4 markets on a 10-game night cost about 40 credits, so 500 credits cover about 12 nights." §10: props "on about 12 nights a month".

**Fix.** 180 + 12 x 40 = 660, over the 500-credit free tier. Plan about 7 prop nights, read the remaining-credit response header in code, and keep a reserve for late-news line refreshes.

#### 18. Low (D). Weekly usage may not be readable by the preflight hook

**Evidence.** §7: "`SessionStart`: preflight (... five-hour and weekly usage reminder)". R7: "The statusline JSON exposes `rate_limits.five_hour.used_percentage` ... documented for Pro and Max subscribers; Team seats are not listed: UNKNOWN."

**Fix.** A status-line script writes the rate-limit fields to a file that preflight reads. If no weekly field exists, preflight asks the user once a day to read `/usage`. The 70% rule cites whichever number is available.

#### 19. Low (E). Small citation and label slips

- §2 table: "Building every contest on one thesis ('games 0 to 2 all go over') | cut average top-1% odds 6.5% to 11.7% (worst contest 19% to 28%)". R9: 6.5% and 19% belong to the "game 0 over" thesis at 118 entries; "games 0 to 2" cost 11.1% to 11.7% (worst 27% to 28.5%).
- §8: "about 2.7 min for reporting on 30,000 fresh scenarios". R9 test set B: 6.6 + 160.7 + 6.6 = 174 s, about 2.9 minutes, and the screening set is not counted anywhere.
- §2: "Real washouts come from being confidently wrong in one direction" sits inside a paragraph labeled "(R9, VERIFIED on a synthetic night)"; R9 calls it "the most likely real cause of washouts ... BET".
- §10: the injury report updates "Every 15 minutes in the 2026 regular season". R4: from October to at least December 20, 2025 it was "One file per hour, overwritten within the hour". The watcher must re-check the hourly file by Last-Modified time if October 2026 starts the same way.
- §1 table: "the salary export (which adds DraftKings' `Status` column)" is stated as fact; §10 says BET for NBA.
- §1 step 3: the build is done "About 30 to 45 minutes after you start"; §8: "About 45 to 60 min after starting | Upload".
- §4: R9's wide player spreads are called "conservative"; wider tails inflate top-1% odds, so "optimistic for Goal 1" is closer.

### 3C. Checked, no new finding (one line each)

- **Determinism.** Keyed draws, no solver time limits, canonical sorts and the expanded manifest hold up. The one addition: finding 1's composition step must give the same file whatever order the news arrived in, and each file's pending or confirmed state must be written to the run manifest so a late-news night can be replayed.
- **Auto-filing from Downloads.** Sound in principle. Repeated downloads arrive as `DKEntries.csv`, `DKEntries (1).csv` and so on, so the filer must pick by content (draft group from the player IDs) plus file time, never by name, and `/status` should print which file it used for each slate. It should open only files whose names and headers match DraftKings formats, not everything in Downloads.

---

## 4. What the TODO-EDGE benchmark must show

The design depends on this result for three things: whether washout is ever a live tradeoff at planned volume, whether the insurance control runs, and how lineups are picked if the layer feeds selection. Before it is read, the design should commit to the following bar.

1. **Washout at real volume.** P(W) at 25, 50 and 118 entries with layer 3 at three priors for the weight on our view (for example means of 0.2, 0.5 and 0.8), with the rule-of-three bound where the count is zero.
2. **A realistic edge.** Under the chosen prior, single entries should cash closer to the user's real 13% (R8) than to R9's 31% to 44%. If they do not, the synthetic edge is still too large and every washout number stays a lower bound.
3. **Effect on selection.** The share of lineups that change against the no-layer portfolio; expected copies per Showdown entry; and Goal 1 of both portfolios on reporting sets drawn with truth equal to our view and truth equal to the public view. Selection should use the layer only if it loses no more than noise when our view is right and gains when the public is right.
4. **Whether insurance buys anything.** With the corrected margin and freeze rule (finding 4), the washout reduction at 25 and 50 entries must exceed two paired standard errors, and the Goal 1 cost must be reported per contest on the reporting set.
5. **Cost.** Build time and peak memory with the layer on (R9: the ownership shock alone made lines 1.5x slower).
6. **The pre-registered decision.** If P(W) stays under the skip threshold at 50 entries for every plausible prior, the design says outright that Goal 2 at planned volume is a delivery and concentration problem, moves the insurance search to nights under about 30 entries, and treats D3 as moot. If P(W) exceeds it, D3's default is re-derived from the new frontier.

**On the claim "at your planned volume, washout is mostly a delivery and concentration risk" (§2).** It is plausible, and real-field evidence supports it better than R9 does: in the user's NFL data, random 20-entry Showdown portfolios had a zero-paid rate of about 0.7% per contest, and a pre-lock filter "cut P(zero paid) from 0.007 to 0.002" (RR2; NFL, four games, in-sample). But R9's own reading is the opposite ("Washout at real volume is a model-error question"), and the design cites only R9. Cite RR2, state the disagreement, and let TODO-EDGE settle it under the decision above.

---

## 5. Are the R9 numbers cited correctly?

Mostly yes. Every runtime, memory and washout figure I checked matches R9. The problems are in how two of them are used (D3 and the narrow re-run), not in the numbers.

| Claim in ARCHITECTURE | R9 says | Verdict |
|---|---|---|
| Full build 211 s at 30,000, 86 s at 10,000; peak 1.66 GB | Same (8G-30k, 8G-10k) | Correct. R9's "30,000" means 15,000 selection plus 15,000 validation; the design's screening set is extra and unmeasured. |
| Lines are 72% of the build (152 of 211 s) | 53.2 + 98.9 = 152.1 s | Correct |
| Simulation 1.9 s and 6.7 s | Same | Correct |
| Fields 3.8 s, 2.4 s, 3.3 s | Same | Correct |
| 4,500 candidate solves in 6.7 s; median 6.4 ms; 0 invalid of 6,500 | Same | Correct |
| Shortlist scoring about 30 s; greedy 0.3 s; search about 1 s | 11.4 + 19.3 s; 0.3 s; 1.2 s | Correct |
| Reporting about 2.7 min | 174 s (sim, lines, scoring) | Slight undercount (about 2.9 min) |
| Narrow re-run 44 s and 103 s; about 33 s per extra Showdown | Same | Correct as measured, but it excludes ingest, export and the rebuild of other if-out files that §8 step 8 includes (finding 10) |
| 118 entries: 0 washouts in 30,000; under 0.01% | Same | Correct |
| 25 entries: about 0.5% (8-game) to 1.0% (2-game) | 0.513% and 0.997% | Correct |
| Doubling symmetric errors changed nothing | 0.493% against 0.513% | Correct |
| Single entries cashed 31% to 44% against 22% paid | Same | Correct |
| 2%: 70% to 92% less washout for 0.4% to 3.5%; 5%: 80% to 94% for 0.7% to 2.7% | Same | Correct as numbers, but measured without the margin and on nights the 1% skip rule would skip (finding 4) |
| 5% budget kept 0.919, about 4 SE beyond; single contests lost 8% to 14% | 0.919 ± 0.008; 14.4% at 2%, 8.1% at 5% | Correct |
| Tie-break swaps cost 0.2% to 3.4% out of sample | Same | Correct |
| One thesis "games 0 to 2" cut odds 6.5% to 11.7%, worst 19% to 28% | 11.1% to 11.7%, worst 27% to 28.5%; 6.5% and 19% are "game 0 over" | Mixed two theses (finding 19) |
| Quantile line understates first-place odds 7% to 38% | Same text; its table shows 22% and 27% lower | Correct as cited |
| Portfolio shape, game shares, duplication changes, 2-game copies about 1 | Same | Correct |
| Totals within 1.4; margin SD 12.7 to 12.9; teammate -0.02, opponent +0.02; star SD 0.30 to 0.34 | Same | Correct |

---

## 6. Brief requirements still unmet

1. **"Give me one control for choosing where on that tradeoff to sit."** The control exists on paper, but it is a stretch item in Phase 1 (§13: "Stretch ... the insurance search"), it is skipped at planned volume, and as written it is loosened or undefined (finding 4). On opening night the user has no working control, and §1 and D3 should say so.
2. **"My hunch ... Test it."** Tested on synthetic nights (R9). The real-field test is underpowered and starved by the skip rule (finding 12).
3. **"Confirm against the live rules pages."** R6 recommends a 2-minute manual copy of both rules pages "once before Oct 20". It is not in §13's schedule or §14's actions.
4. **"Confirm from real DraftKings results ... whether the Captain 1.5x applies to bonuses."** Still SUPPORTED. Make one of the Oct 14 $0.25 entries an NBA Showdown and check the Captain row by hand on Oct 15, before go-live.
5. **"In fields under 100 entries, top 1% means first place."** §2 extends first-place-only to fields of 100 to 199 ("any field under 200 has one top-1% place"). That changes the definition of a fixed goal, so it needs the user's one-line confirmation (RT1 question 13, still open).
6. **Problem 1, "How are questionable players handled before their status is known?"** Handled for "out"; the more common "plays" resolution has no path (finding 3).
7. **"Verify each source works today."** Still open, each with a date: The Odds API (user's key), Daily Fantasy Fuel projections in the regular season, the 2026-27 injury report naming (Oct 19), and the NBA `Status` and `Starting` columns (Oct 14).
8. **"Size the research and QA steps so a full night ... fits comfortably."** Still a BET until the Monday Oct 19 build is measured; QA is unmeasured until week 2. The weekly-window rule may rest on a number preflight cannot read (finding 18).
