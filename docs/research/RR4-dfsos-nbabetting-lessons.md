# RR4. Lessons from four prior projects: dfs-os, nba-betting-system, bleeski/NBA, dfs-architect

**Date:** 2026-10-13. **Scope:** read-only review of four of the user's earlier projects, mined for lessons for the new NBA engine sketched in S1. No tracked content was modified, committed or pushed, and no code from these repos was run. One side effect: a `git status` in the local dfs-architect copy refreshed git's own index file (its timestamp changed); no file content changed. dfs-architect was also cloned into the session scratchpad to read; bleeski/NBA was read through the GitHub API. Three small read-only scripts in the scratchpad computed statistics: two read the whole 2.4 MB `nba_2008-2025.csv` from nba-betting-system (beyond the "peek at names and sizes" the brief allowed for large files; done to get the calibration numbers in section 2.4, and only summary statistics were output), and one read the dfs-os session projection CSVs (section 1.3).

**Labels.** VERIFIED: I read it in a file or commit, or computed it myself; the path or commit is cited with a short excerpt. SUPPORTED: credible inference from what I read, not directly shown. BET: my judgment.

**Jargon used here.** A *PRD* is a product requirements document. An *MCP server* is a small web service that gives Claude extra tools. *D1* and *KV* are Cloudflare's hosted database and key-value cache. *MILP* means mixed-integer linear program, the kind of math problem a lineup optimizer solves. *PuLP/CBC* and *SciPy/HiGHS* are two free solver stacks. A *walking skeleton* is a thin version of the whole pipeline that runs end to end on real inputs before any part is made good.

**Credentials to rotate (values not copied):**
- An Anthropic API key is stored in plain text at `C:\Users\benja\Documents\dfs-os\.env.txt`. It is not tracked by git (VERIFIED: `git ls-files` lists no env file). R7 warns that an `ANTHROPIC_API_KEY` in the shell silently overrides the Claude Code login, so this key must never be exported into the environment the new engine runs in.
- A database password is stored in plain text inside a connection URL in `C:\Users\benja\Documents\nba-betting-system\config\settings.yaml` and in `alembic.ini` in the same folder (VERIFIED: one user-and-password URL in each file, counted without printing values). It is a local default, but it is still a credential in a file.
- `C:\Users\benja\Documents\ben_projects\dfs-architect\worker\.dev.vars` exists but is empty (VERIFIED, 0 bytes). The GitHub OAuth secrets for that Worker live in Cloudflare (errata 11), not on disk.

---

## The answer first

1. **None of the four projects reached a working nightly loop, and three stalled at their first contact with real operation.** nba-betting-system stopped at a PostgreSQL password. dfs-architect's first real slate halted because the pipeline had no entry point. bleeski/NBA declared itself "production ready" with mocked research and a different DFS site's rules. dfs-os ran one afternoon of sessions and was then replaced. The effort went into specifications and infrastructure: six OS revisions in four days (Apr 10 to 13), a PRD at version 4.13, two 84 KB PowerShell installer scripts, and a Cloudflare Worker with a database, a cache and OAuth. VERIFIED (details per project below).
2. **The biggest operational lesson is to build the walking skeleton first.** Before Oct 20, the new engine should run every stage on real preseason DKEntries files, including the user's upload and the "uploaded N of N" readback, even with crude projections. S1 has "valid output first" as a principle (B2.3) but no milestone that forces it. BET, grounded in the stall pattern.
3. **Data integrity, not modeling, caused most past errors.** The user's own NBA betting spec says so in writing, and dfs-os shipped upload files from a session in which 0 of 175 players were confirmed starters. S1 needs explicit freshness stops. VERIFIED.
4. **S1 is the destination the user already named.** The dfs-os PRD lists Monte Carlo simulation plus a synthetic field as "the theoretically correct approach" and deferred it. Every prior engine instead used multipliers on a point projection, rank-based objectives, or salary-based projections, and none modeled outcome distributions. S1's simulation-first design is the right correction. VERIFIED (PRD section 13).
5. **Seven concrete additions to S1** come out of this review (section 5.8): a data-freshness stop, an honest-inputs line in the brief, explicit slot-assignment variables, ownership unit and sum checks, absence duration as a redistribution input, a DraftKings-only validator source, and a seeded lessons file. A measured calibration target for the game layer also comes out of it (section 2.4).
6. **Reuse almost nothing.** One historical game-lines file is worth using as a calibration check, with a provenance caveat. Process text (CLAUDE.md working-style rules, the lessons-file habit, Windows gotchas) is worth copying. No code is worth reusing. Section 5.9.

### Timeline

| When | Project | Runtime for the LLM | Furthest point reached | Why it stopped |
|---|---|---|---|---|
| Before Apr 2026 | "DFS OS v1" in Claude chat Projects, change log to OS-042 | Claude chat with a Python tool | Daily use in chat (SUPPORTED) | Replaced: "construction by narrative judgment" (VERIFIED, `dfs-os\reference-docs\DFS_OS_Change_Log.md`, OS-001 reason) |
| Oct 24, 2025 | bleeski/NBA | Claude Code on the web, one session | A demo on an 18-player sample, never merged to main | Not stated; research was mocked and the site was bet365, not DraftKings |
| Mar 18 to 21, 2026 | nba-betting-system | Claude Code, local | Phase 1 "about 90%": schema, CSV import, 17 tests | "Blocked on PostgreSQL password setup" (VERIFIED, README) |
| Apr 10 to 13, 2026 | DFS OS chat rebuild, OS-001 to OS-006 | Claude chat | Six spec revisions in four days | Superseded by code (dfs-os) |
| Apr 15 to 17, 2026 | dfs-os | Anthropic API key, Sonnet 4.6, plus Claude Code to build | MLB pipeline end to end; 5 real sessions on Apr 17 | Not stated (BET: replaced by a heavier architecture 3.5 weeks later) |
| May 11 to 13, 2026 | dfs-architect | claude.ai Projects, custom MCP connector, code-execution sandbox | MLB Phase 1 library, 28 commits; first real slate attempted May 13 | First slate halted at step 3: no entry point (VERIFIED, local errata 12) |

---

## 1. dfs-os (`C:\Users\benja\Documents\dfs-os`, GitHub bleeski/dfs-os, 12 commits)

