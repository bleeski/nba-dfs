# Adjudication of the round 2 reviews

**Date:** 2026-10-14. **Adjudicator:** Claude (Opus 5.5), acting as architect, with the Fable advisor live in the session. **Inputs:** Review A (`docs/review/NBA_DFS_Round2_Review_Codex.md`, reviewed revision `2598295`) and Review B (`docs/review/NBA_DFS_Round2_Review_Gemini.md`, saved from the owner's attachment `nba_dfs_round2_review_gemini.md`); both kept byte for byte as received; the repo at `2598295` as the source of truth for everything else (`docs/BRIEF.md`, `docs/review/ADJUDICATION.md` for round 1, `docs/ARCHITECTURE.md` v4, `docs/adr/`, `docs/build/`, `CLAUDE.md`, `.claude/commands/`, `docs/research/`).

**How to read this.** Item IDs carry the review that raised them: A-R2-... for Review A, B-R2-... for Review B, X-R2-... for gaps neither review caught. Where both reviews raised the same ground, one entry carries both IDs. Every entry has a verdict (Accept, Modify, Reject, Escalate, or Closed in round 1 with the round 1 entry), a timing (before C01, before a named chunk, before opening night, after opening night, or backlog), my own severity (Blocker, Major, Minor), why, and what changed. "VERIFIED" means I ran it or read it in a primary source, and the evidence is in the verification log below. Round 1 entries are cited as "round 1 entry N" and live in `docs/review/ADJUDICATION.md`.

**A note on Review B.** Review B says it did not open `ARCHITECTURE.md` v4, ADR-023 to ADR-028, or any chunk file. Three of its quotations do not exist anywhere in the repo (V-R2-8): the CLAUDE.md data-posture sentence, the BRIEF "schedule metadata" sentence, and the "single exportable entry file" requirement. Its items were judged on their merits with that in mind; several of its ideas survive, and its multi-entry item led to a real finding (entry R2-5).

---

## Summary

### Verdict: C01 is safe to start once these rulings are applied

Review A said no-go for C01 as written; Review B said go with fixes. Both were right about different things. The four stop-the-line problems that would have frozen wrong interfaces into C01 (the tie formula, the Goal 2 computation, the field interface, the unwalkable Floor-only route) are fixed in the documents in this session, so C01 can start from `CONTRACTS.md` alone.

### Counts by verdict (34 register entries covering 33 review items and 5 gaps of my own)

| Verdict | Entries |
|---|---|
| Accept (as written or with small additions) | 16 |
| Modify | 12 |
| Reject | 3 |
| Closed in round 1 | 3 |
| Escalate | 0 |

By timing: 16 land before C01 (document and contract changes made in this session, including R2-33 from the owner's real files of Oct 14 and R2-34 from the final-gate audits), 8 before a named build chunk or date on the way to opening night, 3 after opening night, 1 to the backlog, and the 3 closed and 3 rejected need no change.

### The stop-the-line rulings

| Item | Raised as stop-the-line by | Ruling | Timing |
|---|---|---|---|
| A-R2-I-01 Floor-only route cannot run | A | **Modify** (entry R2-1): the fix is structural. C04 splits into C04a and C04b, C11 into C11a (operations shell, depends on C04a only) and C11b (news researcher, after opening night). The Floor-only branch is now C01, C02, C03, C04a, C11a, C04b, and every dependency on it resolves; a `deferred` status makes the branch explicit | Before C01 |
| A-R2-I-02 Goal 2 thresholds expected winnings | A | **Modify** (R2-2): settlement returns expected dollars for Goal 1 and one realized joint outcome per scenario for Goal 2 and every probability, drawn so that it stays identical across candidate portfolios | Before C01 (contract); built in C08 |
| A-R2-I-03 Tied prizes divided twice | A | **Accept** (R2-3): one division by the tie group's size; top-1% money counted only from places at or above the cutoff | Before C01 |
| A-R2-I-05 Field interface discards ties, tail and identity | A | **Modify** (R2-4): the field exposes `p_above` and `p_equal` on exact eighth-point scores with a fitted first-place tail; settlement takes lineup hashes; float16 is banned for scores | Before C01 (contract); built in C08 |
| B-R2-I-01 Multi-entry sum breaks diminishing returns | B | **Modify** (R2-5): the owner's goal stands. The additive approximation is deleted because it pays twice for one first prize; every field size uses joint ranks. Review B's claim that the joint objective has diminishing returns is false (V-R2-4), which also falsifies a round 1 claim; greedy stays as a labeled heuristic | Before C01 |
| B-R2-I-02 Data posture contradiction | B | **Closed in round 1** (R2-26, round 1 entry 14, Decision D1): the contradictory quotes do not exist (V-R2-8) | None |
| B-R2-I-04 One upload file across draft groups | B | **Reject** (R2-30): the requirement does not exist; one file per draft group is already the contract (V-R2-8) | None |

### The five rulings that change the design most

1. **The settlement is corrected in three places** (R2-2, R2-3, R2-5; new ADR-029). Tied prizes are split once, not twice (the old formula paid $40 where DraftKings pays $80, VERIFIED V-R2-1). Our own entries always push each other down the standings, in every field size; the old shortcut for fields over 10,000 paid two first prizes for one (V-R2-4). Goal 2 is computed from realized winnings in each simulated night, not from averages (the old way could report no drawdown on a night with a 90% chance of one, V-R2-3). What it means for results: both goals now measure the money DraftKings would actually pay; a portfolio of near-copies no longer looks better than it is.
2. **The Floor-only fallback becomes a route the build can actually walk** (R2-1; new ADR-030). The operations shell (launcher, hooks, flags, slash commands, `dfs start`, the drill timer) moves to C11a right after the Floor core and is rehearsed live on Friday Oct 16, instead of arriving Sunday at the end of the chain. What it means for your workload: on Friday you rehearse the same launcher and commands you will use on opening night.
3. **The field's top end is modeled for first-place money** (R2-4). In a 35,000-entry contest most top-1% prize money is in the top few places, which a raw opponent sample cannot resolve (your NFL engine overpriced first place 18x to 280x from a raw sample, RR2). The field now carries exact eighth-point scores and a fitted upper tail, and C08 must show first-place probability within a factor of 1.5 of a large-sample truth. What it means for results: Goal 1 in the flagship contests stops resting on a handful of sampled opponents.
4. **Time to lock becomes a label, and drills cannot touch live records** (R2-6, R2-7; ADR-030). The exporter now blocks only what DraftKings would reject (a changed player whose game has started or whose lock time is unknown); a file a few minutes before a lock (inside the upload allowance, default 4 minutes) is exported and labeled "tight", and you are told the old lineup stays if the upload misses. Drills on saved nights write to their own folder. What it means for results: a seconds-long repair can still save an entry at T-5 minutes, and the weekend drills cannot overwrite the Oct 16 evidence.
5. **A player's identity no longer depends on his team, and a slate's identity no longer depends on an ID the file lacks** (R2-8, R2-9; new ADR-031). A player traded in the offseason keeps his history; two players whose names collide are flagged and handled by a pick-by-number prompt instead of silently merged; the slate is identified by a fingerprint of its player pool. What it means for results: opening-week projections keep last season's history for traded players instead of falling back to salary.

### Escalations

None. No round 2 item, as ruled, changes either goal or a hard constraint. Review B's data-posture item (B-R2-I-02) and its line-move idea (B-R2-D-03) would have widened Decision D1, but the first rests on quotes that do not exist and the second needs ESPN data D1 turned off; both are closed or rejected with D1 standing (entries R2-26 and R2-29). If you want to reopen D1, say so and it becomes a decision for you, with my recommendation to keep it.

### Where the reviews agree, and where they conflict

**Agree:** Goal 2 must be settled on dollars across all entries (A-R2-I-02, B-R2-I-05); eighth-point Captain scores must be stored exactly (A-R2-I-05, B-R2-I-06); player identity is fragile across sources (A-R2-D-01, B-R2-I-08); the opening-night operations (launcher, flags, Floor-mode commands) are unreachable or too late in the chain (A-R2-I-01, B-R2-I-03).

**Conflict:** on the Floor route, A wants mode-specific variants of C10 and C11 and B wants the launcher pulled into C04 (ruled in between: a separate C11a that depends only on C04a); on readiness, A says no-go and B says go with fixes (ruled no-go until the stop-the-line fixes landed, which they did in this session); on the multi-entry objective, B says the joint settlement keeps diminishing returns and A does not address it (ruled against B on evidence, V-R2-4).

**What the owner's real files added (R2-33).** Four real 2026-27 NBA files sent on Oct 14 confirmed the layout and corrected four assumptions: DraftKings `Status` is present and is the only preseason injury signal; `AvgPointsPerGame` is a free end-to-end check of the scorer; a real Showdown pool has 13.6 million legal lineups, not 440,000; and 70 of 226 matched players changed team. A repository check found the GitHub repository is public.

**Shared blind spots:** neither review noticed that the round 1 claim of a 63% greedy guarantee does not hold for the money objective in fields of 200 or more (X-R2-01), that the slate key and validator rely on a draft group ID the entries file does not contain (X-R2-03, found by the advisor), that the eight-minute drop rule breaks "only DraftKings validity blocks a file", or that Goal 1 in large fields is mostly first-place money the raw field sample cannot resolve.

---

## Verification log (round 2)

Scripts live in the session scratchpad and are reproduced in the entries where they matter. `python -E -P` runs the system Python without the current directory on the import path.

| # | Claim checked | What I ran | What came back | Verdict |
|---|---|---|---|---|
| V-R2-1 | A-R2-I-03: the contract divides tied prizes twice | `r2_checks.py`: a two-way tie over $100 and $60 under the CONTRACTS section 9 formula and under DraftKings' rule; a five-way tie | contract `mean(W(r..r+D))/(1+D)` = 40.0; DraftKings `sum(W(r..r+D))/(1+D)` = 80.0; top-1% share with k = 1 = 50.0; five-way tie 9.2 against 46.0 | VERIFIED. DraftKings' even split was verified in round 1 (V13) |
| V-R2-2 | A-R2-I-05: float16 merges legitimate Showdown totals | `r2_checks.py` | `float16(300.375) = 300.5`, `float16(300.5) = 300.5`; float32 keeps 300.375 exactly; integer eighths fit int16 up to 4,095.875 | VERIFIED |
| V-R2-3 | A-R2-I-02: thresholding expected winnings hides drawdown | `r2_checks.py`: one entry, 10% chance of $100, fees $10, alpha 25% | expected winnings 10.0 above the 2.5 threshold, so "no drawdown"; the true drawdown probability is 0.9 | VERIFIED |
| V-R2-4 | B-R2-I-01: does the joint (rank-displaced) Goal 1 keep diminishing returns, and does the additive shortcut double count | `r2_checks.py`: brute force over every subset of 5 entries in 3,000 random contests with non-increasing top-1% payouts | 480,000 subset-pair checks: 0 monotonicity violations, 16,700 violations of diminishing returns; a k = 1 contest with two of our entries above every opponent pays 1,000 jointly and 2,000 under the additive shortcut | VERIFIED. Adding an entry never lowers the total; diminishing returns fail |
| V-R2-4b | When diminishing returns hold | `r2_submod.py`: the same test by payout shape | convex payouts including the drop to zero after place k: 0 violations; DraftKings-like power-law top-1% curves: 4.08% violations, worst excess 0.445 of first prize; tiered curves: 6.23% | VERIFIED. They hold only when the payout curve, extended by its drop to zero at k+1, is convex, which in practice means k = 1 (fields under 200) |
| V-R2-5 | A-R2-I-08: the history file lacks salary and fantasy points | `r2_checks.py` reading `spikes/data/out/downloads/sportsdataverse/player_box_2026.parquet` | 34,883 rows, 57 columns; no salary column; no DraftKings or fantasy column; `athlete_id` present; minutes, points, rebounds, assists, steals, blocks, turnovers and threes present | VERIFIED |
| V-R2-6 | A-R2-I-07: the entries file layout and its missing ID | `grep` in `docs/research/R6-draftkings-mechanics.md` | line 130: "Entry rows keep going down the left side while the player list runs down the right side on the same rows, so the parser must split by column position"; line 132: "The file does not contain the draft group ID"; line 89: `In Progress` and `Final` appear in Game Info after a game starts (SUPPORTED) | VERIFIED as R6's evidence |
| V-R2-7 | B-R2-I-07: NOT YET SUBMITTED rows | `grep` in `docs/research/R4-data-sources.md` | lines 177, 202, 203: teams that have not filed show "NOT YET SUBMITTED"; 9 and 18 such rows in the 5:30 PM and 11:00 AM ET reports of Mar 15, 2026 | VERIFIED as R4's evidence |
| V-R2-8 | B-R2-I-02, B-R2-I-04, B-R2-D-02: the quoted requirements exist | `grep -rn -i` over every `.md` file for `underdognetwork`, `schedule metadata`, `single exportable`, `one consolidated`, `one batch`, `20-entry`, `independent entries` | no match outside the two reviews. CLAUDE.md says "ESPN JSON, RotoWire, sportsbooks and DraftKings endpoints are off"; BRIEF says "permissive, plus `nba_api` for box scores and game logs only; ESPN JSON off"; ADR-005 agrees; CONTRACTS section 1 names one upload file per slate; ADJUDICATION entry 2 is about simulated confidence, not files | VERIFIED: the quotes are not in the repo |
| V-R2-9 | X-R2-02: X-05 names two items in round 1 | `grep -rn "X-05"` | round 1 entry 1 heading "A-I-01 (with my addition X-05)"; round 1 entry 36 "X-05: the build itself needs a usage budget per chunk"; ADR-023 cites X-05 meaning entry 36 | VERIFIED |
| V-R2-10 | A-R2-I-11, A-R2-I-12: the post-MVP chunks say what the reviews quote | `grep` in C14 and C22 | C14 line 22: "standings files (exact field size and places paid from the..."; C22 line 22: `simulate_game_partial(..., points_so_far, fraction_remaining)` | VERIFIED |
| V-R2-12 | The entries-file layout on 2026-27 NBA files | `r2_files.py` on the owner's `DKEntries_163.csv` (Classic) and `DKEntries_164.csv` (Showdown) of Oct 14 | Entry table from column A, one blank column, then `Instructions` (column index 13 Classic, 11 Showdown); the pool header on physical row 8 at that column, pool data from row 9, so any contest with more than 7 entries overlaps the pool; pool has 9 columns (no `Status`, no `Starting`); UTF-8 without BOM, CRLF; both entries were blank reservations | VERIFIED; CONTRACTS v2's two-region rule is right |
| V-R2-13 | The salary file and `Status` | Same script on `DKSalaries_187.csv` and `DKSalaries_188.csv` | UTF-8 with BOM, CRLF, 11 columns including `Status` and `Starting`; pool IDs equal the entries files' exactly (288 of 288, 82 of 82) with no field differences; `Status`: Classic 54 `Q`, 8 `OUT`, 226 blank; Showdown 6 `Q`, 8 `OUT`; `Starting` blank for every player about 6 hours before tip | VERIFIED; answers round 1 V6's open question |
| V-R2-14 | Identity on a real pool | Same script: normalized keys, suffixes, edit distance, shared surnames | 288 distinct keys, no collisions with or without suffixes; 18 suffixed names; near-homonyms Nikola Jokic and Nikola Jovic (edit distance 1), Mark, Malik and Amari Williams, Cam and Max Christie; 7 Joneses, 7 Williamses, 6 Johnsons, 5 Millers | VERIFIED; edit distance must never auto-resolve a name |
| V-R2-15 | History join with a team-free key | Same script against `player_box_2026.parquet` | 226 of 288 matched exactly; suffix-stripped matching added 0; 62 unmatched, 61 with `AvgPointsPerGame` 0 (no NBA games) and 1 true miss (EJ Harkless); 70 of 226 matched players changed team since last season (Giannis Antetokounmpo MIL to MIA, LaMelo Ball CHA to MIN, Julius Randle, Tyler Herro, Kel'el Ware); 24 more differ only by team code (ESPN `NY` against DraftKings `NYK`, and `SA`, `GS`, `NO`, `UTAH`, `WSH`) | VERIFIED; a name-plus-team key would have lost 94 of 226 (42%), confirming R2-9 |
| V-R2-16 | What `AvgPointsPerGame` is | `r2_files2.py`: last season's DraftKings points per game recomputed with the design's scoring over five game sets | Regular season only: 93 of 224 within 0.01; all games played including playoffs and play-in: 189 of 224 within 0.01, 220 within 0.5 | VERIFIED: it is last season's average over every game played, playoffs included; it doubles as an end-to-end check of the scorer and the identity join |
| V-R2-17 | The triple-double rule | `r2_td.py`: for the 16 players in tonight's pool with triple-doubles, the both-bonuses rule against the replace rule | Both bonuses closer to DraftKings for 14 of 16; Jokic (36 triple-doubles): DraftKings 64.88, both 64.85, replace 64.10 | VERIFIED (again, after R6): a triple-double earns +4.5 |
| V-R2-18 | Showdown pool size | `r2_files2.py`: legal lineups (cap $50,000, Captain plus 5, both teams) on the DEN@LAC pool | 41 players, 37 active; 13,635,490 legal lineups; the 22 highest-average active players give 440,384 | VERIFIED; the design's "full enumeration, about 440,000" holds only for a 22-player subset |
| V-R2-19 | Repository visibility | `gh repo view bleeski/nba-dfs --json visibility,isPrivate` | `{"isPrivate":false,"visibility":"PUBLIC"}` | VERIFIED; ARCHITECTURE said "private repo" |
| V-R2-11 | B-R2-I-03: the usage figure it cites | `grep` in `docs/research/RR3-nhl-golf-soccer-lessons.md` | line 147: after NHL's C10 test runs the plan showed "21% of the session and 54% of the week used" | VERIFIED as RR3's record; known in round 1 |

---

## Register

### R2-1. A-R2-I-01 and B-R2-I-03 (part 1): the Floor-only route cannot run, and the operations shell arrives last

- **Raised by:** A (stop-the-line) and B (top five, as "C11 buried behind ten serial chunks").
- **Verdict:** Modify. **Before C01** (documents). **Severity (mine):** Blocker. The fallback that protects opening night could not be executed by the build protocol.
- **Why:** A is right on the facts: the usage branch says C10 and C11 are "built in Floor mode only", but C10 depends on C09 and C11 on C09 and C10, and the protocol tells a session to stop on unmet dependencies (VERIFIED by reading BUILD_PLAN, C10, C11, CLAUDE.md step 3). B is right that the launcher, hooks and flags arrive on Sunday, two days after the last live rehearsal. A mode-dependent tracker (A's C10-F and C11-F) asks a fresh session to resolve dependencies by mode, which is the kind of judgment the protocol exists to remove; putting the shell inside C04 (B) overloads the Thursday chunk. The fix is a structural split, sized with the advisor: **C04a** (the M1 core: default contest facts, the scoring adapter, simple points, the solver wrapper, the Floor, `dfs night --floor`, brief-lite, fact writing for `dfs out` and `dfs in` with the repair), **C04b** (injury report with the per-team merge, `dfs status --apply`, payout paste, entry history, facts cache), **C11a** (operations shell, depends on C04a only: the slash commands, hooks and permissions, preflight, capability flags with fingerprints, `dfs rehearsed`, `dfs unlock`, the launcher, the fallback card, `dfs start`, `dfs night --game-day` as a release-state-aware rebuild, the `dfs drill news` timer for whichever late-news path is on, the slot-reassignment repair and the export recovery tests), and **C11b** (the news researcher, after opening night; it was always allowed to ship off, round 1 entry 38). C10 depends on C09 and C11a. PROGRESS gains the status `deferred (after opening night)`, and `/run-chunk` treats a deferred dependency as not done. The Floor-only branch is then C01, C02, C03, C04a, C11a, C04b, and every dependency on it resolves (checked by script in the final gate). Calendar (advisor): Friday runs C11a first so rehearsal 2 uses the real launcher and hooks, then C04b, which may slip to Saturday without harm (the payout paste is first needed in C08, and the injury parser first runs live on Monday evening because no preseason reports exist, R4). Sunday evening is a hard cut for C10; if it is not done, it moves after opening night and the repair is the late-news path. Monday stays the live run plus fixes. The usage trigger is measured at M1 (C01 to C04a) at about 35% of a weekly window, scaled down from 40% because C04a is smaller than the old C04. Goals: none directly; opening night: the fallback becomes real; cost: two more sessions in the build (the split chunks), offset by C11b leaving the opening-night path; workload: on Friday you rehearse the shell you will use on Tuesday.
- **Change:** BUILD_PLAN (chunk table, dependency graph, critical path, calendar, usage budget, slip rules, what you provide); new chunk files C04a, C04b, C11a, C11b replacing C04 and C11; C10 dependencies; PROGRESS (rows, `deferred` status); CLAUDE.md step 3 and the change-control rule; `.claude/commands/run-chunk.md`; BRIEF "How to run sessions"; ADR-023 marked partly superseded; new ADR-030.

### R2-2. A-R2-I-02 and B-R2-I-05: Goal 2 thresholds expected winnings instead of possible winnings

- **Raised by:** A (stop-the-line) and B (top five). B's premise (binary min-cash bitsets in C08 and C12) is not in the current contract, which already settles in dollars; its dollar-accumulator point is the same as A's.
- **Verdict:** Modify. **Before C01** (contract); built in C08, consumed in C09 and C12. **Severity (mine):** Major, not Blocker: Goal 2 is reported, not optimized, until C12 after opening night, but C01 types this interface and the Baseline brief prints Goal 2 on Oct 19 and 20.
- **Why:** A is right (VERIFIED V-R2-3): `prize_all` is an expectation over the opponents in each simulated night, and the probability that winnings fall below a threshold is not the probability computed on the average. The same error affects every probability the settlement reports (at least one top-1% finish, recovering the fees, a meaningful prize, literal washout). The fix keeps two outputs: expected dollars for Goal 1 (lower noise, exact by linearity) and one realized joint outcome per scenario for Goal 2 and all probabilities. The advisor caught a flaw in my first construction: drawing opponent counts in the gaps between our sorted scores re-randomizes every draw whenever the portfolio changes, which breaks the paired comparisons C12's insurance search depends on. The realization is therefore portfolio-independent: per scenario and contest, opponent counts are drawn top-down on the fixed score lattice (quarter points for Classic, eighth points for Showdown), each bin keyed by (run seed, scenario set, scenario, contest, bin), and copies of our lineups keyed by `lineup_hash`; our entries are then placed into that one realized field. Contract test: two portfolios that differ by one entry give every unchanged entry the same realized rank apart from the swapped entry's own push. One realization per scenario is enough because Goal 2 already averages over 15,000 to 30,000 scenarios. Goal 2: computed as you defined it; Goal 1: unchanged; cost: about one second of draws per contest; workload: none.
- **Change:** CONTRACTS section 9 (`Settlement` fields `top1_exp`, `prize_exp`, `top1_draw`, `prize_draw`; `night_goal2` thresholds realized winnings; the draw keys; the common-random-numbers test); section 14 (fixtures `tiny_goal2_binary.json`, `tiny_crn_swap.json`); ARCHITECTURE section 2 (settlement and Goal 2); ADR-025 marked partly superseded; new ADR-029; C08 scope and definition of done; C12 reading list.

### R2-3. A-R2-I-03: tied prizes are divided twice

- **Raised by:** A (stop-the-line).
- **Verdict:** Accept. **Before C01.** **Severity (mine):** Blocker. C01 writes the hand-computed fixtures, so the wrong formula would have been frozen into the tests that every later chunk must pass.
- **Why:** VERIFIED (V-R2-1): the contract, ADR-024, ARCHITECTURE section 2 and C08 all say "the average of `W(r+j)` for `j = 0..D`, divided by `1 + D`"; the average already divides by the group size, so a two-way tie over $100 and $60 pays $40 instead of DraftKings' $80, and a five-way tie pays a fifth of the correct amount. The error is an unintended extra penalty on any lineup the field might copy, which is most Showdown chalk. A's boundary point also stands: Goal 1 counts only money from top-1% places, so a tie that straddles place k credits each member the top-1% places' prizes divided by the group size, not the whole group's money. The rule: a tie group occupying ranks r to r+t-1 (t counts opponent copies, other lineups with the same score, and our own tied entries) pays each member `sum(W(j) for j in r..r+t-1) / t`; for Goal 1 the same with `W_top1(j) = W(j)` when `j <= k` and 0 otherwise. Conservation tests: all entrants' payouts sum to the paid pool, and their top-1% allocations sum to the top-1% pool. Goal 1 and Goal 2: both now match DraftKings' payouts; cost and workload: none.
- **Change:** CONTRACTS section 9 (tie rule, top-1% attribution, conservation rule), section 14 (`tiny_tie_100_60.json`, `tiny_tie_across_k.json`; every existing tiny fixture recomputed by the single-division rule); ARCHITECTURE section 2 step 4; new ADR-029 (supersedes ADR-024's Definition bullet); C08 scope.

### R2-4. A-R2-I-05 and B-R2-I-06 (storage): the field interface discards ties, the top tail and lineup identity

- **Raised by:** A (stop-the-line); B on eighth-point storage.
- **Verdict:** Modify. **Before C01** (contract interface); built in C08. **Severity (mine):** Major.
- **Why:** A is right on all three counts. (1) A 400-point quantile grid has a spacing of 0.25% of the field, while first place in a 35,000-entry field is a tail share of about 0.003%; Goal 1 is mostly first-place money in those contests, and the grid gives about four intervals across the whole top 1%. ARCHITECTURE already noted that a raw sample cannot resolve first place in large fields, but only used a fitted tail for a reported diagnostic; Goal 1 itself needs it. (2) Interpolating a grid cannot recover the probability mass at an exact tied score, and C08's memory advice to store float16 merges legitimate Showdown totals (VERIFIED V-R2-2). (3) `settlement_fn` took score arrays only, while copy rates are keyed by lineup identity. The advisor's limit applies: the contract fixes the interface, not the tail family. The field exposes `p_above(s, x)` and `p_equal(s, x)` per scenario on exact eighth-point scores; it carries a bulk grid (float32) for display and screening, the exact top of the weighted field sample (integer eighths with weights), and a fitted upper tail used above the score where too few sample points remain (C08 picks the family; the named default is an exponential excess over the sample's top 1%). Settlement takes lineup hashes with scores. Copies are counted once: the field's mass at a score already includes any sampled copies, and the copy-rate model adds only the excess. C08 may ship first place labeled "tail unfitted" if the fit is not ready, so the fit never blocks the Baseline. Acceptance test: first-place probability within a factor of 1.5 of a ten-times-larger sample on a synthetic field (RR2's raw-sample error was 18x to 280x). B's eighth-point point merges here: scores are float32 (exact for eighths at these magnitudes) or integer eighths, never float16 and never rounded to two decimals. Goal 1: first-place money in large fields stops resting on a few sampled opponents; cost: about 70 MB per large contest at the selection set size; workload: none.
- **Change:** CONTRACTS section 7 (no float16 for points), section 8 (`FieldScores` rewritten; `p_above`, `p_equal`), section 9 (settlement consumes hashes), section 10 (`settlement_fn(entry_points, entry_hashes)`), section 14 (`tiny_same_score_diff_hash.json`, `tiny_eighth_apart.json`), section 15 (`[field] tail_share`, `tail_min_points`); ARCHITECTURE sections 2 and 5; new ADR-029; C08 scope, risks (float16 advice removed) and definition of done.

### R2-5. B-R2-I-01 and X-R2-01: the multi-entry objective, the additive shortcut, and the greedy guarantee

- **Raised by:** B (stop-the-line); X-R2-01 is mine, found while verifying B's claim.
- **Verdict:** Modify. **Before C01** (contract and documents); built in C08 and C09. **Severity (mine):** Major.
- **Why:** Three findings. (1) **Your goal stands.** B says the brief's sentence "every entry's top-1% winnings count" double-counts first place. It does not: ADR-024 and ARCHITECTURE section 2 already settle our entries jointly, so our second entry in a scenario where both beat the field finishes second, which is what DraftKings would pay. Counting real winnings of every entry is the right money accounting; this is not a goal change and needs no escalation. (2) **The additive shortcut is wrong and is deleted.** For fields of 10,000 or more the design ranked each of our entries against the field alone during selection. That pays two first prizes for one (VERIFIED V-R2-4: 2,000 against 1,000) and removes the pressure against near-copies, which is the "one lineup with 17 perturbations" failure your NFL engine showed (RR2). The joint expectation is cheap for every field size: in each scenario, sort our entries; the m-th best has `m - 1` of ours above it, and its expected prize needs only its own opponent count, by linearity of expectation. (3) **Diminishing returns do not hold, which corrects round 1.** B asserts the joint objective keeps diminishing returns; my brute-force test shows it does not (VERIFIED V-R2-4 and V-R2-4b): it holds only when the payout curve, extended by its drop to zero after the last top-1% place, is convex, which in practice means fields under 200 where only first place counts. Round 1 entry 7, ADR-007, ADR-024 and ARCHITECTURE section 6 claimed the 63% greedy guarantee from V16, which was about a different objective (the best of our entries per scenario). This is the round 1 exception "a ruling rests on a false fact", so I rule on it: greedy stays as the selection method because it is fast and sensible, with exact incremental updates (after adding an entry, recompute marginal gains only in the scenarios where that entry finishes in the top 1%) instead of lazy upper bounds, which are only valid with diminishing returns; the 63% bound is claimed only for contests with k = 1; every other result is labeled "best found (heuristic)". Lazy greedy is the labeled fallback if C09's runtime test misses. Goal 1: computed as you defined it in every field; cost: C09 measures; workload: none.
- **Change:** CONTRACTS section 9 (no `mode` argument; joint settlement for every field size), section 10 (`select_contest` uses exact incremental greedy; `search_quality.greedy_bound` says "1-1/e (k = 1)" or "none (heuristic)"), section 14 (`tiny_joint_vs_additive.json`), section 15 (delete `settle.exact_max_field`; add `select.greedy`); ARCHITECTURE sections 2 and 6; ADR-007 (bound statement), ADR-024 (Computation and Selection bullets) marked partly superseded; new ADR-029; C08 and C09 scope and definition of done; round 1 register gets a pointer.

### R2-6. A-R2-I-04 and B-R2-I-10 (part 2): the emergency repair disappears inside eight minutes; what counts as locked

- **Raised by:** A (Blocker in its list, lands before C03); B on stale downloads during swap.
- **Verdict:** Modify. **Before C01** (contract and settings); built in C03. **Severity (mine):** Major.
- **Why:** A is right that the repair, the fallback for news arriving minutes before a tip, used the same exporter that dropped any changed row locking within eight minutes, so at T-5 it could produce nothing (VERIFIED by reading CONTRACTS 11.7, C03's test and C10's drill). The deeper problem is that dropping a row DraftKings would accept breaks the rule that never bends: only DraftKings validity blocks a file; every other check labels. Round 1 asked the engine to "say when there is insufficient time to act" (round 1 entries 10 and 17); the contract turned saying into blocking. The ruling: the exporter refuses a changed cell only when DraftKings would reject it, that is when the cell is locked (it shows `(LOCKED)`, or its game has started by the clock, or Game Info says `In Progress` or `Final`) or its lock time is unresolved (the brief's "lock uncertainty stops an edit"). B's part 2 merges here: a download taken before a tip has no `(LOCKED)` markers, so the clock must count too. Time to lock is a label: a changed row whose earliest changed cell locks within `export.tight_minutes` (default 4, replaced by the measured 90th-percentile upload time from rehearsals 1 and 2) is exported and labeled "tight: locks at HH:MM"; the command says plainly that if the upload misses that lock, the previously uploaded lineup stays, and names it. `resolve.min_minutes_to_lock` (8) now only decides whether the full re-solve is attempted; inside it the news commands go straight to the repair. A failed row at upload is a DraftKings rejection of that row, not a disqualification, so attempting is the better bet. Goals: an entry with a scratched player can still be saved at T-5; opening night: the T-2 drill now expects "re-solve skipped, repair ran, file labeled tight"; workload: a clear message instead of an empty file.
- **Change:** CONTRACTS section 11.2 (locked cell definition), 11.7 (rewritten as "Time to lock"), section 15 (`[export] tight_minutes`); ARCHITECTURE sections 6 and 8; ADR-026 marked partly superseded; new ADR-030; C03 definition of done (three tests replacing the five-minute drop test); C10 drill expectations; C11a drill timer.

### R2-7. A-R2-I-09: saved-night drills can overwrite the evidence they rehearse

- **Raised by:** A.
- **Verdict:** Accept. **Before C01** (contract 1.1, which C01 types as `Paths`); built in C03. **Severity (mine):** Major.
- **Why:** VERIFIED by reading CONTRACTS 1.1: `--night` points the engine at that night's ledger and news state, and the exporter, `dfs uploaded` and `dfs out` all write. Drill B would replace the real Oct 16 confirmation history with fictional actions, and the learning loop and the delivery-failure checks read that history. The rule: `--as-of` puts the engine in drill mode; inputs are read-only from `data/archive/<date>/` (or `fixtures/dk/<date>/` with `--fixtures`); every write (news state, ledgers, manifests, upload-shaped files, simulated confirmations) goes under `runs/drills/<drill_id>/`; nothing writes to `out/uploads/`, the live ledger or the live news state. Replay (C19) writes only under `runs/replays/<id>/`. C03 tests that a completed drill, including simulated uploads and failures, leaves every live artifact byte-identical. Goals: none; opening night: protects the only real-file evidence; cost and workload: none.
- **Change:** CONTRACTS section 1 (layout) and 1.1 (drill mode); new ADR-030; C03 scope and definition of done; C19 scope line.

### R2-8. A-R2-I-07 and X-R2-03: the parser contract describes a different CSV layout, and the slate key depends on an ID the file lacks

- **Raised by:** A; X-R2-03 found by the advisor.
- **Verdict:** Accept. **Before C01** (contract); built in C02. **Severity (mine):** Major.
- **Why:** VERIFIED (V-R2-6): R6 records that entry rows continue down the left while the player pool runs down the right on the same physical rows, that the entries file carries no draft group ID, and that Game Info reads `In Progress` or `Final` after a game starts. The contract said the pool follows a blank line and required `draft_group_id`; a parser built that way works on a few test rows and fails on a long entries list or a post-lock re-download. The advisor found the knock-on: the slate key `classic_<draft group id>` and the validator's "same draft group" check also depend on the missing ID. The rules: parse the entry region and the pool region independently by locating each header's columns, never assume a blank row, and keep every entry even when it shares a row with pool data; `draft_group_id` is optional and only set from verified metadata, never invented; the slate is identified by `slate_fingerprint` (a hash of the sorted pool IDs), and its readable key is `classic_<first tip HHMM>_<games>g` or `sd_<AWAY>-<HOME>`, with `classic_main` still an alias for the largest Classic slate; a post-lock `In Progress` or `Final` reuses the last verified tip time for that exact game from the archive, and an unresolved lock time stops an edit. Fixtures: a many-entry file whose entries overlap the pool rows, and a re-download with locked markers. Opening night: the parser works on the real 150-entry files and on post-lock re-downloads; workload: none.
- **Change:** CONTRACTS section 1 (slate key, fingerprint), 2.1 (layout, optional ID, Game Info variants), 3.1 (`Slate` fields), 11.2 (same slate fingerprint), 14 (fixtures); new ADR-031; C02 scope and definition of done.

### R2-9. A-R2-D-01 and B-R2-I-08: keep a player's identity stable across teams and sources

- **Raised by:** A (new idea); B (major issue, name collisions).
- **Verdict:** Modify. **Before C01** (the person key definition); built in C02, used in C04a, C04b and C11a. **Severity (mine):** Major.
- **Why:** The contract made `person_key` a normalized name plus team, so a player traded in the offseason looks like a new person when tonight's pool is joined to last season's history, and opening week is exactly when that history matters most (A). Suffix stripping can merge two different people, and a fuzzy `dfs out` can pick the wrong one of two similar names on one team (B; B's specific 2026-27 roster examples were not verified and the ruling does not depend on them). The rules: `person_key` is the normalized full name (accents folded, lower case, punctuation removed, suffix kept as a final token), with no team; team lives on each appearance; matching across sources is exact first, then suffix-stripped only when exactly one candidate matches, else unmatched and listed for review; injury-report names in `Last, First` form are flipped before normalizing (`Hardaway Jr., Tim` becomes `tim hardaway jr`); history joins use the history source's athlete ID once a name has matched; `config/identity_overrides.toml` holds manual fixes. The advisor's limit applies: a collision never stops the night. When two different players in tonight's pools share a key, both get a team (or ID) disambiguator, their history join is disabled (salary-implied points), `dfs out` and `dfs in` require a pick by number even with `--yes`, and the brief warns. Goals: traded players keep their history; opening night: a name mix-up cannot bench the wrong star silently; workload: an occasional numbered prompt.
- **Change:** CONTRACTS preamble (person key), section 2.1 (`PoolPlayer.identity_ambiguous`), 4.4 (ambiguous matches), 14 (identity fixtures); new ADR-031; ADR-018 marked partly superseded on suffix stripping; C02 scope and definition of done; C04a (history join), C04b (injury names).

### R2-10. A-R2-I-06: a starter announcement can erase a minutes restriction

- **Raised by:** A.
- **Verdict:** Accept. **Before C01** (contract 4.2); built in C04a (fact writing and supersession) and C06 (translation). **Severity (mine):** Major.
- **Why:** VERIFIED by reading CONTRACTS 4.2: "a later fact for the same `person_key` supersedes an earlier one of any kind", so a starter announcement after a 24-minute restriction deletes the restriction. Supersession is keyed by (person, game, attribute), with three independent attributes: availability (`out`, `in`, `questionable`, `pool_exclusion`), role (`starter_announced`, `bench_announced`) and restriction (`restriction`, the new `restriction_cleared`); a data flag is its own attribute. Within an attribute, precedence follows ARCHITECTURE section 4: an official-report OUT outranks every non-official source until a later official report changes it, your commands outrank LLM records, and otherwise the latest acting fact wins; you can still override an official fact with `dfs fact veto <fact_id>`, which is recorded. Conflicts stay visible in the brief. Tests: restriction then starter, starter then restriction, and an unrelated status update all keep the restriction. Goals: minutes stay right when two kinds of news arrive about one player; workload: none.
- **Change:** CONTRACTS section 4.2 (attribute map, supersession, precedence, `restriction_cleared`); ARCHITECTURE section 4 "Where LLM facts and inferences meet the model"; ADR-026 news-state bullet edited with a changelog note (an execution fix, not a reversal); C04a and C06 scope and tests.

### R2-11. A-R2-I-08: C04 requires features its source and prior chunks do not provide

- **Raised by:** A.
- **Verdict:** Accept. **Before C04a.** **Severity (mine):** Major.
- **Why:** VERIFIED (V-R2-5): the history file has counting stats and `athlete_id` but no salary and no DraftKings points, and the scoring adapter was first built in C05, after the Floor's live rehearsal. A fresh C04 session would either write a scorer on the critical rehearsal day or fit points on salary from a file with no salary. The small pure scoring function (`score_line`, with Captain at 1.5 times the bonus-inclusive total) and its discriminating tests move into C04a; C05 reuses it and adds the vectorized form, versioning and the self-checks. The salary-implied fallback pairs tonight's pool salaries with last season's DraftKings points per game for matched players (a cross-sectional fit, labeled as a fallback). Tests include a player whose rebounds and assists make his fantasy ranking differ from his scoring ranking. Goals: the Floor ranks on fantasy points, not basketball points; opening night: removes an improvised step from Thursday; cost: about 30 minutes moves from C05 to C04a.
- **Change:** CONTRACTS section 6 (`simple_points` definition), section 7 (scoring function owner); C04a scope and tests; C05 scope ("reuse, extend").

### R2-12. B-R2-I-07: a NOT YET SUBMITTED section can erase earlier statuses

- **Raised by:** B.
- **Verdict:** Accept. **Before C04b** (contract 2.6 changed before C01). **Severity (mine):** Major.
- **Why:** VERIFIED (V-R2-7): the official report lists teams that have not filed as NOT YET SUBMITTED, 9 to 18 rows per report. On opening night the 12:45 pm CT run reads a report in which the later games' teams may not have filed (their game-day deadline is 1:00 pm local), so reading only the latest report would wipe Monday evening's Out and Questionable statuses for those teams. The rule: injury state is merged per (game, team); a team's newest submitted section replaces its earlier statuses, and a NOT YET SUBMITTED team keeps its last submitted statuses labeled "cached from the <time> report". Goals: late-game players listed Out on Monday stay out on Tuesday's first run; workload: none.
- **Change:** CONTRACTS section 2.6 (status `NotYetSubmitted`, the merge rule, `InjuryState`); C04b scope and tests.

### R2-13. A-R2-I-10: active decision records still instruct the reversed behavior

- **Raised by:** A.
- **Verdict:** Accept. **Now.** **Severity (mine):** Major (C08 and C09 read these records).
- **Why:** VERIFIED by reading both records: ADR-007's Decision says "Each scenario's value is the best of our entries", and ADR-008's says "Our baseline model is used only when no consensus source has numbers", while their changelogs say the opposite. A fresh session reading the Decision section could build the old objective or leak private projections into the field. These are execution fixes of round 1 rulings, so the bullets are rewritten in place with a changelog note; old wording is kept in a clearly labeled history line.
- **Change:** ADR-007 Decision (per-scenario value is the sum of our entries' top-1% allocations under the joint settlement; the bound per R2-5); ADR-008 Decision (the public formula when consensus is absent; the private baseline never a fallback; the baseline-change test applies always).

### R2-14. B-R2-I-10 (parts 1 and 3): Windows file locks, and a stale download before a swap

- **Raised by:** B.
- **Verdict:** Accept. **Before C02** (part 1) and **before C11a and C10** (part 3). **Severity (mine):** Minor (part 1), Major (part 3).
- **Why:** Part 1: on Windows, Excel and antivirus scans hold files in Downloads; moving or deleting a file that Excel holds fails, while copying it usually works. The rule: copy from Downloads into `inbox/`, never move or delete there; retry up to three times 250 ms apart; skip partial downloads (`.crdownload`, `.part`, `~$*`); a file still locked gets a plain message ("close the file in Excel"). Part 3 enforces a rule round 1 already made (entry 19: re-download before any swap): `dfs swap`, and `dfs repair` after a slate's first lock, refuse when the latest download predates the latest started tip on that slate, and say "download a fresh entries file first". Part 2 is in R2-6. Opening night: no crash on a held file; no swap edited from a pre-lock file.
- **Change:** CONTRACTS section 11.5 (freshness rule) and C02 inbox scope; C11a (post-lock repair freshness); C10 swap scope.

### R2-15. A-R2-D-02: repair the open positions before declaring a player irreplaceable

- **Raised by:** A.
- **Verdict:** Accept. **Before opening night (C11a).** **Severity (mine):** Minor.
- **Why:** The repair searched only for a substitute eligible for the vacated slot; a legal repair sometimes needs an existing unlocked player to move slots first (A's SG and G example). A tiny matching of players to unlocked slots inside one entry finds it; locked cells stay fixed and salary and duplicate rules hold. It is not the contest-entry assignment optimizer rejected in round 1. The advisor moved it out of C03 to keep Thursday's critical path short; C03 keeps the direct-slot repair, and C11a adds the matching step on Friday, with the SG and G hand-counted test inside the 150-entry, ten-second benchmark.
- **Change:** CONTRACTS section 11.6 (two stages and owners); C11a scope and tests.

### R2-16. A-R2-D-03: make rehearsal approval identify the version that passed

- **Raised by:** A.
- **Verdict:** Accept. **Before C01** (the `capabilities.toml` schema); enforced in C11a. **Severity (mine):** Major.
- **Why:** A bare `rehearsed_on` date lets a parser change on Monday ride on Friday's rehearsal, which round 1 forbids (entry 3: rehearse after substantive changes). Each capability records `rehearsed_commit`, `rehearsed_paths` (the source folders whose change makes the evidence stale) and `drill_artifact`. Status shows "passed for this version", "stale after change" or "never rehearsed"; a stale capability counts as not rehearsed on a game night until a replay drill passes or `dfs unlock` is recorded. The Floor is never switched off by staleness; it is labeled. Opening night: Monday evening's allowed injury-parser fix triggers a five-minute replay drill instead of riding on Friday's rehearsal.
- **Change:** CONTRACTS section 1 (`capabilities.toml` fields), section 12 (`RunManifest.capabilities`); ADR-023 changelog; new ADR-030; C11a scope.

### R2-17. A-R2-D-04: publish each upload and its ledger record as one recoverable step

- **Raised by:** A.
- **Verdict:** Modify (split by the advisor). **Before C03** (basic) and **C11a** (full tests). **Severity (mine):** Minor.
- **Why:** An interrupted export can leave a file with no ledger record or a ledger naming a file that was never finished. C03 writes every upload, ledger and manifest to a temporary name, re-reads and validates it, then renames it into place (an atomic rename on the same Windows volume), with the ledger written last; only files named in the ledger are shown as actionable. C11a adds the interrupted-write tests at each boundary and the start-up sweep that removes unfinished temporary files. Opening night: a laptop restart mid-export cannot leave a wrong "latest file".
- **Change:** CONTRACTS section 11.3 (write order); C03 scope; C11a scope and tests.

### R2-18. A-R2-I-11: C14 invents a paid-place cutoff from a file without payouts

- **Raised by:** A.
- **Verdict:** Accept. **Before C14** (after opening night); text fixed now. **Severity (mine):** Major.
- **Why:** VERIFIED (V-R2-10): C14 says standings supply places paid "from the last paid rank", but standings carry rank, score, lineup and ownership, no winnings. The last listed rank is the last entrant. Standings may set the completed field size and lineup and score facts only; places paid and prizes come from a payout paste or the entry-history export; otherwise the cached value and its provenance stay. Test: a full standings file with no winnings cannot change `places_paid`, including when the prior value is unknown.
- **Change:** C14 scope and definition of done.

### R2-19. A-R2-I-12: live-score conditioning loses the stats bonuses need

- **Raised by:** A.
- **Verdict:** Accept. **Before C22** (after opening night); text fixed now. **Severity (mine):** Major for C22, no effect before it.
- **Why:** VERIFIED (V-R2-10): C22 adds simulated remaining points to fantasy points so far, which cannot detect a double-double crossed in the remainder or avoid awarding one twice. In-progress games carry cumulative box-score stats and minutes per player; the remainder is simulated as stats, added, and scored once. If only fantasy points so far are available, the partial-game path is off and labeled. Tests include a double-double crossed in the remainder, one already earned, and a triple-double transition, each at Captain.
- **Change:** C22 scope, contracts and definition of done.

### R2-20. B-R2-I-06 (display part): compare to DraftKings' two-decimal display with a tolerance

- **Raised by:** B.
- **Verdict:** Accept. **Before C05** (and C13). **Severity (mine):** Minor.
- **Why:** DraftKings shows a Captain's 85.875 as 85.88 (R6 line 245); R6 line 263 already prescribes a 0.01 tolerance. The self-checks in C05 and C13 compare exact engine values to DraftKings' display within 0.01 and never round engine values.
- **Change:** C05 and C13 test lines.

### R2-21. B-R2-I-11: document drift between the plan, the tracker and the chunk files

- **Raised by:** B.
- **Verdict:** Modify. **Before C01.** **Severity (mine):** Minor.
- **Why:** A drift check is useful during the build as well as now. The scripted checks written for this session's final gate are committed as `scripts/check_docs.py` (reading lists resolve to real files and sections, chunk IDs match across the plan, tracker and chunk files, the dependency graph has no cycles or forward references, the Floor-only branch resolves, no em dashes), and C01 wires it into the smoke suite.
- **Change:** `scripts/check_docs.py`; C01 scope and definition of done.

### R2-22. A-R2-D-05: spend simulation work where the dollar objective is noisy

- **Raised by:** A.
- **Verdict:** Modify, to the **backlog** with a trigger. **Severity (mine):** Minor.
- **Why:** Stratified or importance sampling can reduce noise per second, but it adds weights to every downstream number and cannot be tested before the plain simulator and settlement pass their exact tiny cases. Trigger: C16's measurements show the paired standard error of portfolio comparisons, not model error, limiting decisions. Then it runs as a frozen challenger per A's acceptance rule.
- **Change:** BUILD_PLAN backlog.

### R2-23. B-R2-D-01: a cold-start Showdown salary-use prior

- **Raised by:** B.
- **Verdict:** Modify. **Before C08.** **Severity (mine):** Minor.
- **Why:** Opponents' salary use drives Showdown duplication, and there are no NBA standings yet. B's specific decay (2.5 per $1,000 left) has no evidence behind it in the repo, so it enters as a labeled BET default for casual Showdown entrants (`field.showdown_salary_left_decay`), alongside the existing salary floor, and C14 fits it from the first Showdown standings files.
- **Change:** CONTRACTS section 15 (`[field]`); C08 scope; C14 calibration list.

### R2-24. B-R2-D-04: order insurance swaps by drawdown reduction per top-1% dollar given up

- **Raised by:** B.
- **Verdict:** Modify. **Before C12** (after opening night). **Severity (mine):** Minor.
- **Why:** Within the per-contest constraint, which swap to take first is a search choice, not a goal change. C12 computes both orderings (largest drawdown reduction; reduction per expected top-1% dollar given up) on saved nights and keeps the better as the frozen default.
- **Change:** C12 scope.

### R2-25. B-R2-D-05: capture real preseason files before the dark days

- **Raised by:** B.
- **Verdict:** Modify. **Tonight (optional), Oct 16 and Oct 17 mornings.** **Severity (mine):** Minor.
- **Why:** Oct 17 to 19 have no NBA games (round 1 V10), and the plan already saves the Oct 15 and 16 entries files, including a post-lock re-download. Two additions: tonight, if you are at the laptop before the first tip, one $0.25 entry and a post-lock re-download gives C03 a real NBA `(LOCKED)` file a day early; and the next-morning standings downloads for the Oct 15 and 16 test contests give C13 a real NBA standings fixture. ESPN snapshots are not taken (off under D1).
- **Change:** OWNER_CHECKLIST (tonight, Oct 16 and Oct 17 mornings); BUILD_PLAN "What you provide"; C13 fixture note.

### R2-26. B-R2-I-02: data-posture contradiction

- **Raised by:** B (stop-the-line).
- **Verdict:** **Closed in round 1** (round 1 entry 14, Decision D1).
- **Why:** The contradiction does not exist (VERIFIED V-R2-8): CLAUDE.md, BRIEF and ADR-005 all say permissive plus `nba_api` for box scores and game logs only, with ESPN JSON and RotoWire off. B's proposed rule would reopen D1, which you decided. The schedule for each slate comes from the Game Info in your own DraftKings files (ARCHITECTURE section 10 already keeps `nba_api`'s schedule endpoints unused), and no chunk calls another `nba_api` endpoint (checked by `grep`).
- **Change:** none.

### R2-27. B-R2-I-03 (part 2): make the per-chunk advisor consultation conditional

- **Raised by:** B.
- **Verdict:** **Closed in round 1** (round 1 entry 15).
- **Why:** Round 1 set the advisor rule you approved in BRIEF: when stuck and once before a chunk is declared done. B's usage evidence (RR3's 21% and 54%) was known in round 1 (V-R2-11). The usage trigger (R2-1) is the guard.
- **Change:** none.

### R2-28. B-R2-I-09: value a late-game Questionable star at a swap salvage score

- **Raised by:** B.
- **Verdict:** **Closed in round 1** (round 1 entry 22, A-D-03, backlog with trigger).
- **Why:** Valuing the option to swap later was ruled a backlog item with a trigger (the late-swap scorecard shows portfolios lacked an affordable pivot). B's claim that the selector "will never roster" a 55% Questionable player is overstated: the sanity check only flags players under 50%, and Goal 1 values the scenarios where he plays.
- **Change:** none.

### R2-29. B-R2-D-03: a line-move canary that adjusts play probabilities

- **Raised by:** B.
- **Verdict:** Reject, with a backlog note.
- **Why:** It reads ESPN's scoreboard JSON, which D1 turns off, and it changes `p_active` from an uncalibrated numerical rule, which round 1 entry 12 forbids until calibrated. An alert-only variant (flag a team whose implied total moved at least 2 points between The Odds API snapshots the engine already takes, no probability change) is noted in the backlog for C21.
- **Change:** BUILD_PLAN backlog line.

### R2-30. B-R2-I-04: one upload file across all contests

- **Raised by:** B (stop-the-line).
- **Verdict:** Reject.
- **Why:** The quoted requirement is not in BRIEF or round 1 entry 2 (VERIFIED V-R2-8). CONTRACTS section 1 already writes one upload file per slate, which is one DraftKings draft group, and R6 line 132 confirms one entries file per draft group.
- **Change:** none.

### R2-31. B-R2-D-02: soft-decay scenario weights and overlap caps

- **Raised by:** B.
- **Verdict:** Reject (overlap caps also closed in round 1 entry 7 and ADR-007 option 1).
- **Why:** The joint settlement (R2-5) already gives a second entry less value in scenarios another entry wins, by the real payout curve; a fixed 0.20 decay would replace your dollar objective with an invented one. The brief question B answers ("20 independent entries or a correlated portfolio") is not in the brief (V-R2-8); ARCHITECTURE section 6 already explains how multi-entry portfolios are built.
- **Change:** none.

### R2-32. X-R2-02: X-05 names two different items in round 1

- **Raised by:** me (the owner asked for this check).
- **Verdict:** Accept. **Now.** **Severity (mine):** Minor.
- **Why:** VERIFIED (V-R2-9). The usage-budget item (round 1 entry 36) keeps X-05 because ADR-023 and both reviews cite it that way. The addition in round 1 entry 1 becomes X-09.
- **Change:** ADJUDICATION.md entry 1 heading and any reference to it.

### R2-33. X-R2-04: the owner's real files of Oct 14 test the design; and the repository is public

- **Raised by:** me, from the four DraftKings files the owner sent on Oct 14 (one $0.25 Classic entry on the 7-game slate, one $0.25 Showdown entry on DEN@LAC, and both salary files), and a repository check. Advisor consultation 4 shaped the ruling.
- **Verdict:** Accept. **Before C01** (contracts, C01's ignore rules and fixture builder) and **before C04a, C08, C09** (behavior). **Severity (mine):** Major (the Showdown pool size and the public repository); Minor for the rest.
- **Why:** The files confirm most of the design and correct four assumptions (VERIFIED V-R2-12 to V-R2-19). (1) **Layout and encodings** match CONTRACTS v2's two-region rule; entries files carry no byte-order mark and salary files do. (2) **DraftKings `Status` is present** in 2026-27 NBA salary files, and with no official injury report in preseason it is the only automated status source for the rehearsals; so the salary file is downloaded with every entries file, the newest one for a slate feeds availability, and its codes are mapped explicitly (out codes to 0, unknown codes to 0.55 and flagged). The Floor rehearsals are therefore injury-scrubbed rather than "not checked for injuries". (3) **`AvgPointsPerGame`** is last season's DraftKings average over every game played, playoffs included; the design's scorer and identity join reproduce it to the cent for 189 of 224 players, so it becomes a regression test, the Floor's second projection source (and the first one shipped on Thursday, because it needs no history join), and a public-view input. The triple-double rule is settled at +4.5 (V-R2-17), so C04a no longer carries it as a setting. (4) **Identity:** 70 of 226 matched players changed team and 24 more differ only by team code, which confirms R2-9 with numbers and adds an ESPN-to-DraftKings team-code map; near-homonyms (Jokic and Jovic) and seven Joneses mean what the owner types is matched by whole name tokens, never by edit distance. (5) **Showdown pools are much larger than assumed:** 41 players and 13.6 million legal lineups. Our candidates are enumerated over a measured subset (active players above a minutes floor, capped at about 22, measured in C09) and labeled as such; the Showdown field is sampled by popularity rather than enumerated, so our subset never shapes the field's thresholds or copy rates (advisor). (6) **The repository is public,** while ARCHITECTURE said private and the plan would have committed the owner's real entries files and copies of third-party downloads as fixtures. Real and third-party fixtures become local-only (gitignored, rebuilt by `scripts/build_fixtures.py`); a missing real fixture fails its test with a message on this laptop and skips only behind an explicit flag; the standings salt is never committed. Changing the repository's visibility is the owner's setting, so it is a recommendation, not an escalation. Goals: unchanged; opening night: rehearsals use real statuses and real file shapes; cost: none; workload: one extra download (the salary file) per run.
- **Change:** CONTRACTS (person-key preamble with `match_query`; sections 2.1, 2.2, 5, 6, 7, 8, 10, 14, 15); ARCHITECTURE v5.1 (sections 3, 4, 5, 6, 10, 11, 12); ADR-005, ADR-008, ADR-020 changelogs; ADR-029 (Showdown bullet); C01 (fixture builder, ignore rules, `realfiles` marker, salt), C02, C03, C04a (Status facts, the `dk_average` source, checkpoint order, the self-check), C05 (team codes, season types), C08 (Showdown field sampling, runtime on the real pool), C09 (Showdown subset); BUILD_PLAN; OWNER_CHECKLIST (tonight's steps, salary files every run, the visibility recommendation); PROGRESS; CLAUDE.md; README; `.gitignore`; the files archived in `data/archive/2026-10-14/`.

### R2-34. X-R2-05: corrections from the final-gate audits

- **Raised by:** two independent audit agents run as step 2 of the final gate (no stake in the rulings): one checked that every accepted ruling of both rounds lands in a document and a chunk and looked for contradictions; the other checked component coverage, contract ownership, reading-list accuracy, the Floor-only route, the owner checklist and each MVP chunk's internal consistency. Every accepted ruling of both rounds had landed in substance; the corrections below are what they found.
- **Verdict:** Accept. **Before C01.** **Severity (mine):** one Blocker for C01 (the tiny-fixture arithmetic), several Major, the rest Minor.
- **Why, and the decisions taken:**
  - **Tiny fixtures were ambiguous (Blocker).** A "known-score" field read through `p_above` gives a binomial expectation, not a counted rank; the rank window truncated small cases; two fixtures were not settlement cases; one depended on random draws. Decision: each tiny contest states its field as explicit per-scenario point masses; counted-rank cases use degenerate fields; expectations sum every rank with binomial mass above 1e-12, so "exact" means equal to 1e-9; `tiny_crn_swap` is a property fixture with no hand values; the infeasible-cap case moves to C09 and the same-team two-out case to C10; the conservation test covers only fixtures with payout tables.
  - **Nothing switched a capability on (Major).** Decision: `floor` starts enabled; `dfs enable <capability>` and `dfs disable <capability>` (C11a) switch the others, refused unless the capability is `passed` or `dfs unlock` is recorded; drill mode runs any capability regardless of its flag, so Drill A can run the Baseline before it is enabled; the owner enables what passed on Sunday night.
  - **A live night was keyed to the wall-clock date (Major).** Monday's run for Tuesday's slates would have stored its ledger and facts under Monday. Decision: a night is the date of its slates' first lock (from Game Info); files, ledgers and news state are stored by that date; a file for a slate whose games have all started is archived, never used live.
  - **The concentration-cap rule was worded backwards (Major).** "The stricter of the minimum feasible cap and the setting" picks the infeasible value. Decision: the looser (larger) of the two, with the relaxation reported.
  - **"Only changed rows" was a blocking validity rule (Major).** DraftKings accepts unchanged rows (R6: they only slow processing), and Thursday's minimum rehearsal round-trips unchanged lineups. Decision: an exporter option; a file with nothing to change, or `--all-rows`, writes every row.
  - **C04a's checkpoint order put the fact writer after the Status facts that need it (Major).** Decision: the news-state file and fact writer move to checkpoint 1; the commands stay at 3.
  - **No team map on the Floor path (Major).** The injury report prints full team names and The Odds API returns full names. Decision: one team map in C02 (DraftKings codes canonical; ESPN codes, NBA full names and Odds API names as aliases), consumed by C04b, C05 and C06.
  - **`lineup_hash` was consumed by C08 before C09 produced it (Major).** Decision: C01 implements the pure function with tests; C08's reading list adds CONTRACTS section 10.
  - **Fixture timing and sources (Major).** `fixtures/dk/2026-10-16/` comes from `scripts/build_fixtures.py` for every archived night, not from C09; the April 2026 NBA salary file is at `C:\Users\benja\Documents\dfs-os\reference-docs\sample-data\dk_nba_salaries_sample.csv` and the entry-history export at `C:\Users\benja\Downloads\draftkings-contest-entry-history.csv` (both checked), so the builder copies them as local-only fixtures; the payout parser is tested on the tables the owner pastes plus written examples of the other layouts; the WNBA file among the public salary files is excluded.
  - **Dependencies the checker could not see (Major):** C05 depends on C04a; C06 on C11a.
  - **The owner's Friday checks ran before Friday's files existed (Major).** Decision: reorder the checklist; save the Oct 16 payout tables; run C04b's check as a drill on Oct 15 if needed.
  - **On the Floor-only route `/news` and `/swap` wrapped unbuilt commands (Major).** Decision: C11a gives `dfs news` (the repair over the current news state) and `dfs swap` (the post-lock repair with the freshness check) their Floor bodies; C10 replaces them.
  - **Stale wording (Major and Minor):** ARCHITECTURE's Goal 1 formula used the whole prize of a tie straddling place k; ARCHITECTURE and two ADRs said the Oct 16 rehearsal measured the re-solve and the Baseline; R2-33's facts had not reached every line (salary file "optional", `AvgPointsPerGame` "never used", full Showdown enumeration, "fuzzy" matching, the salt's location); two repair wordings; five active ADRs (003, 004, 010, 013, 019) still instructed superseded behavior; plus smaller items (`restriction_cleared` missing from two lists, the standings intake, `dfs sim` writes in drill mode, standings timing, settings keys, the duplicated `[projections]` line, `InjuryState`'s key, unowned pieces, CLI gaps, C04a's timing test, C06's credit count, C07's dependency note, the checklist against the chunk checks, scenario labels without an owner).
  - **A gap closed on the way:** there was no owner command for a minutes restriction before the researcher exists; `dfs restrict "<name>" <minutes>` and `--clear` are added to C06.
  - **The checker itself undercounted section references** (it stopped at the first parenthesis); its parser is fixed and every reference re-checked.
- **Change:** CONTRACTS (sections 1, 1.1, 2.1, 2.6, 3, 4.4, 5, 9, 10, 11.2, 11.3, 12, 13, 14, 15); ARCHITECTURE (sections 2, 3, 4, 6, 7, 8, 11, 12, 13); ADR-003, 004, 007, 010, 013, 017, 019, 020, 023, 026; BRIEF (the MVP Floor bullet); chunk files C01 to C13, C16, C17, C22; BUILD_PLAN; OWNER_CHECKLIST; SLATE-BRIEF-MOCK; `scripts/check_docs.py`.

---

## Escalation answers

No escalations were raised, so the owner was not asked a question in this session. One recommendation is left for the owner's own setting: make the GitHub repository private (R2-33); the design keeps real files out of git either way.

## Advisor consultations

Logged in full in `docs/research/advisor-log.md`.

- **Consultation 3 (stop-the-line batch and contract changes):** the real advisor tool, live in this session. All points taken: C11a depends on C04a only and runs first on Friday; `dfs status --apply` moves to C04b; Sunday evening is a hard cut for C10; C11b goes after opening night; the Goal 2 realization is portfolio-independent; the slate is identified by a fingerprint; identity collisions never stop the night; the slot-reassignment repair and extra recovery tests move to C11a; reversals get new decision records (ADR-029, ADR-030, ADR-031); B-R2-I-02 closed in round 1 rather than escalated.
- **Consultation 4 (the owner's real files of Oct 14):** the real advisor. All points taken: tell the owner first that both entries are blank reservations and when to re-download; enumerate our Showdown candidates over a measured subset but sample the Showdown field by popularity; a missing real fixture fails its test on this laptop; map DraftKings out codes explicitly and read the newest salary file; settle the triple-double rule with the harness (done, V-R2-17); ship the Floor on `AvgPointsPerGame` at C04a checkpoint 2; treat repository visibility as a recommendation.
- **Consultation 5 (final gate review of the complete design):** the real advisor. Verdict: coherent; C01 safe to start after two fixes, both applied: C01 relabeled L with its tiny fixtures allowed to move to C08 if it runs long, and the degenerate tiny field defined exactly with binomial hand values from a standalone script. Also applied: drill mode runs only built capabilities regardless of their flags; every final-audit changelog line traced to R2-34; the ADR index updated; a Monday line for a capability left stale by a parser fix. No second round was needed because no field or ruling changed.
