# NBA DFS Engine: Brief (living requirements document)

## Changelog

- **2026-10-14 (v2):** Created as the living brief from the saved architecture brief (`docs/brief/2026-10-13-architecture-brief.md`), the goals and hard constraints restated in the adjudication prompt, and the advisor section as quoted by both critiques (the original `NBA_DFS_Architecture_Prompt.md` was never saved; ADJUDICATION X-04). Both goals rewritten by the owner's decision after adjudication (ADJUDICATION entries 5 and 9). Constraints, problems 1, 2, 6, 7, 10 and 12, the MVP definition, the advisor section, the edge hypotheses and the session rules changed per `docs/review/ADJUDICATION.md`; each change carries its entry ID.
- **2026-10-13 (v1):** the architecture brief as given, saved in `docs/brief/`.

**Provenance.** Sections marked "verbatim" are the owner's words from the 2026-10-13 brief. Sections marked with an adjudication ID were edited by that ruling. If the owner still has the original prompt file, paste it into the repo and the next session reconciles any difference.

---

## Roles (verbatim)

You are the architect and the developer. I'm the business analyst and product manager, and I'm not a software engineer. I'll make product calls; you make technical calls and tell me in one sentence what each means for results, cost, or my nightly workload. If my requirements have a gap, push back the way a senior PM would.

Claude Code builds this engine and also runs it every night. At runtime, the LLM layer is you, working inside Claude Code sessions with subagents, skills, and commands. There's no separate paid model API.

## The two goals (owner's decision of 2026-10-14; ADJUDICATION entries 5 and 9)

These are fixed. Everything else in this brief is negotiable.

1. **Within each contest, maximize top-1% prize equity:** the expected dollars our entries win from top-1% finishing places, after splitting tied payouts with opponent lineups that copy ours and with equal scores, expressed as a share of the contest's top-1% prize pool. Finishes outside the top 1% score zero inside Goal 1. Top-1% places are `max(1, floor(0.01 x field size))`, so any field under 200 entries counts first place only (Decision D10). In a multi-entry contest every entry's top-1% winnings count, not only the best entry's.
2. **Across the night's portfolio, minimize the probability of a severe-drawdown night:** total winnings across every contest that night, Classic and Showdown combined, below a set share of the night's total entry fees. The share (`goal2.alpha`) defaults to 25%; setting it near zero recovers the literal "zero cashing entries" definition.

**Reported beside the goals, never inside them:** the raw probability of a top-1% finish per contest; the probability of a literal washout (zero cashes); total fees; expected net return under stated assumptions; probability of recovering the night's fees; probability of a meaningful prize (at least 10x the entry fee); unfilled entries; per-game concentration. Changes in volume are reported separately from changes in skill (ADJUDICATION entry 4).

**Original wording (2026-10-13), kept for history:** "1. Within each contest, maximize the probability of a top-1% finish. For a single-entry contest, that's the probability our lineup finishes in the top 1%. For a multi-entry contest, it's the probability that at least one of our entries does. In fields under 100 entries, top 1% means first place. 2. Across the night's portfolio, minimize the probability of a total washout. A washout is zero cashing entries across every contest that night, Classic and Showdown combined."

The design must define both goals mathematically, say how each is estimated, show how they trade off, and give me one control for choosing where on that tradeoff to sit. Resolve these inside those definitions:

* Both goals need each contest's payout curve, paid places and field size, and each lineup's expected number of opponent copies. Say where each comes from, label every number by the status of those facts (verified, template, default), and never present a number resting on defaults as measured (entry 1).
* Duplication is inside Goal 1 by definition: a copied lineup that finishes top 1% wins its share of the pooled tied prizes, which DraftKings split evenly (verified). Use money after rank-aware tie splits, never a flat per-copy penalty (entries 5 and 6).
* My hunch is the two goals conflict less than they look, since both reward covering different ways the night can unfold. Test it on real fields, not only in simulation (entry 2).

## Where the edge is supposed to come from (ADJUDICATION entry 20)

Every feature after the MVP names which of these hypotheses it serves and what result would falsify it. Replicating a commercial platform's feature is not a reason by itself.

1. **Execution reliability.** No blank, late or rejected entry. Falsified by any delivery failure.
2. **Late-news reaction.** Our entries reflect a scratch and its beneficiary before the field's stale share does. Falsified if our ownership error on news-driven players is no better than the field's.
3. **Minutes and role on rotation changes.** Our minutes error on news-affected players beats the 75% season plus 25% last-five baseline. Falsified if it does not after 30 such player-games.