### 1.1 What it is, how far it got, why it stopped

- **What:** a Windows command-line app that turns a DraftKings salary CSV into lineups through three stages: (1) an LLM research stage that writes a "projection CSV", (2) a deterministic PuLP/CBC optimizer, (3) validation and output. VERIFIED, `DFS_OS_PRD.md` section 3.4.
- **Why it existed:** the earlier chat-based process had "no state persistence" and redid deterministic work (optimizer, 30+ validation checks) inside chat. VERIFIED, PRD section 1, "Why It Exists".
- **How far:** MLB only. 12 commits on Apr 16 and 17, 2026; commit 36802cc reports "100 tests passing" and a full pipeline "research → edit pause → multi-lineup optimizer → DK upload CSV → slate summary". VERIFIED.
- **Real use:** the SQLite file `dfs.db` holds 5 sessions, all dated 2026-04-17, all WTA mode (winner-take-all) and small field, with a $0.01 entry fee and 7 max entries as entered (likely test values): 2 complete, 2 abandoned, 1 left "active". VERIFIED, read-only query of `sessions`.
- **Why it stopped:** not recorded. dfs-architect started 3.5 weeks later with a different stack. BET: the research stage's quality (section 1.3) and the desire for richer data pushed the user to a heavier design.

### 1.2 What worked

- **The three-stage split with a deterministic optimizer.** This was the fix for the v1 failure: "construction decisions were made by narrative reasoning rather than deterministic optimization." VERIFIED, Change Log OS-001 reason. S1's B4 boundary is the same idea, made stricter.
- **CLAUDE.md working-style rules** ("Think Before Coding", "Simplicity First", "Surgical Changes", "Goal-Driven Execution", "write a rule in lessons.md" on every correction). VERIFIED, `dfs-os\CLAUDE.md`. Ten lessons were captured in two days (VERIFIED, `lessons.md`), and they are concrete and reusable.
- **A plan-then-build cadence**: a planning interview of 10 questions, a phased plan, then one commit per phase with tests. VERIFIED, `tasks\todo.md` and the commit list. Four phases landed in two days.
- **An explicit review gate before writing the upload file** (type "export" to confirm). VERIFIED, commit fab5166.

### 1.3 What broke or was painful

- **The LLM research stage produced weak inputs and still produced upload files.** In session 1, all 175 players were "Assumed" (110) or "Unresolved" (65); zero were "Confirmed", yet `sessions\1\dk_upload.csv` was written. Session 3 had 37 Confirmed of 67. VERIFIED, counts from `sessions\1\projections.csv` and `sessions\3\projections.csv`.
- **The LLM inferred starters from salary.** The lesson added that afternoon reads "Never infer starting status from salary or salary rank." VERIFIED, `lessons.md` and commit fab5166. SUPPORTED that this is what the model had been doing.
- **The "ceiling" carried almost no information.** The LLM's ceiling score was the projection times a near-constant: in session 1 every ratio was 1.40, 1.45, 1.46 or 1.50; in session 3 they ranged 1.36 to 1.43. VERIFIED, computed in the scratchpad (`rr4\ceil_ratio.py`). The upside of each player was never modeled, only a menu multiplier on the mean.
- **The LLM did the arithmetic.** Stage 1 asked Claude to "Apply bounded adjustment multipliers to derive projection and ceiling scores" and emit a full CSV of numbers. VERIFIED, PRD section 3.4. A 175-row CSV of LLM-computed numbers is both expensive and error-prone.
- **Web fetching from an LLM was brittle.** mlb.com lineups were "JS-rendered, unfetchable" (VERIFIED, commit eecd829). The `duckduckgo_search` package was renamed and spammed warnings (VERIFIED, commit f25ec4d). The chat-era OS concluded "Every automated source for odds is fetch-incompatible" and made pasted odds the default (VERIFIED, Change Log OS-005). Contrast R4, where code calling structured JSON endpoints (ESPN, nba_api) worked. The failure was LLM page-fetching of HTML, not the absence of data.
- **The user ended sessions early** because the final Claude message was hidden: users "couldn't tell if Claude needed more info or was ready for CSV output, and ended the session prematurely." VERIFIED, commit c445658.
- **No token logging and a large prompt.** The PRD required "Log actual token usage per session" (section 6.4), but `dfs\research\agent.py` has no usage logging (VERIFIED, grep). The compiled system prompt was 49,697 characters (VERIFIED, commit eecd829), sent every session with an interactive tool loop.
- **Learning never started.** The ownership calibration log and meta-trend log are templates with zero rows, gated on "30+ slates". VERIFIED, `reference-docs\Ownership_Calibration_Log.md` ("Rows Logged 0" for every sport) and `Meta_Trend_Log.md` ("NO ENTRIES YET").
- **Windows friction**, all VERIFIED in `lessons.md`: wrong setuptools backend; `python -m` needing a `__main__` block; multi-line paste spilling into PowerShell after Python exits; a check-mark character crashing Rich on a CP1252 console; a secret file named `.env.txt` slipping past the default `.gitignore`.

### 1.4 NBA knowledge in dfs-os

