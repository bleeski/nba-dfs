# RR2. Lessons from the NFL engine (nfl-dfs), Showdown first

**Prepared 2026-10-13** for the NBA DFS engine design. Read-only review of `C:\Users\benja\Documents\Claude\nfl-dfs` (555 commits, 2026-08-31 to 2026-10-13), its GitHub issues and pull requests, its retrospectives, debriefs, standings studies, code reviews, changelog and roadmap, and the user's three NFL Claude skills. No code was run, nothing in that repo was changed.

**Labels.** **VERIFIED** means I saw it in the repo (file path or commit cited, short excerpt where it matters). **SUPPORTED** means the repo's evidence points that way but does not prove it, or it is my reading of several records together. **BET** means my judgment, usually a translation from NFL to NBA.

**Jargon used below.** *Slate*: one set of games with one DraftKings player pool. *Showdown*: DraftKings' single-game format with one Captain slot (1.5x points and salary) and five other slots (labelled FLEX in the NFL files; R6 expects UTIL for NBA but has not yet seen a 2026 NBA file). *Classic*: the multi-game format. *GPP*: a large tournament with a top-heavy payout. *Chalk*: heavily owned players. *Ownership*: the share of the field that rosters a player. *Washout*: a night where no entry cashes. *Prior*: the engine's pre-game points estimate for a player. *MILP*: the integer-programming solver that assembles lineups. *Hand pass*: a Python script Claude wrote during a slate to edit the engine's lineups.

---

## Bottom line (read this first)

