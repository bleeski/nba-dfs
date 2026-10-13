# R2: Optimization methods, portfolio selection, open-source tools, and solvers

Research memo for the DraftKings NBA DFS engine (Classic and Showdown Captain Mode). Design only: no engine code.
Date: Tuesday Oct 13, 2026. Author: research subagent R2.

Evidence labels used on every claim:
**VERIFIED** (I ran it, or read it in the primary source; command, file, or section given),
**SUPPORTED** (credible source cited),
**BET** (my judgment, or not verified).

---

## 1. The answer, up front

1. **Both goals are the same kind of math problem, and one simulation answers both.** Simulate the whole night once (one shared set of joint player-outcome scenarios used by every contest, Classic and Showdown). In each scenario and contest, find the score needed for top 1% and the score needed to cash. Then "probability at least one of our entries is top 1%" is just the share of scenarios where at least one of our entries clears that line, and "probability of a total washout" is the share of scenarios where none of our entries in any contest clears its cash line. **BET** (design), built on **VERIFIED** pieces below.
2. **Pick entries with a greedy "maximum coverage" loop.** Repeatedly add the candidate lineup that covers the most scenarios not yet covered. This objective is "submodular" (adding a lineup helps less the more you already have), so greedy is provably at least 63% as good as the best possible set from the same candidate pool, and usually much closer. Hunter, Vielma, Zaman prove exactly this property for "P(at least one entry wins)". **VERIFIED** (arXiv 1604.01455 Sec 2, Lemma 1, Thm 2.2). Haugh and Singal prove it for expected payout in top-heavy contests. **VERIFIED** (Management Science 67(1), Sec 5.1, Thm 1).
3. **Control washout with one dial.** Optimize the per-contest top-1% coverage plus a weight times "night-wide cash coverage", and raise the weight until the simulated washout probability is below a target the user picks (for example 5%). This keeps greedy's guarantee because a weighted sum of coverage functions is still a coverage-type (submodular) function. **BET** (design); submodular sums are a standard result, **SUPPORTED** (Nemhauser, Wolsey, Fisher 1978).
4. **Duplication does not lower the probability of a top-1% finish; it lowers what that finish pays.** A lineup tied with field copies still ranks in the top 1%; the prize is split. So duplication belongs in a payout-weighted tie-breaker, not in the probability itself. How much weight to give it is a user decision (see Open questions). **BET** (reasoning from the stated rules); tie splitting as modeled by Haugh and Singal is **VERIFIED** (MS e-companion EC.1.4.2).
5. **Formulation matters more than the solver.** On a synthetic 120-player Classic slate, modeling each player as one yes/no variable plus "Hall's theorem" position rows was 5x (HiGHS) to 25x (GLPK) faster than the common "player-in-slot" model, with identical optimal lineups. **VERIFIED** (spike, Section 7.3).
6. **Showdown does not need a solver.** All 440,121 legal lineups of a 22-player Showdown pool can be listed in 0.015 seconds, and the best one matches the solver's optimum exactly. **VERIFIED** (`spikes/solvers/enumerate_showdown_spike.py`, output in `spikes/solvers/out/20261013-1700_enumerate_showdown.json`).
7. **Solver recommendation: OR-Tools (in-process CBC for Classic, CP-SAT available for complex rules), HiGHS as fallback, single-threaded, version-pinned, with a deterministic tie-break.** All five free solvers found identical optimal values on thousands of solves; the differences were speed, licensing and repeatability. GLPK was the fastest by far on independent solves (6x to 16x faster than CBC) but is GPL-3.0 and unchanged since 2020. PuLP 2.4 (what pydfs uses) pays 35 to 50 ms of file-and-process overhead on every solve. CP-SAT with 8 threads was not repeatable. **VERIFIED** (measurements, Section 7.4); the pick itself is **BET** (Section 7.5).
8. **No open-source tool computes either of our goal metrics.** pydfs-lineup-optimizer (MIT) is a useful reference for rules and late swap but is frozen since Sept 2021 and pins PuLP 2.4 (which ships a 2015 build of CBC). chanzer0/NBA-DFS-Tools has the most complete NBA field and contest simulator but has no license (learn only) and has scoring bugs that would distort top-1% estimates. **VERIFIED** (Section 6).
9. **The literature has no NBA portfolio study and nothing on cross-contest washout.** The best methods were validated on NHL, MLB (Hunter et al.) and NFL (Haugh and Singal), on small samples, and Haugh and Singal's model was optimistic versus realized results. **VERIFIED** (Section 5).

---

## 2. Terms used in this memo

- **Scenario:** one simulated version of tonight, with a fantasy score for every player. The engine draws thousands (S, for example 10,000).
- **Field:** the other entries in a contest. We cannot see them before lock, so we simulate them.
- **Top-1% line:** in a given scenario, the score of the opponent entry ranked at position k = ceil(1% of total entries). For contests under 100 entries, k = 1 (first place).
- **Cash line:** the same idea for the last paid rank.
- **Candidate pool:** a large set of legal lineups (thousands) that the selection step chooses from.
- **Portfolio:** the entries actually submitted, across all contests tonight.
- **MILP (mixed-integer linear program):** an optimization problem with yes/no variables (pick this player or not) and linear rules (salary cap). A **solver** finds the best answer.
- **Submodular:** "diminishing returns": the gain from adding a lineup can only shrink as the set grows. Greedy selection works well on such objectives.
- **Coverage function:** the share of scenarios in which at least one chosen item "hits". Coverage functions are submodular.
- **Overlap cap:** a rule that a new lineup shares at most K players with every lineup already chosen.
- **Deterministic:** the same inputs and seed give exactly the same output every run.

---

## 3. The math, in plain notation

### 3.1 Scenarios and scores
- Players i = 1..n. Scenarios s = 1..S. X[s, i] = simulated DK points for player i in scenario s.
- One X for the whole night. Classic and Showdown on the same game read the same X, so their correlation is real, not assumed away. A Showdown captain scores 1.5 x X[s, i].
- A lineup L scores score(L, s) = sum over its players of m_i x X[s, i], where m_i = 1.5 for a captain and 1 otherwise.

### 3.2 The top-1% line is exact if computed from the field alone
For contest c with total entries N_c, let k_c = ceil(0.01 x N_c) (k_c = 1 for N_c < 100). Let T1[c, s] = the k_c-th highest opponent score in scenario s.

Claim: at least one of our entries is in the top k_c if and only if our best entry scores at least T1[c, s].
Reason: only our best entry matters for "at least one". Its rank is 1 + (number of entries strictly above it), and none of our other entries can be above our best. So its rank is at most k_c exactly when at most k_c - 1 opponents beat it, which is exactly "score at least the k_c-th best opponent score". **VERIFIED** (derivation above). Ties at the line count as a top-1% finish but split the prize.

The same holds for the cash line Tc[c, s] (use the last paid rank instead of k_c).

Practical consequence: we only need, per contest and per scenario, two numbers (T1 and Tc). We never need to store the full field's scores. **VERIFIED** (the spike in Section 8.2 streams them).

### 3.3 Hit matrices
- h1[c, L, s] = 1 if score(L, s) >= T1[c, s], else 0.
- hc[c, L, s] = 1 if score(L, s) >= Tc[c, s], else 0.

### 3.4 Goal 1 (per contest)
For the set E_c of entries in contest c:

P1(E_c) = (1/S) x (number of scenarios s where some L in E_c has h1[c, L, s] = 1).

This is a coverage function, so it is monotone submodular. **VERIFIED** (Hunter et al. Lemma 1 proves this for any "at least one entry wins" event).

