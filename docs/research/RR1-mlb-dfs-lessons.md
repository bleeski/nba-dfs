# RR1. Lessons from the user's MLB DFS engine (bleeski/mlb-dfs)

**Date:** 2026-10-13. **Repo:** `C:\Users\benja\Documents\Claude\mlb-dfs` (819 commits, 662 of them non-merge, 2026-07-17 to 2026-10-13; 155 GitHub PRs from 2026-09-17; zero GitHub issues). **Method:** read-only review of CLAUDE.md, CLAUDE.local.md, the 2026-07-22 build post-mortem, the 2026-09-22 deadline-delivery audit, ROADMAP.md, targeted reads of CHANGELOG.md (2.8 MB) and backlog.md (1.2 MB), hosts.md, the calibration ledger, the standings findings doc, delivery and agent-run records, test names, every commit subject, the PR list, and the user's four MLB desktop skills. Three helper agents mined the CHANGELOG, the ledger, and the PRs and skills; their findings are folded in and labeled. Nothing in the repo was modified or run.

**Labels.** VERIFIED: seen in the repo, with a file path, commit hash, R-number, or PR number. SUPPORTED: inferred from several signals, or computed by me or a helper agent from repo files. BET: my judgment.

**Vocabulary.** A *draftgroup* is one DraftKings slate with one player pool. *R-numbers* (R286, R386, and so on) are the MLB repo's backlog item numbers; every change and its reasoning is filed under one in CHANGELOG.md. *Review-grade* is the MLB repo's label for a legal file that skipped some quality gates. *Satellite* is a contest that pays tickets to a bigger contest, often one seat.

---

## The answer first

1. **The MLB engine never showed an edge. Its lineups ran at or below random, and delivery failures were its clearest, most avoidable single-night losses.** Since delivery records began (2026-09-19), Classic entries finished at the 49.8th percentile [44.7, 55.7], indistinguishable from random, and Showdown at 54.9 [52.4, 58.0], worse than random (higher is worse). Across all 7,598 paid MLB entries, including play before the engine, the finish was 52.05 against a 50.39 uniform reference, and the bottom-decile excess stayed at +2.5 points even with blank entries removed, so the lineups lost on their own. On top of that: 67 engine-era entries (93 counting earlier play) locked blank because a later draftgroup was never filled, one 37-entry slate had no file at lock, and one late swap had 7 of 16 rows rejected by DraftKings. VERIFIED (CHANGELOG R494 entry, commit `1c50378`; R286 entry, commit `6ebcdb9`; CHANGELOG R29(1), commit `d6c160c`).
2. **About four fifths of the effort went to process, records, and correctness plumbing; about one sixth went to strategy.** The repo holds roughly 100,000 lines of production Python, 79,000 lines of tests, 8 MB of markdown, a 1,656-line nightly skill, and a 10,423-line build script. VERIFIED counts; the split is SUPPORTED.
3. **Its strategy beliefs ran opposite to what the standings showed.** The engine built 4-man stacks for 72.5% of entries (the field: 21.6%), built 5-2-1 stacks almost never, and leaned contrarian, while top-decile lineups in the same contests were chalkier than the field. In Showdown it under-used pitcher captains (about 40% against winners' 65.5%) and over-used 5-1 builds (81% against the field's 37%). VERIFIED (ROADMAP "Where the money is", `STANDINGS_GREENFIELD_FINDINGS_2026-08-28.md` section 1).
4. **The things S1 is built around were never built in MLB.** The engine had no contest simulation, no field model, and no payout model, on purpose: a "Do not build" register forbade them until stakes and ownership were settled. An early simulator was retired because its spread was a fixed multiple of each player's mean. Payout tables and min-cash lines were "DATA BLOCKED" all season. VERIFIED (`docs/backlog.md` "Do not build (updated)"; `MLB_Classic.md` section 16; standings findings section 1, item 5).
5. **The patterns that did work are worth keeping as ideas, not as code:** a legal baseline file before any research, every check classed as validity, strategy, or process, an independent preflight that re-reads the output, a plan of every draftgroup in lock order, and a results ledger that grades from the user's own DraftKings export with honest intervals.

---

## 1. Architecture: what the engine does end to end

**Languages and libraries (VERIFIED, `CLAUDE.local.md`, `requirements.lock`).** Python 3.11 to 3.13, numpy, pandas, pydantic, and `scipy.optimize.milp` (the HiGHS solver) as the only lineup solver (CLAUDE.md, "Authority").

**Size (VERIFIED, `git ls-files` line counts).** `mlb_engine/` 54,905 lines; `tools/` 34,249; `skills/generate-lineups/scripts/build_slate.py` 10,423 (one file); `tests/` 79,171; `.claude/hooks/` 1,450. The largest engine files: `execution_pipeline.py` 8,800, `contest_allocator.py` 5,621, `optimizer_v3.py` 5,042, `showdown_theses.py` 3,747, `preflight_upload.py` 3,601. 488 markdown files totaling about 8 MB.

**Storage (VERIFIED).** Flat files only, no database. Per-slate inputs in `data/slates/<date>/` (gitignored); immutable run folders `runs/<run_id>/` (675 on disk); deliverables in `outputs/<date>/`; one JSON delivery record per delivery in `data/deliveries/` (172 records); mined standings in `data/archive/<date>/`; the strategy memory in `ledger/MLB_Classic_Calibration_Ledger.md` (778 KB of markdown).

**Main components (VERIFIED, CLAUDE.md "Build contract", `MLB_Classic.md` sections 4 to 11).**

| Stage | What it did |
|---|---|
| Intake | `live_data_adapters.build_slate_pool`: DKSalaries is authoritative for IDs, salaries, eligibility, and the `Starting` column; batting orders ranked per team: DK `Starting`, then a pasted mlb.com page, then an API pull. |
| Projection | `Base x F1 x F2 x F3 x F4 x F5`, where Base is normally DraftKings' own AvgPointsPerGame and the F terms are hand-set multipliers for market totals, batting order, skill, matchup, and park/weather (`MLB_Classic.md` section 6). |
| Candidate bank | MILP builds a diverse bank of lineups, resumable and cached (`bank_cache.py`). |
| Allocation | One joint MILP assigns one bank lineup to each Entry ID under exposure, stack, pitcher-pair, overlap, and game caps set by contest "posture" (`contest_allocator.py`). |
| Certification and export | Pre- and post-export gates; writes `runs/<id>/final/DKEntries.csv`, never rewritten. |
| Preflight | `tools/preflight_upload.py`, a separate re-check of the delivered file (exit 0 clean, 2 hard fail, 3 I/O error, 4 forced). |
| Late swap and repair | `tools/late_swap.py` and `tools/repair_entry.py` replace benched or scratched players in unlocked slots. |
| Showdown | A "thesis ladder" of hand-weighted game scripts with captain and overlap caps; always review-grade, never certified (CLAUDE.md "Showdown"). |
| Archive and learning | `field_miner.py` parses standings into the archive; the ledger records findings; from October, `results_ledger.py` grades the user's DraftKings entry-history export. |