## My vision: a starting hypothesis (verbatim, with one edit)

Improve on this. Add, cut, reorder, or replace steps. Where you depart from it, tell me what changed and why in terms of the two goals.

1. I upload two CSVs from DraftKings: the salary file (players, position eligibility, teams, salaries, IDs) and my entries file (every contest entry I hold).
2. The engine projects fantasy points for every eligible player using the DAG in the attached blueprint: median, top-1% outcome, and boom/bust potential. It also projects ownership.
3. The LLM layer researches injury reports and removes players who won't play, overrides projections when roles change (an injury replacement getting more minutes and usage, for example), and assigns players to lineups using DFS strategy such as stacking.
4. An adversarial QA agent reviews the full portfolio. It looks for data-backed changes and for Pareto improvements that raise our top-1% odds or lower drawdown risk. *(Edited per entry 18: QA is one pre-lock coherence pass that files cited missed-news challenges and lineup-coherence flags; historical splits are computed by code, not proposed by the agent. The original "at most three iterations" is kept here as the hypothesis it was; say so if it was a requirement.)*
5. Claude Code presents the DraftKings upload file.
6. After contests finish, I upload the standings and we work out whether we perform better in certain contest types or sizes, whether the projections need refinement, and whether the ownership model needs refinement.

## Context you already have from me (verbatim, plus answers of 2026-10-14)

* Contest mix: single-entry, 3-max to 20-max, and 150-max GPPs. Showdown is a large share of volume.
* I can re-run and late swap close to tip most nights.
* Go-live: NBA opening night is Tuesday, October 20, 2026. Plan an opening-week MVP that ships valid, sensible portfolios. Simulation depth, the field model, and the learning loop can mature after that.
* Volume: about 10 contests, 50 to 200 entries, 2 to 4 Showdown games a night. Start at about 25 to 50 entries a night until the ramp gate passes (Decision D9).
* Availability (answered 2026-10-14): at the laptop Thursday Oct 15 evening, Friday Oct 16 evening, and Tuesday Oct 20 from 12:30 to 2:00 pm CT; afternoons at the desk; about 30 minutes before most tips through the last lock.
* Claude plans: a Team standard seat and a Pro plan; both may run the engine; size LLM work to roughly Pro-level limits.
* No past NBA DraftKings standings files exist (cold start for the field model).

## Constraints (hard constraints verbatim; wording edits marked)

* **Free only.** Open-source software and free data. I won't pay for data or subscriptions. A free tier is fine if nightly use fits inside it. Flag any source whose terms prohibit what we'd do with it, and respect rate limits. My Claude plan, including the Fable advisor, is the only paid component. *Data posture decided 2026-10-14 (Decision D1): permissive, plus `nba_api` for box scores and game logs only; ESPN JSON off; DraftKings manual in every posture.* "Verified source" means the chosen local path returned the required current data, parsed, and passed freshness checks; documentation-only and historical probes carry separate labels; every required input names its fallback; free data availability is an operating constraint, not an assumed solved problem (entry 14).
* **Correct files, every time.** Deterministic code validates every lineup before it reaches the upload file: salary cap, roster slots, position eligibility, the right player ID for each slot, Classic's two-game minimum, Showdown's both-teams rule, and locked players. *Restated per entry 11:* every exported file passes the validator against its identified input snapshot and lock time; platform acceptance is confirmed separately by my read-back and a re-download; optional modeling failures preserve the last usable portfolio; identity or lock uncertainty stops an edit rather than shipping it; known-OUT unlocked players are removed whenever a legal repair exists; missing evidence is visible and never relabeled as verified.
* **Deadline beats perfection.** If an advanced step fails near lock, ship a valid portfolio from what we have and tell me what was skipped.
* **Scope.** DraftKings NBA, Classic and Showdown Captain only. Don't build a multi-sport framework.
* **I upload to DraftKings myself.** Nothing automates actions on the DraftKings site.
* **Runs on my machine.** Measure what it can do. Set runtime budgets for the first full build and for a late-news re-run, which has to finish fast enough to act on news that breaks 30 minutes before tip.
* **LLM work has a budget too.** Size the research and QA steps so a full night, including late-swap re-runs, fits comfortably within Claude Code's usage limits. The advisor has its own rule (below).

## Resources

Reference files, now in `docs/reference/`:

