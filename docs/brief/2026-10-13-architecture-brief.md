# NBA DFS Engine: Greenfield Architecture Brief (from the user, 2026-10-13)

Verbatim except the last three sections ("How to run this session", "Deliverables", "How to write for me"), which are condensed without changing their requirements.

I want you to design the architecture for a new DraftKings NBA DFS engine covering Classic and Showdown Captain Mode contests. The engine's job is to build a portfolio of entries for the contests I enter each night.
This session is design only. Don't write engine code. When the architecture is done, stop and wait for my approval before we start the build. Depth beats speed here, so take the time to think it through.

## Roles
You are the architect and the developer. I'm the business analyst and product manager, and I'm not a software engineer. I'll make product calls; you make technical calls and tell me in one sentence what each means for results, cost, or my nightly workload. If my requirements have a gap, push back the way a senior PM would.
Claude Code builds this engine and also runs it every night. At runtime, the LLM layer is you, working inside Claude Code sessions with subagents, skills, and commands. There's no separate paid model API.

## The two goals
These are fixed. Everything else in this brief is negotiable.

1. Within each contest, maximize the probability of a top-1% finish. For a single-entry contest, that's the probability our lineup finishes in the top 1%. For a multi-entry contest, it's the probability that at least one of our entries does. In fields under 100 entries, top 1% means first place.
2. Across the night's portfolio, minimize the probability of a total washout. A washout is zero cashing entries across every contest that night, Classic and Showdown combined.

The design must define both goals mathematically, say how each is estimated, show how they trade off, and give me one control for choosing where on that tradeoff to sit. Resolve three things inside those definitions:

* Goal 1 can't be computed without an estimate of each contest's top-1% score, and that depends on the slate and the field. Decide how to estimate it.
* A duplicated lineup that finishes top 1% still counts, but it splits the prize. Decide whether and how the objective penalizes duplication. Showdown makes this acute.
* My hunch is the two goals conflict less than they look, since both reward covering different ways the night can unfold. Test it.

## My vision: a starting hypothesis
Improve on this. Add, cut, reorder, or replace steps. Where you depart from it, tell me what changed and why in terms of the two goals.

1. I upload two CSVs from DraftKings: the salary file (players, position eligibility, teams, salaries, IDs) and my entries file (every contest entry I hold).
2. The engine projects fantasy points for every eligible player using the DAG in the attached blueprint: median, top-1% outcome, and boom/bust potential. It also projects ownership.
3. The LLM layer researches injury reports and removes players who won't play, overrides projections when roles change (an injury replacement getting more minutes and usage, for example), and assigns players to lineups using DFS strategy such as stacking.
4. An adversarial QA agent reviews the full portfolio. It looks for data-backed changes (a player who performs much worse on back-to-backs, for example) and for Pareto improvements that raise our top-1% odds or lower washout risk. Example: two near-identical players with different projected ownership, where moving to the lower-owned one gains leverage. QA runs at most three iterations.
5. Claude Code presents the DraftKings upload file.
6. After contests finish, I upload the standings and we work out whether we perform better in certain contest types or sizes, whether the projections need refinement, and whether the ownership model needs refinement.

## Context you already have from me
* Contest mix: single-entry, 3-max to 20-max, and 150-max GPPs. Showdown is a large share of volume.
* I can re-run and late swap close to tip most nights.
* Go-live: NBA opening night is Tuesday, October 20, 2026. Plan an opening-week MVP that ships valid, sensible portfolios. Simulation depth, the field model, and the learning loop can mature after that.

## Constraints
* Free only. Open-source software and free data. I won't pay for data or subscriptions. A free tier is fine if nightly use fits inside it. Flag any source whose terms prohibit what we'd do with it, and respect rate limits. My Claude plan is the only paid component.
* Correct files, every time. Deterministic code validates every lineup before it reaches the upload file: salary cap, roster slots, position eligibility, the right player ID for each slot, Classic's two-game minimum, Showdown's both-teams rule, and locked players. The engine never hands me an invalid file.
* Deadline beats perfection. If an advanced step fails near lock, ship a valid portfolio from what we have and tell me what was skipped.
* Scope. DraftKings NBA, Classic and Showdown Captain only. Don't build a multi-sport framework.
* I upload to DraftKings myself. Nothing automates actions on the DraftKings site.
* Runs on my machine. Measure what it can do. Set runtime budgets for the first full build and for a late-news re-run, which has to finish fast enough to act on news that breaks 30 minutes before tip.
* LLM work has a budget too. Size the research and QA steps so a full night, including late-swap re-runs, fits comfortably within Claude Code's usage limits.

## Resources
Attached files:
* `NBA Classic.txt` and `NBA Showdown Captain Mode.txt`: DraftKings rules and scoring. Treat them as the source of truth, then confirm against the live rules pages and real contest results.
* `NBA_DraftKings_DAG_Expanded.md`: a projection DAG and simulation blueprint. Start from it and critique it; it's a draft.
* `DFS_Platforms_Competitive_Edge_Report_2026-10-13.md`: how SaberSim, Stokastic, Ship It Nation, RotoGrinders, FantasyLabs, and FantasyCruncher create their edge. I want to emulate that secret sauce wherever it serves the two goals and can be done for free. Research these platforms beyond the report.

My prior engines (research only): https://github.com/bleeski/mlb-dfs, https://github.com/bleeski/nfl-dfs, https://github.com/bleeski/nhl-dfs, https://github.com/bleeski/soccer-dfs, https://github.com/bleeski/golf-dfs

