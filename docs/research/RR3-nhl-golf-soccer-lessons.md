# RR3. Lessons from the NHL, golf, and soccer engines

**Date:** 2026-10-13. **Scope:** read-only review of three of the user's prior DraftKings engines: `nhl-dfs` (473 commits, Sep 26 to Oct 13, 2026), `golf-dfs` (93 commits, Jul 29 to Aug 28), `soccer-dfs` (12 commits, Aug 19 to Sep 9), plus the user's `golf-generate-lineup`, `golf-leaderboard`, and `soccer-generate-lineup` skills. Nothing in those repos was run or changed. MLB and NFL engines were not opened; anything said about them here is secondhand from the NHL plan's own review of them and is labeled that way.

**Labels.** **VERIFIED** means the cited repo file or commit records it (path and a short excerpt given). It means "the repo says so", not that I re-ran the analysis behind it. Where I ran a check myself (an encoding scan, commit counts), I say so. **SUPPORTED** means consistent evidence from more than one place but not a primary record. **BET** means my judgment.

**Redaction.** No entry IDs, contest IDs, DraftKings player IDs, file hashes, or other people's usernames appear here. Athletes are not named.

**Jargon used below.** *GPP*: a large tournament with a top-heavy prize table. *Cash game*: Double Up or Triple Up, where a flat prize goes to the top 20 to 50%. *Booster*: DraftKings' "Top N Win $X" contests, a flat prize to the top N. *Chalk*: heavily owned players. *Stack*: several players from one team. *Late swap*: editing entries after some games have started. *Captain / FLEX / UTIL*: Showdown slots; Captain scores 1.5x; NHL Showdown calls the other five slots FLEX, NBA calls them UTIL. *Draft group*: one DraftKings slate with one player pool. *Referee*: an independent checker that re-reads the output file with its own parser. *MILP*: the integer-programming solver used to build lineups. *Common random numbers*: comparing two options on the same simulated draws.

---

## Bottom line

1. **The only systematic performance measurement across the three repos is NHL's, and its Classic numbers are poor.** Over the engine's first 16 slates, NHL Classic entries cashed 23 times in 136 against 32.2 expected for random lineups, and 0 of 135 tournament entries reached the top 1% (1.2 expected). Showdown from the same engine cashed 34 times in 78 against 22.4 expected. The repo labels both samples THIN. VERIFIED (`nhl-dfs/BACKLOG.md` B110 and B112). That the top-1% objective *caused* the Classic shortfall is only a hypothesis: NHL files it as "Hypothesis, thin" and the same window had dropped odds, priors-only cloud runs, hand-built entries, and an engine that changed mid-period. Golf's ledger scored 0 of 24 recorded events (one event was hand-scored in a retro) and soccer settled nothing. So this is weak but real evidence on what an objective like S1's Goal 1 can cost; it supports keeping S1's washout control and measuring the frontier from night 1. That S1's 5% default is too small is a BET.
2. **Delivery near lock is where money was actually lost, in two sports.** Golf locked 7 paid entries blank because 45 minutes of environment repair ate a 90-minute window. On an NHL night DraftKings accepted 20 of 28 uploaded rows and refused exactly the 8 rows carrying late repairs (a scratched skater and a non-starting goalie), because that version reached DraftKings after the first game started; every version had been named `DKEntries.csv`. VERIFIED (golf `WYNDHAM_2026_RETRO.md` section 1; NHL `BACKLOG.md` B119). No modeling problem in any repo cost as much, per the repos' own accounting.
3. **A check that can never pass gets bypassed.** Golf's `UPLOAD_READY` status was never produced on any build, so every file shipped `DO_NOT_UPLOAD` and the user uploaded anyway. Soccer's certification could not pass either, so an LLM session built the upload file outside the program. NHL shipped a portfolio its own risk budget flagged as breached. VERIFIED (golf `ops/policy.yaml` header; soccer `DFS_SYSTEM_GREENFIELD_SPEC.md` section 1.5; NHL `reviews/2026-10-01_run_session_report.md` F2). Recurs in all three sports.
4. **Contest facts (field size, payout table, contest type) were wrong or guessed in every repo,** and every repo's model leaned on them. Golf's default payout curve paid 35.6% of the pool to first against a real 10 to 18%. NHL priced contests as 5,000-entry fields when the names implied about 400. NHL's fix that worked: a contest facts table built from the user's own DraftKings entry-history export. VERIFIED (golf `BACKLOG.md` B53; NHL `reviews/2026-10-03_showdown_stl_col_run_record.md`, `BACKLOG.md` B111, C50).
5. **The first real post-lock file broke late swap.** DraftKings writes started players as `Name (ID) (LOCKED)`; NHL's late swap had only ever seen synthetic files and rejected every entry. Whether DraftKings accepts an upload that still carries `(LOCKED)` is still unknown. VERIFIED (NHL `BACKLOG.md` B118, B122).
6. **Ownership read off a simulated field, which is S1's design, is what NHL built, and it still missed news-driven chalk by about 10x** (a replacement forward 50.7% owned against 4.7% predicted), because the news inputs never reached the field model. VERIFIED (NHL `reviews/2026-09-29_slate_review.md`; `BACKLOG.md` B20, B63). "News flows through automatically" is a hypothesis to test, not a property of the design.
7. **Replays and paired comparisons broke in two repos.** NHL picked different lineups from identical inputs when the laptop was busy, because solver steps run on wall-clock time limits. Golf's simulation drew random noise by row position, so reordering the input file changed every projection. VERIFIED (NHL B98; golf B52). S1 depends on common random numbers and on replay; both need to be designed in.
8. **Process overhead outgrew the stakes in all three repos, and each repo's own later review said so.** Golf: four rounds of greenfield specs and outside critiques for about 6 entries an event. Soccer: about one third of the code proved data was allowed to be used, and the data was never used. NHL: 106 open decisions queued for the user, 128 backlog rows, and a 21 to 24 minute check at the start of every build session. VERIFIED (golf `DFS_SYSTEM_GREENFIELD_RESPONSE.md`; soccer spec section 3.1; NHL `BUILD_STATUS.md`, B86).
9. **The engines got safer over time but not leaner.** NHL fixed golf's and soccer's worst gaps (it measured results against a random baseline within two weeks, built the legal file and late swap first, and keyed identity by person and role from day one). It repeated others: environment failures inside the entry window, dependence on DraftKings' own endpoints, a file-delivery failure at lock, and much more ceremony.
10. **Reuse is mostly ideas, not code.** The one strong code-reuse case is NHL's reader for the DraftKings entry-history export plus its results-versus-random report, which reads the exact 14-column file R8 already uses and depends only on the Python standard library and numpy. Everything else: learn the lesson, rebuild small.

### Do today (one item, about 2 minutes, no money)

NHL's next real late swap after the first puck drop is the cheapest way to settle the one open DraftKings mechanic that both NHL (B122) and R6 (section 2.5) list as a BET: does DraftKings accept an uploaded entries file whose started cells still carry ` (LOCKED)`? The user should read back DraftKings' "uploaded N of M" count on that upload and record it. NBA late swap can then be designed on a fact instead of a guess.

---

## 0. Chronology and scale

| | Golf | Soccer | NHL |
|---|---|---|---|
| Built | Jul 29 to Aug 28, 2026 | Aug 19 to Sep 9, 2026 | Sep 26 to Oct 13, 2026 (live) |
| Commits | 93 | 12 (large agent-written PRs) | 473 |
| Runtime | A Cowork skill (765 lines) driving Python tools in a cloud sandbox with a mounted folder | A Python CLI; operated by a Cowork skill (483 lines) | Python engine; Claude Code skills and two subagents; runs both on the laptop and in Claude Code cloud sessions |
| Formats | Classic, Showdown, Captain Showdown | Classic only | Classic and Showdown (Captain + FLEX) |
| Real use | About 20 builds; about 6 entries an event at $0.10 to $1 | One operated slate (6 entries), one later draft build | 214 entries in 82 contests over 16 slates by Oct 9; more since |
| Measured results | Ledger scored 0 of 24 recorded events; one event hand-scored in a retro | None (0 slates settled) | Yes: results report against a random baseline |