- **NBA variance profile:** Cash Conservatism 5, GPP Divergence 2, because "Minutes/usage is genuinely predictable. GPP differentiation is hard without unacceptable floor risk." Also: "NBA Massive GPP is structurally difficult at Divergence 2. The scenario must involve an information edge the consensus field has missed." VERIFIED, `reference-docs\DFS_OS_Handoff.md` and `DFS_OS_System_Instructions.md` (NBA Scenario Targeting). In S1 terms: NBA leverage comes mostly from news timing and combinations, not from fading good players. SUPPORTED.
- **The NBA "bounded adjustment menu"** (about 20 multipliers such as confirmed starter x1.10, usage 28%+ x1.10, minutes 34+ x1.08, pace-up x1.06, blowout risk x0.88). VERIFIED, System Instructions, "NBA Bounded Adjustment Menu". The numbers have no cited source, and several overlap (a confirmed 34-minute, high-usage starter collects three correlated boosts that multiply). BET: these are invented and double-count; do not port them as priors.
- **NBA base projection:** "Vegas player prop (if available) or (team implied total x usage share x minutes share)." VERIFIED, System Instructions, base projection derivation. This matches S1's market anchor (component 7).
- **Salary-structure ownership effect:** players at "clean" price points appear in more optimizer solutions, so they are more owned than equivalent players at awkward prices. VERIFIED as the user's stated belief, Change Log OS-003 item 5. S1's simulated field reproduces this automatically if opponents are salary-cap-bound optimizers with a realistic salary-left distribution (R3 section 7 lists salary left as a calibration target). SUPPORTED.
- **An April 2026 DK NBA Classic salary file** is in the repo (`reference-docs\sample-data\dk_nba_salaries_sample.csv`): a two-game slate on 2026-04-15 (GSW@LAC and ORL@PHI, 70 players; BET that these were play-in tournament games). It has the 9 classic columns and no `Status` or `Starting` columns, and its `Roster Position` values (`PG/G/UTIL`, `SG/SF/F/G/UTIL`, `C/UTIL`, and so on) match R6's eligibility table exactly. VERIFIED. That the user downloaded it is SUPPORTED (the PRD says sample files "must be provided by the user"). This adds a more recent NBA file to R6's evidence for the eligibility table. It also shows an NBA Classic file still lacked `Status` and `Starting` on 2026-04-15; R6's 2026 files with those columns were other sports, so whether 2026-27 NBA files carry them stays open until the user exports one.

### 1.5 DraftKings knowledge not already in R6

- dfs-os wrote upload files with only slot columns: header `P,P,C,1B,2B,3B,SS,OF,OF,OF` and one row of IDs per lineup, no Entry ID columns. VERIFIED, `sessions\3\dk_upload.csv`. That is DraftKings' blank-template path, not the Edit Entries path R6 recommends. Nothing here contradicts R6; it confirms the prior engines never filled already-purchased entries.
- **Terminology trap:** dfs-os's "Late-Swap Sequence" means re-running before lock when news arrives (VERIFIED, `Execution_Project_Template.md`, "Execute when new information arrives after the initial build but before contest lock"). DraftKings' late swap means editing unlocked slots after earlier games lock (R6 section 2.5). The new engine's glossary should pin the DraftKings meaning.
- The PRD notes that the DK results file has no winnings column, so winnings must come from the payout table (VERIFIED, PRD FR-POST-1). Already consistent with R6 and R8.

### 1.6 LLM layer patterns

- **Runtime:** the Anthropic SDK with an API key from `.env.txt`, model `claude-sonnet-4-6`, max 8,096 output tokens, a streaming loop with two home-made tools (DuckDuckGo search, httpx plus BeautifulSoup fetch, 8,000-character cap). VERIFIED, `dfs\research\agent.py` and `dfs\research\tools.py`. This is pay-per-token API use, not the subscription R7 plans around.
- **Output protocol:** the CSV was pulled out of free text between `=== PROJECTION CSV START/END ===` markers. VERIFIED, `dfs\research\csv_extractor.py`. Lesson recorded: Claude's CSV used different column names from the parser's (VERIFIED, `lessons.md`). S1's schema-validated JSON override records are the stronger version.
- **No hooks, subagents or skills** were used (VERIFIED: `.claude\settings.json` holds only a pytest allow rule). There is no evidence here about their cost or flakiness.

### 1.7 Architecture ideas vs S1

| dfs-os idea | Status in S1 | Verdict |
|---|---|---|
| Consensus simulation: a vanilla optimizer run marks what the field will build (FR-OPT-11) | Generalized by S1's simulated field (B7) | S1 is stronger. Keep the "field optimizer" as one opponent type, as R3 says. |
| Scenario-coverage penalty on game exposure (FR-OPT-12) | Replaced by per-scenario coverage in the selector (A4, component 14) | S1 is stronger; the penalty was a stand-in for simulation, by the PRD's own words. |
| Entry-count derivation by marginal EV, with a "circuit breaker" (OS-006) | Absent: S1 takes entries as given | Worth a small add: report the marginal Goal-1 gain of the last few entries per contest so the user can buy fewer or more next time. BET. |
| News severity triage: minor, moderate, critical (Execution Template) | S1 has a narrow re-run (B5) | Use the triage to pick re-run scope: minor means no rebuild, critical means affected games only. Cheap. BET. |
| Confidence tiers (Confirmed, Assumed, Unresolved) with a fixed penalty | S1 keeps questionable players random | S1 is stronger; tiers are a coarse stand-in for P(active). |
| 30-slate gates before any calibration | S1 learns per player from night 1 (B8) | S1 is right; the gates are why dfs-os never learned anything. |

---

## 2. nba-betting-system (`C:\Users\benja\Documents\nba-betting-system`, no commits)

### 2.1 What it is, how far it got, why it stopped

- **What:** a pregame NBA spread and totals betting system specified in a 37 KB `SPEC.md` written to let "a stranger with normal development skills" rebuild it, consolidating earlier chat-era "v6, v7, and v9 documents". VERIFIED, `SPEC.md` header and section 1.
- **How far:** Phase 1 only: package scaffold, 16 SQLAlchemy tables, Alembic migrations, a CSV importer and 17 passing tests that need no database. VERIFIED, `tasks\plan.md`. The folder has a `.git` directory with no commits (VERIFIED: "your current branch 'main' does not have any commits yet"). Files are dated Mar 18 to 21, 2026.
- **Why it stopped:** "Phase 1 (Foundation) is ~90% complete. **Blocked on PostgreSQL password setup.**" VERIFIED, `README.md`. `tasks\todo.md` is a pgAdmin walkthrough for the user to run as administrator. A non-engineer was asked to set a database server password, and the project never moved again.
- **Never reached:** game-level box scores (the plan says the CSVs "do NOT have game-level box scores", VERIFIED `tasks\plan.md`), nba_api calls, any model training or backtest. So this project gives **no** first-hand evidence about nba_api reliability, rate limits or blocks. R4 remains the only measured source on that.

### 2.2 What worked (patterns worth keeping)