### 3.5 Goal 2 (whole night)
For the whole portfolio E = all E_c:

W(E) = (1/S) x (number of scenarios s where no L in any E_c has hc[c, L, s] = 1).

1 - W(E) is a coverage function over (contest, lineup) pairs, so it is also monotone submodular. **BET** (follows from the same argument; not stated in any paper I found).

### 3.6 Combining the goals
Two equivalent ways to state it:

- **Constrained:** maximize sum over c of w_c x P1(E_c), subject to W(E) <= epsilon and |E_c| <= max entries for c.
- **Weighted (what to build):** maximize F(E) = sum over c of w_c x P1(E_c) + lambda x (1 - W(E)). Raise lambda in small steps (or bisect) until W(E) <= epsilon.

w_c is how much the user values a top-1% finish in contest c (for example its top-1% prize pool, or 1 for all contests if every contest counts the same). lambda is the washout dial.

F is a positive sum of coverage functions, so it is monotone submodular. Greedy works as follows: at each step, add the single (contest, lineup) pair with the largest gain in F, among contests that still have open entries. Under per-contest entry limits (a "partition matroid"), plain greedy is guaranteed at least 1/2 of the best possible; within one contest (a plain count limit) it is at least 1 - 1/e, about 63%. **SUPPORTED** (Nemhauser, Wolsey, Fisher 1978; Fisher, Nemhauser, Wolsey 1978). "Lazy greedy" (Minoux 1978) gives the same answer much faster by re-checking only the candidates whose stale gain could still be the best. **SUPPORTED**.

Why one shared scenario set is required: if Classic and Showdown were simulated separately, washout would look much rarer than it is, because a bad night for the core players hurts every contest at once. **BET** (direction is certain; size unknown until the simulator exists).

### 3.7 Where duplication enters
- For goal 1 as written, a duplicated lineup that clears T1 still counts. Duplication does not change P1. **BET** (reading of the stated goal).
- Duplication does change money. If a lineup L has d[c, L] expected copies in the field, a top-1% finish pays roughly prize / (1 + d) for tied ranks. Haugh and Singal split tied payouts across adjacent ranks. **VERIFIED** (EC.1.4.2).
- Recommended handling: compute d[c, L] from the simulated field (count exact matches), and use it only as a tie-breaker or as a down-weight on the hit: h1'[c, L, s] = h1[c, L, s] / (1 + d[c, L]) if the user wants the probability weighted by payout share. The weighted version is still a coverage-type objective if applied as a per-lineup weight on the scenario hit, so greedy still applies. **BET**.
- Showdown has a much smaller lineup space (Section 7.4), so duplication is far more common there. **BET** (industry lore, plus the arithmetic of 440,000 legal lineups versus contests with hundreds of thousands of entries).

### 3.8 How the spike behaved (synthetic data, cost and shape only)
See Section 8.2 for numbers. In short, on synthetic data: greedy coverage beat "take the top-projected lineups" at every portfolio size (for example 48% versus 35% chance of at least one top-1% finish with 20 entries), adding cash coverage to the objective lowered the no-cash probability at a visible cost in top-1% probability on small portfolios (3 entries: 26% to 15% no-cash, 11.3% to 9.9% top-1%), and the whole selection step ran in seconds to a minute with under 1 GB of memory. **VERIFIED** (spike), but the absolute levels are meaningless because the field is synthetic.

---

## 4. Turning player simulations into a candidate pool, then a portfolio

### 4.1 Candidate pool (Classic)
Generate many lineups that each have a real chance of winning a plausible version of tonight:
1. **Scenario-optimal lineups:** for a sample of scenarios s, solve "maximize sum of X[s, i] over chosen players" under DK rules. Each answer is the best lineup in one plausible world. This is the direct analogue of "solve with perturbed projections". **BET** (design); the speed is measured in Section 7.
2. **Mean plus leverage:** maximize sum of (mean_i - alpha x ownership_i) for several alpha values. This is the practical form of Haugh and Singal's finding that low covariance with the field raises the top-heavy objective. **VERIFIED** (their mean-variance objective includes -2 x Cov(entry, field benchmark), MS Sec 4, 5); the ownership shortcut is **BET**.
3. **Overlap-capped sequences:** the Hunter et al. sequence (best lineup, then the best lineup sharing at most K players with every earlier one). Hunter et al. found the best K depends on slate size (more overlap allowed on small slates). **VERIFIED** (Sec 5.3).
4. **Structural variants:** game stacks and "bring-backs" (players from both teams in a high-total game), since NBA teammates compete for usage and positive correlation comes mostly from game environment. **BET**.
5. De-duplicate, then score every candidate against all scenarios.

Pool size: 5,000 to 20,000 unique Classic candidates per slate is a reasonable starting point. **BET**; the cost is measured in Section 7.

### 4.2 Candidate pool (Showdown)
Enumerate every legal lineup (Section 7.4), screen to the top tens of thousands by a cheap score (for example, mean plus a variance bonus, or hits in a small scenario subsample), then score the survivors against all scenarios. No solver is needed. **VERIFIED** (enumeration count and time); screening rule is **BET**.

### 4.3 Portfolio selection
1. Build the field for each contest (owned by another research track), and stream T1[c, s] and Tc[c, s].
2. Build hit matrices h1 and hc for every candidate. Store them as bits: 5,000 candidates x 10,000 scenarios is about 6 MB per contest. **VERIFIED** (spike, Section 8.2).
3. Run the weighted greedy of Section 3.6 with lazy evaluation across all contests at once, sweeping lambda until W(E) <= epsilon.
4. Apply hard rules last (max exposure per player, late-swap flexibility) as filters on which candidates are eligible at each greedy step. **BET**.

---

## 5. Literature

### 5.1 Hunter, Vielma, Zaman, "Picking Winners in Daily Fantasy Sports Using Integer Programming"
arXiv 1604.01455, v1 April 2016 (titled "Winning Daily Fantasy Sports Hockey Contests Using Integer Programming"), v3 January 2019, marked as submitted to INFORMS Journal on Optimization. I found no published journal version. **VERIFIED** (v3 header; Crossref search by the literature subagent), "no published version" is **BET**.

What matters for us:
- **The objective is ours.** They pick k entries to maximize P(at least one entry wins), prove it is NP-hard (Thm 2.1, "very hard to solve exactly") and monotone submodular (Lemma 1), so greedy gets at least 1 - 1/e of optimal (Thm 2.2). **VERIFIED** (Sec 2).
- **But they then optimize a stand-in.** "Win" means beating a fixed score threshold, not a field-dependent line. Their integer program maximizes mean projection with stacking rules and an overlap cap, solved k times in sequence, and they note the 1 - 1/e guarantee does not carry over to that stand-in. **VERIFIED** (Sec 2.2, 2.4, Eq 4.8).
- **Pairwise approximation is not usable at our scale.** Their approximation error bound is 20c(kp)^3; with 150 entries at about 1% each, kp is about 1.5 and the bound is useless. **VERIFIED** (Thm 2.4), consequence is **BET**.
- **Three rules of thumb:** high mean, high variance (from correlated players in the lineup), low correlation between our lineups (less overlap). **VERIFIED** (Sec 2.3).
- **Results.** NHL: 38 DraftKings top-heavy contests (Oct to Dec 2015), 200 lineups each. MLB: 10 contests (May to June 2016). Best MLB lineups ranked 1, 2, 3, 7 in four contests. About $15,000 in real winnings. More stacking beat no stacking at 100 and 200 lineups. With 1 lineup the median profit margin was -100% (lost the entry), and adding lineups moved the whole distribution up. **VERIFIED** (Sec 5, Table 4, Figs 4, 5).
- **Breadth wins:** the eventual best lineup was usually built late in the sequence (median build rank 124.5 of 200; rank correlation 0.09). **VERIFIED** (Sec 5.4). Meaning for us: the top-projected lineup is not special; the portfolio is.
- **Overlap by slate size:** overlap 7 (of 9) best on nights with under 4 games; overlap 4 best on nights with over 9 games. **VERIFIED** (Sec 5.3).
- **Not modeled:** opponents, duplication, prize splitting, NBA. **VERIFIED**.
- **Transfer to NBA:** the submodular selection and overlap-by-slate-size findings transfer. Hockey line stacks do not; NBA correlation is mostly game-level. **BET**.
- Code: github.com/zlisto/Daily-Fantasy-Baseball-Contests-in-DraftKings (Julia, GLPK, MLB, no license file, last commit 2018). **VERIFIED** (gh api).