Sources: commit logs; golf `CLAUDE.md` and `BACKLOG.md` B47; soccer `CLAUDE.md` ("Zero slates settled"); NHL `BACKLOG.md` B110. Soccer's PRs came from branches named `codex/...` and `agent/...`, which suggests a non-Claude coding agent wrote much of it (SUPPORTED, from branch names only).

The order matters for section 12 ("better or worse"): golf first, soccer second, NHL third.

---

## 1. Architecture and how a slate runs

### NHL (closest to NBA; Showdown has Captain + FLEX)

- **Shape.** A deterministic Python engine (`src/nhl_dfs/{intake,export,referee,data,models,sim,build,learn}`) with a PowerShell wrapper `nhl.ps1`. CLAUDE.md line 3: "Deterministic Python engine; Claude Code runs commands, relays agent output, and never edits lineups by hand." VERIFIED.
- **Inputs.** The user's `DKSalaries.csv` and `DKEntries.csv`. "The uploaded `DKSalaries.csv` and `DKEntries.csv` bytes are authoritative for players, IDs, salaries, positions, entries, and template layout." VERIFIED (`CLAUDE.md`, Authority 4).
- **One command per slate.** `/nhl-run "<DKSalaries>" "<DKEntries>"` is a skill whose first line runs the engine *before the model reads anything* (the skill's `!` preprocessing: ``!`.\nhl.ps1 slate $ARGUMENTS` ``), then launches a researcher and an adversary subagent in parallel, saves their JSON verbatim, and runs two deterministic apply commands. VERIFIED (`.claude/skills/nhl-run/SKILL.md`).
- **Three versions per run.** v1 is a legal baseline from local files only; v2 a provisional leverage pass; v3 the scenario-simulation pass. "Always produce the checked baseline first, from local inputs only; network enhancement comes after the first publish and never blocks it." VERIFIED (`CLAUDE.md`, Slate rules). Measured: Classic 74 s and Showdown 52 s end to end offline; a 150-entry Classic run took 216 s and peaked at 1,036 MB. VERIFIED (`BUILD_STATUS.md`, C8 log line; `BACKLOG.md` B16).
- **Publishing.** Atomic replace under a slate lock, a lock-time recheck immediately before publish, and an independent referee with its own parser that compares output bytes to the input file. VERIFIED (`docs/CONTRACTS.md`, "Publication lock safety").
- **Late swap.** `/nhl-late-swap <run> "<fresh DKEntries>"` runs the engine only, no agents, and pins locked cells. VERIFIED (`.claude/skills/nhl-late-swap/SKILL.md`).
- **Pre-lock refresh without Claude.** A Windows Task Scheduler job polls every 5 minutes and refreshes at T-60 and T-20 before first lock, showing a Windows toast when a file changes. VERIFIED (`config/scheduled_refresh.yaml`, `tools/notify.ps1`).
- **Morning after.** `settle` reads standings exports; `results` reads the DraftKings entry-history export and compares each entry with a random lineup's expectation. VERIFIED (`docs/CONTRACTS.md`, "Results report (C49)").
- **Build process.** Work is cut into numbered "chunks" with exit checks (`BUILD_CHUNKS.md`, `chunks.yaml`, `tools/next_chunk.py`), and each chunk is a PR. VERIFIED.

### Golf

- **Shape.** A pinned engine (`engine/`) plus a toolchain (`tools/`) driven by the `golf-generate-lineup` Cowork skill, which is "the only procedure". VERIFIED (golf `CLAUDE.md`).
- **A slate.** `sh tools/boot.sh` (install pinned packages, solver smoke test, repo doctor), `dk_reconcile.py` (names, encoding, contest inventory), `run_manifest.py snapshot` (freeze input bytes), contest facts from the DraftKings lobby through the user's connected browser, venue research by a subagent, `make_inputs`, `make_yamls`, `run_all_contests.py` (engine plus `robust_select` per contest), `apex_select.py` for large GPPs, `qa_lineups.py`, `make_entered.py`, `fill_entries.py`, then a run record and a git commit. VERIFIED (skill, Flow sections 1 to 6).
- **Runtime.** About 8 s for the engine and 37 s for `robust_select` per contest. VERIFIED (skill, "Environment facts").

### Soccer

- **Shape.** A Python CLI (`soccer.ps1` verbs: `new`, `build`, `refresh`, `simulate`, `certify`, `settle`, `evaluate`) with immutable snapshots, byte-aware parsing, a guarded exporter, and a fail-closed `certify` step. VERIFIED (soccer `CLAUDE.md`, Operator commands).
- **A slate.** Phase A (hours early): the LLM researches projected starting lineups and writes start probabilities into an Excel workbook; Phase B (T-45): fresh salary file, `refresh`, `build`, `certify`; Phase C (last 15 minutes): the LLM patches scratches by hand. VERIFIED (`soccer-generate-lineup/SKILL.md`).
- **What actually drove the upload.** "There is no solver." Lineups were weighted random draws, and the correlated simulation "never reaches the exported lineups." VERIFIED (soccer `DFS_SYSTEM_GREENFIELD_SPEC.md` sections 1.4 and D-04).

---

## 2. What worked well

| What | Where | Evidence |
|---|---|---|
| Legal file first, improvements second | NHL | Milestone "Uploadable legal file, offline, with lock-safe late swap" reached on day 3 (Sep 28), before any projection model. VERIFIED (`BUILD_STATUS.md`, Milestones). |
| Engine runs before the model reads; model only relays | NHL | Skill preprocessing plus `permissions.deny` on `Write(outputs/**)` and `Write(**/DKEntries*.csv)`. VERIFIED (`.claude/settings.json`). Measured cost of one headless run: 4 model turns, 137 s, about $0.46 at list price. VERIFIED (`docs/measured_usage.md`). |
| Byte-preserving output | NHL, soccer | NHL splices only changed cells and keeps every other byte; soccer's certified file "differs from `raw/DKEntries.csv` on exactly the six reservation lines". VERIFIED (NHL `intake/entries.py` keeps `line_bytes`; soccer spec section 1.5). No repo records a DraftKings rejection caused by formatting. |
| Honest status lines | NHL | `FILE_VALID`, `PAYOUT_SOURCE` (EXACT, TEMPLATE, PRIOR), `MARKET_COVERAGE`, `RISK_BUDGET`, and "Checked means the checks passed, nothing more." VERIFIED (`CLAUDE.md`). |
| Measuring against a random baseline | NHL | The results report corrects for small fields: a random entry averages (N+1)/2N of the field, not 50%. VERIFIED (`BACKLOG.md` B110). |
| Standings synthesis as a hypothesis source | NHL | 17 standings files turned into specific, testable claims (goalie in 91.8% of top-1% lineups; top 1% keeps the top two chalk pieces). VERIFIED (`reviews/2026-10-03_standings_synthesis.md`). |
| Decide and disclose instead of ask and wait | Golf | "A build runs start to finish without stopping for approval... This replaced a single blocking gate that failed on every build the workspace ever produced." VERIFIED (golf `CLAUDE.md`). Soccer's skill copied it. |
| Blocking checks that each map to a real near-miss | Golf | 11 checks, each answering "does this stop a wrong file reaching DK?" VERIFIED (golf `ops/policy.yaml`). |
| A living trap register | Golf | `ops/NAME_TRAPS.md` and the skill's trap list; for example, a prefix matcher silently swapping two golfers whose surnames share a prefix. VERIFIED. |
| DraftKings' own `Starting` column as lineup evidence | Soccer | 44 of 44 flagged starters matched independently published lineups. VERIFIED (soccer `BACKLOG.md` DEC-4). |
| LLM research that found real edges | Soccer | The UCL draft build found an absence DraftKings had not flagged, five players not registered for the competition, and a forward listed at a defensive role. VERIFIED (`slates/2026-09-09-ucl-classic/PHASE_A_HANDOFF.md`). |
| Showdown results | NHL | The one positive measured signal: 34 cashes in 78 against 22.4 expected, 16 top-10% finishes against 7.5, 5 of 7 slates better than random. THIN. VERIFIED (B110). |

---

## 3. What broke, and what recurred

### 3.1 The incidents that mattered most

| Incident | Sport | What happened | Evidence |
|---|---|---|---|
| Entries locked blank | Golf | R2 Showdown build was "BLOCKED 11 min past lock; 7 reserved entries locked blank". About 45 of 100 minutes went to environment repair. "That is the only realized money loss this workspace has produced and none of it was modelling." | VERIFIED (`WYNDHAM_2026_RETRO.md` section 1; skill, Boot) |
| Late repair reached DraftKings after lock | NHL | DraftKings accepted 20 of 28 rows and refused exactly the 8 rows v5 had repaired, because v5 arrived after a game started. v4, v5, and v5 again all downloaded as `DKEntries.csv`. | VERIFIED (B119; commit a38a582 "v5's 8 repairs were refused after lock") |
| Late swap failed on the first real post-lock file | NHL | 114 cells read `Name (ID) (LOCKED)`; the referee rejected the file; nothing published. The real-file test had always been skipped for lack of a fixture. | VERIFIED (B118) |
| Non-starting goalie entered | NHL | A confirmation posted five hours before lock never reached the file; the user was told to swap by hand and the entry went in unchanged. | VERIFIED (`reviews/2026-09-29_slate_review.md`, "What did not work" item 1) |
| Same lineup repeated across entries | Golf | The fill loop cycled lineups with a modulo; "every legality check still passed, so nothing surfaced it." | VERIFIED (commit 7e2801d) |
| Same golfer at Captain and FLEX passed the duplicate check | Golf | The check compared DraftKings IDs, and Captain and FLEX are different IDs for one person. | VERIFIED (`ops/policy.yaml`, INTRA_LINEUP_DUP comment) |
| Same-named contests overwrote each other | Golf | Contest config files were named from the contest name; DraftKings names are not unique. | VERIFIED (`BACKLOG.md` B38) |
| Lineups public before lock | NHL | Cloud runs committed entered lineups to a public GitHub repo through a PR before lock; one refresh changed two entries 36 minutes after the merge. The user said this is not acceptable. | VERIFIED (B113) |
| Gate bypassed by the LLM | Soccer | "The gate was routed around": the uploaded file was "not produced by any code in the repo." | VERIFIED (soccer spec section 1.5) |
| Odds dropped for 3 of 4 games | NHL | Team codes not marked verified, so the market feed was ignored for those games; the favored side flipped. | VERIFIED (`reviews/2026-10-01_run_session_report.md` F1) |
| Goalie in 85% of fees, flagged and shipped | NHL | "no knob setting meets the risk budget; least-risk point chosen"; stdout did not show it. | VERIFIED (same report, F2, F6) |

### 3.2 Recurrence by theme

Counts come from two crude methods, both stated so they are not over-read. **Commits:** commits whose message mentions the theme, and of those, how many also contain fix-like words (fix, bug, defect, repair, wrong, refuse). Golf writes large batch commits, so its counts are inflated per change. **Backlog:** NHL backlog rows (128) and golf backlog items (117) whose title or problem text mentions the theme. I ran both counts myself on the repos as of today.

| Theme | NHL commits (fix-like) | Golf commits (fix-like) | Soccer | NHL backlog | Golf backlog | Recurs in |
|---|---|---|---|---|---|---|
| Late swap, lock, clock | 39 late swap (21); 32 lock (10) | 9 lock (6) | 1 | 34 | 3 | All three (soccer had no clock at all: "Kickoff time is never parsed; the system has no clock", spec D-21) |
| Upload and delivery | 3 (1) | 28 (16) | 0 | 17 | 13 | NHL, golf, soccer |
| Contest facts and payouts | 18 (3) | 19 (12) | 0 | 25 | 10 | All three |
| Identity, IDs, Captain/FLEX | 27 ID (12); 7 captain (1); 1 FLEX (1) | 14 ID (10); 23 captain (18); 4 FLEX (4) | 1 | 23 | 17 | All three |
| Duplicates | 3 (1) | 17 (14) | 0 | n/a | n/a | Golf, NHL |
| Salary | 11 (7) | 19 (13) | 0 | n/a | n/a | Golf, NHL, soccer (one bad `Game Info` row aborted the salary parse, spec D-22) |
| Standings and measurement | 13 (1) | 4 (3) | 0 | 42 | 10 | All three |
| Environment and boot | 23 (5) | 19 (16) | 1 | 20 | 8 | All three |
| Encoding | 2 (1) | 6 (3) | 0 | n/a | n/a | Golf, soccer |
| Timezone | 4 (2) | 3 (1) | 0 | n/a | n/a | Weak signal; see below |
| Reproducibility | n/a | n/a | n/a | 15 | 2 | NHL, golf |
| "Invalid" | 2 (1) | 0 | 0 | n/a | n/a | No DraftKings "invalid lineup" incident recorded anywhere |

**Reading.** No repo records DraftKings rejecting a file as malformed. The failures were all about *time* (lock), *which file* (naming and versions), *which facts* (contests, statuses), and *who is who* (IDs and roles). Timezone bugs as such are rare: NHL stores UTC and displays America/Chicago from the start (`CLAUDE.md`, Style). But lock-time logic broke repeatedly: NHL's controller froze its own clock so the final lock check could never fire (`reviews/2026-10-03_independent_code_review_7140e0a.md` R01), and golf's lock time was "a hard fact that nothing enforces" until a later fix (`BACKLOG.md` B58).

---

## 4. What was painful to operate

1. **Environment setup inside the entry window.** Golf: 45 minutes of repair in a 90-minute window (above). NHL cloud: "a fresh cloud container has no `.venv`... The first `uv sync --frozen` hit a permission prompt that Ben rejected, which stalled the session", with first lock 40 minutes away. VERIFIED (NHL B34; `reviews/2026-10-01_run_session_report.md` section 1). Soccer: the Cowork sandbox shipped Python 3.10 while the code needed 3.12, so tests failed in ways "that look like broken code". VERIFIED (soccer `CLAUDE.md`, Environment gotchas).
2. **Cloud sessions lost everything between runs.** NHL cloud runs had no history store ("every cloud run projects on priors", B71), no cached payout tables (B91), and their run folders vanished, so they could not be settled later (B68). Four experiments were tested only on made-up data because "the cloud container that built C22 had no saved real runs" (B126, B127, also B102, B107). VERIFIED.
3. **Too many questions for the user.** Golf: "Ben's complaint: the build took a long time and he had to intervene multiple times to answer questions he didn't think were his to answer." VERIFIED (golf `BACKLOG.md`, "Read this before touching anything"). NHL: 106 open `[BEN]` flags with defaults in force. VERIFIED (I counted the table in `BUILD_STATUS.md`).
4. **Heavy session start-up.** NHL's selector reran every finished chunk's checks at the start of each build session (21 to 24 minutes logged), and the full test suite took 18 to 35 minutes (1,500+ tests). VERIFIED (`BUILD_STATUS.md` session log lines for C50, C23, C24; B86).
5. **A PR for every slate.** Each NHL cloud run opened a pull request just to keep a record of entered lineups, which ran CI on a data-only change. VERIFIED (B106; the PR list shows 27 entered-record PRs).
6. **Mounted-folder quirks (golf, Cowork).** Stale `.git/index.lock` files, deletes denied on the mount, `TMPDIR` on a full volume making the solver fail at first solve, and a 45-second command ceiling early on. VERIFIED (golf skill, "Environment facts" and Boot).
7. **Manual news handoff.** The user often knew news first. NHL added a one-line command so the user's own report counts as a source ("Ben's report in session is a source (B120)"). VERIFIED (NHL `CLAUDE.md`).
8. **Confusing or stale messages.** Soccer printed limitations that no longer applied ("The `[LIMITATION]` lines carry forward and go stale"). NHL labeled a -10.51 gain as "inside the band" (B80). Golf's "PASS" lines that checked nothing (B45). VERIFIED.
9. **LLM usage limits** were not recorded as a blocker in any repo. The one measurement: after NHL's C10 test runs the user's plan showed 21% of the session and 54% of the week used, with no per-skill split available in the desktop client. VERIFIED (`docs/measured_usage.md`). The binding constraints were context length during build sessions (NHL's rule: hand off at about 60% context) and wall clock near lock, not plan usage.

---

## 5. Hard-won DraftKings knowledge

Items R6 already covers (dual Captain IDs, 1.5x salary, FLEX versus UTIL labels, the entries file layout, standings layout, `(LOCKED)` cells) are only cross-referenced. New or sharper items are marked **new**.

**File formats and bytes**

- **new: Encodings differ inside one download.** The golf skill's trap register says DraftKings encodings "differ within one download: salaries UTF-8, entries cp1252. Write the filled file back in the source encoding." VERIFIED (golf skill; golf build notes record the byte `0xF8` for an accented name in DKEntries and `0xC3 0xB8` for the same letter in DKSalaries). Soccer: "DK files are not valid UTF-8 (cp1252 bytes in player names break a `utf-8-sig` decode)." VERIFIED (soccer skill, Pre-share verification). **My own scan** of the user's Downloads folder today: every `DKSalaries*.csv` (about 50 files, all sports) is UTF-8 with a byte-order mark; no `DKEntries*.csv` has a byte-order mark, and the four soccer files and one golf file that contain accented names are not valid UTF-8. The MLB, NFL, and NHL files are pure ASCII, which is why NHL's UTF-8-only reader (`intake/entries.py` line 71) never failed. For NBA: eight third-party copies of historical DraftKings NBA salary files are all ASCII (SUPPORTED that DraftKings strips accents from NBA salary names), while one third-party NBA standings copy carries UTF-8 accented names. So the parser must read bytes and detect the encoding per file, and the standings-to-salary name join needs accent folding. R6 and S1 mention only the byte-order mark and CRLF line endings; this is a gap to close.
- **new: DraftKings player IDs are per draft group.** Two soccer slates shared 26 player names and 0 IDs. VERIFIED (soccer spec section 1.5). Never key history, ownership, or results on a DraftKings ID.
- **new: Two salary rows can collapse to one name key,** and a writer that looks players up by name silently keeps the last ID while "every check still passes." VERIFIED (golf skill, trap register; `BACKLOG.md` B51). NHL avoided this by carrying role IDs end to end.
- **The entries file's embedded player list and the salary file can disagree after DraftKings adds players.** Players appeared in final standings who were not in the downloaded salary file. VERIFIED (NHL B27). NHL accepts a fresh salary file whose only difference is added rows, and refuses any changed original row. VERIFIED (B1 result).
- **new: A started game reads `In-Progress` in the salary file's Game Info and `In Progress` in the entries file's embedded list** (two spellings). VERIFIED (NHL `docs/CONTRACTS.md`, "Started slates").
- **new: One irregular Game Info value** (a postponed match) aborted soccer's whole salary parse. VERIFIED (soccer spec D-22). Parse row by row and degrade per row.

**Uploads and the entries file**

- Fill only the rows you change; DraftKings' instruction 5 says so, and golf trims the entries file to in-scope rows before filling. VERIFIED (golf skill, section 1). R6 agrees.
- **new: One lineup per entry, exactly.** Golf's highest-value check after the cycling bug. VERIFIED (golf `ops/policy.yaml`, ENTRY_CARDINALITY).
- **new: Check the Captain column in both directions.** A Captain-priced ID in a FLEX slot and a FLEX-priced ID in the Captain slot are both rejected. Golf's first check covered one direction only, and its Captain check "verifies its own assumption" because writer and checker share the column index. VERIFIED (golf `ops/policy.yaml`, CPT_SLOT and `known_circular`; skill, section 5).
- **new: Name every delivered file by version.** NHL now writes `DKEntries_v<N>_<hash prefix>.csv` and refuses to publish a late swap over a newer file. VERIFIED (B119 result; `docs/CONTRACTS.md`, C53).
- **No file from golf's toolchain was ever confirmed accepted by DraftKings** while its status gate existed, because every build was labeled do-not-upload or replaced by hand. VERIFIED (golf B59). NHL has upload read-backs ("20 of 28 accepted"). The NBA engine should ask for that count every time.

**Late swap**

- `Name (ID) (LOCKED)` cells in a post-lock download, also in the embedded list's `Name + ID` column; started games read `In Progress`. VERIFIED (NHL B118). Same as R6.
- **Unknown:** whether DraftKings accepts those markers back in an upload. NHL keeps them byte for byte and waits for evidence. VERIFIED as open (B122). See "Do today".
- **new: A repair delivered after a game starts is refused for the changed rows, and the earlier lineup stands.** VERIFIED (B119). A late fix has to beat the *earliest* game it touches, not the slate's last game. NHL now prints `LOCK_SOON` for any changed cell whose game starts within 30 minutes. VERIFIED (`docs/CONTRACTS.md`, C53).

**Contest metadata**

- **new: The dollar figure in a contest name is often not a prize pool.** "$3K mini-MAX [150 Entry Max]" cannot guarantee $3,000 from a 150-entry, $0.50 field, and a loose parser read "$25 Millionaire" as $25 million. When a name carries "[N Entry Max]", that cap wins. VERIFIED (golf skill, section 2 and trap register).
- **new: "Top N Win $X" (Booster) contests pay a flat prize to the top N** and need their own objective; NHL priced one as a 5,000-entry GPP until it read the name. VERIFIED (NHL B108, C47).
- **new: DraftKings' contest pages and draftables endpoints answered HTTP 403 to NHL's machine** for most of its life, so field sizes fell back to priors. VERIFIED (NHL B24, B72; `reviews/2026-10-03_showdown_stl_col_run_record.md`). R6 independently concludes the engine should not call those endpoints at all, for terms reasons.
- **new: The user's entry-history export gives field size, prize pool, places paid, and our place for every past contest,** and NHL turned it into a committed facts table that sizes and prices 44 recurring contest keys. VERIFIED (NHL B91 and B111 notes; `data/contest_facts/nhl.csv`). R8 found the same export for NBA.

**Standings and settlement**

- Ties pool the tied places' prizes and split them evenly; NHL's working rule floors each share to the cent, but the DraftKings terms verify only the even split. VERIFIED (NHL `docs/payouts.md`; `BUILD_STATUS.md` flag 9).
- Standings files do not carry our winnings; the entry-history export does. Settling needed both. VERIFIED (NHL B47, B110).
- Large fields held 7 to 16% duplicate lineups, and one opponent entered 150 identical lineups. VERIFIED (`reviews/2026-10-03_standings_synthesis.md`, section 4). The field model must keep multiplicities.
- **new: Standings retention is unknown.** Golf could not confirm how long DraftKings keeps the standings download and noted a third-party claim that DraftKings edits historical files. VERIFIED as open (golf B73). Pull standings the next morning, not weeks later.

**Showdown (Captain + FLEX)**

- NHL treated each person once and mapped the Captain and FLEX rows to that person's single simulated outcome, from day one: "Simulate once per person. Role rows (CPT and FLEX, or a Classic row) map to that person's outcome; Captain scoring is applied once at lineup scoring." VERIFIED (NHL plan, "Decisions that shape the design").
- An exposure cap keyed on the person across all slots cannot express "how often is X the Captain"; golf's tools could not, so the LLM checked it by hand. VERIFIED (golf skill, section 4b).
- **new: Float literal trap.** A "33%" Captain cap written as `0.33` floors to zero Captains at 3 lineups; use the fraction 1/3. VERIFIED (golf skill, section 4b).

---

## 6. Data sources, failures, and terms

| Source | Repo | Used for | What went wrong, or what the terms say |
|---|---|---|---|
| DraftKings lobby, contest, draftables JSON | NHL | Field size, payouts, status | Plan revision 2 made them "first-class inputs" (VERIFIED, `NHL_DFS_PLAN_AND_ARCHITECTURE.md`); they answered 403 for most runs (B24, B72). R6 says DraftKings' terms bar automated access. **Do not carry over.** |
| DraftKings lobby through the user's logged-in browser | Golf | Contest facts | "Fill them from the DK lobby through the connected browser." VERIFIED (golf skill, section 2). Same terms problem. **Do not carry over.** |
| DraftKings public salary endpoints, polled | Soccer (proposed only) | Fresh salary file | Recommended "Yes for a 2-minute poll" (soccer `BACKLOG.md` DEC-3). Same terms problem. |
| DraftKings `Starting` column | Soccer | Confirmed lineups | 44 of 44 matched. VERIFIED (DEC-4). R6 lists the NBA `Starting` column as a BET to confirm. |
| NHL web API, NHL partner odds | NHL | Rosters, box scores, odds | The odds feed was 31.8 days stale on one run; team codes not marked verified dropped 3 of 4 games. VERIFIED (B5, B35). |
| Covers | NHL | Fallback odds | Parser failure on the live page. VERIFIED (B5). |
| MoneyPuck | NHL | History | "free to use for non-commercial purposes", credit required, "non-approved scraping ... will be blocked". VERIFIED (plan section 3). |
| Daily Faceoff | NHL | Goalies, lines | Parsed from the page's embedded JSON; line pages were often over 24 hours old, so a team's lines were dropped. VERIFIED (`docs/sources.md`). |
| RotoWire news page | NHL | Second goalie source | Its terms forbid automated access in writing; the user accepted that, and NHL reads one page with strict rate limits. VERIFIED (`docs/sources.md`, "Terms"). |
| DataGolf, PGA Tour leaderboard, VegasInsider | Golf | Skills, live state, odds | DataGolf uses `-9999` as an undocumented missing-value marker; the odds capture "silently degraded to skipped" one week. VERIFIED (golf skill, trap register; retro section 6). |
| the-odds-api | Golf and soccer (proposed), MLB (in use) | Odds | Recommended in both; the key already exists in the MLB tooling. VERIFIED (soccer `BACKLOG.md` rank 1; golf retro section 5). |
| Paid player-rate provider | Soccer | Rates | Never bought (DEC-1), so projections stayed at position priors. VERIFIED. |

**Pattern across sports.** Every engine reached for DraftKings' own data automatically (NHL endpoints, golf browser, soccer polling proposal), and every engine leaned on at least one third-party page whose terms forbid or limit automated use. The user has twice accepted third-party terms risk (RotoWire, MoneyPuck). R6's finding that DraftKings' own terms put the real-money account at risk is new relative to all three repos; S1 already follows it.

---

## 7. Modeling: believed versus measured

| Belief at build time | What was measured | Evidence |
|---|---|---|
| A top-1% payout objective picks better tournament lineups (NHL Classic) | Classic cashed 23 of 136 against 32.2 expected; 0 of 135 GPP entries in the top 1% against 1.2 expected; return -62.5% against a rake-implied -12.2%. Showdown beat random. Both THIN. The objective as the cause is NHL's own "Hypothesis, thin": the same period had dropped odds (B35), a slate with zero skaters from the 8-goal team (B51), priors-only cloud runs (B71), entries built outside any recorded run, and engine changes. | Numbers VERIFIED (B110, B112); cause is a hypothesis |
| The projection layer adds ordering skill (golf) | Rank correlation with results: projection 0.391, salary 0.408, raw DataGolf rank 0.415. | VERIFIED (`WYNDHAM_2026_RETRO.md` F1) |
| Golf win probabilities are tournament-shaped | 9.83% on the favorite (finished 61st), 1.24% on the winner. | VERIFIED (retro F2) |
| The ownership model predicts the field (golf) | Its ownership had rank correlation 1.000 with the engine's own value column: "a value echo, not a field model." Real chalk was inverted. | VERIFIED (retro F3) |
| Ownership from a sampled opponent field (NHL; S1's design) | Classic ownership correlation 0.43 to 0.54 on opening night; news-driven chalk missed (50.7% versus 4.7%; 43.7% versus 3.7%). Later per-player grades were acceptable (mean error 3.9 to 4.3 points, correlation 0.71 to 0.75), but the field gave only 25% of opponents a stacking behavior when 93.5% of real lineups held a 3+ stack. | VERIFIED (`reviews/2026-09-29_slate_review.md`; `reviews/2026-10-03_standings_synthesis.md` section 4) |
| Median, 90th, 99th percentile and expected-payout objectives give different portfolios (golf) | They "produce identical 20-lineup portfolios, player for player", because the ceiling statistic was a rescaled mean (R-squared 0.99864). | VERIFIED (retro F4; `BACKLOG.md` B55) |
| A stylized payout curve is close enough (golf) | 35.6% of the pool to first against a real 10 to 18%; min-cash at 2% of the fee. Rank resolution saturated about two orders of magnitude below first prize. | VERIFIED (B53, B54) |
| A few thousand sampled opponents resolve first place (NHL) | A 300-lineup field gave a $1 GPP lineup 1.4% first-place equity; at 5,000 lineups it fell to 0.18%. The repo also flags its sampled field as weaker than the real one, so GPP figures read optimistic. | VERIFIED (`BUILD_STATUS.md` C8 log line, item 3; B15) |
| Fading chalk wins tournaments (common belief) | NHL top-1% lineups kept the slate's top two chalk pieces 90 to 100% of the time and differentiated with low-owned teammates; they were chalkier than the field whenever the chalk hit. | VERIFIED (synthesis section 4, item 2) |
| Contrarian Captains pay (NHL Showdown) | The two contrarian-Captain entries were the two worst Showdown entries on opening night; in one later game no top-1% lineup had a goalie Captain while 23% of the field did. One or two games: anecdote. | VERIFIED (09-29 review item 4; synthesis section 3) |
| The simulator is calibrated (NHL) | Calibration checks pass for goals, assists, shots, saves; the 3+ point tail is too thin (66 observed versus 47.1 expected) and linemates' joint ceilings are under-predicted (ratio 0.55). | VERIFIED (`docs/calibration/2026-10-13.md`) |
| Independent Poisson team goals fit the market (soccer) | It cannot fit an extreme favorite: 75.6% win modeled against a 92.6% devigged market for one match, which made the underdog's players look underpriced. | VERIFIED (`slates/2026-09-09-ucl-classic/PHASE_A_HANDOFF.md`) |
| A weighted sampler is close to an optimizer (soccer) | The best sampled lineup averaged 5.7% below the exact optimum on a real 44-player pool. | VERIFIED (soccer spec D-08) |
| Projected starting lineups are reliable (soccer) | 77 of 88 starters correct; 16 projected starters benched, clustered by team. | VERIFIED (soccer skill, "Expect this to be wrong a lot") |

**What carries to NBA.** The NHL standings findings have NBA analogs worth testing on NBA standings rather than assuming: (1) cashing looks like the field plus the right chalk; (2) the top 1% adds the right low-owned pieces around the chalk rather than fading it; (3) news-driven value chalk is the ownership event a field model most often misses. Item 3 matters more in NBA, where injury replacements drive ownership. BET on the transfer; VERIFIED for NHL.

---

## 8. The LLM layer

| Element | Repo | Effective? | Evidence |
|---|---|---|---|
| Skill that runs the engine before the model reads (`!` preprocessing, `disable-model-invocation`, narrow `allowed-tools`) | NHL | Yes. One headless run: 4 turns, 137 s, about $0.46 at list price. | VERIFIED (`docs/measured_usage.md`) |
| Skill frontmatter | NHL | Fragile: invalid YAML "silently dropped shell and allowed-tools"; fixed with a test that parses frontmatter. | VERIFIED (commit a041d1e) |
| Write denial on outputs and entries files | NHL | Yes; nothing records the model editing a lineup file. | VERIFIED (`.claude/settings.json`) |
| Researcher subagent (web search; JSON overrides with source URL and confidence) | NHL | Useful for goalie confirmations, but scoped too narrowly at first: it researched only players already in the portfolio, so research "can never promote a goalie who is not already chosen." User-named players were added later. | VERIFIED (run report F3; B37; B120) |
| Adversary subagent (sees only a packet, returns typed swap proposals; code accepts on paired simulations) | NHL | Low yield so far: 1 of 4 accepted on Oct 1 (one more rejected only because of proposal ordering), 0 of 3 on Oct 3. Isolation rehearsals passed (canary echoed, no CLAUDE.md leakage). | VERIFIED (run report F4; STL@COL run record; `docs/measured_usage.md`) |
| Main model relaying a packet by retyping it | NHL | Failed once: "A packet value was mistyped when relayed to the adversary." | VERIFIED (B81) |
| One long skill as the whole procedure (765 lines) | Golf | Drifted from the code and CLAUDE.md, and needed a byte mirror plus a drift check. | VERIFIED (golf B96, B99, B112) |
| LLM doing deterministic work | Golf, soccer | Golf's Captain cap was an "OPS procedural check that no tool performs"; soccer's LLM hand-picked the lineup, checked legality by hand, and built an upload outside the CLI. | VERIFIED (golf skill 4b; soccer handoff "Legality checked by hand"; spec section 3.3) |
| LLM research of news and roles | Soccer | High value: unflagged absences, unregistered players, role changes. The skill says these edges "are often worth more than the optimizer." | VERIFIED (soccer skill; handoff) |
| Usage limits | All | Never recorded as the binding constraint. Context length during build sessions was (NHL hands off at about 60%). | VERIFIED (NHL `CLAUDE.md`, Development session protocol) |

**Net.** The evidence supports S1's boundary (the LLM files beliefs; code builds lineups) from both sides: where the LLM did deterministic work (golf, soccer), it produced bypasses and hand checks; where it did research (soccer, NHL goalies), it added the most value per minute. NHL's QA adversary has not yet earned its cost; keep it cheap and scored.

---

## 9. Testing, validation, and wrong files that reached the user

**What the repos did.** NHL: 1,500+ tests, real-file fixtures kept out of git with loud skips when absent, and an independent code review that reproduced 4 high-priority defects (two ways to publish after a game starts, an override that could re-add an OUT player, and a selector that credited one owned entry for another's prize) before they cost money. VERIFIED (`reviews/2026-10-03_independent_code_review_7140e0a.md`). Golf: a `doctor` that checks paths and imports, the blocking list, byte re-reads after writing. Soccer: an independent final-byte re-parse in `certify`.

**Where testing failed.**

- Tests passed on synthetic files while the real format differed: NHL's real post-lock test "skips for lack of the fixture", and the first real file broke late swap. VERIFIED (B118).
- Circular tests: golf's fill test "reproduces a historical artifact byte-identically, but that artifact was produced by this same code path, so the test is circular." VERIFIED (B59). Golf's regression gate "auto-widens to whatever the engine currently does, so it cannot fail." VERIFIED (B46).
- Checks that printed PASS without checking: "Four gates emit PASS without checking anything." VERIFIED (golf B45). Golf's QA once reported a pass over 5 of 13 lineups because it audited only the files it could find. VERIFIED (golf skill, trap register).
- Experiments that could not be decided: four NHL strategy experiments ran only on synthetic data and shipped switched off. VERIFIED (`docs/roadmap/plain.yaml`, ask "real-data-tests").

**Wrong or late files that reached the user or DraftKings.**

1. NHL Oct 11: v5 reached DraftKings after lock; 8 repairs refused (B119).
2. NHL Sep 29: the delivered Classic lineup held a goalie who was confirmed not starting five hours before lock; the engine did not repair it, the user was told to swap by hand, and the entry went in unchanged (09-29 review).
3. NHL Oct 1: a portfolio with one goalie in 85% of fees, flagged by the engine, shipped without the flag in the summary (run report F2, F6).
4. Golf, July: lineups repeated across entries by modulo cycling, passing every check (commit 7e2801d).
5. Golf, early August (third sighting Aug 5): an already-committed filled entries file changed on disk about 6 minutes after being written, remapped onto other contests' entries, with no tool call explaining it; flagged, never explained. VERIFIED (golf B30). Lesson: check the delivered file's hash at hand-off.
6. Soccer, Aug 29: the uploaded lineups were "random confirmed-starter lineups ranked by role multiplier," built outside the CLI (spec section 1.5).
7. Golf Wyndham Captain Showdown: the user's own hand-built lineup outscored all six engine lineups (graded on a to-par proxy), and on another build the user replaced all five engine lineups with his own picks before upload. VERIFIED (retro section 2; `BACKLOG.md` B73). Not a wrong file, but nothing ever scored engine against user.

---

## 10. Against the S1 sketch: what the evidence confirms, what is missing, what may be wrong

### 10.1 Confirmed by the prior engines (keep as written)

- **Valid output first (S1 B2.3, B9.2).** NHL reached a legal, lock-safe file on day 3, and no NHL record shows a slate lost to a missing file; golf's only recorded money loss was blank entries. VERIFIED (sections 2 and 3).
- **The LLM sets beliefs; code sets lineups (S1 B2.2, B4).** Supported from both sides (section 8).
- **Manual DraftKings, Claude only on command, background polling in plain Python (S1 B2.5, B2.6).** NHL's Task Scheduler refresh with a Windows toast is a working example. The prior engines broke the DraftKings half (section 6); S1 is stricter and should stay so.
- **Questionable players random inside the simulation, with precomputed swaps (S1 B5).** NHL built "DTD participation inside the simulator" only on Oct 13 (C24), after a season of handing the user manual swap advice that did not get acted on (09-29 review). Soccer's last-15-minutes triage was done by hand by the LLM. Both point the same way as S1.
- **Pair Captain and UTIL rows by person, read slot labels from the header (S1 B6).** NHL did this from the start; golf's ID-based checks let one golfer hold both slots.
- **Duplication matters (S1 A2).** 7 to 16% of large-field NHL lineups were duplicates, including one block of 150.
- **Fast per-layer signals over slow results (S1 B8).** NHL's slow signal after 16 slates is still THIN; golf's "measurements" were the model grading itself (golf B47: "all of it is the model grading its own homework").

### 10.2 Missing from S1, or likely wrong

1. **The one measured result touches Goal 1's cost, weakly.** NHL Classic entries built on a top-1%-payout objective cashed at about 70% of a random lineup's rate, with no top-1% hits (THIN; numbers VERIFIED). Whether the objective caused it is a hypothesis, because the same period had several confounds (section 7). S1's 5% insurance default (A5) is already labeled a bet; this evidence does not settle it, but it is a reason not to treat washout protection as a tie-breaker. Recommendation (BET): on night 1 publish the frontier, and for the first 20 nights track per-entry cash rate against each contest's paid share as the first gate, before any top-1% claim.
2. **Goal 1 is undefined for flat-prize contests.** "Top 1%" is the wrong target in a Double Up, a Booster ("Top N Win $X"), or a satellite that pays the same ticket to every winner. NHL found a 2,300-entry contest paying 23% of its field being "chosen like a top-heavy GPP" (B112), and golf's best lineups landed in satellites where "1st and 500th pay the same $25 seat" (retro F5). S1 needs a per-contest-type definition (NHL used: cash = probability of clearing the line; Booster = probability at least one entry is in the top N; satellite = probability of a seat) and the user should confirm which contest types count toward Goal 1. VERIFIED evidence; the definitions are BET.
3. **Field strength, and field sample size where k = 1, matter more than scenario count (S1 A2, A6).** S1 quotes Monte Carlo error over scenarios. NHL's evidence splits two cases. For a large field's top-1% probability, the sampled field size barely mattered: P(top 1%) stayed flat at about 0.033 as the field sample grew from 300 to 5,000 lineups. What it got wrong was *strength*: a single-entry GPP lineup showed 3.4% against a 1% fair share, and the repo flags its sampled field as weaker than the real one (B15). Where only first place counts (S1's k = 1, fields under 200) and for prize-share and duplicate estimates, sample size does matter: first-place equity fell from 1.4% to 0.18% as the sample grew, and golf's band-averaged ranks "saturated" far below first prize (B54). So: calibrate field strength against standings first, size field samples to resolve first place where k = 1, and treat "predicted top-1% line versus the actual line from standings" (already a fast signal in S1 A6) as a go/no-go check before quoting Goal 1 numbers. VERIFIED evidence (`BUILD_STATUS.md` C8 log line, item 3); remedy BET.
4. **Field realism needs structure checks, not only player ownership.** NHL's per-player ownership looked acceptable while the field's team concentration was badly wrong (25% stacking behavior against 93.5% real), and its sampled field was weaker than the real one (B15). Golf's sampled opponents were 673 of 1,000 over the salary cap. Check the simulated field against standings on salary used, team concentration, chalk pairs, and duplicate rate, per contest type. VERIFIED.
5. **"Late news flows through automatically" (S1 B7) must be an acceptance test.** NHL built the same design and still missed replacement chalk by 10x because news never reached the field inputs (B20, B63). Test before opening night: rule a starter OUT in a preseason slate and require the replacement's predicted ownership to rise to a plausible range. VERIFIED evidence; test is BET.
6. **Common random numbers and replay need design rules, because both broke before.** (a) Draw random numbers per player from a stream keyed by a stable person ID, never by row position (golf B52). (b) No wall-clock time limit on any step that decides lineups; use iteration or node limits, or record every limit hit (NHL B98). (c) Results must not depend on thread count (NHL tested this). VERIFIED evidence.
7. **The salary file should be required for the final build, not optional (S1 B3 item 1, B9.1).** It is DraftKings' only player-status source, it marks started games, and DraftKings adds players after earlier downloads (NHL B1, B27; R6 says the entries file's embedded list has no `Status`). Recommendation: entries file always; a fresh salary file required for any build inside the last two hours, optional before that. BET on the cut-off.
8. **Encoding rules are missing from R6 and S1.** See section 5: entries files with accented names are cp1252, salaries are UTF-8 with a byte-order mark, standings can carry UTF-8 accents. NBA names look ASCII in salary files (SUPPORTED), but the parser should not depend on it.
9. **"Payout tables from an optional paste or a default by contest class" (S1 B9.1) is the weakest input in the plan.** Class defaults were badly wrong in golf and NHL. Build a contest facts table from the user's entry-history export (R8 has the file; NHL C50 shows the method), add the name rules from section 5, ask for a paste only for contests not in the table, and print each contest's payout source (exact, history, prior) in the brief, as NHL's `PAYOUT_SOURCE` does. VERIFIED evidence.
10. **Late swap needs four concrete safeguards beyond S1 B5.** (a) Rehearse on a real post-lock export before Oct 20 (R6 found a real mid-slate MLB download with `(LOCKED)` cells; NHL's B118 export is another). (b) Version-named delivery files only. (c) Warn per changed cell when its game starts within 30 minutes, keyed to the earliest game the change touches. (d) Ask the user for DraftKings' "uploaded N of M" count after every upload. VERIFIED evidence (NHL B118, B119, B122).
11. **Privacy and where runs happen.** Never put entered lineups in a public repo before lock (NHL B113); run slates locally, because cloud runs lost history, payout tables, and run folders (B68, B71, B91). R7 already says laptop; make it a rule, and make the NBA repo private. VERIFIED.
12. **Environment preflight hours before lock.** Golf's `boot.sh` (solver smoke test, package check) exists because of the blank entries; NHL's cloud bootstrap exists because of a stalled install. The NBA preflight should run when the user opens the session, before the first build, and include R7's `ANTHROPIC_API_KEY` check. VERIFIED evidence.
13. **The researcher's scope must include players the engine does not own.** NHL research covered only the current portfolio's players, which locked in the baseline's choices (B37). S1 B3 item 20 reads a "deterministic news diff"; make that diff cover every pool player whose status or role changed, plus any player the user names (B120). VERIFIED.
14. **Agents read their input from a file with a hash or canary; the main model never retypes it.** NHL's one relay error came from retyping (B81). VERIFIED.
15. **The brief must lead with breaches.** NHL shipped a flagged concentration because the flag was in the notes file, not the printed summary (run report F6). Any breached budget, stale input, or prior-sourced payout table goes in the first lines of S1's slate brief. VERIFIED.
16. **Score the user's own overrides as a layer.** The user replaced engine lineups by hand in golf and once beat them; nothing measured it (golf B73). Add "user override" to S1 B8's per-layer scorecards. VERIFIED evidence.
17. **Build process limits belong in the design.** S1 is silent on how the engine is built and maintained, which is where the prior engines spent most of their effort. Proposed limits (BET): at most five open decisions for the user at any time, each with a recommended default; a fast test tier under 5 minutes; no strategy experiment on synthetic data only; no more than six status words; and no blocking check without a code path that can make it pass.
18. **Captain diversification in Showdown is unstated.** Golf carried a standing user rule (no player Captain in more than one third of a contest's lineups); NHL capped Captains at small entry counts. S1's coverage objective may diversify Captains on its own, but the user should say whether the one-third rule carries over. VERIFIED that the rule existed; whether it applies to NBA is the user's call.

---

## 11. Reuse candidates (default: learn, do not reuse)

| Candidate | For | Against | Verdict |
|---|---|---|---|
| NHL `learn/entry_history.py` and `learn/results.py` (DraftKings entry-history reader; results against a per-entry random baseline with small-field correction, slate bootstrap, THIN label) | Reads the exact 14-column header R8 uses; standard library plus numpy only; 37 tests on synthetic fixtures; definitions already written down (`docs/CONTRACTS.md`, "Results report") | Hardcodes `SPORT = "NHL"` and an engine-era date; NHL contest-kind name rules need NBA review; about 780 lines | **Reuse with small edits.** The strongest code-reuse case found. |
| NHL entries reader, byte-splicing writer, and independent referee (`intake/entries.py`, `export/writer.py`, `referee/`) | Handles `(LOCKED)` cells, `In Progress` rows, CRLF, byte-for-byte preservation; proven on real NHL files | Decodes UTF-8 only (fails on cp1252 accents); NHL roster rules and FLEX label baked in; tied to NHL contracts | **Learn the pattern; rebuild small for NBA; port the test cases** (especially the post-lock fixtures). |
| NHL `normalize_name` (accent folding plus transliteration of letters Unicode does not decompose) and `person_key` | Small, pure, tested | Trivial to rewrite | **Copy the function and its tests.** |
| NHL `tools/notify.ps1` and the Task Scheduler refresh pattern | 30 lines, no network, Windows PowerShell 5.1; fits R7's rule that only Python runs on a schedule | Trivial to rewrite; the dispatcher is NHL-specific | **Copy `notify.ps1`; rebuild the dispatcher.** |
| NHL skill pattern (`!` engine run, `disable-model-invocation`, `allowed-tools`, write denial, `omitClaudeMd` agents, canary rehearsal) | Measured cheap and safe | Frontmatter errors fail silently | **Reuse the pattern plus a frontmatter-parsing test.** |
| Golf blocking-check list (`ops/policy.yaml`) | Each of the 11 checks exists because of a real near-miss | Golf code; partly circular (CPT_SLOT) | **Reuse the list as a checklist against R6's validator list; no code.** |
| Golf and NHL trap registers (`NAME_TRAPS.md`, skill trap list, NHL `docs/sources.md`) | Cheap, specific | Sport-specific content | **Learn the habit: one living traps file.** |
| NHL contest facts method (C50) and contest-kind name rules | Solves the worst input problem with data the user already has | NHL key format and families | **Rebuild for NBA from R8's export.** |
| NHL field sampler, portfolio selector, objectives, controller (C3, C8, C18 to C23) | Most sophisticated piece in any repo | Nondeterministic under load (B98); 1 GB at 150 entries (B16); objective under question (B112); hockey-specific stacks and goalie logic; heavy | **Do not reuse. Learn from its measurements.** |
| Golf engine, `robust_select`, `apex_select` | Winner-equity idea is interesting | Golf-specific; never scored | **Do not reuse.** |
| Soccer code | Byte-aware ingest and guarded export are fine | Governance modules slated for deletion; no solver; never settled | **Do not reuse.** |
| MLB baseline-first workflow and NFL byte-aware slot editing | NHL's plan says they were strong patterns | Seen only secondhand here (NHL plan section 1) | **Out of scope for this memo; other reviewers cover them.** |

---

## 12. Did the engines get better or worse?

Read in build order: golf (Jul 29), soccer (Aug 19), NHL (Sep 26).

- **Golf learned inside its own life, mostly about process.** It started with a six-status vocabulary, a human approval gate, and long build notes for a reader who did not read them; from Aug 6 it deleted the status vocabulary and the approval gate and cut the notes back to a short run record ("A gate that has never once passed carries no information", golf B74, B75, B76). Its ledger never closed the measurement loop (0 of 24 events scored, B47); one event was hand-scored in the Wyndham retro.
- **Soccer repeated golf's central mistake after golf had already fixed it.** Golf deleted its never-passing gate on Aug 6; soccer, started Aug 19, built a fail-closed certification that could not pass on any real slate, and on Aug 29 the operator built the file around it (soccer spec section 1.5). Its red-team audit said the plan was over-built "by roughly two orders of magnitude", and the repo then added a 980-line provenance validator and a 971-line identity workflow anyway (spec section 3.1). **Worse.**
- **NHL fixed the big modeling and measurement gaps of both predecessors.** It built the legal file and late swap first, made identity role-aware from day one (citing the MLB defect), settled real slates within days, produced the first honest results-versus-random report within two weeks, and replaced guessed contest facts with the user's own history. **Better on safety and measurement.**
- **NHL repeated other mistakes and scaled up the ceremony.** It paid the environment tax inside the entry window again (cloud install stall, B34), depended on DraftKings endpoints (403s) as golf depended on the lobby, lost a late repair at lock (B119) as golf lost entries at lock, and ran experiments on synthetic data. Its decision queue (106 flags) and test suite (18 to 35 minutes) are larger than golf's whole operation. **Not leaner.**

The direction is clear: each engine got more careful about *correctness* and the last one finally measured *results*, but none of them got cheaper to build or run per entry.

---

## Lessons that recur across sports

Recurrence across sports is the strongest signal in this review. Count = number of the three repos where the lesson shows up with evidence.

| Lesson | Sports | Evidence |
|---|---|---|
| A blocking check with no path to pass gets bypassed, and a status that fires on every run carries no information | 3 of 3 | Golf `ops/policy.yaml` header; soccer spec 1.5 and 3.1; NHL run report F2 (breached budget shipped) |
| Lock time is where money is lost (blank entries, refused late repairs, a clock that cannot fire) | 3 of 3 | Golf retro section 1 and B58; NHL B119 and review R01; soccer spec D-21 ("the system has no clock") |
| Contest facts (size, payouts, type) are missing or wrong, and the model leans on them | 3 of 3 | Golf B53, B54, retro F5; NHL B72, B108, B111; soccer field sizes and payouts typed into Excel by hand (spec section 3.2) |
| Person identity versus DraftKings role ID breaks things (Captain and FLEX, per-draft-group IDs, name collisions) | 3 of 3 | Golf policy INTRA_LINEUP_DUP and B51; soccer spec 1.5 (0 of 26 IDs shared); NHL plan section 1 (MLB's role-blind duplicate key) |
| Environment and session setup fail inside the entry window | 3 of 3 | Golf R2SD; NHL B34; soccer Python 3.10 sandbox |
| Process overhead outgrows the stakes | 3 of 3 | Golf greenfield adjudications; soccer spec 3.1; NHL 106 flags and B86 |
| Measurement is planned but not done, or is the model grading itself | 2 of 3 (NHL fixed it) | Golf B47 (ledger 0 of 24; one event hand-scored in the Wyndham retro); soccer "zero slates settled"; NHL B110 is the counterexample |
| The LLM ends up doing deterministic work when the code cannot | 2 of 3 | Golf skill 4b; soccer handoff and spec 3.3 |
| Ownership models miss the field (value echo; news-driven chalk; team concentration) | 2 of 3 (soccer never built one) | Golf retro F3; NHL 09-29 review and synthesis section 4 |
| Encoding of accented names in DraftKings entries files | 2 of 3 | Golf skill; soccer skill; my Downloads scan |
| Same inputs, different outputs (row order, wall-clock limits) | 2 of 3 | Golf B52; NHL B98 |
| Automated access to DraftKings data despite account risk | 3 of 3 (soccer proposed only) | NHL plan revision 2; golf skill section 2; soccer DEC-3 |
| News arrives after hand-off and depends on the user acting | 2 of 3 | NHL 09-29 goalie; soccer Phase C triage |
| One-off (single sport, weaker signal): versioned delivery names (NHL), public-repo exposure (NHL), same-named contests overwriting (golf), an unexplained file mutation (golf), the Poisson fit failing on heavy favorites (soccer), contrarian Captains failing (NHL, one or two games) | 1 of 3 | Sections 3 and 7 |

---

## Top 10 lessons for the NBA engine

1. **Win the clock first.** Run the environment preflight when the session opens, build the legal fallback before anything else, and treat "file delivered before the earliest affected game locks" as the engine's first success measure. Two sports lost money here and none lost money to a bad model. (3 of 3)
2. **Version every delivered file and read back the upload count.** `DKEntries_v<N>_...csv`, a per-cell `LOCK_SOON` warning, compare-and-swap publishing, and the user's "uploaded N of M" line after each upload. (NHL B119)
3. **Rehearse late swap on a real post-lock file before Oct 20, and settle the `(LOCKED)` upload question on tonight's NHL slate.** (NHL B118, B122)
4. **Build the contest facts table from the user's entry-history export before opening night,** with the name rules ("[N Entry Max]" beats the dollar figure; "Top N Win $X" is a Booster; Double Up and Triple Up are cash), and print each contest's payout source. (3 of 3)
5. **Define Goal 1 per contest type and watch its cost in cash rate from night 1.** Publish the frontier and track cash rate against paid share as the first gate. NHL Classic, built on a top-1% objective, trailed random at cashing and had no top-1% hits (numbers THIN; the objective as cause is a hypothesis). (NHL B110, B112)
6. **Validate the simulated field against standings on structure and strength, not just player ownership,** and make "starter ruled out raises the replacement's ownership" a pre-opening-night test. (Golf retro F3; NHL B15, B20, B43)
7. **Make replay and paired comparisons real:** per-player random streams keyed by stable person ID, no wall-clock limits on decision steps, thread-independent results. (Golf B52; NHL B98)
8. **Identity by person, never by DraftKings ID or name alone,** with role-aware duplicate and exposure checks, Captain-slot checks in both directions, and byte-level reading that handles cp1252 entries files and UTF-8 standings. (3 of 3)
9. **Keep the LLM on research, aimed wide, and keep it off the critical path.** Researcher covers every changed pool player plus anything the user names; agents read inputs from files; the main model never retypes; the QA adversary stays one cheap round and is scored. (Golf, soccer, NHL)
10. **Budget the process, not just the engine.** Few statuses, few user decisions at a time with defaults, a fast test tier, no gate without a passing path, no experiment without real NBA data, a private repo, and local runs. (3 of 3)

---

## Appendix: method

- **Read:** each repo's `CLAUDE.md`, plans, backlogs, build status, reviews, retros, skills, agent definitions, settings, selected source files, and full commit logs; NHL PRs with `gh pr list` (golf and soccer have no issues; NHL has no issues and 66 PRs). Nothing was run except read-only scripts that count, scan bytes, or parse tables.
- **Commit theme counts:** a Python script over `git log --format=%B` per repo, case-insensitive keyword patterns per theme, a commit counted once per theme; "fix-like" means the same message also matches fix, bug, defect, repair, wrong, broke, regress, or refus. Keyword hits, not a classification of each change.
- **Backlog theme counts:** the same idea over NHL's 128 backlog table rows (ID, date, and problem columns) and golf's 117 backlog item titles. Golf titles are short, so golf counts understate.
- **Encoding scan:** counted bytes above 127 in every `DKEntries*.csv` and `DKSalaries*.csv` in the user's Downloads folder and in R6's saved third-party NBA files, then tried a UTF-8 decode. Only counts and a few public player-name fragments were printed; no entry rows were read into this memo.
- **Not opened:** `mlb-dfs`, `nfl-dfs`, `dfs-os`, `nba-betting-system`.