All VERIFIED in `CLAUDE.md` or `SPEC.md`:
- "Model predicts the error, not the raw score": targets are `actual_total - market_total` and `actual_margin - market_spread`. The DFS analog is S1's market anchor: start from the line and model the residual.
- "Do not call external APIs during model scoring. All data must be pre-loaded." Matches S1's snapshot-then-compute design.
- "Do not overwrite market ticks, always append with timestamp." Matches S1's snapshot store (component 2).
- "No-bet is an explicit output with a stored reason, not an omission." The DFS analog: "kept the fallback portfolio because X" is an explicit, logged decision.
- Thresholds in a config file, never in code.
- A "shadow mode" of 7 days or more before trusting the system (SPEC section 9).
- Task files (`plan.md`, `todo.md`, `lessons.md`) reviewed before each phase.

### 2.3 What broke or was painful

- **Infrastructure that needed an administrator.** PostgreSQL 17 via winget, a password set in pgAdmin, and `psql` not on PATH (VERIFIED, `tasks\lessons.md`, "PostgreSQL installer doesn't add psql to PATH"). For a single-user laptop engine this was pure cost.
- **Encoding:** a player-usage CSV failed under Windows' default code page; fix was `utf-8-sig` first, then `latin-1`. VERIFIED, `tasks\lessons.md`.
- **The same setuptools backend error as dfs-os, a month earlier.** VERIFIED in both lessons files. Lessons did not travel between projects, because each project kept its own file.

### 2.4 NBA knowledge, including a measured calibration target

**The key lesson, in the user's own spec:** "many historical errors came from stale schedules, missing injuries, or incomplete data, not from the core model alone." VERIFIED, `SPEC.md` section 8. The QC gates that follow are directly useful for DFS (VERIFIED, SPEC sections 8.1 and 8.2):
- Verify "the correct date in user time zone" and that every game on the official slate is present.
- Cross-check major injury statuses across at least two sources.
- If sources disagree on a high-usage player near tip, do not force a conclusion. (For betting this meant "no bet"; for DFS the analog is to keep the player random in the simulation and prefer late-swap-friendly slots, which S1 already does.)
- If more than 65% of the slate leans one direction, treat it as calibration drift, not edge.

**HUPO rule ("High Usage Player Out"):** a player with season usage above 25% who has been out at least 3 and at most 15 games opens a "new-rhythm window before the market fully prices the absence." VERIFIED, SPEC section 5.6 and `config\settings.yaml`. It was never backtested (BET on its value). The transferable idea: **how long a player has been out changes how well everyone has priced the absence.** On a star's first game out, DraftKings salaries have not moved and the field projects the redistribution from scratch; after several games, real with-and-without minutes exist and salaries have adjusted. S1's minutes redistribution should take "games missed so far" as an input: lean on priors for the first game, and on observed splits after a few games. BET.

**Measured game-level calibration targets (new, VERIFIED arithmetic).** The project's `data\raw\nba_2008-2025.csv` holds 23,118 games from 2007-10-30 to 2025-06-22 with final and quarter scores, overtime columns, the favorite, the spread, the total and moneylines. I computed, for regular-season games (scripts `rr4\lines_stats.py` and `rr4\lines_stats2.py` in the scratchpad):

| Measure | Last 3 seasons (2022-23 to 2024-25), 3,690 games | Trend |
|---|---|---|
| Actual total minus listed total: mean | +0.6 points | Near zero in every season (-0.5 to +1.2) |
| Actual total minus listed total: standard deviation | 17.9 points | 16.9 to 18.7 across all 18 seasons |
| Home margin minus expected margin from the spread: mean | 0.0 points | Confirms the sign convention |
| Same, standard deviation | 13.2 points | Rose from 11.1 to 11.8 (2007-08 to 2015-16) to 12.5 to 13.6 (2020-21 to 2024-25) |
| Games that went to overtime | 5.4% | 4.7% to 6.6% per season |
| Games with a final margin of 20 or more | 18.6% | 12.3% to 16.7% from 2007-08 to 2017-18; 21.1% in 2024-25 |

What it means for S1's night simulator (component 9): the simulated game layer should reproduce a total spread of about 18 points around the market total, a margin spread of about 13 points around the spread (R3 used "about 12", sourced weakly to a blog post), about 5% overtime, and about 19% of games decided by 20 or more. The blowout rate matters most: it drives fourth-quarter minutes for starters, and it has risen. **Caveats:** the file's source, sportsbook, and whether lines are opening or closing are not documented, so the file's provenance is SUPPORTED at best; the arithmetic on it is VERIFIED. Cross-check against the historical lines R4 found (ESPN back to 2014) before relying on it.

**Other files** (headers only, VERIFIED): season-level team style (pace, three-point rate, free-throw rate) 2008 to 2025, team usage depth (max usage, top-two usage sum, number of 8, 10, 12 point scorers), and player usage by team and season (names only, no IDs). These are seasonal aggregates; nba_api gives the same and more (R4).

### 2.5 DraftKings knowledge

None. This was a betting project. Its planned sources ("Underdog NBA / Rotowire" for injuries, "Odds API" for markets; VERIFIED SPEC section 4.1) are covered by R4, which found Underdog rejects old app versions and RotoWire bans scraping.

### 2.6 LLM layer patterns

Claude Code locally with a CLAUDE.md that sets a "Decision Authority" split: Claude owns architecture and implementation; "Escalate to user: business logic tradeoffs, cost decisions ... changes to betting rules or thresholds". VERIFIED, `CLAUDE.md`. That split is a good fit for a product-manager owner and is worth copying. No hooks, subagents or skills (VERIFIED, `.claude\settings.local.json` holds only permission rules).

---

## 3. bleeski/NBA (GitHub, private)

### 3.1 What it is, how far it got, why it stopped

- **What:** a FastAPI backend plus React frontend that takes a **bet365** DFS CSV (columns `Tournament, PlayerID, Name, FName, Club, Lineup, Position, Price`) and returns two lineups, "optimal" and "leverage". VERIFIED, `README.md` on the branch.
- **How far:** `main` holds only an initial commit (`.gitattributes`). The work sits on a Claude Code web branch named `claude/nba-dfs-lineup-generator-...`, two commits at 18:36 and 18:38 UTC on 2025-10-24, about 12 minutes after the repo was created. Never merged. No issues or PRs. VERIFIED, `gh api repos/bleeski/NBA/commits` and the branch tree.
- **Why it stopped:** not stated. SUPPORTED: a one-shot generation that was never wired to real data.

### 3.2 What it shows