* `NBA Classic.txt` and `NBA Showdown Captain Mode.txt`: DraftKings rules and scoring. Treat them as the source of truth, then confirm against the live rules pages and real contest results.
* `NBA_DraftKings_DAG_Expanded.md`: a projection DAG and simulation blueprint. Start from it and critique it; it's a draft.
* `DFS_Platforms_Competitive_Edge_Report_2026-10-13.md`: how SaberSim, Stokastic, Ship It Nation, RotoGrinders, FantasyLabs, and FantasyCruncher create their edge. *Per entry 20: a paid platform technique earns implementation effort only through a specific hypothesis and a measurable improvement over our simpler baseline.*

My prior engines (research only): https://github.com/bleeski/mlb-dfs, https://github.com/bleeski/nfl-dfs, https://github.com/bleeski/nhl-dfs, https://github.com/bleeski/soccer-dfs, https://github.com/bleeski/golf-dfs. Reuse nothing by default; justify any reuse in a decision record. Established operational failure facts from them may be consulted at any time (entry 26).

Research leads (verbatim): Hunter, Vielma and Zaman (arXiv 1604.01455); Haugh and Singal (SSRN 3393127); open-source DFS optimizers and contest simulators; free NBA data (official stats endpoints and wrappers, the official injury report, play-by-play, free lines and props); free MILP and constraint solvers chosen on merits.

## Problems the design must solve (verbatim except where marked)

1. **Late news.** Statuses resolve close to tip, and staggered tip times split the slate. How does the build stay right as news lands? What's the re-run and late-swap path, how fast is it, and how do we construct lineups to keep swap flexibility for late games? How are questionable players handled before their status is known? *Added per entries 10 and 17:* late-news acceptance must cover two same-team absences, conflicting pivots, a status reversal, an unrostered scratch that changes our beneficiaries, and a failed upload crossing a lock; every late-news file is built on the complete current news state; detection-to-confirmed-upload time, including my work, is measured at 30, 10 and 2 minutes before tip; the engine says when there is insufficient time to act. Late swap re-optimizes every open slot, because the beneficiary of a scratch is the point. The news digest is ordered by exposure times fees at risk, so research lands where it moves lineups (entry 21).
2. **Minutes and usage.** When a player sits, how are his minutes and usage redistributed across teammates, with uncertainty? This is where LLM role overrides meet the model, so define that interface precisely. *Added per entry 12:* an LLM's stated confidence is not a statistical weight; facts and numerical inferences are separate records; a verified quote supports only what it says; unknown or mismatched event time cannot authorize an availability change; numerical override influence must be earned through prospective calibration.
3. **Correlation.** NBA correlation differs from MLB and NFL. Teammates often compete for usage, while pace, game totals, and blowouts drive shared outcomes. How do we capture it, and how does it shape Classic versus Showdown construction?
4. **Showdown.** Captain selection, the both-teams rule, small player pools, heavy duplication, and separate Captain and UTIL ownership. DraftKings lists each player twice with separate IDs and salaries for Captain and UTIL (verified); handle it. Captain totals need eighth-point precision (entry 23).
5. **Ownership without a paid feed.** How do we project it, how fast does it react when news creates new chalk, and how do we bootstrap before we have our own history?
6. **The field.** Ownership says how often each player gets picked. It doesn't say how opponents combine players. Decide what field model Goal 1 needs and how to build it. *Added per entry 6:* treat the field as a family of plausible opponent behaviors; ownership fit alone cannot qualify it; qualify thresholds and duplication separately on held-out games and news conditions; test dependence across contests explicitly; "private" is a hypothesis about informational advantage, not evidence that opponents lack it; the public view never falls back to our private baseline model.
7. **Contest details.** *Replaced per entry 1:* for each current contest, record its entry fee, entry limit, field capacity, observed entries with a timestamp when captured, and exact payout schedule or verified paid cutoff, classified by contest type. Historical contest families and cached facts supply estimates only and prefill the form. Missing facts never prevent a legal file, but they prevent claims of measured prize equity, drawdown protection or payout-aware optimization for that contest, and the brief labels them. Never infer cashing from finishing percentile alone.
8. **One night, one portfolio.** Classic and Showdown entries share games, and Goal 2 is measured across the whole night. How do we measure drawdown risk and cross-contest correlation across the full night?
9. **The LLM and solver boundary.** Where does judgment end and arithmetic begin? Decide and defend it.
10. **QA that earns its changes.** *Edited per entry 18:* the QA agent is one pre-lock pass, independent of the builder, that may file only cited missed-news challenges and lineup-coherence flags; code judges both; historical splits are computed by code in the priors module; pairwise leverage swaps are found by the deterministic local-improvement step.
11. **Measuring each layer.** Keep the baselines (projections before overrides, portfolio before QA) next to the final versions so post-contest analysis can score each layer.
12. **Learning without fooling ourselves.** *Added per entry 13:* calendar time and file count never certify a model; state the independent nights, news regimes, uncertainty interval and repeated-testing policy for every promotion; freeze challengers before their evaluation period; score actual submitted entries separately from hypothetical alternatives, and replace our historical entries rather than adding entries to the field; reproducing spike output proves regression consistency only. Simulation count controls numerical noise, not truth; synthetic tests establish speed and arithmetic only (entry 2).
13. **Early season.** Opening week brings new rosters, rookies, coaching changes, and little current-season data. How do priors work until the season's data catches up?
14. **Scoring edge cases.** Confirm from real DraftKings results whether a triple-double also earns the double-double bonus, and whether the Captain 1.5x applies to bonuses.
15. **Reproducibility.** Any night should be replayable: inputs, data snapshots, model versions, seeds, and LLM decisions stored as structured records.
16. **Operability.** A night should run from a few commands, explain errors in plain language, and produce a slate brief I can read in two minutes.