I want this design to be greenfield, so read these only after you've drafted a first-principles design. Read them for lessons: what worked, what broke, what was painful to operate, which bugs recurred, and hard-won knowledge about DraftKings file formats, upload quirks, standings files, and late swap. Commit history, issues, and notes often say more than the code. Reuse nothing by default. If you recommend reusing a component or pattern, justify it in a decision record on its merits, the same as any other choice.

Your knowledge and the open web: use everything you have: training, web search, and creativity. Evaluate these leads on their merits:
* Research: Hunter, Vielma, and Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming" (arXiv 1604.01455), and Haugh and Singal, "How to Play Fantasy Sports Strategically (and Win)" (SSRN 3393127), which models opponents in top-heavy contests. Find newer work.
* Open-source DFS optimizers and contest simulators on GitHub and Hugging Face. pydfs-lineup-optimizer is one; look for NBA-specific simulators that generate opponent fields.
* Free NBA data: the official stats endpoints and the packages that wrap them, the NBA's official injury report, play-by-play and possession data, and free betting lines and player props. Verify each source works today from this machine, and record what it returns and how fresh it is.
* Free MILP and constraint solvers. I mentioned PuLP; choose on merits.

## Problems the design must solve
1. Late news. Statuses resolve close to tip, and staggered tip times split the slate. How does the build stay right as news lands? What's the re-run and late-swap path, how fast is it, and how do we construct lineups to keep swap flexibility for late games? How are questionable players handled before their status is known?
2. Minutes and usage. When a player sits, how are his minutes and usage redistributed across teammates, with uncertainty? This is where LLM role overrides meet the model, so define that interface precisely.
3. Correlation. NBA correlation differs from MLB and NFL. Teammates often compete for usage, while pace, game totals, and blowouts drive shared outcomes. How do we capture it, and how does it shape Classic versus Showdown construction?
4. Showdown. Captain selection, the both-teams rule, small player pools, heavy duplication, and separate Captain and UTIL ownership. As far as I know, DraftKings lists each player twice with separate IDs and salaries for Captain and UTIL; verify that and handle it.
5. Ownership without a paid feed. How do we project it, how fast does it react when news creates new chalk, and how do we bootstrap before we have our own history?
6. The field. Ownership says how often each player gets picked. It doesn't say how opponents combine players. Decide what field model goal 1 needs and how to build it.
7. Contest details. As far as I know, the entries file has entry IDs, contest names and IDs, and fees, but not field size or payout structure. Verify, and find a free way to get what's missing.
8. One night, one portfolio. Classic and Showdown entries share games, and washout is measured across the whole night. How do we measure washout risk and cross-contest correlation across the full night?
9. The LLM and solver boundary. Where does judgment end and arithmetic begin? For example, should the LLM pick players for lineups, or set theses, player pools, and constraints that the solver turns into lineups? Decide and defend it.
10. QA that earns its changes. The adversarial agent needs an evidence bar: sample size, effect size, and whether the projection already prices the effect in. Score its proposals against the two goals before accepting them; an argument alone isn't enough. Define what an iteration is, the stop rule, and how the QA agent stays independent of the agent that built the portfolio.
11. Measuring each layer. To learn, we need to know whether LLM overrides and QA changes helped. Keep the baselines (projections before overrides, portfolio before QA) next to the final versions so post-contest analysis can score each layer.
12. Learning without fooling ourselves. A few contests a night is mostly noise at the contest level. Every player's projection and ownership error is a lot of signal per night. Decide what we can learn fast and what only slowly, what statistical guardrails stop us chasing variance, and how a model change gets adopted (tested on held-out slates, versioned, signed off by me). Add analyses beyond my three if they serve the goals, such as field-model accuracy and the value of LLM overrides.
13. Early season. Opening week brings new rosters, rookies, coaching changes, and little current-season data. How do priors work until the season's data catches up?
14. Scoring edge cases. Confirm from real DraftKings results whether a triple-double also earns the double-double bonus, and whether the Captain 1.5x applies to bonuses. Don't assume either.
15. Reproducibility. With an LLM in the loop, any night should be replayable: inputs, data snapshots, model versions, seeds, and LLM decisions stored as structured records.
16. Operability. A night should run from a few commands, explain errors in plain language, and produce a slate brief I can read in two minutes: the thesis, key assumptions, exposures, risks, and what news would change the build.

## How to run this session
1. Read and ask. 2. Research (parallel subagents, findings memos with sources). 3. First-principles sketch (don't open my repos yet). 4. Repo review (revise the sketch and record what changed and why). 5. Red team (independent critic subagent attacks the design against the two goals, the free-only constraint, the late-news timeline, and operability by a non-engineer; revise; two rounds at most). 6. Deliver and stop.

## Deliverables
`docs/ARCHITECTURE.md` (sections: summary; goals as math; system overview; projections; ownership and field; lineups and portfolio; LLM layer; slate-night runbook; learning loop; data; testing; risks; build plan; decisions for me), `docs/adr/` (one short decision record per significant choice: context, options, choice, what it means for results, cost, or workload), `docs/research/` (research and repo-review memos with sources), `spikes/` (verification scripts, clearly marked as throwaway).

## How to write for me
Lead with the answer. Plain language; define jargon the first time. Every technical choice gets one sentence on what it means for results, cost, or my workload. Each section stands alone; no "see above". No em dashes. When you say something is verified, show what you ran and what came back. Separate what's verified, what's well supported, and what's a bet.