- **Self-declared completion is not evidence.** `PROJECT_SUMMARY.md` says "Status: READY FOR DEPLOYMENT" and the README promises "Research phase: 2-3 minutes (with real web searches)", while the research code is a `MockResearchService` and every real fetch is a `TODO` (VERIFIED, `backend\app\services\research_service.py`, lines with "In production, this would call web_search" and "TODO: Parse injury data").
- **Projections from salary:** `base_projection = (player.salary / 1000) * 5.5` times multipliers. VERIFIED, `lineup_generator.py` line 59. This makes the optimizer reproduce salary, which is exactly what the field already knows.
- **Nondeterminism:** the fallback leverage lineup calls `random.shuffle` without a seed. VERIFIED, line 300.
- **Different site rules.** bet365 rules here are "Salary < $50,000 (strictly less than)", "Maximum 3 players from any single team", and position ranges (PG 1 to 3, C 1 to 2). VERIFIED, README. **None of these apply to DraftKings** (R6: salary at most $50,000, no team cap in Classic, fixed slots). The new validator must take its rules from R6 and the downloaded DK files only.
- Two README lines echo chat-era pain: "Late scratches will kill you in no-late-swap formats" and "Never trust model-reported totals - recalculate everything." VERIFIED. SUPPORTED that the second refers to LLM arithmetic errors in earlier chat use.

### 3.3 NBA, DraftKings and LLM knowledge

No NBA data-source evidence (all mocked) and no DraftKings knowledge (bet365). The LLM lesson is the one above: a single autonomous session will produce polished, confident documentation for software that does not do the job. Acceptance must be a real file through the real pipeline, checked by code. BET.

---

## 4. dfs-architect (GitHub bleeski/dfs-architect, 28 commits; local copy at `C:\Users\benja\Documents\ben_projects\dfs-architect`)

### 4.1 What it is, how far it got, why it stopped

- **What:** a multi-sport "DFS Operating System" with four runtime surfaces (VERIFIED, `docs\dfs_first_slate_runbook.md` and the file tree):
  1. A Cloudflare Worker in TypeScript acting as an MCP server, with GitHub OAuth, a D1 database and a KV cache.
  2. A claude.ai "Execution Project" whose knowledge is synced from GitHub by clicking "Sync now".
  3. Python run inside claude.ai's code-execution sandbox.
  4. A separate claude.ai "build project" that produced the code as PowerShell installer scripts. The local copy holds `install_chunk5.ps1` and `install_chunk5_patch.ps1`, 83,858 bytes each, which overwrite Python files when run (VERIFIED, local file header: "This installer overwrites the chunk 5 files only").
- **How far:** MLB Classic Phase 1 library: DK CSV parser, MLB handler, ownership heuristic, a three-stage optimizer with two solvers, a portfolio generator, a DK CSV emitter and a "provenance footer". 12,394 lines of Python including 7,016 lines of tests, written May 11 to 13, 2026. VERIFIED (line counts from the clone). Five of seven data tools were stubs: `health_check`, `get_vegas_lines`, `get_statcast_rolling`, `get_weather`, `get_injury_report` "return canned data". VERIFIED, `docs\dfs_execution_project_system_prompt.md`.
- **Why it stopped:** the first real slate, May 13, halted. Uncommitted errata 12 in the local copy says the build "shipped all library modules ... plus an end-to-end smoke test, but no callable entry point" and "Execution Claude correctly halted at workflow step 3 on the first slate." VERIFIED, `ben_projects\dfs-architect\v4_13_errata.md` (local only; the GitHub copy ends at errata 11). An `orchestrator.py` and its test were then written but never committed, and the local pytest cache lists all five orchestrator tests as failed on their last run. VERIFIED that the cache says so (`.pytest_cache\v\cache\lastfailed`); SUPPORTED that this was the final state. Nothing after May 13.

### 4.2 What worked

- **The build and execution boundary.** The execution prompt says "You orchestrate slates. You do not build the system ... If Python breaks at runtime, report the error and stop; do not patch the code." VERIFIED, system prompt. It worked: execution halted rather than improvising (errata 12). S1's split between the LLM's role and the code's role is the same discipline.
- **A data-freshness canary.** "If more than 10% of the salary CSV pool is being hard-excluded ... raise it mandatorily before proceeding. This is the data-freshness canary." VERIFIED, system prompt. S1 lacks this.
- **Per-game freshness, not per-slate.** "The cutoff is anchored to each game's start time, not slate lock." Players in late games may use projected lineups. VERIFIED, system prompt. For NBA, a 10 pm ET game's starters can stay "expected" at a 7 pm lock.
- **Honest provenance.** Errata 9: a footer "claiming 'recent FP-derived' when outcome equals base is a provenance lie" that would pollute later calibration. VERIFIED, `v4_13_errata.md`. S1's brief should say, input by input, what was real and what was a fallback.
- **Build-time findings that transfer to NBA**, all VERIFIED in `v4_13_errata.md`:
  - Errata 2: a selection-only MILP lets one multi-position player satisfy two slot minimums at once, producing a lineup that cannot be assigned to DK slots. The fix is selection variables plus assignment variables (`x[p]`, `y[p, slot]`).
  - Errata 3: the same set of players can be placed in slots several ways, so slot assignment must be chosen deliberately in code, not taken from the solver.
  - Errata 7: DraftKings' `AvgPointsPerGame` is season-to-date and is "0.0 (not blank)" for players without prior data (seen on MLB files). Never use it as a projection input. NBA behavior is a BET; the same rule applies.
  - Errata 8: store ownership in one unit (percentage points, 0 to 100) everywhere. "If ownership is stored as 0.125 and a cumulative cap is 87, the cap never binds."
  - Errata 13 (local only): DraftKings player IDs and league player IDs do not overlap, so matching fell back to normalized name plus team, with unmatched players surfaced as warnings. S1's identity map (component 3) is the right answer; this confirms it is needed on day one.

### 4.3 What broke or was painful