**How a night ran (VERIFIED from the skills and PRs, summarized by a helper agent; timings as noted).**

1. The user downloads DKSalaries and DKEntries by hand for each draftgroup and attaches them to the chat (cloud) or leaves them in Downloads (Windows). He re-downloads as batting orders post; one 10-game slate on 2026-09-22 used three downloads and about 80 minutes of rebuilds and repairs (PRs #26, #27).
2. Optional pastes: the mlb.com starting-lineups page, an odds table, and evidence for opener or bulk-pitcher games.
3. Claude runs: lock-clock check, environment probe, `stage_slate.py --from-attachments` (finds files by header, not name), `day_plan.py` (added 2026-10-12), `autobuild.py` (a supervisor with a 12-minute wall), `qa_portfolio.py`, an ownership prediction, `preflight_upload.py`, then hands the file and its sha256 into the chat.
4. The user uploads by hand. He allows about 5 minutes for it, so the effective deadline is first lock minus 5 (ROADMAP "Facts Ben answered", F-1).
5. As lineups post, repairs and late swaps, each preflighted and re-uploaded by hand.
6. Next day: the user downloads standings for each contest from a clickable checklist; periodically, the DraftKings entry-history export.
7. Separately, DEV sessions change the engine, gated by a 9-minute test suite and CI.

**Timing (SUPPORTED, from delivery-record file names, which mark when a record was written, not when a file was uploaded).** Across 19 Classic slates from 2026-09-19 to 10-07, the first delivery record landed between about 11 and 139 minutes before lock, most often 20 to 60 minutes before. Slates often carried several records (up to 11), because of rebuilds and repairs. By 2026-10-12 the tracked records held 101 deliveries (40 certified, 49 review-grade, 12 baselines) and 46 refusals (SUPPORTED, CHANGELOG agent, R499 premise 5). The September audit concluded the records "cannot support an on-time delivery rate" (VERIFIED, deadline audit section 7). One slate (2026-09-25, `2140_4g`) went past lock and was rebuilt on its later games only (commits `24c7bb0`, `1b7e464`; PR #67).

**Hosts (VERIFIED, `docs/hosts.md`).** Three hosts in three months: Cowork (a sandbox whose shell calls were killed after about 45, later 130, seconds), a Claude Code cloud container (ephemeral, often reached from a phone, with blocked data feeds), and the user's Windows laptop (DEV only). The repo spent dozens of commits adapting to each.

---

## 2. What worked well (keep as patterns)

1. **Delivery first, with every check classed V, S, or P** (VERIFIED, R386, commit `424c92d`; `MLB_Classic.md` section 2). V is validity (IDs, salary, slots, locks, exact bytes) and never relaxes. S is strategy (exposures, stacks, overlap) and relaxes under deadline. P is process (feeds, tests, research) and is recorded but never withholds a valid file. This came out of the 2026-09-01 no-file night and is the single best rule in the repo.
2. **Baseline first** (VERIFIED, R389, commits `799631f`, `1ad76cf`, `29be775`). An entry-mapped legal file is written before research or enhancement. The record cannot credit it with stopping blank entries: blanks stopped after 2026-08-10 (0 of 2,094 since, R494), six weeks before baseline-first landed on 2026-09-24 and 25. Keep it as a pattern on first principles (BET): it directly answers the 2026-09-01 no-file night.
3. **An independent preflight that re-reads the delivered bytes** (VERIFIED, `tools/preflight_upload.py`; tests in `tests/test_upload_integrity.py`). It catches blank rows, partial rows, duplicate Entry IDs, over-cap lineups, float-formatted Entry IDs, truncation, started games, and a file whose sha256 does not match its record. `--force` never reports clean.
4. **Never trim the legal player pool to fit a compute limit** (VERIFIED, post-mortem section 3; CLAUDE.md "Hard walls"). A limit may cut search effort, never the players the solver may see, because a trimmed pool is invisible in the output.
5. **Measure before working around** (VERIFIED, post-mortem section 9; `tools/solver_probe.py`). The 2026-07-22 session lost about 15 minutes at T-30 guessing at a bottleneck that a 10-second timing would have shown.
6. **Determinism**: sorted sets before the solver and `PYTHONHASHSEED=0` (VERIFIED, CLAUDE.md "Hard walls"). Replays are exact (R384's replay tool reproduces 353 of 361 archived contests; SUPPORTED, ledger agent).
7. **sha256 on every delivered file and in every brief** (VERIFIED, CLAUDE.md "Hard walls"; delivery records). It is the only way to tie a finish back to a build.
8. **The DraftKings wall, enforced three ways**: the contract, a settings deny list for every draftkings.com domain, and a PreToolUse hook that blocks commands naming it (VERIFIED, `.claude/settings.json`, `.claude/hooks/guard_commands.py`, per helper agent).
9. **Grading from the user's own DraftKings entry-history export** with a per-entry uniform reference and slate-bootstrap intervals (VERIFIED, R496, `tools/results_ledger.py`). This is the first honest "are we any good" measurement the project produced, and it arrived in October.
10. **The rigorous standings study** (VERIFIED, `STANDINGS_GREENFIELD_FINDINGS_2026-08-28.md`): slate-clustered bootstrap, a chronological discovery and validation split, false-discovery control, and permutation tests. Only four findings survived. That is the right bar for strategy claims.
11. **Premise checks before building** (VERIFIED, `.claude/agents/dfs-premise.md`; backlog). The agent file says a filed backlog entry "has been wrong about the mechanism more often than right" (per helper agent), and the R286 post-mortem itself carried a confident wrong diagnosis.

---

## 3. What broke, and what recurred

### 3a. The incidents that cost entries or nearly did (VERIFIED unless marked SUPPORTED)

| Date | What happened | Root cause | Fix |
|---|---|---|---|
| 2026-07-22 | First-lock clock wrong by 65 minutes, in the direction that locks you out | Doubleheader legs keyed by matchup only; the second leg's time overwrote the first | Key games by matchup plus start time; cross-check the clock against DKSalaries `Game Info` (post-mortem section 2; commit `0a5a805`) |
| 2026-07-22 | Seven starting pitchers dropped from the pool to fit a 43-second call limit | A compute limit treated as a strategy choice; the trim did not even fix the timing | "Never trim the legal pool" rule (post-mortem section 3) |
| 2026-07-29 | DraftKings rejected 7 of 16 late-swap entries | A hand-typed list of locked teams went stale during a 40-minute swap; three games locked underneath it and the verifier still printed PASS | Locked teams re-derived from the clock on every run (CHANGELOG R29(1), commit `d6c160c`) |
| 2026-07-20 to 2026-08-03 | 67 engine-era entries locked blank in four later-starting draftgroups (07-20 Turbo 15 of 15; 07-22 Showdown 17 of 17, the same day as the doubleheader scare; 08-03 Turbo 15 of 17; 08-03 Showdown 20 of 20). The export shows 93 blanks in all, 26 of them from April and May, before the engine | Later draftgroups on a day were never built; no tool listed the day's draftgroups. 08-03 followed three failed scipy installs in the sandbox | `tools/day_plan.py` (R499, commit `664a8af`, PR #146) |
| 2026-07-29 | A pitcher from a postponed game reached several entries "before a manual catch" | DK's `Game Info` held the literal text "Postponed", which matched no parser rule | R26, commit `831dfd7` |
| 2026-07-29 and 30 | Review-grade Showdown files were labeled `upload_ready` on two live deliveries | Label set without checking the certification it claimed | R34 (SUPPORTED, CHANGELOG agent) |
| 2026-08-01 to 08-14 | Dependency installs failed five times in the sandbox (disk full twice, scipy missing); 17 of 20 minutes lost on 08-03 | Host not reproducible; installs done at build time | R42; later a pinned venv (SUPPORTED, CHANGELOG agent) |
| 2026-08-08 | 9 entries shipped with only 7 distinct lineups and one pitcher in 5 of 9 | Bank search budget silently floored at 5 seconds, so about 2% of the planned search ran; the operator loosened caps instead. "Fourth instance of the pattern in eight days" | R98, R390 "a thin bank delivers" (SUPPORTED, CHANGELOG agent) |
| 2026-09-01 | 37 entries across 16 contests had no file at the 19:40 lock; a hand-built file existed at about 20:00, after the session was stopped, by which time three games had started and were out of reach | The error message named a bank-level cause, so the supervisor kept growing the bank; the real blocker was a slate-level floor. A self-imposed rule (no hitter facing your own pitcher) was enforced as if it were a DraftKings rule. The preflight had no started-game check | R286 to R289, commit `6ebcdb9`: failing checks printed first, the convention demoted to a warning, a started-game check added |
| 2026-09-02 | The repair tool wrote a file with the entry block doubled (13 duplicate Entry ID failures); a hand-patched file shipped | Repair tool rewrote rows instead of editing cells | R292, commit `924bb4f`. A sibling on 10-07: `--dead a,b` repaired only the second player (SUPPORTED, backlog_inbox fragment) |
| 2026-09-04 | One handoff said "T-6" at a real T-18; another session spent 24 minutes without reading a clock | Clock figures stated from memory | R318: print Eastern time in every build call (SUPPORTED, CHANGELOG agent) |
| 2026-09-25 | 4-game slate: a later refinement missed the 21:40 lock | The session believed the whole draftgroup closes at first pitch and told the user the rebuild "likely still can't be uploaded" | Rebuild on the two open games only (PR #67, commits `24c7bb0`, `1b7e464`). See section 5, item 10: the export suggests late filling does work |
| Through 2026-10 | Of 480 Entry IDs in delivery records, 447 appear in more than one record and 395 with different rosters, so which file was uploaded is unknown | Several deliveries per slate, all labeled "candidate"; manual upload left no trace | R497 resolves the entered lineup by matching scores in standings (CHANGELOG R497 entry) |

### 3b. Recurring themes in commit subjects (SUPPORTED)

Counts are over the 662 non-merge commit subjects, using the regex shown. This repo's subjects rarely say "fix"; the usual form is "R123: X stops doing Y", so keyword counts understate fixes. Each theme lists example commits.

| Theme | Count | Regex (case-insensitive unless noted) | Examples |
|---|---|---|---|
| Process: records, board edits, adjudications, landings, pins | 197 | ` record: \| Board[:]\| [Aa]djudicat\| landing[:]\|Quick Card pin\| backlog[: ]\|docs only\|CHANGELOG (entry\|gate\|carries\|says)` | `bcd03af`, `06c44be` |
| Tests, gate, audit, CI, flakes | 99 | `\bgate\b\|\baudit\b\|\bCI\b\|flake\|test_core pin\|pin \d` | `adb40eb`, `fb9e8ac` |
| Late swap or repair | 51 | `late.swap\|late_swap\|\brepair` | `38b022b`, `5a309f5` |
| Standings pulls and archive mining | 33 | `standings\|zero-byte\|unsettled\|\bmine\b\|miner` | `686c931`, `2d7c636` |
| A tool or record said something untrue (false clean, silent, "stops claiming") | 28 | `false clean\|stop(s)? (claiming\|asserting\|attesting\|telling)\|silent\|fail(s)? (open\|loud)\|\bfalse\b\|truthful` | `d51aea9`, `b83e553` |
| Showdown captain role | 26 | `captain\|\bCPT\b` | `fb21235`, `0a21839` |
| Defects found by a review of the session's own work | 26 | `review fixes\|defects an adversarial\|review pass on my own\|review:` | `03f1b20`, `c7a8cd1` |
| Host, sandbox, dependencies, call budget | 25 | `\bhost\b\|sandbox\|cowork\|container\|scipy\|\bpip\b\|venv\|wheel\|install\|call budget\|pylibs` | `b9bf147`, `62415fb` |
| Clock, ET or UTC, lock, deadline, started game | 24 | `\bET\b\|\bUTC\b\|calendar\|clock\|deadline\|past-lock\|first pitch\|started\|lock truth\|lock-clamp` | `0a5a805`, `3db5a96` |
| One authority for a rule that had drifted copies | 23 | `\bone (ET\|id\|title\|owner\|team-code\|clock\|definition\|reading\|...)\b\|N\+1\|sibling` | `baaf682`, `3db5a96`, `ecd0e68` |
| Pitcher role (opener, bulk arm, declared starter) | 21 | `opener\|bulk arm\|PO token\|declare` | `fae8c24`, `0ef231f` |
| Salary-file resolution, wrong slate, draftgroup | 15 | `salary (file\|resolution)\|wrong slate\|wrong draftgroup\|draftgroup` | `0a5a805`, `5f533df` |
| Player or Entry IDs, Excluded column | 14 | `entry id\|\bids?\b\|id dtype\|id-string\|Excluded` | `baaf682`, `ecd0e68` |
| Names, accents, crosswalk | 9 | `accent\|crosswalk\|nickname\|name form\|name-form\|shared DK name` | `3575103` |
| Doubleheader or postponed game | 7 | `doubleheader\|postpone` | `0a5a805`, `831dfd7` |
| Team codes | 4 | `team.code\|abbrev\|ATH->OAK\|team-code` | `ad690f7` (DK uses ATH, not OAK) |

**Cross-check by R-number theme (SUPPORTED, CHANGELOG agent; estimated from backlog sections and CHANGELOG entries that hit three or more theme keywords, so ranges, not exact counts).**

| Theme | Estimated R-items | Examples |
|---|---|---|
| Showdown CPT/UTIL handling | 30 to 45 | R235, R39, R34, R153, R250 |
| Late swap and repair | 25 to 40 | R25, R29(1), R428, R468 |
| Solver infeasible, timeouts, thin bank | 20 to 35 | R98, R294, R390, R158 |
| Git, claims, multi-session collisions | 20 to 30 | R24, R29(4), R109, R110 |
| Salary-file columns (Status, Starting, Excluded, Postponed) | 15 to 25 | R26, R143, R159, R289, R471 |
| Host and sandbox time budget | 15 to 25 | R271, R349, R415, R290(c) |
| Eastern clock, timezone, lock | 12 to 20 | R65, R58, R318, R460 |
| Contest, entry, draftgroup identity | 10 to 15 | R70, R446, R403, R473 |
| Standings and results parsing | 10 to 15 | R95, R341, R472 |
| Test or audit gate red | 10 to 15 | R348, R152, R478, R486 |
| Player ID and name crosswalk | 8 to 12 | R151, R165, R55, R133 |
| Team codes | 5 to 8 | R33, R59, R248 |
| Windows paths and encoding | 5 to 8 | R477, R478 |
| Determinism and flaky tests | 6 to 8 | R487, R28, R373 |

**What the pattern says (SUPPORTED).**
- **The same rule lived in several places and drifted.** Examples: four different clocks (R65 "one ET calendar authority"), several readers of a roster cell (R68: three more raw readers found in `build_slate.py`), several salary-file resolvers (R234), several title parsers (R447 "one title reader"). This is the most common root cause in the repo, and it is a size problem: one 10,000-line script and several 5,000 to 9,000-line modules.
- **Checks that reported success without checking.** 28 subjects are about a gate, record, or report that claimed something it had not verified (R51 and R52 "both upload gates stop returning a false clean", commit `6fa0fa6`).
- **Every self-review found defects.** 26 subjects record defects found by reviewing the session's own commits. Claude-written code needed an independent review pass every time.
- **Showdown role identity kept breaking.** The captain row and the UTIL row of one player were counted as two players (R235, commit `0a21839`), and the standings miner's duplicate key ignored which player was captain (standings findings, item 4). That bug is still open per the findings doc.

---

## 4. What was painful to operate nightly

1. **Many manual downloads, repeated.** Salaries and entries per draftgroup, re-downloaded as lineups posted; standings one contest at a time (342 contests were waiting on 2026-10-02, PR #102); the entry-history export periodically. VERIFIED (`data/standings/CONTESTS_AWAITING_STANDINGS.md` cited in CHANGELOG R497 entry).
2. **Repairs after lineups posted were the most common late work.** Benched hitters had to be replaced after the first upload on many slates (PRs #26, #27, #44, #123; commits `7d34869`, `957e7d3`, `a47f69b`). On 2026-09-22, 11 of 18 entries held a benched player after two teams posted late (PR #44, per helper agent). VERIFIED.
3. **Time pressure ate quality.** The CLAUDE.md T-schedule skips the test gate at T-30, opens every binding control at T-15, and hand-builds at T-6 (VERIFIED, CLAUDE.md "T-schedule"). The 2026-07-22 build used about 35 minutes of a 40-minute window (post-mortem). One late-swap refinement on 2026-07-28 took about 75 minutes and more than 30 tool calls (SUPPORTED, CHANGELOG agent, R25).
4. **Host churn.** Each move broke the first command of a build: a hardcoded Cowork path failed on every other host (PR #3); the cloud container could not reach statsapi, the odds API, Savant, or FanGraphs and had no `.env` for keys, so the odds factor was neutral on every cloud build (`docs/hosts.md`; delivery record 2026-09-25 shows "statsapi unreachable, odds unreachable"); on Windows, `python` resolves to an interpreter without scipy, the gate takes about 9 minutes and has hung, a sleeping laptop killed an overnight run, and tracked fixtures carry a ReadOnly attribute that breaks tests (VERIFIED, `CLAUDE.local.md`).
5. **A queue of decisions only the user could make.** ROADMAP "Decide these first" held at least nine open decisions (D-1 to D-12) on topics like stakes, captain caps, and satellite routing, each written in dense engine language. VERIFIED.
6. **Errors a non-engineer had to decode.** Refusal messages named internal controls ("shared_players_floor", "max_sp_pair_repetition"), and on 2026-09-01 the message pointed at the wrong lever (R286). CHANGELOG entries run to hundreds of lines of engine prose. VERIFIED.
7. **Uncertainty about which file went in.** Several deliveries per slate and no upload confirmation (section 3a). VERIFIED.
8. **Multi-session collisions.** Three uncoordinated Cowork sessions sharing one folder clobbered each other's staging (CHANGELOG 2026-07-28 note). The response was a claims and roles system (BUILD, ARCHIVE, DEV), a PreToolUse guard, and branch-per-session rules. VERIFIED. Much of the 1,450 lines of hooks exists to police concurrency (SUPPORTED, helper agent).
9. **Usage limits: no recorded incident.** No file in the repo mentions plan usage limits, five-hour windows, or weekly limits (VERIFIED absence, grep for "usage limit|session limit|five-hour|weekly limit" over CHANGELOG, backlog, ROADMAP; helper agent searched all files). The repo never measured tokens either: agent-run records carry durations only. This is a measurement gap, not evidence that limits did not bite.

---

## 5. Hard-won DraftKings knowledge

Facts the MLB repo learned or confirmed. Items marked NBA-check need confirming on an NBA file before relying on them.

**Files and identity**
1. **DKSalaries is the authority for IDs, salaries, teams, and eligibility; never correct it against real rosters** (VERIFIED, CLAUDE.md "Authority"). DK codes can differ from every other source: DK uses ATH after the A's relocation (commit `ad690f7`); feeds say AZ where DK says ARI; FanGraphs uses WSN, TBR, CHW, KCR, SDP, SFG (post-mortem section 5). NBA-check: map every source's team codes to DK's at ingest and fail on any unmapped code.
2. **Identify files by their header, not their name.** A re-attached file can land under a hashed name while the generic name still points at the older upload, and "a stale-but-valid salary file ... certifies and reports clean gates for the wrong slate" (VERIFIED, `skills/generate-lineups/SKILL.md` "Confirm which slate you were handed"). State the slate identity (games, first lock, contest IDs) back to the user before solving.
3. **Several Classic draftgroups can share a date** (main and night slates). The repo tags each by first lock and game count, such as `1905_10g` (VERIFIED, SKILL.md). DK saves the plain `DKSalaries.csv` name for whichever slate was clicked last, so two downloads in a row overwrite each other in Downloads (SUPPORTED, CHANGELOG agent, R70).
   - **`Game Info` can hold the literal text "Postponed"** instead of a time (VERIFIED, R26, commit `831dfd7`). A parser that does not know the word lets a postponed game's players through.
   - **DK's own `Starting` and `Status` columns were often ahead of third-party feeds** and became the first source for MLB batting orders (VERIFIED, R143). NBA-check: whether NBA salary files carry a useful `Status` close to lock.
4. **Read slot geometry from the file's header.** A writer that padded Showdown rows to the Classic width overwrote DK's Instructions column, and the preservation check exempted the very columns it destroyed (VERIFIED, `mlb_engine/entries/dk_entries_manager.py`, docstring of the template writer).
5. **Spreadsheet artifacts break IDs.** Float-formatted Entry IDs (for example `1234567890.0` or scientific notation) once read as zero entries; there is a dedicated preflight test (VERIFIED, `tests/test_upload_integrity.py`, `test_float_formatted_entry_ids_fail_instead_of_passing_as_zero_entries`).
6. **One parser for roster cells.** Re-downloaded or repaired files carry `Name (ID)` cells; readers that took raw cells scored them as unknown (VERIFIED, CHANGELOG R68).

**Upload rules**
7. **The user allows 5 minutes to upload, so the effective deadline is first lock minus 5** (VERIFIED, ROADMAP F-1, the user's answer; it is his stated allowance, not a measurement).
8. **DK accepts a partial file only when unresolved rows are removed, not left blank** (VERIFIED, ROADMAP F-2, the user's answer). The repo's earlier text said the opposite twice before being corrected, and the removed-rows partial file was never built or tested (SUPPORTED, CHANGELOG agent: R290(c), R386, R401 still pending).
9. **DK allows one lineup in two entries of one contest; the user never wants it** (VERIFIED, ROADMAP F-3). The repo treats this as a "never relax" rule.
10. **Blank reserved entries that are never filled score zero** (VERIFIED, R499 table). **Whether a blank entry can still be filled after first lock is contradictory inside the repo.** On 2026-09-25 the session told the user DK "locks the whole draftgroup at first pitch" (commit `1b7e464`). But on 2026-09-01 there was no file at the 19:40 lock, a file was built at about 20:00, and in the entry-history export none of the 48 entries in the 19:40 contests that day scored zero (my aggregate count of the export). That suggests DK accepted lineups for blank entries after first lock, using only players from games not yet started. An alternative explanation: the user may have entered some lineups by hand in DK's web page before lock. SUPPORTED, not VERIFIED; only the user can say which happened. This matters for NBA washout planning; settle it with one $0.25 test (fill a blank Classic entry after the first game tips).
11. **Late swap: re-derive locked games from the clock at the moment of upload, every time.** A static list went stale and cost 7 of 16 rows (VERIFIED, CHANGELOG R29(1)). The preflight's `--as-of HH:MM` reads today's Eastern date, so a replay after midnight needs the full ISO time (VERIFIED, `CLAUDE.local.md`). R6's open question 2 (what DK accepts in a locked cell: bare ID, `Name (ID)`, or the `(LOCKED)` suffix) stays open: a grep of the MLB late-swap reference and code did not show which form MLB wrote into locked cells.
12. **Conventions are not DK rules.** The engine refused lineups with a hitter facing the user's own pitcher; DK allows it, and 18.7% of 102,201 field entries did it, including the top three in one contest (VERIFIED, CHANGELOG R286 entry, premise 4). Encoding a convention as a hard rule helped cause the no-file night.

**Showdown**
13. **CPT and UTIL rows are roles of one person, not two players.** Ownership priors and duplicate counts went wrong when they were treated as separate players (VERIFIED, R235, commit `0a21839`; standings findings item 4). Duplicate lineups must be keyed on (captain person, set of UTIL persons).
14. **A Showdown game locks all at once**, so there is no Showdown late swap (VERIFIED, CHANGELOG R494 entry, correction 5).

**Standings and results files**
15. **A standings export pulled before the slate settles comes back zero-byte**, and the old tool then counted it as pulled (VERIFIED, R95, commit `2d7c636`). **Exports also appear to age out some days after settlement**: five contests came back empty on a twelve-day-old pull (VERIFIED record of the loss, `686c931`; the aging cause is SUPPORTED, stated in the ledger as a theory). About 25 contests were lost this way (SUPPORTED, ledger agent).
16. **Player points are the same in every contest of one draftgroup**, so one standings pull per draftgroup recovers every lineup's score; ownership still differs by contest (VERIFIED, R497). Standings lineups carry player names, not IDs, so they must be matched by name against that slate's salary file (SUPPORTED, CHANGELOG agent). A browser's " (1)" suffix on a re-downloaded zip once broke contest-ID extraction (SUPPORTED, backlog_inbox fragment of 2026-10-05).
17. **The entry-history export** has `Contest_Entries`, `Entry_Fee`, `Prize_Pool`, `Places_Paid`, `Place`, `Points`, and winnings split into cash and ticket (VERIFIED header of `data/reference/draftkings-contest-entry-history_2026-10-09.csv`). The 2026-09-15 copy omitted GPP entries; the 10-09 copy covered all types (VERIFIED, backlog rider on R13). Ticket face value is not realized value, and the user's promotional channel was never measured (VERIFIED, CHANGELOG R494 entry).

**Time zones**
18. **Use one Eastern-time authority.** A container on UTC reads tomorrow's date after 8 pm Eastern, exactly when a night slate is live; this put unsettled contests on the pull list (VERIFIED, R95 and R65, commits `2d7c636`, `3db5a96`).

**Contest metadata**
19. **Contest identity comes from the contest name.** The repo keeps a curated table of name patterns (Dime Time, Quarter, Jukebox, and so on) with buy-in, type, and default payout shape (VERIFIED, `data/reference/dk_contest_archetypes.csv`), reads entry caps from titles, and matches " SE" as a whole token (VERIFIED, R446 and R447, commit `c1c8f3c`).

---

## 6. Data sources

| Source | Used for | What went wrong | Evidence |
|---|---|---|---|
| DraftKings (manual files only) | Salaries, entries, `Status`, `Starting`, standings, entry history | Never automated, by terms; every file by hand | VERIFIED, CLAUDE.md "Hard walls"; settings deny list |
| statsapi.mlb.com | Lineups, probable pitchers, handedness | Blocked by the cloud container's network policy | VERIFIED, `docs/hosts.md`; delivery record 2026-09-25 |
| mlb.com starting-lineups page (pasted) | Primary lineup source from R32 | Three different page layouts; parser rewritten several times (R117, R429) | VERIFIED, commits `17a6966`, `22fa7af` |
| RotoWire | Projected lineups for unposted teams | Parser silently returned empty (R65) | VERIFIED, commit `3db5a96` |
| FanGraphs | Platoon splits, pitcher stats | Returns 403 to Python's urllib and 200 to curl; refreshed by hand from a browser-saved page; pitcher K-rate moved to MLB StatsAPI (R278) | VERIFIED, `docs/hosts.md`; backlog R107; commit `50d1b9e` |
| Baseball Savant | Expected stats | Manual refresh; data was 25 days stale before one refresh | VERIFIED, commit `620d801` |
| the-odds-api.com | Game lines (F1) | Key unavailable in the cloud; 403 through the cloud proxy; F1 neutral on every cloud build | VERIFIED, `docs/hosts.md` |
| Action Network (pasted) | Odds fallback | Client-rendered page; needs a real browser | SUPPORTED, helper agent from skills |
| Open-Meteo | Weather | No failures found | VERIFIED reference in code |
| A third-party "DFS_Architect_MCP" server | Lineup fallback when statsapi was blocked | Its Vegas-lines tool is a stub that returns a made-up game | SUPPORTED, helper agent from repo SKILL.md |

**Pattern (SUPPORTED):** paste paths became primary because live fetches failed on whichever host was in use. "Egress is measured, never asserted": three documents in the repo gave three different answers for the same hosts, each true where it was taken (VERIFIED, `docs/hosts.md`). The NBA engine runs on one laptop with open egress, which removes most of this; the lesson that survives is to probe each source at session start and print what was reached.

---

## 7. Modeling and measured results

### 7a. What existed

- **Projections:** DraftKings AvgPointsPerGame times five hand-set multipliers (VERIFIED, `MLB_Classic.md` section 6). A September critique called this out: "AveragePointsPerGame is not a forecast" (VERIFIED, `DFS_SYSTEM_GREENFIELD_SPEC.md`, F-03).
- **Ownership:** a labeled prior, graded later (below).
- **Field and contest simulation:** none in production. `slate_sim.py` existed in v2.x and was retired at v2.20.0 because it "fell back to a static tail and added no signal" (VERIFIED, `MLB_Classic.md` section 16). Its spread came from Floor and Ceiling, so sigma was a constant multiple of mu (VERIFIED, `docs/backlog.md` "Sim-gate precondition").
- **Portfolio:** a candidate bank plus one joint MILP with exposure caps by contest posture (VERIFIED, `MLB_Classic.md` sections 7 and 8). The "dual objective" (big wins and no washout) was measured only as deterministic proxies: ceiling sums, and the share of portfolio ceiling kept if one game's hitters score zero (VERIFIED, R126, commit `952a85b`).
- **"Truthful labels"** forbade any claim of ROI, win rate, cash rate, or probability (VERIFIED, CLAUDE.md). Profit was never claimed, and for three months it was also never computed.

### 7b. What was measured

**Money and finishes (VERIFIED, CHANGELOG R494 entry, recomputed from the user's entry-history export).** All MLB paid entries outside Best Ball, 2023-10-29 to 2026-10-09 (this includes play before the engine):

| Measure | Value |
|---|---|
| Entries, slates | 7,598 in 242 |
| Fees, net (cash plus ticket face) | $1,249.05, net -$270.36 |
| What the same prize pools return to a random entrant | 91.9% of fees |
| Finish percentile (higher is worse) | 52.05 [51.1, 53.1] against a uniform 50.39 |
| Top decile | 10.03% against 9.61% reference (+0.4, interval includes zero) |
| Bottom decile | 13.96% against 10.40% (+3.6) |
| Fields over 2,000 entries | fees $303.41, net -$199.04 |
| Classic since 2026-09-19 (engine with delivery records) | 286 entries, finish 49.8 [44.7, 55.7]: indistinguishable from random |
| Showdown since 2026-09-19 | 180 entries, finish 54.9 [52.4, 58.0]: worse than random |

Engine-era subset, 2026-06-03 to 10-08, Classic and Showdown (SUPPORTED, computed by the ledger agent from the same export): 5,575 entries, $1,044 in fees, $414 cash and $351 ticket face. Net was -60% on cash alone and -27% counting ticket face. 86 entries (1.5%) finished top 1% and 46 finished first, but the largest field won was 237 entries and the largest cash prize $22. The 1.5% is not evidence of skill: in a field under 100, "top 1%" means first place, which a random entry hits more than 1% of the time.

**Construction against the field (VERIFIED, ROADMAP "Where the money is"; standings findings section 1; CHANGELOG R494 attribution).**
- Top-decile Classic lineups were chalk-positive against their own field, replicated.
- The engine built 4-man primary stacks for 72.5% of entries (field 21.6%) and 5-2-1 for 1.44% (field 30.7%). Its 4-4, 4-3-1, and 4-2-2 builds carried a bottom-decile excess of +13.3 points [+6.8, +19.5].
- Its low-chalk entries were 43.6% of its total (33.3% by construction) and carried a bottom-decile excess of +7.7.
- Showdown: pitcher captains were 57.7% of top-decile lineups against 44.7% of the field, and only about 40% of the engine's. The engine built 5-1 for 81% of entries against 37% for the field.
- **Inconsistency inside the repo:** the ROADMAP says the user's entries ran 7.6 to 21.4 points below the field's cumulative ownership (contrarian), while the standings findings say the user's Classic entries "were already much chalkier than the field" on a different measure. Both are VERIFIED quotes; which measure is right was never reconciled.

**Projection accuracy (VERIFIED, R408, commit `8430fd2`).** Graded once, on 9 slates, because DK salary files had not been kept beside the standings. Hitter rank correlation with actual points ranged from 0.04 to 0.41, and the engine's projection barely beat salary or AvgPointsPerGame.

**Ownership prior (SUPPORTED, ledger agent, ledger section 3.21).** Ordering usable (median rank correlation 0.45 to 0.6); level badly compressed (players projected above 20% owned were under-predicted by about 17 points; top-10 chalk recall 28.6%).

**Min-cash and payout lines: never measured.** Paid places were known for 97 of 610 mined contests, and the findings doc reports "DATA BLOCKED" for cash and seat economics (VERIFIED, standings findings section 1, item 5).

**Sample-size honesty.** The standings study is rigorous. The ledger's per-tranche regrades flip-flopped on 8 to 46 contests, and the ledger itself calls a "crowding" story a coincidence later falsified (SUPPORTED, ledger agent).

### 7c. Believed versus measured (SUPPORTED)

| Belief built into the engine | What the archive said |
|---|---|
| Contrarian or leverage construction wins large fields | Top-decile lineups were chalkier than the field; low-chalk entries busted more |
| 4-man stacks as the default | Field and winners favor 5-man and 5-2-1 |
| Exposure caps by posture help | Set by judgment ("a judgment call and not a fit", ledger section 3.11); never measured |
| Showdown hand-weighted theses | Showdown finished worse than random since 09-19 |
| More gates make better files | Gates caused the one no-file night and many refusals |

---

## 8. LLM layer: how Claude Code was used

**Setup (VERIFIED, `.claude/` folder, read by helper agent and me).**
- CLAUDE.md as the contract (about 180 lines), path-scoped rules in `.claude/rules/`, and a 1,656-line per-slate skill (`skills/generate-lineups/SKILL.md`) whose own rules file targets 150 lines.
- Skills: `/dev-session`, `/land`, `/ship` (push, PR, CI, merge with no human review), `/handoff` (writes the user's next-session prompt).
- Hooks: a command guard (denies DK domains, `git add -A`, force-push), a session-start orientation of about 300 tokens, a PreCompact hook that re-injects task state, a SubagentStop recorder, and a push reminder before an ephemeral container ends.
- Subagents: `dfs-premise` (checks a filed item's premise before building) and `dfs-qa` (adversarial review of a delivered portfolio), both on Opus.
- An advisor model on every session (R424).

**Cost and flakiness (SUPPORTED).**
- 135 subagent runs recorded from 2026-09-20 (my count of `data/agent_runs/`): 57 `dfs-premise` (median about 11 minutes), 48 general-purpose (median about 34 minutes), 8 `dfs-qa` (median about 26 minutes). Models: mostly Opus, then Fable and Sonnet. One planning session ran 24 subagents (VERIFIED, commit `17aee4a` subject).
- The first `dfs-qa` run cost about 109,000 tokens for one acted-on finding out of five (VERIFIED, `.claude/agents/dfs-qa.md`, per helper agent).
- The run recorder mostly failed to capture findings (47 of 48 general-purpose runs have no findings line), so cost per finding was never measured (SUPPORTED, helper agent).
- No usage-limit incident is recorded (section 4, item 9).

**What was effective (SUPPORTED).** Premise checks that caught wrong diagnoses; the hard DK wall; refusal by default with exit codes; session-start orientation; PreCompact carry-over; and the advisor-review step at landing.

**What was expensive or brittle (SUPPORTED).**
- Ceremony per change: every DEV item updates the CHANGELOG, roadmap, register, and ledger pins, plus mutation-checked tests. One planning PR added about 10,000 lines (PR #138).
- Thirteen editions of an external "greenfield" critique were each adjudicated at length and rejected (VERIFIED, `docs/` critique files; commits `579bcf2`, `5a84ed6`, `cfd5b6c`).
- The engine was edited during live slates, which forced a claims system and "never edit engine paths while a slate beacon is lit" (VERIFIED, CLAUDE.md "Roles, claims, and git").
- Sessions were often run from a phone in an ephemeral container, so anything uncommitted was lost (VERIFIED, `.github/workflows/gate.yml` comment; `docs/hosts.md`).
- No scheduled Claude runs: "Scheduled tasks: none exist; ask Ben before creating one" (VERIFIED, CLAUDE.md). This matches S1's rule.

---

## 9. Testing and validation

**What existed (VERIFIED).**
- About 3,700 tests across seven suites, with per-suite count pins (`tools/audit.py`), a golden replay, hand mutation checks on new tests, a CI gate on Ubuntu (`.github/workflows/gate.yml`), and skill evals (8 scenarios in `skills/generate-lineups/evals/`).
- `verify_export.py` and `preflight_upload.py` as independent checks of the delivered bytes.

**Incidents where an invalid, wrong, or mislabeled file reached the user, or nearly did (VERIFIED unless marked).**
- 2026-07-29: a late-swap file passed `verify_export` and DK rejected 7 of 16 rows (section 3a).
- 2026-09-01: no file at lock; the session's preflight had no started-game check at all (R287), and on the same night it passed files holding 151 and 78 started-game slots (SUPPORTED, CHANGELOG agent).
- 2026-09-02: the repair tool produced a file DK would reject (doubled entry block); a hand-patched file shipped (R292).
- 2026-07-29 and 30: two review-grade Showdown files carried an `upload_ready` label (R34).
- 2026-08-15: a false "duplicate lineup groups: 9" alarm nearly made the session reject a good portfolio at T-5; none of the duplicates were inside one contest (SUPPORTED, CHANGELOG agent, R128).
- 2026-09-22 and later: certified files with benched players, fixed by repair after upload (PRs #26, #44).
- A QA claim of "zero dead slots" was false one minute later because lineups posted (PR #12, per helper agent). Re-pulling lineups became the mandatory last step.
- The 2026-09-22 audit found delivery records that listed no entries, or the previous file's entries (DD-10), and manifest statuses stuck at "candidate" (VERIFIED, `docs/2026-09-22_deadline_delivery_qa.md` section 2).

**What testing did not catch (SUPPORTED).** The tests guarded engine internals well and the delivery chain poorly. The audit's verdict: "A green code gate does not establish timely operator delivery" (VERIFIED, deadline audit, "Evidence standard"). The gate also ran red on the Windows laptop for host reasons while CI was green (PRs #101, #128), which trains people to ignore it.

---

## 10. Against S1: what the MLB experience says

These are checks for the designer, not verdicts. Each cites the MLB evidence.

1. **Washout has a delivery cause that S1's math does not see.** S1's `P(W)` assumes every entry holds a lineup. In MLB the clearest, most avoidable zero-cash events were entries that never got a lineup (67 blank in the engine era) and a no-file night (37 entries). How many of the user's zero-return nights were delivery-caused rather than lineup-caused was never measured; the lineups also ran below random on their own. S1 should add a *night plan* step: the user names every draftgroup with reserved entries, the engine lists them in lock order, and each gets a legal baseline before any is enhanced. Report "entries with no valid file yet" next to `P(W)`. Also settle early whether DK lets a blank Classic entry be filled after first lock with later-game players (section 5, item 10): if it does, a missed lock becomes a partial loss instead of a certain zero, and the engine needs a "late fill" mode. (Evidence: R499, R286.)
2. **The fallback builder must be real code, tested, and instant.** On 2026-09-01 the only file came from a throwaway greedy script written after the lock. S1 principle B2.3 is right; make the fallback a deterministic, tested builder that needs only the DKEntries file, with no data feeds. (Evidence: R286 entry.)
3. **Grade on scenarios the optimizer did not see.** MLB's own preconditions for reopening a simulator: a real per-player variance basis, *separate* scenario banks for selection and grading with logged seeds, and joint settlement of all own entries in one simulated contest (VERIFIED, `docs/backlog.md` "Sim-gate precondition"). S1 has the third (`B_c(s)` is the max over our entries) and common random numbers for comparisons, but it does not specify separate selection and reporting scenario sets. If `G1` and `P(W)` are reported on the scenarios that chose the portfolio, both are inflated (the winning portfolio looks best on the draws that picked it). Add a held-out scenario set for every number shown to the user.
4. **Variance basis.** MLB's retired simulator derived spread from Floor and Ceiling, so sigma was a fixed multiple of the mean and the tails carried no signal. S1's stat-level simulation is the right answer, but it needs a gate: check simulated quantiles against realized player outcomes before any portfolio decision reads the tails.
5. **Payout tables will not arrive by optional paste.** S1 makes payout tables "an optional paste or a default by contest class". MLB had payout data for 97 of 610 contests after a full season, and its posture tiers returned "UNRESOLVED" for every recent contest because the capture never happened (SUPPORTED, ledger agent, section 3.20). Build defaults from the entry-history export by contest family (`Places_Paid`, `Contest_Entries`, `Prize_Pool`), keep them current weekly, and treat satellites as "cash equals win": `m_c` is the number of seats, often 1, so `m_c = k_c = 1`.
6. **Do not let leverage or duplication terms carry weight until standings say so.** MLB's contrarian lean and 4-stack default ran against what the winners did. S1's field model derives ownership from a simulated field, which is better than hand rules, but the same risk applies: grade predicted ownership, duplication, and the top-1% line against standings files before the duplication penalty or leverage moves lineups. Key Showdown duplicates on (captain person, set of UTIL persons).
7. **Projections are the biggest gap MLB never closed, and grading needs the inputs kept.** Only 9 slates could be graded because salary files were not kept with standings. S1's run store (component 18) should archive the DKSalaries, DKEntries, projections, and field sample for every draftgroup on the night, keyed by draftgroup.
8. **Record what was actually uploaded.** S1's run store should end each delivery with the user's read-back: which file, and DK's "uploaded N of N" count. MLB could not tell which of several files was entered for 395 of 480 Entry IDs.
9. **Lock clock: derive it, do not type it.** Re-derive locked games from DK's `Game Info` and the current time on every invocation, including at validation time just before upload, and refuse a file where any newly placed player's game has started. S1's late-swap checklist (R6) says this; the MLB incident shows the stale-list failure is real.
10. **Classify every validator rule as V, S, or P from day one.** R6's validator checklist is mostly true DK rules today, which is good; the risk is drift as rules are added. MLB's no-file night came partly from a convention enforced as a rule. Only DK rules and the user's never-relax rules (no duplicate lineup within a contest) may block a file; tag each rule with its class and source.
11. **Standings capture has a window.** Pull only after the slate settles (next morning, Eastern date), one export per draftgroup for points plus one per contest where ownership matters, detect zero-byte files, and do not wait more than a few days.
12. **Budget the process, not just the LLM.** S1 lists 21 components plus challengers, shadow adoption, and replay. MLB shows how process can eat a project: about 80% of PRs were records, governance, or correctness, and each change carried heavy documentation. Suggest: one host (the laptop), a fast smoke test that runs in under a minute before each build, the full suite only in DEV, and no engine changes inside a build window.
13. **The LLM QA adversary needs a time box.** MLB's `dfs-qa` took 11 to 33 minutes per run and about 109,000 tokens on its first run. S1's component 21 should have a hard time and token budget and should be skippable inside T-30.
14. **Repairs after news will dominate the late window.** In MLB the most common late work was replacing benched hitters after lineups posted. S1's precomputed contingency swaps (B5) are the right shape for NBA late scratches; make applying them a one-command, no-LLM step, and re-run the validator with the live clock.
15. **Showdown carried the worst measured results.** MLB's Showdown finished worse than random and was never certified. S1's enumeration plus duplication-aware scoring is a big change; validate it on standings before raising Showdown volume.
16. **Windows host traps** (VERIFIED, `CLAUDE.local.md`): call the project venv's Python by full path, request keep-awake for long runs, and do not depend on tracked fixture files being writable.
17. **Do not drop DKSalaries from the nightly inputs.** S1 B9 item 1 replaces "salary file plus entries file" with one DKEntries file per slate. In MLB, DK's own `Starting` and `Status` columns (salary file only; the player list embedded in DKEntries lacks them, R6 section 2.3) were the best late-news source and often ahead of third-party feeds (VERIFIED, R143). Keep DKSalaries as an optional but encouraged input, re-downloaded close to lock, and use the DKEntries list as the ID authority.

What MLB confirms in S1: manual DK files only; Claude never scheduled; structured LLM output validated by code; the validator as the only writer; sha256 and replayable runs; a valid file before optional work.

---

## 11. Reuse candidates

Default: learn, do not reuse. The MLB code is large, MLB-specific, and coupled (one 10,423-line build script, an 8,800-line pipeline). The items below are judged on their merits.

| Candidate | For | Against | Verdict (BET) |
|---|---|---|---|
| V/S/P gate taxonomy (`mlb_engine/entries/gate_classes.py`, 490 lines) | Proven idea; raises on any unclassified gate | Its gate names are MLB's | Reuse the idea and the "raise on unclassified" test; write new |
| Preflight (`tools/preflight_upload.py`, 3,601 lines) | Exit-code contract (0, 2, 3, 4), `--as-of` clock, sha256 binding, a test list built from real failures | Far too big; MLB slots and manifest coupling | Port the test cases in `tests/test_upload_integrity.py` as a checklist; write a small NBA preflight from R6 |
| DK entries reader and writer (`dk_entries_manager.py`) | Encodes BOM, header geometry, Instructions preservation, completed-row immutability | Ten-slot MLB constants throughout | Do not reuse; copy its failure cases into NBA tests |
| `tools/day_plan.py` | Directly prevents the blank-entry washout | Reads MLB delivery records and modules | Rewrite the idea in a few dozen lines; make it part of S1's ingest |
| `tools/awaiting_standings.py` and the standings-checklist skill | Pure operations win: settled-only, per-draftgroup, zero-byte detection, clickable list | Small and easy to rewrite | Rewrite; keep the three rules |
| `tools/results_ledger.py` (entry-history ingest, uniform reference, slate bootstrap) | Statistically sound and nearly sport-neutral; answers "are we better than random" | Tied to MLB slate keys and record formats | The strongest reuse case; still rewrite, but port its definitions and tests (R496) |
| `tools/replay_slate.py` (exact settlement against archived real fields) | A true backtest instrument (353 of 361 contests reproduced) | Classic MLB only; refuses Showdown | Learn its settlement rules (integer hundredths, ties) |
| `field_miner.py` (standings parser) | Handles ragged rows and many file shapes | Known Showdown duplicate-key bug (ignores captain) | Do not reuse |
| Hooks (`guard_commands.py`, session start, PreCompact) | Cheap, stdlib, fail-open safety | Much of it polices multi-session claims S1 does not need | Reuse the DK-domain deny and session-start orientation ideas only |
| `solver_probe.py` and per-host call budgets | Stops guessing about runtime | The laptop has no 45-second limit | Replace with S1's R9 night benchmark |
| Delivery record (`delivery_record.py`) | Makes results gradeable | Had bugs that recorded empty entries (DD-10); 935 lines | Rewrite simply: file bytes, sha256, predictions, user's upload read-back |
| Optimizer, allocator, pipeline, Showdown theses, claims system, ROADMAP and backlog process | None that S1 needs | Huge, MLB-specific, and the archive did not show they helped | Do not reuse |

---

## Top 10 lessons for the NBA engine

1. **Every reserved entry gets a legal file first.** Plan the night by draftgroup in lock order, baseline each one before enhancing any, and report unfilled entries as a washout risk beside `P(W)`. MLB's clearest, most avoidable losses were blank and missing files.
2. **Validity rules block; everything else only labels.** Class every check V, S, or P on day one. Never let a convention, a missing feed, a failed test, or a QA opinion withhold a valid file.
3. **Derive the lock clock from DraftKings' own file, every time, at upload.** Stale lock lists caused the one confirmed DK rejection.
4. **Prove an edge before adding machinery.** MLB built about 100,000 lines and finished no better than random. Get the results ledger (entry-history export, uniform reference, bootstrap intervals) running in week one and judge every layer by it.
5. **Grade on held-out scenarios and keep every input.** Report `G1` and `P(W)` on scenarios the optimizer did not use, and archive salaries, entries, projections, and field samples per draftgroup so every night can be graded later.
6. **Get payout and field-size data from the entry-history export.** Optional pastes did not happen in MLB. Satellites with one seat make cashing and winning the same event.
7. **Check strategy beliefs against standings before they move lineups.** MLB's contrarian and 4-stack habits ran opposite to what won. In Showdown, key lineups and ownership by role (captain person plus UTIL set).
8. **One parser, one clock, one ID rule, one team-code map.** Drifted copies of the same rule were MLB's most common root cause.
9. **Record what was uploaded.** Each delivery ends with the user's read-back of the file and DK's "uploaded N of N" count. Pull standings after settlement, per draftgroup, within a few days, and detect empty files.
10. **Keep the process small.** One host (the laptop), a quick smoke test before builds, no engine edits during build windows, short skills, time-boxed LLM review, and plain-language errors the user can act on.