## The MVP and release states (replaced per ADJUDICATION entries 3 and 38)

Opening-night acceptance requires a complete, frozen workflow that I have rehearsed, including an initial confirmed upload, one late-news update, and recovery with Claude unavailable. Three release states, each a floor for the next:

* **Floor:** parsers, validator, exporter, contest facts, injury-scrubbed lineups ranked on simple projections under the concentration cap, no simulation. Rehearsed with a real upload on Thursday Oct 15, and at scale with the news and swap drills on Friday Oct 16.
* **Baseline:** adds the night simulation, a first field model, per-contest selection on Goal 1, the live late-news re-solve, the open-slot late swap, the manual news commands, and the one-page brief. Drilled on saved Oct 16 files over the weekend; first live run Monday Oct 19 evening with the Floor already uploaded.
* **Optimizer:** adds the insurance control, QA, the learning loop, the news watcher and the edge-uncertainty layer, after opening night.

A Floor launch defers the simulation-based selection; a Baseline launch defers the insurance control, QA and learning; each labels what is unavailable. Upload the Floor file early on opening night; replace it only after an improved file passes checks. An unrehearsed feature stays off. "Sensible" has a deterministic test: at least 95% of the cap used on average, no two identical lineups in one contest, the concentration cap honored or its relaxation reported, no lineup below the projection floor (default 85% of the slate's best single-lineup projection), and no player with a play probability under 0.5 unless I asked for him.

## Consult the advisor (ADJUDICATION entry 15)

I've set Fable as the advisor with `/advisor fable`. Consult it during architecture and adjudication work (before committing to a design sketch, after a critique, before delivery), in build sessions when a chunk is stuck and once before a chunk is declared done, and during the weekly post-contest model review. Give each consultation one named decision and one call; log it in `docs/research/advisor-log.md`. Do not call the advisor during nightly `/night`, `/news`, `/swap` or `/results` runs; nightly runs stay fast, deterministic, and within a single Pro session budget. The advisor is not independent empirical validation. If it is unavailable, continue through the deterministic path.

## How to run sessions (replaced per entries 26 and 36)

* Research ends when it resolves the named decision or reaches its time budget. No new research memos before opening night except a spike a build chunk needs to settle a contract.
* The build runs as chunks, one per fresh Claude Code session, from `docs/build/BUILD_PLAN.md`; the session protocol is in `CLAUDE.md`; progress lives in `docs/build/PROGRESS.md`.
* Every session records its Claude usage at the end. If the first four MVP chunks use more than about 40% of a weekly window, the Floor is the opening-night release: C05 to C09 move after Oct 20 and C10 and C11 are built in Floor mode only.
* Use subagents for verification and consistency checks to keep the main context lean.

## Deliverables

`docs/BRIEF.md` (this file), `docs/ARCHITECTURE.md`, `docs/adr/`, `docs/research/` (including `advisor-log.md`), `docs/review/ADJUDICATION.md`, `docs/build/` (plan, chunks, progress), `docs/reference/` (the four reference files), `spikes/` (throwaway verification scripts), `CLAUDE.md` (session protocol).

## How to write for me (verbatim)

Lead with the answer. Plain language; define jargon the first time. Every technical choice gets one sentence on what it means for results, cost, or my workload. Each section stands alone; no "see above". No em dashes. When you say something is verified, show what you ran and what came back. Separate what's verified, what's well supported, and what's a bet.