- **Too many moving parts for one person.** Each slate needed: `git push` in PowerShell, "Sync now" in claude.ai (the runbook warns the integration "had reliability issues in late 2025"), an OAuth-authenticated connector, a Cloudflare Worker, and a sandbox that reads code from project knowledge. Errata had to be copied from chat into the repo by hand ("Do not claim to have updated the file yourself"). VERIFIED, runbook and system prompt.
- **Building through chat-generated installer scripts.** Code moved from a chat into the repo through 84 KB PowerShell scripts. A patch installer of the same size followed the first one. VERIFIED, local files and commit a14239f ("gitignore: chunk installer scripts").
- **Spec churn by delta.** The PRD is v4.13 and most sections read "Per v4.10", "Per v4.7" or "Unchanged", so the full spec exists only across 13 versions, most not in the repo. VERIFIED, `docs\dfs_os_prd_v4_13.md`. The tool inventory had to be rebuilt "because the tool inventory is split across versions" (VERIFIED, `docs\dfs_os_mcp_tool_inventory.md`). The PRD ends "No v4.14."
- **Effort spent on the wrong kind of rigor.** v4.13's only change is a three-stage solve so that CBC and HiGHS return byte-identical lineups, plus a "collision test" preflight. VERIFIED, PRD section 1. Errata 1 then found the 1e-9 tolerance was tighter than the solvers' own 1e-6. BET: determinism should come from one solver, fixed seeds and recorded outputs (S1 component 18), not from cross-solver parity.
- **Tests did not test the product.** 7,016 lines of tests passed while no function could run a real slate. The "end-to-end" test "builds synthetic Player specs in code and is a regression harness, not a runnable orchestrator." VERIFIED, local errata 12.
- **Documentation drift.** The runbook tells the user to check that the upload file's header is `Entry ID, Contest Name, Contest ID, Entry Fee, P, P, ...`, but the emitter writes slot columns only, for the user to paste "into the right side of a DK template", with `Name (PlayerID)` cells and LF line endings. VERIFIED, runbook Step 5 vs `python\emitter\dk_csv.py` docstring. R6 found DKEntries uses CRLF and recommends bare IDs on the Edit Entries path.

### 4.4 NBA and DraftKings knowledge

- NBA appears only as a future phase. No NBA data.
- **Planned sources clash with R4's terms findings.** Appendix A lists "Injury: ESPN (bulk)" and "Projected lineups (for late games): RotoWire (bulk)". VERIFIED, PRD Appendix A. R4 found both ban automated access. The plan also used The Odds API, which R4 found permits app use.
- **DraftKings upload facts it relied on:** one contest template per file, 500 lineups max per file, desktop-only upload. VERIFIED, system prompt. Consistent with R6.

### 4.5 LLM layer patterns

- claude.ai Projects plus a custom MCP connector plus the code-execution sandbox. This put Claude in the loop for every slate run, inside chat, with no headless path. It does not fit R7's design (Claude Code, repo-level `.claude/`, user-typed commands). VERIFIED (architecture) and BET (fit).
- The execution prompt's communication rules ("No em dashes", "Lead with the point", "Push back") match the style asked for here. VERIFIED, system prompt.
- No hooks, subagents or skills (VERIFIED: no `.claude` folder in the repo).

### 4.6 Architecture ideas vs S1

| dfs-architect idea | S1 | Verdict |
|---|---|---|
| Rank-based objective: `(1-λ-μ) x ceiling_rank - λ x ownership_rank + μ x residual` | S1 optimizes P(top 1%) directly | S1 is better: ranks discard how much better a player is, and λ and μ have no meaning a user can check. |
| Ownership heuristic from salary and projection percentiles | S1 reads ownership off a simulated field | S1 is better; the heuristic can be a day-one sanity check. |
| Exposure caps, max-overlap, "unique core" rules | S1 lets coverage come from the simulation, with guardrails | S1 is better; keep a few guardrails for the user's comfort. |
| Confirmation-gap canary at 10% of pool | Missing | Add (section 5.8). |
| Per-game freshness cutoff | Implicit in B5 | Make explicit. |
| Provenance footer | Run manifest (component 18) and brief (17) | Merge: one honest "inputs" block in the brief. |
| Hosted MCP server, D1, KV, OAuth | Local Python and files | Do not adopt. |

---

## 5. Synthesis by question

### 5.1 What each project was and why it stopped

See the timeline. Pattern (VERIFIED for each case above): every project put specs, infrastructure and tests ahead of one real end-to-end run, and each ended at the first real-world step: a database password, a missing entry point, mock data, or a weak research stage. The user's stated goals were consistent across all of them: persistence, learning loops, a deterministic optimizer, and pushing judgment into structured inputs. What changed between attempts was the runtime surface, not the goals.

### 5.2 What worked well (keep)

1. CLAUDE.md working-style rules plus a lessons file updated on every correction (dfs-os, nba-betting).
2. Plan file, todo file, and one commit per phase with tests (dfs-os, nba-betting).
3. The code-vs-LLM boundary, and an execution role that halts instead of improvising (dfs-os, dfs-architect).
4. Explicit "no action" outputs with stored reasons; append-only snapshots; thresholds in config (nba-betting).
5. A review gate before writing the upload file (dfs-os).
6. Freshness canary, per-game cutoffs, honest provenance, ownership units, slot-assignment variables (dfs-architect).
7. A decision-authority split in CLAUDE.md: Claude owns implementation; the user owns business rules and thresholds (nba-betting).

### 5.3 What broke or recurred

1. **Stalling before the first real run** (all four).
2. **Data freshness and completeness**: 0 of 175 confirmed (dfs-os), the spec's own admission (nba-betting), stubbed injuries and lines (dfs-architect), mocked research (bleeski/NBA).
3. **LLM doing work code should do**: arithmetic, starter inference from salary, HTML page fetching (dfs-os, chat-era OS).
4. **Infrastructure needing admin or many surfaces**: PostgreSQL; Worker, OAuth, sync, installers.
5. **Spec churn**: OS-001 to OS-006 in four days; PRD v4.13 written as deltas.
6. **Windows gotchas repeated across projects**: the same setuptools error in March and April.
7. **Learning gated on 30 slates**, so it never began.

### 5.4 NBA-specific knowledge