### 5.2 Haugh and Singal, "How to Play Fantasy Sports Strategically (and Win)"
Management Science 67(1):72-92, January 2021, DOI 10.1287/mnsc.2019.3528 (online May 2020); SSRN 3393127 (2019); an earlier MIT Sloan SSAC 2018 version. **VERIFIED** (Crossref, accepted manuscript at Imperial Spiral). No arXiv version. **VERIFIED**.

What matters for us:
- **The benchmark is the field.** They define the winning line as the r-th best opponent score, which is random because both player outcomes and opponent lineups are unknown. Top-heavy contests maximize expected payout summed over prize tiers. **VERIFIED** (Sec 2). This is the same object as T1 in Section 3.2.
- **Opponent model:** for each roster position, a Dirichlet-multinomial distribution (a probability distribution over "which player the field picks", whose own probabilities are uncertain), with parameters driven by a public ownership estimate, salary and projection, fit by Bayesian regression. Positions are joined with a stacking model (share of stacked QB-WR entries 0.35 in top-heavy contests), and generated lineups must use at least 99% of the salary cap. **VERIFIED** (Sec 3, EC.1.1).
- **Shortcut for big fields:** draw the r-th best opponent score directly from its distribution rather than simulating every opponent. **VERIFIED** (EC.1.2). Useful for our memory budget.
- **Single entry:** mean-variance optimization against the stochastic benchmark; when an entry is unlikely to win on average (top-heavy), maximize mean plus lambda times variance, where variance includes -2 x Cov(entry, benchmark). Low correlation with the field is rewarded: this is the formal source of "leverage". **VERIFIED** (Sec 4, 5); the "leverage" reading is **BET**.
- **Multi-entry:** greedy, justified because the top-heavy objective is submodular when the payout curve is convex. Without an overlap rule, greedy gave only about 10 unique lineups out of 50. With overlap at most 6 of 9, expected reward almost doubled. Expected profit was flat across overlap 5, 6, 7. **VERIFIED** (Sec 5.1, EC.3.2).
- **Duplication:** ties split adjacent payouts. In all 17 weeks, nobody in the field had entered the after-the-fact best lineup, which favors diversifying over copying. **VERIFIED** (EC.1.4.2, EC.2.3).
- **Double-ups (50/50 style):** for a risk-neutral player, many copies of one lineup is optimal or near-optimal; a risk-averse player should diversify. **VERIFIED** (Sec 4.2.3, EC.1.3.2). Meaning for goal 2: copying in cash games raises washout risk. **BET**.
- **Results:** FanDuel NFL 2017, 17 weeks. Top-heavy: +$280.74 versus +$91.50 for their benchmark strategy, on $850 of fees (about 33% return on fees). Quintuple-up and double-up ended slightly negative. Realized results were below the model's expectations in every contest type. **VERIFIED** (Table EC.1, Fig 4).
- **Value of opponent modeling:** most of the gain came from simply using ownership estimates; modeling ownership uncertainty added about another 10%. **VERIFIED** (Sec 7.1).
- **Copying hurts:** in one week, 50 diversified entries had expected profit 578.6 versus 123.9 for 50 copies of one entry. **VERIFIED** (Sec 7.3).