1. **The NFL engine became an excellent file-safety system wrapped around a weak model, and the real lineups were built by hand passes.** In six weeks it grew to about 59,000 lines of source, 64,000 lines of tests and 43,000 lines of docs, yet the operating path still "maximises summed prior points under the policy's structural rules. No scenario bank, no ownership term and no ceiling statistic reach selection" (VERIFIED, `docs/critiques/Code_Review_2026-09-25.md` §1). The roadmap sessions for the simulator, field, ownership, copy counts and dilution (Sessions 24 to 29) are all still `Pending` (VERIFIED, `docs/ROADMAP.md` §2.2). S1 is built around exactly those pieces. The lesson is about order, not about the math: build the thin end-to-end quant path first.
2. **Governance ate the build budget.** Of 555 commit subjects, 159 are merges, 58 are "Claim Session" commits, 40 mention a close-out and 29 mention ledgers; these groups overlap, so do not add them, but roughly half the history is process (VERIFIED, `git log --format=%s`). A red team predicted this before the season: "Governance absorbs half the build" (VERIFIED, `red-team-critique.md` V1). Release-truth labels (`FILE_VALID`, `EVIDENCE_STATE`, `MODEL_STATUS`, `RELEASE_DECISION`, `DELIVERY_STATE`) end every run at `DO_NOT_UPLOAD`, so they never told the user anything he acted on.
3. **Delivery failed twice, in two different ways.** On 2026-09-20 the engine produced nothing on two Classic slates because a weather field "that moves no number" had veto power over construction and the cloud session could not reach the weather host; a hand-built file with four backup quarterbacks shipped instead, and the QA script that would have blocked it was never run (VERIFIED, `docs/changelog-archive/changelog-2026-09-14-through-2026-09-21.md`). On 2026-09-17 a file was built for DET@BUF and 12 of 13 entries still locked blank; those are the only blank entries in the engine era (VERIFIED, `changelog.md` 2026-10-10). So the costliest failure was the handoff to upload, not the build. The user then ruled R28: ship a valid baseline first, name every gap (VERIFIED, `CLAUDE.md`). S1 already says this; keep it as law, and add an upload confirmation step.
4. **Showdown's top 1% is a crowd of duplicates, and uniqueness was the worst feature.** In the large NFL Showdown fields, 83% to 98% of top-1% entries were lineups shared six or more times; unique lineups were the worst feature on both goals in every game; a 23-way tie for first in a $1M-to-first contest paid each tied entry 5.4% of face (VERIFIED, `docs/STANDINGS_DUAL_OPTIMIZATION_FINDINGS_2026-09-15.md` §4.2, §8.3). S1's duplication penalty is the right shape, but the engine must never reward rarity for its own sake.
5. **Concentration is a measured washout mechanism.** Across 8,007 field portfolios of 10+ entries, those with 85%+ of entries on one player had zero-paid rates 1.4x to 12x higher, and a lower chance of any top-1% finish, in all four games (VERIFIED, same file §5.3). The NFL engine shipped 94% on one player in one Showdown and cashed 0 of 18. Some levers cost both goals at once, which supports S1's "the frontier is flat near the optimum" hunch.
6. **Identity and "who is actually playing" broke on almost every slate.** Name variants (Josh/Joshua, Matt/Matthew, accents, nicknames) blocked runs again and again, including players accepted on earlier slates. Starting QBs with no prior-season row were left out. Backup QBs and practice-squad players were selectable. The user corrected the same omission twice and then ruled (R35 to R37). (VERIFIED, details in §3.)
7. **The user wants an LLM judgment layer that acts, not one that only reports.** He asked for a layer that says a starting QB should captain "in at least X number of lineups despite the absence of data" and that a heavy projection is "violating our dual optimization goals" (VERIFIED, `docs/ROADMAP.md` §2.5 R35). S1's "LLM sets beliefs, solver sets lineups" boundary is the cleaner way to give him that, as long as the belief schema can express a player with no history.
8. **Late swap must edit DraftKings' current export in place.** Regenerating the late-swap file from the blank template moved locked players in 107 cells before it was caught (VERIFIED, commit `823fb26`).
9. **The learning loop never ran until week six, and its signals are slow.** No build was graded against a result until 2026-10-10. A 5-point percentile shift needs about 88 slates to detect; a top-1% rate moving from 1% to 2% needs about 328 (VERIFIED as the repo's own power arithmetic, `changelog.md` 2026-10-10). Most Showdown construction features flipped sign from game to game, and copying last game's winning shape into the next game was itself a ruin mechanism (VERIFIED, standings findings §1 item 4).
10. **Measured results do not show an edge.** Engine era: 348 entries over 17 slates, $223.20 in fees, minus $92.14, average finishing percentile 55.2 (lower is better; 50 is a random entry), or 53.8 with blank entries removed, with an interval of 47.9 to 59.0 that includes random; in fields above 2,000, one top-1% finish against 1.89 expected at random (VERIFIED, `changelog.md` 2026-10-10). Prior against realized lineup points, rank correlation per slate: -0.03, +0.38, +0.63, +0.06 (VERIFIED, same entry).

---

## The record in numbers

| Item | Value | Label |
|---|---|---|
| Life of the repo | 2026-08-31 to 2026-10-13, 555 commits, busiest days 51 and 60 commits | VERIFIED, `git log` |
| Code size | `src/` 58,788 lines (largest: `cli.py` 5,520, `prior_review.py` 3,946, `priors.py` 3,344); `tests/` 144 files, 63,645 lines; `scripts/` 12,442 lines; docs about 43,000 lines | VERIFIED, `wc -l` |
| Test suite | 3,687 passed, 1 skipped, about 19 minutes on Linux; CI with Windows 17 to 26 minutes | VERIFIED, commit `e9163f7`; `docs/claude/working.md` |
| Slates operated | 17 engine-era slates (4 Classic, 13 Showdown) by 2026-10-10, more after (MIN@NO, BAL@ATL, BUF@LAR, Week 5) | VERIFIED, `changelog.md` 2026-10-10 |
| Roadmap | 57 sessions Complete, 39 Pending, 8 Deferred | VERIFIED, `docs/ROADMAP.md` §2.2 |
| Open items only the user can do | 12 of 13 operator items open (publish standings to a private repo, paste payout ladders, save post-upload entries files, run intake commands) | VERIFIED, `docs/ROADMAP.md` §2.6 |
| Money | All-time NFL: 145 entries (to 2026-09-14), minus $98.87; engine era to 2026-10-10: minus $92.14 on $223.20 | VERIFIED, standings findings §3.1; `changelog.md` 2026-10-10 |

---

## 1. Architecture: what the engine does end to end

**Stack.** Python 3.13 pinned with `uv`, HiGHS MILP solver, nflverse data from GitHub releases as the only model source, Windows launcher `nfl.ps1` and Linux launcher `nfl.sh`, GitHub Actions CI, Claude Code on the Windows desktop app and in cloud sessions (VERIFIED, `docs/START_HERE.md`, `README.md`). An earlier "Claude Cowork" surface was retired after a Windows update broke its file bridge (VERIFIED, `docs/START_HERE.md`: "Claude Cowork is retired").

**Storage.** Every run is an immutable folder `data/runs/<run_id>/` holding hashed snapshots of the DraftKings files and every fetched artifact; reports go to `outputs/<run_id>/`; committed slate records live in `data/inbox/slates/<slate>/` (inputs, hand-pass scripts, QA output, final CSV); standings exports sit in a gitignored `data/standings/inbox/`; every structured input has a versioned contract in `docs/DATA_CONTRACTS.md` (5,219 lines) and every refusal code has a class in `config/gate_registry_v1.json` (VERIFIED).

**How a slate runs (as of 2026-10-11).** VERIFIED from `docs/claude/working.md` and the MIN@NO and BAL@ATL slate records in `changelog.md`:

1. User uploads the DK salary CSV and DKEntries CSV and says "run the slate".
2. `run-slate --profile prior_review --build-priors`: a session probe checks which data hosts are reachable; files are classified by their header (never by filename), hashed and snapshotted; a **baseline** of legal, distinct lineups is built from the DK bytes alone and published first; then seven nflverse artifacts are fetched and frozen; an identity gate matches every DK player to nflverse; weather is resolved; a point "prior" is computed per player; the MILP selects lineups under a portfolio policy (exposure caps, captain caps, thesis rules, structural bounds) with a relaxation ladder if infeasible; an independent audit re-checks the policy; the review CSV is written by a byte-exact writer and audited against the template.
3. Hand passes, every slate: a practice-squad check (excludes players not elevated), a "judgment pass" (adds starters the prior missed, rotates concentration), a "ceiling pass" (large-prize tie-break), a "contest pass" that moves lineups between Entry IDs so each contest's entries differ, then the deterministic QA script, then often an adversarial subagent pass when the user asks.
4. Delivery: the user uploads by hand. Classic late swap: the user re-downloads the entries file and Claude edits named cells in place.
5. Results (new in October): entry-history intake, player grading, results report and results join.

**Timing.** Week 1 Classic: 134-minute window, first portfolio at minute 97, 22 engine runs, final file 9 minutes before lock (VERIFIED, `docs/CLASSIC_C4_RETROSPECTIVE_2026-09-13.md`). DAL@NYG Showdown: 61-minute clock, legal file at T-21, shipped v6 at T-7 (VERIFIED, `docs/SHOWDOWN_RETROSPECTIVE_2026-09-13_DAL_NYG.md`). By October: MIN@NO first file 12 minutes after the request, then ten versions in about 30 more minutes; BAL@ATL first file 11 minutes after the request, final v6 18 minutes before lock (VERIFIED, `changelog.md` 2026-10-11).

**The model that actually ran.** "Prior points of the expected stat line": last season's per-player shares times this game's team volume, scored as one expected box score. It has no distribution, no correlation, no ownership and no payout (VERIFIED, `docs/RUN_RECORD_20260914_DEN_KC.md` defect 1). A legacy `build` path with a simulator, ownership, field and economics existed but "nothing on the operating path calls" it (VERIFIED, `docs/critiques/Code_Review_2026-09-25.md` §1), and an early audit found that path's field model priced top-heavy payouts "18x to 280x too high" (VERIFIED, `DFS_SYSTEM_GREENFIELD_SPEC.md` D-01).

---

## 2. What worked well (keep as patterns)

| Pattern | Evidence | Label |
|---|---|---|
| **Start the clock first, from the file.** Read the earliest lock from `Game Info` before anything; every clock statement from a measurement taken that turn. Mental clock arithmetic drifted 45 minutes once and was reported to the user as fact. | Showdown and C4 retrospectives §3, changelog archive 09-20 | VERIFIED |
| **Ship a legal file early, improve in place.** "At no point after T-21 was there no file on the board." Later formalised as baseline-first (R28). | Showdown retrospective §3 | VERIFIED |
| **Deterministic QA on the exported bytes, written separately from the builder.** `qa_showdown_portfolio.py` checks slots, Captain/FLEX role rows, salary, both teams, person uniqueness, lineup distinctness, Entry ID coverage, overlap, inactives, and that nothing outside the roster cells changed. It caught QB-less rows, an all-one-team row and broken thesis rows that hand passes created. | `docs/RUN_RECORD_20260914_DEN_KC.md`; `docs/claude/working.md` (TB@DAL `SINGLE_TEAM_LINEUP`, MIN@NO 8 rows) | VERIFIED |
| **An adversarial subagent that assumes the build is wrong.** "Highest value per minute in the session by a wide margin": in 8 minutes it found 3 players covering 17 of 20 lineups, DSTs against their own offense, and too few bring-backs, none of them illegal. It also found the candidate-bank truncation in DAL@NYG. | C4 retrospective §2; Showdown retrospective §6 | VERIFIED |
| **Re-verify every agent proposal through the real validator.** "The agent's diagnosis was correct and its fix was wrong. Shipping it unverified would have put a QB-less lineup into a live contest." | Showdown retrospective §3 | VERIFIED |
| **Parallel research agents for injury news.** One caught a site publishing a fabricated inactive list naming a star as out, plus two prior-season articles surfacing as current. | C4 retrospective §2 | VERIFIED |
| **Byte-exact writing and a replay anchor.** Classify by schema, hash inputs, never overwrite, and a stored replay that must reproduce the same export hash byte for byte. Independent reviews called the safety shell "sound". | Showdown skill; `DFS_SYSTEM_GREENFIELD_SPEC.md` §3.2; X4 brief F9 | VERIFIED |
| **One-command run with named stops.** Collapsing six CLI calls into `run-slate` and having every stop name the smallest next action. | `nfl-showdown-lineups` skill | VERIFIED |
| **Capability probe at run start.** A 3-second stdlib script that says which hosts this session can reach, run before anything else after the engine produced nothing on two slates because of an unreachable host. | changelog archive 2026-09-20, 09-21 | VERIFIED |
| **Contest pass for within-contest diversity.** Permuting the same lineup set across Entry IDs so each contest's entries differ, at zero cost to the lineup set. | MIN@NO, BAL@ATL records | VERIFIED |
| **Mining standings exports.** One study of 1.87 million entry rows produced most of the real knowledge in this memo. | standings findings 2026-09-15 | VERIFIED |
| **A plain-English tracker for the user.** Built on 2026-10-12 because the roadmap was unreadable to a non-engineer; it bans words like EV and edge. | `docs/claude/working.md` | VERIFIED |

---

## 3. What broke, and which bugs recurred

### 3.1 How to read the commit history

Commit subjects are not "fix:" style. Only 33 of 555 subjects contain a fix-type word (fix, correct, repair, refuse, bug, defect, wrong, gap) (VERIFIED, `git log --format=%s`). Fix-type subjects by theme (a subject must contain both a fix word and the theme word): identity or name 4, lock or clock 3, quarterback 2, salary 2, line endings 2, thesis 2, late swap 1, Windows 1, baseline 1; standings, duplicate, Captain, FLEX, Entry ID, timezone, ownership, payout, weather and bank all 0 (VERIFIED, same command piped through `grep -iE`). Message bodies are useless for counting because they repeat boilerplate (almost every body says `DO_NOT_UPLOAD`). These small numbers are themselves the finding: **fixes were recorded inside "Record the X slate" commits and the changelog, not as fix commits.** So the table below counts **slates and incidents** from the slate records instead.

### 3.2 Recurring problems, by theme

| Theme | Where it hit | Times | Label |
|---|---|---|---|
| **Identity: DK name differs from data source name.** Josh/Joshua, Matt/Matthew, Scotty/Scott, Mitch/Mitchell, Hollywood/Marquise, Nick/Nicholas, an accent, a hyphenated surname, a team code (DK `LAR`, nflverse `LA`). Reviewed matches were not reused: MIN@NO blocked "the same IDs earlier slates accepted". | Week 2 (6 blocks), DET@BUF, MIN@NO, BAL@ATL, BUF@LAR | 5+ slates | VERIFIED, changelog archive 09-17 and 09-20; `changelog.md` 10-11; commit `e9163f7` |
| **Starter missing from the pool, or backup in it.** No prior-season row means no projection means never selected: Keenum (PHI@CHI), Watson (PIT@CLE), Wentz miss (Week 2), Mullens (Week 4). Backups rostered or captained: Purdy beside his own backup (SF@LAR), four backup QBs in the Week 2 shipped file, a backup captained in the PIT@CLE baseline. Depth chart lagging the news (BAL@ATL: the chart still listed the injured starter). | 7+ slates | VERIFIED, commits `4cccbf1`, `0a43d4a`; Showdown skill §6; changelog 10-11 |
| **Concentration breaches fixed by hand.** DEN@KC 94% on one QB, 0 of 18 paid; ATL@GB "five captains at 25% each and four people in 13 of 20"; Week 1 v1 85% concentrated and "shipped confidently"; Week 3 fallback "three players in 25 of 25 lineups and zero stacks"; BAL@ATL one TE in 19 of 32 rows. | 5+ slates | VERIFIED, standings findings §1; ROADMAP R34 and Session 49 row; C4 retrospective §4; changelog 10-11 |
| **Hand passes breaking legality or structure, caught only by QA.** QB-less lineups (DAL@NYG v5, DEN@KC v1, MIN@NO drafts v1 to v3 with 4 QB-less rows and 4 over-stacked rows), an all-one-team row (TB@DAL), a swap helper that could put the same person at Captain and FLEX (found by review, not shipped). | 4 slates plus 1 reachable defect | VERIFIED, retrospectives; `changelog.md` 10-11; `docs/critiques/Code_Review_2026-10-02_Codex.md` F-01 |
| **Candidate bank too small.** "Malik Nabers was SELECTABLE ... and appeared in zero lineups because no candidate in the bank contained him." Bank exhaustion again at DEN@KC v3, DET@BUF (needed 120), MIN@NO (resize). | 4 slates | VERIFIED, Showdown retrospective §6; changelog |
| **Stale role priors.** Last season's shares priced a star RB on a new team at 7.3 points against a $10,600 tag (field: 0 of 99,349 lineups without him paid); a per-game versus season-total unit mismatch understated players who missed games by up to 2.77x; judgment passes repeatedly lowered the engine's prior total because "the priors price last season's roles". | Every slate | VERIFIED, standings findings §4.4; Showdown retrospective §9; changelog 10-11 |
| **Non-playing players still selectable.** Practice-squad players with a blank DK status (one $200 player was in 7 of 28 rows); 13 of 54 flagged in one night. | Every Showdown after DET@CAR | VERIFIED, `docs/claude/working.md` |
| **Gates that no real source could clear.** Weather for unplayed retractable-roof games (nflverse fills `roof` only after the game, 15% of games); a Classic role gate demanded evidence "no approved source publishes", missed by 619 tests because fixtures supplied synthetic evidence. | Week 1 to Week 2 | VERIFIED, changelog archive 09-21; Showdown skill "Never" |
| **Windows and environment traps.** 260-character path limit, PowerShell 5.1 cannot pipe `git commit -F -`, heredocs rewriting backslashes, env-var length cap breaking parametrized tests, CRLF versus LF ledgers, cloud egress blocking hosts, strict TLS failing behind the proxy, two concurrent test suites deleting each other's temp folder. | Throughout | VERIFIED, `docs/claude/working.md` |
| **Hardcoded clocks in tests.** 18 failures on slate morning because a test pinned a date that had passed; another test failed daily after its fixed expiry. | Week 1, 09-17 | VERIFIED, C4 retrospective §3; changelog archive 09-17 |

Themes the brief asked about that did **not** recur as bugs: Captain/FLEX dual-ID mix-ups (the parser pairs by `TEAM|POSITION|Name` and checks the 1.5x salary, VERIFIED `src/nfl_dfs/dk.py`), timezone errors (DK `Game Info` is Eastern; parsed with `America/New_York`, VERIFIED same file), and invalid uploads (no DraftKings rejection is recorded anywhere in the repo, VERIFIED by search).

### 3.3 Incidents where a wrong, weak or missing file reached the user

| Date | What happened | Label |
|---|---|---|
| 2026-09-13 Week 1 Classic | v1 shipped "confidently" with an 85% concentration defect; an adversarial agent found it; the final 20 lineups that ran match no engine artifact (a 7-file hand chain), so 64% of the era's fees have no provenance | VERIFIED, C4 retrospective §4; standings findings §2.3 |
| 2026-09-10 SF@LAR | The shipped file rosters a QB the retained policy excludes; "the exact policy bytes behind the shipped file are not retained" | VERIFIED, standings findings §2.3 |
| 2026-09-13 DAL@NYG | The chalkiest lineup went into the one winner-take-all contest because Entry IDs were filled in template order | VERIFIED, debrief §4 |
| 2026-09-17 DET@BUF | 12 of 13 entries locked blank although a file had been built (first slate run from a cloud session). These are the only blank entries in the engine era. The repo does not record why the file never reached DraftKings. | VERIFIED facts; cause not recorded |
| 2026-09-20 Week 2 Classic | Engine produced nothing (weather gate plus blocked host); the hand-built file that shipped first held four backup QBs and eight lineups under the intended salary floor; the QA script that would have blocked it "was never run" | VERIFIED, changelog archive 09-20 |
| 2026-10-11 Week 5 late swap | The fallback writer would have moved locked players in 107 cells; caught before shipping | VERIFIED, commit `823fb26` |

---

## 4. What was painful to operate

- **The user had to steer, live, slate after slate.** Slate records are full of "Ben asked" passes during the last 30 minutes. His own words: "Let's capture this thought process and discipline ... so I don't need to steer so much" (VERIFIED, `docs/ROADMAP.md` R37). Several rulings were the same correction made twice ("Ben corrected the same omission on two slates", VERIFIED commit `4cccbf1`).
- **Serial gate discovery under the clock.** Five blockers surfaced one at a time on Week 1, about 41 minutes, "four of the five were the same underlying assumption" (VERIFIED, C4 retrospective §3).
- **Solver throughput.** Classic candidate building ran at 4 to 6 seconds per candidate on a 2-core container; "43 minutes produced nothing, and 10 minutes produced the portfolio" (VERIFIED, C4 retrospective §1). The relaxation ladder loosened structure when the real problem was time.
- **Manual steps pushed onto the user.** Copy payout ladders from the lobby, copy four contest numbers into a CSV, pull each standings export by hand (61 contests tracked, 35 still awaiting on 2026-10-10), save the post-upload entries file, publish standings to a private repository, run intake commands and paste output back (VERIFIED, ROADMAP §2.6 and Session 69 card). Most of these stayed open.
- **Errors a non-engineer had to decode.** Blocker codes like `PRIOR_REVIEW_IDENTITY_BLOCKED`, `CANDIDATE_BANK_EXHAUSTED_INCOMPLETE`, `WEATHER_CAPTURE_REQUIRED:roof=blank`; four release truths that always read `DO_NOT_UPLOAD`. The project added a plain-English tracker late (VERIFIED).
- **Two runtimes.** Desktop (Windows, has the files, slow suite) and cloud (fast, but blocked hosts and no access to gitignored standings). Several items exist only because the standings inbox could not reach cloud sessions (VERIFIED, X-track briefs).
- **LLM usage limits.** The repo records no usage-limit incident. It records context pressure instead: "Never Read a standings export ... into context", ledgers read "by section, never whole", a review finding that every session loaded 3,275 bytes of Showdown-only procedure (VERIFIED, `docs/claude/working.md`; Codex review F-05). It also records harness failures: the advisor skill's hook crashed in cloud sessions, and the auto-mode classifier blocked a TLS setting and `rm -rf` mid-slate (VERIFIED).

---

## 5. Hard-won DraftKings knowledge

### 5.1 Salary file (DKSalaries)
- UTF-8 with a byte-order mark; fall back to cp1252 when there is none (VERIFIED, `dk.py` reads `utf-8-sig` on BOM else `utf-8`, `cp1252`).
- `Game Info` is Eastern time; the slate locks at the **earliest** kickoff (VERIFIED, `dk.py`; RUNBOOK).
- `AvgPointsPerGame` was kept out of every model input by rule (VERIFIED, `CLAUDE.md`). SUPPORTED reasoning: it is DK's own number, often stale, and it herds you toward the field.
- A blank DK `Status` does not mean available: practice-squad players who were not elevated could not play and appeared on no inactive list (VERIFIED, working.md). **BET for NBA:** two-way players, G League assignments and recently traded players will play the same trick.
- Showdown pool: every person appears twice, a CPT row and a FLEX row with different IDs; CPT salary is exactly `round(1.5 x FLEX)`; the parser refuses a pool where any person lacks either row, the IDs match, or the 1.5x fails (VERIFIED, `dk.py` lines 466 to 496). An operator exclusion of one ID removes both rows of that person; official-status files needed both rows per person (VERIFIED, Showdown skill §5).

### 5.2 Entries file (DKEntries)
- Header must start `Entry ID, Contest Name, Contest ID, Entry Fee`, then the roster columns, then a blank column or `Instructions` (VERIFIED, `dk.py`).
- **DK writes the whole player pool to the right of the entry block**, starting at the `Instructions` column, on fixed physical rows. Past about seven entries those rows carry both an Entry ID and pool cells; a strict parser rejected real files with many entries until this was handled (VERIFIED, `dk.py` comment; Showdown skill §1). That embedded pool is also the cheapest way to prove which slate an entries file belongs to (VERIFIED, `embedded_pool_ids`).
- **What the embedded pool does and does not carry.** In the committed MIN@NO Showdown files, the entries file's embedded table has `Position, Name + ID, Name, ID, Roster Position, Salary, Game Info, TeamAbbrev, AvgPointsPerGame`, while the salary file from the same slate adds `Status` (VERIFIED, `data/inbox/slates/min-no-sd-2026-10-11/input/`, header rows only). So one entries file per slate is enough for IDs, salaries, slots and lock times, but DK's injury status needs the salary file. This supports S1 B9.1 and its "optional DKSalaries for Status" note. The entries file also had no byte-order mark while the salary file did (VERIFIED, same files).
- One entries file covers one draft group and routinely spans many contests and fees (11 entries over 8 contests and 4 fees) (VERIFIED, Showdown skill §1).
- DK writes CRLF; a hand-edited file written with LF was refused by the engine's own tools (VERIFIED, working.md). Write CRLF.
- Prefilled cells read `Name (ID)`; after lock, late-swap exports read `Name (ID) (LOCKED)` (VERIFIED, `docs/DATA_CONTRACTS.md` §entry record; commit `823fb26`).
- Rows already filled by the user must be preserved byte for byte; only blank cells of authorized Entry IDs may change (VERIFIED, `CLAUDE.md`).
- The user's rule R29: "within a given portfolio keep all submitted lineups distinct and unique", applied across the whole file, all contests included; a different Captain makes a different lineup (VERIFIED, `CLAUDE.md`).

### 5.3 Showdown (Captain) specifics
- **No late swap.** The whole Showdown locks at once, so a re-run after inactives (about 90 minutes before an NFL kickoff) is the only recourse (VERIFIED, Showdown skill §7: "re-run after actives are announced ... A dead roster spot is the largest avoidable loss").
- **Captain caps behave strangely.** Capping Captain exposure pushes a mean-maximizing solver toward a cheap Captain, because a cheap Captain preserves the expensive core underneath; zeroing Captain eligibility for kickers and min-salary punts was "the step that is easy to miss" (VERIFIED, Showdown skill §4). **BET for NBA:** the same will happen with min-salary bench players.
- **Captain ownership is more spread than folklore.** Max Captain ownership was 19.6% in a 475-entry contest and 16.5% in a 59,000-entry contest, both on the same game (DAL@NYG), not the "20 to 35 percent" the skill asserted; top three Captains summed to about 49% (VERIFIED, debrief §2; DEN@KC run record). One game, so treat it as a direction, not a number.
- **Captain and FLEX are separate markets.** A salary-only model fit Captain ownership as proportional to salary^3.75 and FLEX to salary^1.75 (Captain MAE 1.2 points on a held-out game); log Captain salary alone explained R-squared 0.49 (VERIFIED, Codex review "Ownership and duplication"; debrief §2).
- **Very low-owned Captains rarely win.** Captains under 3% owned had 0.00x to 0.19x top-1% lift in three of four games; the low-owned winning Captains were 3% to 6% Captains or players heavily rostered at FLEX (VERIFIED, standings findings §8.3).
- **Duplication is the norm.** Only 20.4% of 59,161 entries in one game were unique lineups; ties for first of 23 and 206 entries (VERIFIED, DEN@KC run record; standings findings §4.1).
- **Salary.** $1 to $500 left helped in all four games; more than $3,000 left hurt everywhere; $0 left was dead in three of four (VERIFIED, standings findings §4.3). **BET for NBA:** the "$0 left" penalty is a duplication effect and may carry over; re-measure.

### 5.4 Late swap (Classic)
- The file must be **DK's current export edited in place**: "Never re-export a swapped portfolio ... it fills the blank template and assigns slots itself, and on Week 5 it moved locked players in 107 cells" (VERIFIED, working.md; commit `823fb26`).
- A swap must fit the outgoing player's slot (a TE can replace a FLEX, never a WR) (VERIFIED, same). **BET for NBA:** the same with G, F and UTIL; S1's "put late players in UTIL, G, F" is right.
- Unspent salary is late-swap option value: a portfolio at $49,900 average had $0 to $800 of room at the late window, so every swap was sideways or down (VERIFIED, C4 retrospective §11).
- Swap flexibility is decided at build time: the best early entries had 0 to 1 unlocked slots, the worst had six (VERIFIED, C4 retrospective §12).
- Mid-contest rank is a completion artifact; compare entries by points per $1,000 of locked salary (VERIFIED, same).
- Mid-slate standings exports hide every unlocked player, so late ownership is not observable at swap time; early ownership is (VERIFIED, working.md; C4 §14).
- The governed late-swap code must compare its "as of" time to the wall clock, or a stale timestamp makes locked cells look replaceable (VERIFIED, Code review 2026-09-25 V12).

### 5.5 Standings exports and the entry-history export
- **Standings exports** (per contest, a zip from the contest page) contain every entry's lineup, rank, points and DK's `%Drafted` per player, with Captain and FLEX rows separate in Showdown and base and FLEX rows separate in Classic; `%Drafted` uses all entries including blanks as the denominator (VERIFIED, standings findings §2.2).
- A standings file pulled mid-game is a snapshot, not settlement ("Every one of the 475 entries reports the identical `TimeRemaining`"); always check `TimeRemaining` is zero (VERIFIED, debrief §0).
- Exports can arrive truncated (no end-of-central-directory record); 99.5% was recovered by streaming the zip member (VERIFIED, C4 §14).
- Exports "age out some days after a contest settles", so pull the oldest first (VERIFIED, `nfl-standings-pull-checklist` skill).
- Standings carry other users' names and lineups; the NFL repo is public, so they had to stay out of git (VERIFIED, ROADMAP O1).
- **The account entry-history export is the better results source**: one download, 14 columns, every sport, keyed by Entry ID and Contest ID, with place, points, field size, fee, prize pool, places paid and winnings. Quirks: `Entry` is a label (contest name plus `(n/m)`), `Contest_Date_EST` is Eastern local time and equals the earliest kickoff, free contests that ran under their guaranteed size can show `Places_Paid` above `Contest_Entries`, BOM and CRLF (VERIFIED, ROADMAP Session 69 card). It already holds the user's NBA rows (VERIFIED, same: "NBA 2024-02-22").

### 5.6 Contest metadata
- The two DK files never contain payout tables, field size or ticket value (VERIFIED, RUNBOOK). The NFL engine never got payouts into the loop: 1 of 26 contests in the first study had a ladder (VERIFIED, standings findings §2.1).
- Never infer payouts, field size or ticket value from a contest name: a "satellite" may pay 3%, a "single entry" 40% (VERIFIED, RUNBOOK screening checklist).
- Rake was 14.9% to 15.9% in 26 of 28 contests; two opening-night contests were 9.1% and 10.7% (VERIFIED, standings findings §6).
- Contest type mattered more than lineups for results: within each slate, top-heavy contests finished worse than flatter ones on 11 of 12 slates (VERIFIED, `changelog.md` 2026-10-10, with the caveat that about 20 slices were examined).
- Ownership differs by contest on the same game (one QB at 49.8% in the large field, 32.9% in single-entry) (VERIFIED, standings greenfield findings).

---

## 6. Data sources

| Source | Use | Failure or terms issue | Label |
|---|---|---|---|
| nflverse (GitHub releases) | All priors: stats, rosters, depth charts, schedule with lines | `roof` filled only after a game; depth chart lags news by hours; names differ from DK; the injuries feed died after 2024 | VERIFIED, changelog archive 09-21; BAL@ATL record; red-team B1 |
| api.weather.gov | Weather gate | Blocked by the cloud egress proxy (403); a field that changed no number still blocked the run; the engine produced nothing on two slates | VERIFIED |
| Sleeper, the-odds-api | Allowlisted, secondary | Sleeper also blocked in cloud | VERIFIED, `src/nfl_dfs/sources.py` |
| nfl.com, draftkings.com | Prohibited hosts in code | Terms | VERIFIED, `sources.py` `PROHIBITED_HOSTS` |
| Team sites, ESPN, Yahoo live blogs, FantasyPros | Inactives and elevations, by research only, never a number | One site published a fabricated inactive list | VERIFIED |
| Public ownership projections | Week 1 only | Transcribed board summed QBs to 200.6%; rank correlation with real ownership 0.13 to 0.18; projections compress toward the mean (chalk over-projected by about 6 points, sub-10% under-projected) | VERIFIED, standings findings §8.1 E; C4 §9 |
| Paid ownership (4for4, Establish The Run, Stokastic) | Considered | A spending decision never taken; free tiers paywalled at the Captain level | VERIFIED, Showdown retrospective §7d |
| An attached MCP server | Weather tool | **Returned stub data shaped exactly like the real answer**; the repo's rule became "MCP output is never a model input and never evidence" | VERIFIED, `docs/chunks/X3-execution-postmortem.md` |

---

## 7. Modeling: believed versus measured

| Belief (in the engine or its docs) | What was measured | Label |
|---|---|---|
| Maximising expected points with caps gives a good GPP portfolio | Engine portfolios "look like one lineup with 17 perturbations"; the hand-built Classic portfolio was the only one that looked like a scenario portfolio | VERIFIED, standings findings §5.5 |
| Low ownership is leverage | "Low ownership is overwhelmingly a signal that a player has no role"; 374 players under 2% owned produced zero 20-point games; two thirds of ceiling games came from the 2% to 10% band; gains came from being 3 to 4 times overweight good players at 8% to 13% | VERIFIED, C4 §24, §25, §23 |
| Unique lineups are ceiling | Worst feature on both goals in every Showdown game; neutral in Classic (where 90% of the field is unique anyway) | VERIFIED, standings findings §6, §8.3 |
| Exclude kickers and defenses | DST in a lineup had 1.34x to 2.87x top-1% lift in three of four games and was in two of four winning lineups; 25 of the top 25 in one contest had a DST, we had 0 of 20 | VERIFIED, debrief §1; findings §8.3 |
| Captain chalk runs 20% to 35% | 16.5% to 19.6% | VERIFIED |
| Read next game's shape from last game's top 1% | Every target it set flipped in the next game; called "itself a ruin mechanism" | VERIFIED, findings §1 item 4 |
| Two-QB Showdown builds are standard | Top-1% lift 0.03x to 1.45x by game; cap near field share, never 67% | VERIFIED, findings §8.2 I |
| Spend all salary | Blind salary-maximising passes cut bring-backs from 12 of 20 to 8 of 20; the user ruled unused salary is never a defect, redeploy only when both goals improve | VERIFIED, C4 §3; ROADMAP R37 |
| Field simulator prices top-heavy payouts | 1,000 sampled opponents cloned to fill 235,000 made first-place equity 18x to 280x too high | VERIFIED, greenfield spec D-01 |
| A candidate bank built by the same objective that selects is enough | "A bank generated by the selecting objective cannot surprise that objective" | VERIFIED, X4 brief F3 |
| Projections | Prior-season shares mis-priced role changes; prior versus realized lineup rank correlation -0.03 to +0.63 per slate | VERIFIED |
| Darts (deliberate long shots) | 19% worse per scored dollar on one slate, "close to uninformative"; judge darts on top-1% hit rate over 15 to 20 slates, not one-slate means | VERIFIED, C4 §13 |
| Structural hygiene helps both goals | A pre-lock filter (one QB, 1 to 2 of his pass catchers, at most $1,500 left, at most one K and one DST) raised random 20-entry P(any top-1%) from 0.19 to 0.28 and cut P(zero paid) from 0.007 to 0.002 in every game | VERIFIED, findings §5.4 (fitted on the same four games, so in-sample) |
| Contest allocation | Template-order assignment put the weakest lineups on the first-place contests (WTA, satellites) by construction | VERIFIED, DEN@KC run record §5; debrief §4 |

What the NFL engine never measured: ownership prediction error of its own (it emitted none on the operating path), copy-count prediction, P(zero paid) from a simulation, or any calibration of a distribution (VERIFIED, findings §8.4; ROADMAP Sessions 24 to 29 Pending).

---

## 8. The LLM layer

- **Skills.** User-level skills `nfl-showdown-lineups` (430 lines), `nfl-classic-lineups` (305) and `nfl-standings-pull-checklist` (136), last edited 2026-09-12 to 09-14 (VERIFIED, file times). They still describe the retired Cowork device tools and a `docs/COWORK_RUNBOOK.md`, so they **drifted from the repo within days** (VERIFIED). The repo moved its own procedure into `docs/claude/working.md` (about 300 lines, loaded every session) and project skills `dev-session`, `verify`, `close-out`, `post-merge`, `advisor`, `onboard`, `standings-checklist` (VERIFIED, `.claude/skills/`).
- **Subagents.** `explorer` (read-only sweeps) and `reviewer` (diff review before close-out), both `model: inherit` (VERIFIED, `.claude/agents/`). Ad hoc: the adversarial QA agent and parallel research agents (high value, §2), and an "advisor" consult on a different model for second opinions.
- **Hooks.** `SessionStart` prints a state digest; `PreToolUse` on Bash guards git and destructive commands; both "exit 0 unconditionally" so a hook crash never stops a slate (VERIFIED, `.claude/settings.json`; X3 brief). Planned postmortem and compaction hooks never landed (Session 19 Pending).
- **Effective:** adversarial review with a conceded-limitations list ("The limitations list is what made tonight's agent productive"), parallel news research, re-verifying every agent proposal, deterministic QA as the final word (VERIFIED, Showdown retrospective §7a).
- **Flaky or risky:** the agent's fixes (correct diagnosis, wrong fix twice), a stub MCP tool, the advisor hook crash in cloud, classifier denials mid-slate, multiple Claude instances working one repo (hence `claim.py` and 58 claim commits) (VERIFIED).
- **Expensive:** context, not dollars, in the record. Session-per-chunk discipline, "one session per conversation, then `/clear`", and a rule against reading any data file into context (VERIFIED). No plan-limit incident is recorded.
- **The role conflict.** The NFL engine banned the LLM from writing numbers, so the LLM's judgment had to be expressed as hand-edited lineups (judgment pass, ceiling pass, value-add swaps). That is the opposite of S1's boundary and it produced most of the legality near-misses in §3.2 (SUPPORTED, from the slate records).

---

## 9. Testing and validation

- **Volume is not coverage.** 3,687 tests, more test lines than source. Yet "619 tests missed" a gate no real source could clear, because every fixture supplied synthetic evidence (VERIFIED, Showdown skill "Never"). The supplied fixtures held only two entries, so the real many-entry DKEntries geometry was never parsed until a live slate (VERIFIED, `dk.py` comment).
- **What caught real problems:** the independent QA script on final bytes, the adversarial agent, the replay anchor, and field data from standings (VERIFIED).
- **What did not:** the builder's own QA ("a checker written by the person who built the thing inherits that person's blind spots", C4 §4); tests with fixed dates; a QA gate that existed but "was never run" on the Week 2 file (VERIFIED).
- **Process risk under the clock:** six engine files modified during Week 1, uncommitted, suite not re-run (VERIFIED, C4 §4); the export path patched 40 minutes before DAL@NYG lock "with no anchor and no test run" (VERIFIED, Showdown retrospective §2).
- **Full suite too slow for a slate:** 10 to 20 minutes; CI 17 to 26 minutes, and each push cancels the previous CI run (VERIFIED, working.md).
- **Incidents of wrong or missing files:** see §3.3. No DraftKings upload rejection is recorded.

---

## 10. Against our sketch S1

### 10.1 Where the NFL record supports S1

- **One shared simulated night, scored against a simulated field, with duplication-adjusted payout.** This is exactly what the NFL engine lacked and every review asked for (VERIFIED, Code reviews 09-25 and 10-02; findings §8.4). S1 component 9, 11, 12 and the `share_c` term are the right core.
- **Valid output first** (S1 B2.3) is the user's R28 ruling, learned the hard way (VERIFIED).
- **Arithmetic in code, judgment in the LLM, joined by a schema** (S1 B2.2, B4). The NFL alternative, the LLM editing lineups by hand, caused most near-misses (SUPPORTED).
- **Per-contest objective.** The NFL engine's single portfolio across contests sent chalk to the winner-take-all and its weakest lineups to satellites (VERIFIED). S1's per-contest Goal 1 fixes this by construction.
- **The insurance hunch.** Several levers cost both goals (85%+ concentration, more than $3,000 unspent, sub-5% players with no role, over-stacking), so moving away from them is free (VERIFIED, findings §7). That is evidence the frontier near the optimum is flat in places.
- **Ownership from the field, not a separate guess** (S1 B7). Published projections were badly calibrated (§6), so building it ourselves is right.
- **Manual DraftKings boundary** (S1 B2.5) matches the NFL permanent boundary (VERIFIED).

### 10.2 What S1 is missing or getting wrong

1. **Build order is the biggest risk, not the math.** The NFL plan (`plan.md`) was S1-like (scenario banks, field generation, a sealed referee bank) and never reached the operating path in six weeks, while governance and hand passes absorbed the effort. **Change:** S1 should add a build-order rule: night 1 runs the full chain at low fidelity (simple simulator, simple field, the real selector, the validator), then each layer gets better. No release-truth vocabulary beyond "valid file: yes or no" plus named gaps. (VERIFIED evidence; recommendation BET.)
2. **Whole-file distinctness (R29).** The user ruled that every lineup in a portfolio is distinct, across contests. S1's per-contest selector could legally put the same lineup in two contests. **Decision for the user:** keep R29 for NBA, or allow reuse across contests where it helps both goals. (VERIFIED rule; decision open.)
3. **"Top 1%" versus "large prizes".** In NFL the user's goal was worded "winning large prizes, and minimizing washouts" (R34), with a tie-break: "Err on side of trying to win large prizes if at odds with minimizing the washout factor" (VERIFIED, ROADMAP R34; working.md). The NFL red team warned that top 1% of a 150,000-entry field is about 1,500th place, "low-single-digit multiples of entry fee" (VERIFIED, `red-team-critique.md` B2). **Change:** report P(top 0.1%) and duplication-adjusted P(first) beside P(top 1%) in the brief, and ask the user whether top 1% is the target or a proxy. The tie-break also argues for an insurance default below 5%, or at least asking him (BET).
4. **Duplication: do not reward rarity.** S1's `share_c` only penalizes ties where the payout differs, which is right. Add an explicit guard: uniqueness bought with no-role players or unspent salary is the NFL's most consistent losing pattern. The field model's predicted copy counts must be checked against observed copies (the NFL card set a bar of rank correlation above 0.5) before the penalty is trusted (VERIFIED, findings §8.1 F).
5. **Per-lineup thesis labels (R33).** The user wants every Showdown lineup to carry a named game thesis ("GB win big, ATL win close, defensive battle, shootout"), and to see Captain spread across theses (VERIFIED, ROADMAP R33). S1's coverage math produces this implicitly. **Change:** the brief labels each lineup with the scenario cluster it wins in, in the user's words, and shows Captain counts per thesis. Do not hard-code theses as constraints; derive them from the scenarios (BET).
6. **The LLM layer must be able to add a player with no history.** The user twice demanded that a starting QB with no data captain a minimum number of lineups (VERIFIED, R35, R36). S1's override schema (minutes and usage ranges) covers NBA rookies, trades and promotions, but S1 should state that a zero-history player can be fully specified by an override, and that concentration limits (the NFL defaults: no person above 60% of lineups, no Captain above 20%) are enforced in code, not by the LLM (VERIFIED defaults, `docs/claude/working.md`).
7. **The identity map must remember.** Reviewed matches have to persist across nights, or the same players block every slate (VERIFIED, §3.2). S1 component 3 lists accent folding; add nickname and legal-name variants, team-code mapping, and a persistent reviewed-match store. (BET for NBA specifics.)
8. **"On the team and able to play" is its own check.** Practice-squad players were selectable with a blank DK status. **BET for NBA:** two-way and G League players, and players just traded, need an explicit eligibility check before the simulator gives them minutes.
9. **Candidate generation must not be shaped by the selector alone.** "A bank generated by the selecting objective cannot surprise that objective", and bank truncation silently removed good players (VERIFIED). S1 component 13 (MILP on scenario points plus leverage-adjusted means) should log, per player, why he is absent from the pool, and Classic generation needs a measured seconds-per-candidate budget (4 to 6 seconds per candidate in NFL on 2 cores) before the night plan is fixed (VERIFIED; ties to the R9 benchmark).
10. **Showdown enumeration still needs Captain screening.** S1 B6 enumerates every legal Showdown lineup, which removes the bank problem entirely (good). Add the NFL lessons as screens, not rules: no Captain whose ceiling at 1.5x cannot reach the winning line; spend within about $500 unless the leftover buys something; heavy duplication checks on chalk cores (VERIFIED evidence; BET translation).
11. **Late swap file mechanics.** S1 B5 is right on strategy. Add the mechanics: edit DK's current export in place, keep `(LOCKED)` cells byte-identical, swaps must fit the slot, compare the run clock to the wall clock (VERIFIED, §5.4).
12. **Handoff to upload is a failure point.** DET@BUF built a file and 12 of 13 entries still locked blank (VERIFIED). **Change:** the nightly checklist asks the user to re-download the entries file after uploading, and the engine confirms every Entry ID is filled. That download is also the record of what was actually entered.
13. **The learning loop: cheaper inputs, slower signals.** Use the account entry-history export for results (one download covers every contest; it carries field size, places paid and prize pool), and standings exports only for field and ownership fitting (VERIFIED, §5.5). Keep a per-Entry-ID build record that covers hand edits, because the NFL's biggest-fee slate had no provenance (VERIFIED). S1 B7's "fitted to the user's own standings files from night 2" needs heavy shrinkage: most construction features flipped sign between games, and copying last game's shape was a ruin mechanism (VERIFIED). Fit only stable shapes (ownership curve by salary, duplication rate, salary left distribution).
14. **No gate may veto construction unless it protects file validity.** NFL's weather gate stopped the engine on two slates while moving no number (VERIFIED). S1 should state the rule outright.
15. **The far tail of the field needs its own model.** S1 estimates each contest's opponent score distribution `F_{c,s}` from a sample of field lineups. The NFL legacy path failed exactly here: it sampled 1,000 opponents and cloned them up to the real field size, so every rank finer than one-in-1,000 collapsed onto first place and top-heavy payouts were priced 18x to 280x too high (VERIFIED, `DFS_SYSTEM_GREENFIELD_SPEC.md` D-01). With about 10,000 sampled opponents, `F` near 0.99 (top 1% of a large field) is resolvable; `F` near 1 - 1/N, which P(first) and P(top 0.1%) need in a 100,000-entry field, is not. That spec's remedy was a fitted upper tail plus binomial settlement against the real opponent count, which is the binomial form S1 already uses. **Change:** S1 should name a tail model for `F` before it reports first-place or top-0.1% numbers, and should budget memory: the red team computed a 150,000-entry field scored over 10,000 scenarios at about 5.6 GiB as a float32 matrix (VERIFIED, `red-team-critique.md` B4), so score sampled field lineups, never the full field.
16. **Privacy and repo visibility.** The NFL repo is public; standings carry other users' names and the entry history carries winnings, so both stayed gitignored and cloud sessions could not see them (VERIFIED). Decide early where NBA data lives.

### 10.3 Decisions to put to the user

- Keep R29 (all lineups distinct across the whole file) for NBA? (Recommend yes until measured otherwise. BET.)
- Is "top 1%" the goal, or a stand-in for "large prizes"? Should the brief show P(top 0.1%) and P(first)?
- Given his NFL tie-break toward large prizes, is a 5% insurance default too high?
- Will he re-download the entries file after every upload (catches blanks and anchors late swap)?
- Private repo for NBA, or data kept outside git?

---

## 11. Reuse candidates (default: learn, do not reuse)

| Candidate | For | Against | Verdict |
|---|---|---|---|
| `src/nfl_dfs/entry_history.py` (647 lines) parser for the DK account entry-history export | The export is identical across sports and already holds the user's NBA rows; the parser already handles measured quirks (Entry label `(n/m)`, Eastern dates, `Places_Paid` above `Contest_Entries`, BOM, CRLF, exact cents); it imports only a hashing helper and one canonical-bytes function | It is wrapped in the NFL gate-registry and contract ceremony (registry codes, re-pinned hashes); it refuses a whole file on one bad row, which is stricter than a learning loop needs | **Port the rules, maybe the module.** The strongest reuse case in the repo. Strip the registry coupling. |
| `dk.py` parsing rules (524 lines) | Encodes the embedded-pool geometry, `Instructions` marker, BOM and cp1252, Captain pairing by person and the 1.5x check | Hard-coded NFL roster tuples (`FLEX`, `DST`, `RB/FLEX`); NBA uses UTIL and multi-position eligibility | **Learn, reimplement.** Use its comments as a test list. |
| `scripts/qa_showdown_portfolio.py` checks (331 lines) | The check list is proven: byte diff restricted to roster cells, Captain/UTIL role rows, both teams, distinctness, Entry ID coverage, inactives | NFL-specific rules (QB, kicker, DST, backups); identity by name in places (a review finding) | **Learn the check list.** S1's validator should include every generic check. |
| Late-swap in-place editing (`late_swap_cells_record.py` in the Week 5 slate folder) | Correct mechanics, refuses LOCKED cells and wrong-slot swaps | A slate-folder script, not engine code | **Learn the pattern.** |
| `scripts/session_probe.py` (288 lines) | Three-second host reachability check that would have saved two slates | Reads NFL's allowlist by parsing source | **Learn the pattern**, a few lines in S1's preflight. |
| `scripts/standings_checklist.py` (844 lines) clickable pull list | Turns standings pulls into one click per contest, oldest first | Standings pulls still lagged (35 of 61 awaiting); the entry-history export makes most pulls unnecessary for results | **Learn**; build only if field fitting needs many standings files. |
| `contest_assignment.py` within-contest diversity (840 lines) | Moves lineups between Entry IDs at zero lineup cost | S1 selects per contest, so assignment is part of selection | **Learn**, likely unnecessary. |
| Release truths, gate registry, contracts, claims, ledgers | Rigor and audit trail | Absorbed most of the effort; every run ended `DO_NOT_UPLOAD`; the user needed a separate plain-English tracker | **Do not reuse.** Keep only: valid file yes or no, named gaps, hashes and a run manifest. |

---

## Top 10 lessons for the NBA engine

1. **Build the quant path end to end first, behind a small safety shell.** The NFL engine perfected the shell and never shipped the simulator, field or duplication-aware selection. (VERIFIED evidence.)
2. **A valid file always ships, early, no non-validity gate can stop it, and the engine confirms it was uploaded.** The engine produced nothing on two NFL slates because of a gate that changed no number, and on another a built file still left 12 of 13 entries blank. (VERIFIED.)
3. **In Showdown, value the Captain by ceiling and duplication, never by rarity.** Top 1% is a crowd of duplicates; unique lineups and sub-3% Captains lost; first place can pay 5% of face after a tie. (VERIFIED.)
4. **Enforce concentration limits in code.** 85%+ on one player raised washouts 1.4x to 12x in the field and produced our 0-of-18 night. (VERIFIED.)
5. **Persist identity and eligibility decisions.** Name variants, missing starters, backups and inactive-but-listed players broke almost every slate. (VERIFIED.)
6. **Give the LLM a belief schema that can express a player with no history,** so it never has to hand-edit lineups. Hand passes caused the near-misses. (SUPPORTED.)
7. **Independent QA on the final bytes and an adversarial reviewer, every night; re-verify every agent fix.** These caught what the builder could not. (VERIFIED.)
8. **Late swap edits DraftKings' current export in place;** unspent salary and late-game players in flexible slots are option value decided at build time. (VERIFIED.)
9. **Grade every night from the entry-history export and a per-Entry-ID build record; expect slow signals and do not chase last night's winning shape.** (VERIFIED.)
10. **Ask the user the goal questions now:** top 1% versus large prizes, whole-file distinctness, insurance default, and the post-upload re-download. NFL rulings arrived mid-season, mid-slate. (VERIFIED that rulings came late; recommendation BET.)

---

## Appendix: main sources read

`CLAUDE.md`; `docs/START_HERE.md`; `docs/claude/working.md`; `docs/ROADMAP.md` (§1, §2.2, §2.5, §2.6, §2.8, Session 69 card); `docs/RUNBOOK.md` (sections on DK files and contest screening); `docs/SHOWDOWN_RETROSPECTIVE_2026-09-13_DAL_NYG.md`; `docs/CLASSIC_C4_RETROSPECTIVE_2026-09-13.md`; `docs/DEBRIEF_2026-09-13_DAL_NYG_contest_*.md`; `docs/RUN_RECORD_20260914_DEN_KC.md`; `docs/STANDINGS_DUAL_OPTIMIZATION_FINDINGS_2026-09-15.md`; `docs/STANDINGS_GREENFIELD_FINDINGS_2026-09-15.md`; `DFS_SYSTEM_GREENFIELD_SPEC.md`; `red-team-critique.md`; `docs/critiques/Code_Review_2026-09-25.md`; `docs/critiques/Code_Review_2026-10-02_Codex.md`; `docs/chunks/X3`, `X4`, `P8`; `changelog.md` (2026-10-10 to 10-13) and `docs/changelog-archive/changelog-2026-09-14-through-2026-09-21.md`; `src/nfl_dfs/dk.py`, `sources.py`; `.claude/settings.json`, `.claude/agents/`, `.claude/skills/advisor`; GitHub issue #40; commits `823fb26`, `4cccbf1`, `0a43d4a`, `e4e195b`, `e9163f7`, `d995675`; the three user-level NFL skills.