- **Data sources:** these projects add no measured evidence on nba_api, the injury PDF, rate limits or blocks; none of them got that far. R4 stays the authority. The one data-source lesson is indirect: LLM page-fetching failed where code calling JSON endpoints succeeds (section 1.3).
- **Modeling tried:** multiplier menus (dfs-os), salary times 5.5 (bleeski/NBA), market-error XGBoost (nba-betting, never trained). None was evaluated on outcomes. VERIFIED absence.
- **Minutes and injuries:** HUPO's usage over 25% and 3-to-15-game window; dfs-os's "primary absence" and "secondary absence" multipliers; the "secondary beneficiary" idea (the teammate whose role changes because the backup plays differently; VERIFIED, `Execution_Project_Template.md`). All untested. Useful as hypotheses for S1's override schema, not as numbers.
- **Measured:** the game-level calibration table in section 2.4.

### 5.5 DraftKings knowledge not in R6

Small, because R6 is thorough:
- An April 15, 2026 NBA Classic salary file in dfs-os matches R6's `Roster Position` table and lacks `Status` and `Starting`; whether 2026-27 NBA files carry those columns is still open (section 1.4).
- `AvgPointsPerGame` is 0.0 for players with no prior data, at least in MLB files (dfs-architect errata 7).
- The prior engines wrote slot-only files for template paste, never Edit Entries files. The new engine's path (R6) is untested by any prior project, so the first preseason upload is the real test.
- "Late swap" was used for pre-lock news re-runs in dfs-os; pin the DraftKings meaning.

### 5.6 LLM layer patterns