### 5.3 Newer work (2019 to 2026)
- **Bergman, Cardonha, Imbrogno, Lozano (2023),** INFORMS Journal on Computing 35(2):304-317, arXiv 2112.07002. The only academic Showdown paper found (DraftKings NFL Showdown 2018). Models captain as a 1.5x copy of each player, maximizes E[max of two entries' scores] with a cutting-plane method, no field model. Backtest profit $5,376 on $9,674 of fees in 16 small contests (69 to 1,189 entries), versus a loss for "best lineup plus one variation". **VERIFIED** (Sec 6.1, App A.3).
- **Decary, Bergman, Cardonha, Imbrogno, Lodi (2024),** arXiv 2407.13438: maximizing the best-of-many score for March Madness brackets; exact methods blow up with entry count, heuristics win. **SUPPORTED** (abstract).
- **Liu, Liu, Teo (2023),** Production and Operations Management 32(9):2864-2884: choosing a small diversified set to maximize the chance one is optimal (robust optimization). **SUPPORTED** (abstract); DFS experiments unconfirmed.
- **Mlcoch and Hubacek (2024),** International Transactions in Operational Research 31(3):1515-1532: generative models for player-score distributions plus a quadratic program for top-heavy payouts; reported over 34% return over 8 weeks. **SUPPORTED** (abstract; sport not confirmed).
- **Mbeledogu (MIT SSAC 2026):** robust single-lineup optimization for NFL 50/50s; raised the worst-case score but cash rates against real cash lines were mixed. **VERIFIED** (Tables 1 to 3). Relevant only as a warning that "safe" single lineups do not reliably cash.
- **NBA-specific work** is all projections or single lineups: Papageorgiou, Sarlis, Tjortjis (2024, IJDSA); Dopke, Kohler, Tegtmeier (2024, J. Economics and Finance), who found commercial NBA projections inefficient and only modestly better than naive ones; an MS thesis (Cal Poly 2019). **SUPPORTED** (abstracts).
- **Classic results we rely on:** greedy for submodular maximization (Nemhauser, Wolsey, Fisher 1978; Fisher, Nemhauser, Wolsey 1978), lazy greedy (Minoux 1978), office-pool strategy (Kaplan and Garstka 2001, Clair and Letscher 2007). **SUPPORTED**.
- **Gaps:** no NBA portfolio study, one small NFL Showdown study, no academic DraftKings ownership model, nothing on late swap, nothing on washout across contests. **VERIFIED** (literature search by subagent across arXiv, SSRN, Crossref, OpenAlex, Semantic Scholar citation lists).

---

## 6. Open-source tools

All metadata below was read with `gh api repos/<owner>/<repo>` and PyPI JSON on Oct 13, 2026. **VERIFIED** unless marked.

| Tool | License | Last commit | NBA Classic / Showdown | Use it for |
|---|---|---|---|---|
| DimaKudosh/pydfs-lineup-optimizer | MIT | 2021-09-27 (PyPI 3.6.1, same day) | Yes / Yes | Rules reference, late-swap flow, stack and exposure rule ideas. Do not depend on it. |
| chanzer0/NBA-DFS-Tools | none (all rights reserved) | 2024-11-13 | Yes / Yes, plus GPP and Showdown simulators | Learn how a field and contest simulator is wired; do not copy code. |
| JonnyRank/nba-dfs-optimizer | MIT | 2026-09-22 | Yes / No | Clean slot-variable PuLP + HiGHS model with a correct min-games rule; pytest suite. |
| SamBamCH/ivan | none | 2026-01-02 | Yes / partial | Correct tie-group payout splitting; contest-conditioned field model idea. Code looks broken as committed. |
| BenBrostoff/draftfast | none | 2024-01-29 | Yes / Yes | Avoid: pins numpy 1.26.2 and ortools 9.8, not installable on Python 3.13. |
| sansbacon/pangadfs | MIT | 2026-08-12 | NFL-centric | Genetic-algorithm alternative with a field-ownership penalty. |
| dfs-with-r/coach | GPL-3.0 | n/a | R, has DK NBA | Learn only (GPL). |
| zlisto/Daily-Fantasy-Baseball-Contests-in-DraftKings | none | 2018-12-04 | MLB only | Official Hunter et al. code; overlap constraint reference. |
| garethmarkel/mlb_dfs_optimizer | none | 2024-12-31 | MLB, Julia + Gurobi | Only public Haugh-Singal style implementation found (needs a commercial solver as written). |

Details that matter:
- **pydfs-lineup-optimizer.** `setup.py` pins `PuLP==2.4`; CI covers Python 3.6 to 3.9 only. **VERIFIED**. In our venv, PuLP 2.4 ships `cbc.exe` reporting "Version: 2.9.0, Build Date: Feb 12 2015". **VERIFIED** (ran `cbc.exe` with `quit`). It handles multi-position players with aggregated "at least k players eligible for this position set" rows (no slot variables) and assigns slots afterward by trying permutations, ordering by game start time (good for late swap). **VERIFIED** (`rules.py` PositionsRule, `utils.py` get_positions_for_optimizer, link_players_with_positions). Its randomness is independent per-player uniform noise of up to 12%, with no correlation. **VERIFIED** (`fantasy_points_strategy.py`, per OSS subagent). Its Showdown unique-player rule groups by full name, not player ID. **VERIFIED** (code), risk is **BET**. Open issue #248 "DK NBA Lateswap breaks for some entries" since 2021. **VERIFIED**. Every lineup copies the whole PuLP problem and launches `cbc.exe` again (`lineup_optimizer.py` optimize loop). **VERIFIED**.
- **chanzer0/NBA-DFS-Tools field generation.** Fills slots in order PG, SG, SF, PF, C, G, F, UTIL, each drawn in proportion to projected ownership among eligible unused players under remaining salary, then rejects lineups outside the salary range, below a projection floor (85% of optimal in the sample config), or from one game. **VERIFIED** (`NBA_GPP_Simulator.generate_lineups`). Player outcomes come from one multivariate normal per game with hard-coded position correlations (for example same-position teammates slightly negative); games are independent; points are not floored at zero. **VERIFIED** (`run_simulation_for_game`, `load_projections`). Showdown captain = 1.5 x the UTIL draw. **VERIFIED**.
- **chanzer0 bugs that matter for top-1%:** scores are cast to `float16`, which near 300 points only resolves to about 0.25 points, creating false ties. Top-1% and cash counts are computed over unique lineups, ignoring duplicate counts. Lineups that tie are ordered arbitrarily, not split. **VERIFIED** (`run_tournament_simulation`); the 0.25 resolution is **SUPPORTED** (IEEE half precision has 11 significant bits, so spacing is 0.25 between 256 and 512).
- **Nothing open computes P(at least one top-1%) or night-wide washout.** chanzer0 reduces each lineup to marginal counters, so joint "any of our entries" events cannot be recovered. **VERIFIED**.
- **Safety note:** the JonnyRank repo ships `CLAUDE.md`, `AGENTS.md`, `.claude/skills/*` and a `.claude/settings.json` SessionStart hook that runs `pip install -e`. It should never be opened as a Claude Code project. **VERIFIED** (file listing by OSS subagent; nothing was executed).
- **Hugging Face:** no DFS salary, contest, or ownership datasets found. Box-score datasets exist (for example `cbratkovics/nba-game-logs`, labeled CC0, which drops did-not-play rows; `cdechoch/nba-data-archive`, labeled Apache-2.0). Whether those labels hold for NBA.com-derived data is **BET**. Listing is **VERIFIED** (HF API search).

---

## 7. Solvers

### 7.1 What the candidates are
| | HiGHS | CBC via PuLP 2.4 | CBC via OR-Tools | CP-SAT (OR-Tools) | SCIP | GLPK |
|---|---|---|---|---|---|---|
| Python package tested | highspy 1.15.1 (July 2026) | pulp 2.4 (Dec 2020) with bundled cbc.exe 2.9.0 (built Feb 2015) | ortools 9.15 (Jan 2026), `pywraplp` | ortools 9.15, `cp_model` | PySCIPOpt 6.3.0 (Oct 11, 2026) bundling SCIP 10.0 | swiglpk 5.0.13 (Feb 2026) bundling GLPK 5.0 (Dec 2020) |
| License | MIT | PuLP MIT; CBC EPL (1.0 in this bundle) | Apache-2.0; CBC EPL-2.0 | Apache-2.0 | PySCIPOpt MIT; SCIP Apache-2.0 since 8.0.3 | GPL-3.0 (copyleft) |
| Windows wheel, Python 3.13 | Yes | Yes (pure Python + exe) | Yes | Yes | Yes (46 MB, includes SCIP) | Yes |
| How the solver is called | In-process | New file + new `cbc.exe` process for every solve | In-process | In-process | In-process | In-process |
| API ergonomics | Low-level arrays or a newer modeling layer; fine | Easiest to read | Verbose but simple | Clean; whole-number coefficients only | Pythonic; must call `freeTransform()` before every change | Raw C calls, 1-indexed arrays; awkward |
| Change model between solves | Yes, in place (`addRow`, `changeColsCost`) | Python-side edits; full re-solve in a new process | Python-side edits; re-sent to CBC each solve | Python-side edits; each solve starts from scratch | Yes after `freeTransform()` | Yes, in place |
| Warm start | `setSolution` (did not help in a spot test) | `.mst` file | hints | hints | solutions and a "reoptimization" mode (not tested) | not tested |
| Seeds and determinism | `random_seed`; repeat runs identical | randomCbcSeed; repeat runs identical | repeat runs identical | `random_seed`; identical with 1 worker; **not** identical with 8 workers | `randomseedshift`; repeat runs identical | no seed needed; identical |
| Threads | `threads` option; the MIP log reports "Parallel search off" | `threads` | `SetNumThreads` | `num_workers` (default all cores) | single thread | single thread |
| Maintenance | Active | PuLP active (4.0.0 Sept 2026 has breaking changes and makes CBC an optional extra); the 2.4 pin is frozen | Active (Google) | Active (Google) | Active | GLPK itself unchanged since 5.0 (2020) |

Sources: PyPI JSON for each package (version, date, license, wheel list), **VERIFIED** (`curl https://pypi.org/pypi/<pkg>/json`, Oct 13, 2026); `cbc.exe` version, **VERIFIED** (ran it); bundled license files, **VERIFIED** (read in `site-packages`); SCIP license history, **SUPPORTED** (scipopt.org); HiGHS options, **SUPPORTED** (HiGHS options reference); CP-SAT `interleave_search` "deterministic (independently of num_workers!)", **SUPPORTED** (sat_parameters.proto); determinism results, **VERIFIED** (Section 7.4).

### 7.2 Benchmark design
All numbers are **INDICATIVE, not final**: other agents were running on this laptop (Intel Core Ultra 7 258V, 8 cores, 32 GB RAM, about 6 GB free during the runs). CPU load from other work, sampled before each run, ranged from about 5% to 60% and is recorded per run in the raw file.

- **Synthetic Classic pool:** 120 players, 12 teams, 6 games. Salaries $3,000 to $11,500 in $100 steps; positions PG, SG, SF, PF, C plus dual eligibility PG/SG, SG/SF, SF/PF, PF/C; projections 2.3 to 62.8 points, rounded to 0.01; standard deviation 0.30 x projection + 1.5. A 12-game, 240-player version was also used. **VERIFIED** (`make_classic_pool` in `bench_solvers.py`).
- **Synthetic Showdown pool:** 22 players, 2 teams, UTIL salary $1,000 to $12,000; each player has a CPT row (1.5x salary, 1.5x points) and a UTIL row; at most one of the two per player; both teams required. **VERIFIED** (`make_showdown_pool`, `build_showdown`).
- **Two Classic formulations:**
  - "slot": one yes/no variable per (player, eligible slot), 415 variables. This is what most open-source NBA optimizers do.
  - "hall": one yes/no variable per player (120 variables), exactly 8 chosen, plus 31 rows from Hall's marriage theorem: for every group of non-UTIL slots, enough chosen players must be eligible for at least one slot in the group. This guarantees a valid slot assignment exists, and the slots are assigned afterward by a matching routine. **VERIFIED** (`hall_rows`, `assign_slots`).
- **Same model for every solver:** each solver receives the identical generic list of variables and rows, so differences are the solver's, not the model's. Every lineup is re-validated by solver-independent code, and the objective is recomputed. **VERIFIED**.
- **Tasks:**
  1. one max-projection lineup;
  2. 150 lineups in sequence, each sharing at most 6 players (Classic) or 4 players (Showdown, counted by player, ignoring CPT/UTIL role) with every earlier lineup (this also rules out exact repeats);
  3. N independent solves, each with every player's projection perturbed by a seeded normal draw (projection + sd x z, floored at 0); N = 500 for all solvers, 5,000 for the faster ones.
- **Settings:** relative MIP gap 0 (prove optimal) for every solver so results can be compared; single thread unless stated; fixed seed 7. CP-SAT needs whole-number coefficients, so projections are multiplied by 100 (exact because they are rounded to 0.01).
- **Solvers:** `highs` (highspy 1.15.1, one live model changed in place), `highs_tuned` (same, with sub-MIP heuristics off), `highs_rebuild` (new model each solve, Showdown only), `pulp_cbc` (PuLP 2.4 + its bundled CBC 2.9.0, new subprocess each solve, the pydfs path), `ortools_cbc` (CBC inside OR-Tools 9.15 pywraplp, in-process), `cpsat` (CP-SAT, 1 worker), `cpsat_mt` (CP-SAT, 8 workers), `scip` (PySCIPOpt 6.3.0 / SCIP 10.0), `glpk` (swiglpk 5.0.13 / GLPK 5.0).
- **Memory:** Windows peak working set of the benchmark process, plus a 20 ms sampler that adds up child processes (catches `cbc.exe` and worker processes).
- **Determinism:** most configurations were run twice with the same seed, comparing a hash of the ordered lineup list.

### 7.3 Formulation result
Time for the first 20 lineups of the overlap sequence on the 120-player Classic slate, "slot" model versus "hall" model (seconds, single thread):

| Solver | slot model | hall model | Speed-up |
|---|---|---|---|
| HiGHS | 95.4 | 18.5 | 5.2x |
| GLPK | 20.0 | 0.82 | 24.5x |
| CP-SAT | 68.3 | 3.5 | 19x |
| CBC (OR-Tools) | 30.5 | 4.5 | 6.8x |
| SCIP | 81.8 | 5.7 | 14x |
| CBC (PuLP 2.4) | 27.9 | 6.2 | 4.5x |

- All 12 runs produced the same 20 optimal objective values (sum 6,154.75), so the faster model loses nothing. **VERIFIED** (`spikes/solvers/out/20261013-1656_bench_raw.jsonl`, phase A; summary in `20261013-1656_bench_summary.txt`).
- Why: in the slot model the same 8 players can be arranged across PG/SG/G/UTIL (and so on) in many equivalent ways, and the solver wastes effort proving that each arrangement is no better. The player-only model removes that symmetry. **BET** (standard explanation; consistent with the solver logs).
- The hall model is exact, not a shortcut: by Hall's marriage theorem, a valid slot assignment exists if and only if every group of slots has at least as many eligible chosen players as slots in the group. UTIL accepts anyone, so only the 127 groups of the other 7 slots matter, and after removing duplicates and dominated rows 31 rows remain. Every lineup was then assigned to slots by a matching routine and re-checked; zero failures. **VERIFIED** (`hall_rows`, `assign_slots`, `validate`; `n_problems` = 0 in every run).
- pydfs-lineup-optimizer uses a similar aggregated-count idea, but builds its position groups from the multi-position combinations present in the pool rather than from all slot groups. Whether that is always exact was not tested. **VERIFIED** (code read), exactness **BET**.

### 7.4 Results
Raw data: `spikes/solvers/out/20261013-1656_bench_raw.jsonl` (phases A to E) and `spikes/solvers/out/20261013-1834_bench_F_raw.jsonl` (phase F, rerun with a trimmed list after the first run was stopped; the first run's one completed phase F item, GLPK 150 lineups on 240 players in 63.9 s, agrees with the rerun's 61.6 s); tables: the matching `_summary.txt` files. Everything below is **VERIFIED** (measured) and **INDICATIVE** (shared machine).

**Classic, 120 players, hall model.** Times in seconds unless marked ms (milliseconds). "Median solve" is for the perturbed-projection task.

| Solver | 1 lineup (ms) | 150 overlap lineups | Median solve (ms) | 5,000 perturbed, 1 process | 5,000 perturbed, 4 processes | Peak memory per process |
|---|---|---|---|---|---|---|
| GLPK | 3.5 | 30.8 | 2.2 | 21.8 | 7.6 | 43 MB |
| CBC (OR-Tools) | 39 | 74.4 | 23.5 | 131 | 37.7 | 63 MB |
| SCIP | 52 | 229 | 26.7 | 286 | not run | 124 MB |
| CP-SAT, 1 worker | 36 | 68.8 | 42 | 267 | 78.7 | 105 MB |
| CP-SAT, 8 workers | 54 | 75.1 | 49 | not run | not run | 134 MB |
| HiGHS, tuned | 99 | 227 | 47 | 403 | 124 | 93 MB |
| HiGHS, default | 132 | 369 | 66 | about 430 (extrapolated from 500 in 42.6) | not run | 84 MB |
| CBC (PuLP 2.4) | 119 | 108 | 76 | about 480 (extrapolated from 500 in 47.9) | not run | 51 MB + 21 MB for cbc.exe |

**Showdown, 22 players.**

| Solver | 1 lineup (ms) | 150 overlap lineups | Median solve (ms) | 5,000 perturbed, 1 process |
|---|---|---|---|---|
| Enumeration (no solver) | 15 for all 440,121 lineups | 1.3 | not needed | not needed |
| GLPK | 1.0 | 9.5 | 0.23 | 4.5 |
| CP-SAT, 1 worker | 23 | 16.9 | 7.5 | 64 |
| CP-SAT, 8 workers | 38 | 11.8 | 21 | not run |
| CBC (OR-Tools) | 25 | 55.1 | 8.7 | 70.5 |
| SCIP | 31 | 57.6 | 3.7 | not run |
| HiGHS, tuned | 37 | 50.6 | 20 | 116 |
| HiGHS, default | 74 | 159 | 28 | not run |
| CBC (PuLP 2.4) | 44 | 82.9 | 43 | not run |

What the numbers say:
1. **Every solver found the same optimal value on every one of the thousands of solves** (maximum difference 0.0000 against GLPK, solve by solve). **VERIFIED** (cross-solver section of the summary file).
2. **But they often returned different lineups with that same value.** Ties are common with 2-decimal projections, and each solver breaks them its own way. Switching solvers (or possibly upgrading one) silently changes the lineups. **VERIFIED** (`identical_lineups=False` while `max_abs_diff=0.0000`).
3. **Single-thread runs were repeatable for every solver.** CP-SAT with 8 workers was not: 3 of 4 repeat checks produced different lineup lists. **VERIFIED** (determinism section of the summary file).
4. **Splitting work across processes did not change results.** The 4-process runs returned exactly the same lineup lists as the 1-process runs for GLPK, CBC, CP-SAT and HiGHS, because each draw is seeded by its own index. **VERIFIED** (identical hashes).
5. **PuLP's file-and-process round trip costs about 35 to 50 ms per solve** (PuLP CBC versus in-process CBC: 76 versus 23.5 ms Classic, 43 versus 8.7 ms Showdown). That is the pydfs-lineup-optimizer path. **VERIFIED**.
6. **Sequences with many overlap rules get slower every step**, because each "share at most K players" rule weakens what the solver can prove quickly. HiGHS took 0.13 s for the first Classic lineup but a median of 2.6 s per lineup (maximum 4.5 s) across the 150-lineup sequence. **VERIFIED**. This is another reason to generate candidates by independent perturbed solves (no accumulating rules) and handle diversity in the selection step.
7. **Perturbation gives diversity cheaply on Classic, less so on Showdown.** 5,000 perturbed Classic solves produced 5,000 different lineups; 5,000 Showdown solves produced only about 1,150. **VERIFIED**. For Showdown, enumeration covers everything anyway.
8. **Showdown overlap rules bite hard.** With at most 4 shared players, the 150th Showdown lineup projected 228.2 versus 267.0 for the best, a 15% drop. **VERIFIED**. Real Showdown portfolios will need looser overlap or none (let the coverage objective decide). **BET**.
9. **Enumeration reproduced the solvers' 150-lineup Showdown sequence exactly** (same objective sum, 36,226.67) in 1.3 s, versus 9.5 s for the fastest solver and 159 s for the slowest. **VERIFIED** (`spikes/solvers/out/20261013-1835_enumerate_showdown_seq150.json`).
10. **Memory is a non-issue for solvers:** under 135 MB per process for all of them. **VERIFIED**.

**Bigger Classic slate (12 games, 240 players), phase F.**

| Solver | 150 overlap lineups | Median solve, perturbed (ms) | 500 perturbed solves |
|---|---|---|---|
| GLPK | 61.6 | 4.9 | 4.5 |
| CBC (OR-Tools) | 94.4 | 36.8 | 17.8 |
| CP-SAT, 1 worker | 87.4 | 65.1 | 37.1 |
| SCIP | not run | 65.7 | 56.4 |
| HiGHS, tuned | not run | 79.7 | 60.4 |

Doubling the pool size raised per-solve time by roughly 1.4x to 2.2x, with the same solver ranking and the same agreement on optimal values. Extrapolating, 5,000 candidates on a 240-player slate would take about 3 minutes on one process with CBC, or under a minute on four. **VERIFIED** (measured), extrapolation **BET**.

### 7.5 Recommendation
**Recommendation: OR-Tools as the one solver dependency, using its in-process CBC backend for the Classic lineup model, with HiGHS as the tested fallback and cross-check. No solver for Showdown (enumerate). Do not use PuLP 2.4 or pydfs-lineup-optimizer.** **BET** (judgment), resting on the **VERIFIED** measurements above.

Why:
- **Fast enough by a wide margin.** CBC through OR-Tools made 5,000 Classic candidates in 131 s on one process, or 38 s on four. Meaning for the user: solver time is about a minute of the nightly run; the simulator, not the solver, will set the schedule.
- **Repeatable.** Single-thread CBC gave identical lineups on every repeat, and splitting across processes did not change results. Meaning: re-running a night reproduces it exactly, which makes bugs findable.
- **Permissive license, maintained, Windows wheels for Python 3.13.** Apache-2.0 (OR-Tools) and EPL-2.0 (CBC). Meaning: no licensing constraint on how the engine is used later.
- **One package, two engines.** The same install gives CP-SAT, which handles "if this player then that player" style rules naturally, should stacking or exposure rules get complicated. Meaning: no second dependency if the rule set grows.
- **HiGHS as fallback.** It is MIT, very active, and has the cleanest in-place model editing. It was the slowest in-process solver here (on the 5,000 Classic run, about 1.5x slower than CP-SAT and 3x slower than CBC), which matters little at these sizes. Meaning: if a future OR-Tools release drops CBC (a risk, not a known plan; **BET**), switching costs one adapter.
- **GLPK is the speed outlier, with caveats.** On independent solves (the workload recommended here) it was 6x to 16x faster than CBC, and on long overlap sequences 1.2x to 2.4x faster than the next-best solver. It kept that lead on the 240-player slate (4.9 ms versus 36.8 ms per solve). But it is GPL-3.0, GLPK itself has not changed since 2020, and its Python binding is a raw C interface. Meaning: worth keeping as an optional fast path for time-critical late swap if the user accepts GPL; not the default.
- **Avoid:** PuLP 2.4's bundled CBC (2015 build, 35 to 50 ms of file and process overhead per solve, and pinned by pydfs so it blocks newer PuLP); CP-SAT with more than 1 worker unless its deterministic mode is turned on and re-tested; the slot-assignment model on any solver.
- **Whatever the solver:** pin its exact version, add a deterministic tie-break (for example, a tiny bonus by player ID, or a second pass that picks the lexicographically smallest optimal lineup), and keep the solver-independent rule checker.

---

## 8. Supporting spikes

### 8.1 Showdown enumeration
- 22 players, 26,334 five-player UTIL sets, 440,121 legal lineups after the salary cap and both-teams rule (19,478 to 20,097 per captain). Enumerate and filter: 0.015 s. Best projection by enumeration 266.99, identical to the solver optimum. **VERIFIED** (`spikes/solvers/enumerate_showdown_spike.py`; `spikes/solvers/out/20261013-1700_enumerate_showdown.json`).
- Meaning: Showdown candidate generation is a filter, not an optimization. **BET** that this holds for real pools (real pools are similar in size; salary scale differs).

### 8.2 Portfolio selection cost on synthetic data
Spike: `spikes/solvers/portfolio_select_spike.py`; output `spikes/solvers/out/20261013-1847_portfolio_select_N20000.json` and `20261013-1849_portfolio_select_N100000.json`. Synthetic 120-player slate, 10,000 scenarios (game factor, team factor, individual noise), 5,000 GLPK candidate solves (4,998 unique), and a synthetic field: 60% optimizer lineups built from different noise and sampled with replacement (this creates duplicates; the most-copied lineup had 46 copies in 20,000 and 266 in 100,000), 40% ownership-weighted random lineups projecting at least 85% of the optimum. Cash line = top 20%. **VERIFIED** (code and output). The field is not realistic, so only cost and the direction of the trade-offs mean anything.

Cost (seconds, one process):

| Step | Field of 20,000 | Field of 100,000 |
|---|---|---|
| 10,000 scenarios | 0.05 | 0.05 |
| 5,000 candidate solves (GLPK) | 16.2 | 16.4 |
| Build the synthetic field | 14.8 | 36.8 |
| Top-1% and cash lines for all 10,000 scenarios (streamed, 500 scenarios at a time) | 3.8 | 12.3 |
| Hit matrices for all candidates | 0.7 | 0.8 |
| All greedy selections (5 strategies x 4 portfolio sizes) | 50.2 | 51.4 |
| Peak memory | 645 MB | 815 MB |

- **Memory trap found and fixed:** the first version scored lineups with a three-way array lookup and peaked at 3.5 GB (about 60% of the free RAM) on the 20,000-entry case. Rewriting scoring as a matrix multiply (scenarios x players times players x lineups) cut the peak to 645 MB. **VERIFIED** (console output from the first run; that output file was replaced when the spike was reworked, so the 3.5 GB figure survives only in this memo and the session log). Meaning: the engine must score lineups by matrix multiplication in chunks, never by building a scenarios x lineups x players array.
- **Hit matrices are small:** 5,000 candidates x 10,000 scenarios is 47.7 MB as true/false values and 6.0 MB bit-packed. **VERIFIED**.

Trade-off shape (field of 20,000; columns are P(at least one top-1%) / P(no entry cashes) for one contest):

| Entries | Top projection | Greedy top-1% | Greedy cash | Greedy blend (cash weight 0.5) |
|---|---|---|---|---|
| 1 | 3.3% / 56% | 4.4% / 63% | 3.3% / 56% | 3.3% / 56% |
| 3 | 8.2% / 18% | 11.3% / 26% | 9.9% / 15% | 9.9% / 15% |
| 20 | 35% / 0.7% | 48% / 0.01% | 28% / 0% | 47% / 0% |
| 150 | 90% / 0% | 98.8% / 0% | 51% / 0% | 98.8% / 0% |

What this shows (direction only):
- Greedy coverage beats "top projection" on the top-1% goal at every size. **VERIFIED** (synthetic).
- With one or three entries, chasing top-1% raises the no-cash risk; the blend recovers most of the cash safety while keeping more top-1% chance than top projection. **VERIFIED** (synthetic).
- With 20 or more entries in one contest, no-cash risk nearly vanishes in this synthetic field, so night-wide washout risk will come mostly from nights with few total entries and from player outcomes that sink every contest at once. That is exactly why the washout term must use the shared scenario set. **BET**.

---

## 9. Recommendations

Each recommendation ends with what it means for results, cost, or the user's nightly workload.

1. **Optimize the two goals directly with scenario coverage** (Section 3): per-contest P(at least one top-1%) plus a weighted night-wide cash coverage term, tuned so P(washout) stays under a target. *Meaning:* the engine chases the user's actual goals instead of proxies like "highest projection", at the cost of needing per-scenario cut lines from the field simulator.
2. **Use one shared scenario set for every contest on the night.** *Meaning:* the washout number the user sees is honest about correlated bad nights; it costs nothing extra (one simulation instead of several).
3. **Select entries with lazy greedy over a fixed candidate pool, not with one giant optimization.** *Meaning:* selection takes seconds and has a proven quality floor (at least 63% of the best possible per contest, 50% across contests, usually far better).
4. **Generate Classic candidates from many independent solves on scenario draws and leverage variants, not from long overlap sequences.** *Meaning:* 5,000 distinct candidates in about 40 s on 4 processes (CBC), and no slowdown from accumulating overlap rules.
5. **Generate Showdown candidates by enumerating every legal lineup.** *Meaning:* no solver and no missed lineups; listing takes a fraction of a second per game, and the real cost moves to scoring the screened survivors against all scenarios.
6. **Model Classic positions with one variable per player plus Hall's-theorem rows, and assign slots afterward.** *Meaning:* 5x to 25x faster solves with identical answers; late-swap slot ordering (later games in G/F/UTIL) is handled in the assignment step.
7. **Use OR-Tools (CBC backend) single-threaded behind a thin solver interface, with HiGHS as tested fallback** (Section 7.5). *Meaning:* about a minute of solver time per night, reproducible runs, permissive licenses.
8. **Add a deterministic tie-break and a solver-independent rule checker.** *Meaning:* re-running a night gives the same lineups, and no illegal lineup can reach DraftKings even if a solver or formulation has a bug.
9. **Do not build on pydfs-lineup-optimizer or chanzer0's code; borrow ideas (with attribution) only from MIT-licensed code.** *Meaning:* avoids a 2015 CBC build, a frozen dependency pin and unlicensed code, at the cost of writing about the same amount of rule code ourselves.
10. **Treat duplication as a payout weight, pending the user's decision** (Open question 1). *Meaning:* the engine will avoid chalky Showdown lineups only as much as the user wants it to.
11. **Keep an overlap cap as an optional pool-shaping knob, tuned by slate size in backtests.** Start from Hunter et al.'s finding (more overlap on small slates, less on large) and Haugh and Singal's 6-of-9. *Meaning:* one setting to test in backtests rather than a fixed rule; Showdown likely needs a loose cap or none.

---

## 10. Open questions

1. **Duplication policy (needs the user's decision).** Should a top-1% finish that is shared with field duplicates count fully (pure probability, as goal 1 is written), or be weighted by the payout share 1/(1 + expected copies)? The same question applies to first place in contests under 100 entries: does a tie for first count as "first place"? The choice changes which Showdown lineups the engine picks more than anything else in this memo. **BET**.
2. **Washout target.** What epsilon (the highest acceptable probability of zero cashes tonight) should the engine aim for, for example 5% or 10%? The lower it is, the more top-1% probability the engine gives up. The engine can print the trade-off curve each night so the user can see the price.
3. **Contest weights.** Is a top-1% finish in a $3 single-entry contest worth the same as one in a $20 150-max? The default proposal is to weight by the contest's top-1% prize money, but equal weights match the goal as written.
4. **Who picks contests and entry counts?** If the engine is allowed to decide how many entries go to each contest (contest selection), the same greedy can allocate them, adding a budget limit in dollars. If the user fixes the contests nightly, the greedy only fills them.
5. **Overlap cap as a hard rule or not.** Both papers found an overlap cap helped, but they used it to make up for weak objectives. With a scenario-coverage objective, diversity is rewarded automatically. A backtest should compare "coverage only" against "coverage plus cap". **BET**.
6. **Scenario count S.** 10,000 scenarios estimates a 1% event with a standard error of about 0.1 percentage points per lineup, which is fine for the portfolio but noisy for ranking single lineups. Whether S should be higher depends on the simulator's speed (owned by another track).
7. **Late swap.** Should late swap re-run the same coverage selection on unlocked slots? The math allows it (fix locked players, regenerate candidates for open slots, re-score). Cost and timing need checking against real lock times.
8. **Ownership and field source.** The field model needs ownership projections; who supplies them, and can past DraftKings contest-standings files (which the user can download after contests) be used to calibrate field duplication? Owned by the field research track.
9. **GPL acceptance.** If GLPK is used anywhere, the engine links GPL-3.0 code. That is fine for private use on the user's laptop but matters if the engine is ever shared or sold.

---

## 11. Implications for the architecture

1. **One night-level scenario store.** A single matrix X (scenarios x players, float32) shared by every contest. 10,000 scenarios x 300 players is about 12 MB. Classic and Showdown read the same player rows; a Showdown captain is 1.5 x the same draw, and the CPT and UTIL DraftKings IDs map to one internal player ID. **VERIFIED** (arithmetic); design is **BET**.
2. **Fields produce cut lines, not score tables.** Each contest's field simulation outputs only T1[c, s], Tc[c, s], and duplicate counts for our candidates, streamed in scenario chunks. A full table of 100,000 field entries x 10,000 scenarios in float32 would be 4 GB and must never be built. Haugh and Singal's order-statistic shortcut (sample the k-th best opponent score directly) is the fallback if streaming is too slow. **VERIFIED** (arithmetic; EC.1.2).
3. **Two candidate generators behind one interface.** Classic: MILP solves on scenario draws and leverage variants, through a thin solver adapter so the solver can be swapped. Showdown: full enumeration plus a screen. **VERIFIED** (both measured in this memo).
4. **A solver-independent rule checker.** Every lineup from any source is re-checked against DraftKings rules before it can be selected: distinct player IDs, slot assignment by matching (Classic), CPT/UTIL ID pairing (Showdown), salary cap, at least 2 games (Classic) or both teams (Showdown). The spikes did this for every lineup and found zero violations. **VERIFIED** (spike output, `n_problems` = 0 in every run).
5. **Hit matrices as bits, greedy across all contests at once.** Store h1 and hc bit-packed (about 6 MB per 5,000 candidates x 10,000 scenarios), run one lazy greedy over (contest, lineup) pairs, and sweep the washout weight lambda. **VERIFIED** (memory figures from spike); design is **BET**.
6. **Reproducibility.** Fix a seed per slate; run solvers single-threaded; add a deterministic tie-break, because different solvers (and possibly different versions) return different lineups with exactly the same projected score. Record solver name and version in each night's run record. **VERIFIED** (Section 7.4: identical objective values, different lineups across solvers).
7. **Parallelism by processes, not solver threads.** Candidate generation splits cleanly across 4 worker processes, each with its own small model (under 150 MB each in the spike), well inside the roughly 6 GB of free RAM. **VERIFIED** (Section 7.4).
8. **Budget.** Solver time is minutes at most; the simulator and field scoring will dominate nightly runtime. Design the job so a failed or slow solver step can fall back to the previous candidate set. **BET**.
9. **Regression test.** Keep a fixed synthetic slate (like the one in `bench_solvers.py`) and assert that two different solvers return identical objective values for a fixed list of seeds. This catches formulation bugs and solver upgrades that change behavior. **BET**.

---

## 12. Sources

Papers
- Hunter, Vielma, Zaman. Picking Winners in Daily Fantasy Sports Using Integer Programming. arXiv 1604.01455 (v1 2016, v3 2019). https://arxiv.org/abs/1604.01455
- Haugh, Singal. How to Play Fantasy Sports Strategically (and Win). Management Science 67(1):72-92 (2021). https://doi.org/10.1287/mnsc.2019.3528 ; SSRN https://papers.ssrn.com/abstract=3393127 ; accepted manuscript https://spiral.imperial.ac.uk/handle/10044/1/77220 ; Sloan 2018 version https://www.sloansportsconference.com/research-papers/how-to-play-strategically-in-fantasy-sports-and-win
- Bergman, Cardonha, Imbrogno, Lozano. Optimizing the Expected Maximum of Two Linear Functions Defined on a Multivariate Gaussian Distribution. INFORMS J. Computing 35(2):304-317 (2023). https://arxiv.org/abs/2112.07002 ; https://doi.org/10.1287/ijoc.2022.1259
- Decary, Bergman, Cardonha, Imbrogno, Lodi. The Madness of Multiple Entries in March Madness. arXiv 2407.13438 (2024). https://arxiv.org/abs/2407.13438
- Liu, Liu, Teo. Picking winners: Diversification through portfolio optimization. Production and Operations Management 32(9) (2023). https://doi.org/10.1111/poms.14013
- Mlcoch, Hubacek. Competing in daily fantasy sports using generative models. International Transactions in Operational Research 31(3) (2024). https://doi.org/10.1111/itor.13344
- Mbeledogu. Robust Daily Fantasy Sports. MIT SSAC 2026. https://www.sloansportsconference.com/research-papers/robust-daily-fantasy-sports-maximizing-reward-via-the-robust-optimization-paradigm
- Papageorgiou, Sarlis, Tjortjis (2024). https://doi.org/10.1007/s41060-024-00523-y
- Dopke, Kohler, Tegtmeier (2024). https://doi.org/10.1007/s12197-023-09646-7
- Evangelista, Cal Poly MS thesis (2019). https://digitalcommons.calpoly.edu/theses/2025
- Nemhauser, Wolsey, Fisher (1978), An analysis of approximations for maximizing submodular set functions I, Mathematical Programming 14:265-294 (cited by both Hunter et al. and Haugh and Singal). Fisher, Nemhauser, Wolsey (1978), An analysis of approximations for maximizing submodular set functions II, Mathematical Programming Study 8:73-87 (the 1/2 bound under a matroid constraint). Minoux (1978), Accelerated greedy algorithms for maximizing submodular set functions (lazy greedy). The last two are cited from my own knowledge, not re-read for this memo: SUPPORTED.
- Kaplan, Garstka (2001), Management Science 47(3). https://doi.org/10.1287/mnsc.47.3.369.9769 ; Clair, Letscher (2007), Operations Research 55(6). https://doi.org/10.1287/opre.1070.0448
- Hall, P. (1935), On representatives of subsets (Hall's marriage theorem), J. London Math. Soc. 10:26-30.
- Citation trackers used: https://api.semanticscholar.org/graph/v1/paper/arXiv:1604.01455/citations ; https://api.openalex.org/works?filter=cites:W2982894598

Open-source tools
- https://github.com/DimaKudosh/pydfs-lineup-optimizer ; https://pypi.org/project/pydfs-lineup-optimizer/
- https://github.com/chanzer0/NBA-DFS-Tools
- https://github.com/JonnyRank/nba-dfs-optimizer
- https://github.com/SamBamCH/ivan
- https://github.com/BenBrostoff/draftfast ; https://pypi.org/project/draftfast/
- https://github.com/sansbacon/pangadfs
- https://github.com/dfs-with-r/coach
- https://github.com/zlisto/Daily-Fantasy-Baseball-Contests-in-DraftKings
- https://github.com/garethmarkel/mlb_dfs_optimizer
- https://github.com/jnederlo/dfs_optimizers ; https://github.com/tburger101/dfs_simulator
- https://huggingface.co/datasets/cbratkovics/nba-game-logs ; https://huggingface.co/datasets/cdechoch/nba-data-archive

Solvers
- HiGHS / highspy: https://pypi.org/project/highspy/ ; options reference https://ergo-code.github.io/HiGHS/dev/options/definitions/
- PuLP: https://pypi.org/project/PuLP/ (4.0.0, Sept 2026, breaking changes, CBC now an optional extra via cbcbox) ; PuLP 2.4 tag https://github.com/coin-or/pulp/tree/2.4
- OR-Tools: https://pypi.org/project/ortools/ ; CP-SAT parameters https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto
- PySCIPOpt: https://pypi.org/project/PySCIPOpt/
- swiglpk (GLPK bindings): https://pypi.org/project/swiglpk/
- python-mip: https://pypi.org/project/mip/

Spike code and raw output (this memo)
- `spikes/solvers/bench_solvers.py`, `spikes/solvers/run_bench.py`, `spikes/solvers/analyze_bench.py`
- `spikes/solvers/enumerate_showdown_spike.py`, `spikes/solvers/portfolio_select_spike.py`
- Raw output: `spikes/solvers/out/` (file names cited in Sections 7 and 8)