- **Tried:** Claude chat Projects with a Python tool (the OS-042 era), the Anthropic API with a key (dfs-os), Claude Code on the web for a one-shot build (bleeski/NBA), Claude Code locally (nba-betting, the dfs-os build), and claude.ai Projects with a custom MCP connector (dfs-architect). VERIFIED.
- **Hooks, subagents and skills:** not used in any of the four repos (VERIFIED). There is **no evidence** here on whether they are effective, expensive or flaky. (The user's current skill library, visible in this session, includes per-sport lineup skills and a skill-architecture rule set, so a later project moved to skills; those repos are covered by other reviewers.)
- **Effective:** CLAUDE.md rules plus lessons files; build vs execution separation; echo-and-confirm of inputs before running (dfs-architect).
- **Expensive:** a 49,697-character compiled prompt per research session with an interactive tool loop and no usage logging (dfs-os); an LLM writing 175 rows of numbers.
- **Flaky:** LLM starter inference, LLM-computed ceilings, JS-rendered pages, a renamed search package, GitHub-to-Project sync, a hidden final message that made the user quit early.
- **Usage limits:** no evidence in these repos. dfs-os paid per token. R7's plan (subscription, user-typed commands, small diffs to subagents) is untested by any prior project.

### 5.7 Architecture ideas the prior projects had that S1 lacks, or tried and failed

**Lacks (add):** freshness canary, per-game freshness rule, honest-inputs block, slot-assignment variables, ownership unit checks, news severity triage, a marginal-entry report, absence duration as an input.

**Tried and failed (avoid):** LLM-written projections; multiplier menus; rank-based objectives; hosted infrastructure for a single-user tool; solver-parity determinism; delta-versioned specs; 30-slate learning gates; template-paste upload files.

### 5.8 Against S1: what we are missing or getting wrong

1. **No forcing milestone for a real end-to-end run.** Add Phase 0: by the last preseason night, run ingest, identity map, a crude projection, the simulator, Showdown enumeration, Classic candidates, a greedy selector and the validator and exporter on the user's real preseason DKEntries files. The user uploads, reads back "uploaded N of N", and the morning-after standings parse. Everything else layers on a loop that already works. BET, grounded in 5.3 item 1.
2. **No data-freshness stop.** Add a "freshness gate" to component 1 or 2 that refuses to proceed silently, and alerts in plain language, when any of these hold. Thresholds are BET; the pattern is VERIFIED from dfs-architect and dfs-os.
   - More than a set share of DraftKings players are unmatched in the identity map.
   - The newest official injury PDF is older than its 15-minute cadence plus a margin.
   - A game within an hour of tip has no starters, expected or confirmed.
   - The schedule date does not match the files' Game Info dates.
3. **No honest-inputs line.** The brief (component 17) should open with one line per input: real, cached (with age), fallback, or missing. Example: "Props: missing for 2 of 5 games, market anchor used team totals only." VERIFIED pattern, dfs-architect errata 9.
4. **Slot assignment is unstated.** Component 13 should use selection plus assignment variables for Classic, and component 14 should choose slot assignment on purpose: late-game players in G, F and UTIL where eligibility allows. S1 B5 says this; tie it to the MILP formulation explicitly so it is not lost. VERIFIED risk, dfs-architect errata 2 and 3.
5. **Ownership units and sums.** Store ownership as percentage points. Assert the field's sums every night: 800% across players in Classic; 100% Captain and 500% UTIL in Showdown (R3). A failed sum is a field-model bug, not a slate fact.
6. **Absence duration.** Add "games missed so far" and "first game without this teammate this season" to the minutes and usage redistribution inputs (component 6) and to the news researcher's override schema. BET, from HUPO.
7. **Validator rules come only from R6 and the downloaded file.** No rule may be imported from bet365-era code (strict cap, 3-per-team) or from MLB code. VERIFIED risk, bleeski/NBA README.
8. **Game-layer calibration targets.** Use section 2.4's numbers as the first acceptance test of component 9: simulated totals about 18 points SD around the market, margins about 13, overtime about 5%, 20-point margins about 19%. VERIFIED arithmetic, SUPPORTED provenance.
9. **Never use `AvgPointsPerGame`**, except as a display hint with 0.0 treated as missing. VERIFIED risk, dfs-architect errata 7 and the dfs-os CLAUDE.md ban.
10. **Scope risk in S1 itself.** S1 lists 21 components, two of them LLM roles, a week before opening night. Prior projects show that breadth before a working loop is how this user's projects stall. Rank components by "needed for a valid, sensible upload" and defer the QA adversary, challenger models and override blending until after the first real nights. BET.
11. **Keep LLM research narrow.** dfs-os's open-ended research agent produced zero confirmed starters in one session. S1 already has the LLM read a deterministic news diff. Keep starter and status confirmation in code (injury PDF parse, the chosen lineup source), and give the LLM only the ambiguous items. VERIFIED risk.
12. **One living design doc, not deltas.** When S1 becomes S2, rewrite it whole with a short "changes" list at the top. Never write "per S1" sections. VERIFIED risk, PRD v4.13.

S1 is **right** where the prior projects were wrong: distributions over point projections, a probability objective, ownership from a simulated field, learning from night one, local Python, and Claude started only by the user.

### 5.9 Reuse candidates

| Candidate | For | Against | Verdict |
|---|---|---|---|
| `nba-betting-system\data\raw\nba_2008-2025.csv` (23,118 games with quarter scores, overtime and lines) | Free, on disk, 18 seasons; quarter and overtime columns can calibrate blowout and overtime behavior | Source, book, and open vs close unknown; license unknown; ends June 2025; team codes need mapping | **Use as a calibration check only**, never as a runtime input. Cross-check with ESPN historical lines (R4). |
| The April 15, 2026 DK NBA salary file (dfs-os sample data) | A real DK NBA file, likely from the user's account | Two-game slate (likely play-in); lacks the `Status` and `Starting` columns | **Use as one parser test fixture** among several. |
| CLAUDE.md working-style rules (dfs-os) and the Decision Authority block (nba-betting) | Proven useful; short; fits a PM owner | Must be cut to fit R7's under-200-line guidance with NBA rules added | **Adapt the text.** |
| Lessons entries on Windows (both projects) | Each cost real time once | None | **Copy into the new lessons file on day one.** |
| `normalize_name` (dfs-os `name_utils.py`; dfs-architect errata 13) and `team_map.py` | Already handle accents, dots and suffixes | Trivial to rewrite; NBA needs more (Jr., Sr., II to IV, nicknames) | **Learn; take the test cases, not the code.** |
| PuLP optimizers (dfs-os, dfs-architect) | Tested | MLB-specific; built around point projections and rank objectives; R2 benchmarked better options | **Do not reuse.** Keep the x and y formulation pattern. |
| DK emitter (dfs-architect) | Tested | Template-paste format, `Name (ID)` cells, LF endings, conflicts with R6 | **Do not reuse.** |
| NBA multiplier menu (dfs-os) | Encodes the user's intuitions | Invented, overlapping numbers | **Do not reuse as numbers.** Use the factor list as a checklist for the override schema. |
| Player and team usage CSVs (nba-betting) | On disk | Seasonal, names only; nba_api gives more | **Skip.** |

---

## 6. Top 10 lessons for the NBA engine

1. **Run the whole loop on real files before making any part good.** Three of four projects died at first contact with reality: a password, a missing entry point, mock data. Make "one real preseason night, uploaded, read back, and parsed the next morning" the first milestone, before Oct 20. (Sections 2.1, 3.1, 4.1.)
2. **Gate every run on data freshness, per game.** The user's own spec says most past errors came from stale schedules, missing injuries or incomplete data, and dfs-os wrote upload files from a session with 0 of 175 confirmed starters. Add a plain-language freshness stop and an unmatched-player canary. (Sections 1.3, 2.4, 4.2.)
3. **Keep the LLM out of arithmetic, starter confirmation and page scraping.** LLM-computed ceilings were a fixed multiple of the mean; the LLM inferred starters from salary; HTML fetching broke. Code reads structured sources; the LLM gets only ambiguous news, as schema-checked records. (Section 1.3.)
4. **Model distributions and calibrate them to measured numbers.** Every prior engine scaled a point projection. Start S1's game layer from the measured targets: totals SD about 18, margin SD about 13, overtime about 5%, 20-point games about 19% and rising. (Section 2.4.)
5. **Zero-admin, one-surface infrastructure.** No database server, no hosted Worker, no OAuth, no chat-to-repo sync, no installer scripts. Local Python, files and SQLite or DuckDB, run from Claude Code in the repo. (Sections 2.3, 4.3.)
6. **One living spec, rewritten whole; freeze only after the first real nights.** Six OS revisions in four days and a PRD at v4.13 written as deltas preceded zero working slates. (Sections 1.1, 4.3.)
7. **Learn from night one at the player level.** Both earlier designs gated calibration on 30 slates and logged zero rows. S1's per-player minutes, points, ownership and threshold checks from night one are the fix; keep them. (Section 1.3.)
8. **Fill purchased entries through the Edit Entries file and confirm the readback.** Both prior DFS engines wrote slot-only files for template paste, and one runbook contradicted its own emitter. The R6 path has never been exercised by any prior project, so test it on a cheap preseason contest. (Sections 1.5, 4.3.)
9. **Make slot assignment explicit and purposeful.** Multi-position players need selection plus assignment variables, and the chosen assignment should place late-game players in G, F and UTIL for late swap. (Section 4.2.)
10. **Make outputs honest and verify every "done".** The brief must say which inputs were real, cached, fallback or missing. An agent's "production ready" is not evidence: acceptance is a real file through the real pipeline, checked by code. Seed the lessons file with the Windows gotchas both projects hit. (Sections 3.2, 4.2, 1.3.)

---

## Appendix: commands and evidence

- dfs-os: `git log`, `git ls-files`; read-only SQLite queries (`file:dfs.db?mode=ro`); file reads of `DFS_OS_PRD.md`, `CLAUDE.md`, `lessons.md`, `tasks\`, `reference-docs\`, `sessions\`, `dfs\research\`.
- nba-betting-system: file reads of `CLAUDE.md`, `README.md`, `SPEC.md`, `tasks\`, `config\settings.yaml` (credentials redacted on display), CSV headers only.
- Scratchpad scripts (run with `python -I`, reading data files by path): `rr4\lines_stats.py`, `rr4\lines_stats2.py` (game-line statistics), `rr4\ceil_ratio.py` (dfs-os ceiling ratios).
- bleeski/NBA: `gh repo view`, `gh api .../commits`, `gh api .../git/trees/<branch>?recursive=1`, `gh api .../contents/<file>?ref=<branch>`, `gh issue list`, `gh pr list`.
- dfs-architect: `gh repo clone` into the scratchpad (`repos\dfs-architect`), file reads; local copy at `C:\Users\benja\Documents\ben_projects\dfs-architect` read for uncommitted errata 12 and 13 and the pytest cache.
- Not opened, per instructions: mlb-dfs, nfl-dfs, nhl-dfs, golf-dfs, soccer-dfs.
