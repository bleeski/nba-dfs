# Adjudication of the two critiques

**Date:** 2026-10-14. **Adjudicator:** Claude (Fable 5.1), acting as architect. **Inputs:** Critique A (`NBA_DFS_Brief_Critique.md`, reviewer "Codex", 2026-10-13) and Critique B (`nba_dfs_brief_critique.md`, 2026-10-13); the design (`docs/ARCHITECTURE.md` v3, ADR-001 to ADR-022, research memos, spikes); the four reference files now in `docs/reference/`; the owner's goals and hard constraints as restated in the adjudication prompt.

**How to read this.** Item IDs are prefixed A- or B- for the critique that raised them and X- for gaps neither caught. Where both critiques raised the same point, one entry carries both IDs. Every verdict is Accept, Modify, Reject, or Escalate; Escalate is used only where a critique would change one of the two goals or a hard constraint, plus one pending owner decision that carries terms risk. Timing is **before MVP** (lands in an opening-night build chunk), **after MVP** (first weeks of the season), or **backlog**. "VERIFIED" means I ran it or read it in a primary source and the evidence is in the verification log. **Numbering note:** component and risk numbers in the Change lines use the v3 numbering (the architecture as critiqued); v4 removed Component 15, so v3 components 16 to 25 are v4 components 15 to 24, and v3 risks 6 and 7 are v4 risks 8 and 9.

**What the MVP is, for every ruling below.** Three release states, each a floor for the next (entries 3 and 38). **Floor:** parsers, validator, exporter, contest facts, injury-scrubbed lineups ranked on simple projections under the concentration cap, no simulation; rehearsed with a real upload on Oct 15. **Baseline:** adds the night simulation, a first field model, per-contest selection, the live late-news re-solve, the open-slot late swap, the manual news commands, and the one-page brief; drilled on saved Oct 16 files over the weekend and run live on Monday Oct 19 evening with the Floor already uploaded (the Stage 3 calendar refines the advisor's "rehearsed on Oct 16": the Baseline cannot exist by then). **Optimizer:** adds the insurance control, QA, the learning loop, the watcher and the edge-uncertainty layer, after opening night (duplication is inside Goal 1 by the owner's decision, entry 5). The LLM news researcher is a flagged capability that may ship off, with the manual commands as the rehearsed path. The opening-night MVP is whichever of Floor or Baseline has been rehearsed by Oct 19; everything else is labeled **not yet available** in the brief.

---

## Summary

### Counts by verdict (39 register entries covering 39 critique items and 8 gaps of my own)

| Verdict | Entries |
|---|---|
| Accept (as written or with small additions) | 22 |
| Modify | 10 |
| Reject | 2 |
| Escalate | 3 (two proposed goal changes from Critique B; the data posture, a pending owner decision with terms risk) |
| Backlog (accepted in principle, scheduled last) | 2 |

The advisor consultation (end of this document) adjusted seven entries before they were finalized; those adjustments are already in the entries below and marked "(advisor)".

### The five rulings that change the design most

1. **Delete the precomputed replacement store (Component 15, `dfs apply`) and run a live re-solve on the joint news state instead** (entry 10: B-I-04, A-I-09, B-D-06). Two stored replacement tuples can collide on the same entry's salary or players, and the measured narrow re-run already fits the budget (44 seconds at 10,000 scenarios, VERIFIED in R9). This removes the most complex MVP component and leaves one late-news code path.
2. **Specify the insurance margin exactly, prove the implementation matches it, and move the control after the MVP** (entry 8: A-I-08, B-I-02 part 3). The spike's margin used the unpaired standard error of the level, not the paired standard error of the change (VERIFIED in code), which froze every contest with top-1% odds under about 40%. The R9 insurance numbers behind Decision D3 are downgraded to indicative.
3. **Both goals now run on money, by the owner's decision against my recommendation** (entries 5 and 9: B-I-01, B-I-02, with A-I-05 and B-I-07). Goal 1 is top-1% prize equity in dollars after rank-aware tie splits; Goal 2 is the probability of recovering under 25% of the night's fees. The spike's duplication penalty was the flat formula ADR-009 rejects (VERIFIED), so the evidence cited for Decision D2 described a different method; D2 is retired because duplication is now inside the objective, and contest payout facts become the recommended week-1 input for every contest. Raw top-1% probability and literal washout stay as reported diagnostics.
4. **Late news and late swap act on the joint state and on every open slot** (entries 10 and 17: B-I-08, A-I-09). The MVP late swap re-optimizes every unlocked slot of every entry, not only slots holding a ruled-out player, because the beneficiary of a scratch is the point of late swap.
5. **The build becomes a chunked walking skeleton with three honest release states (Floor, Baseline, Optimizer) and a feature flag per capability** (entries 3, 32 and 38: A-I-03, B-I-03, X-01, X-07). Only two live preseason rehearsal nights remain (Oct 15 and Oct 16, VERIFIED); the Floor is rehearsed live on Oct 15 and 16, the Baseline is drilled on saved files and runs live on Oct 19 evening with the Floor underneath, and anything that fails its drill stays off and is labeled.

### Questions for the owner that are not escalations

- **Rehearsal availability (entry 39, X-08):** can you be at the laptop on Thursday Oct 15 and Friday Oct 16 evenings with one $0.25 Classic entry and one $0.25 Showdown entry each night? The whole calendar rests on those two nights.
- **Opening night (Decision D7):** can you be at the laptop from 12:30 to 2:00 pm CT on Tuesday Oct 20?
- **QA iterations (entry 18):** your vision said "QA runs at most three iterations"; the ruling cuts QA to one pass because your vision section said "improve on this". Say so if you meant three as a requirement.

### Escalations

| ID | Proposal | My recommendation | Owner's answer |
|---|---|---|---|
| B-I-01 | Replace Goal 1 with expected top-1% prize equity | **Reject the goal change.** Keep raw top-1% probability as Goal 1; use dollar prize equity as a bounded tie-breaker and report it beside Goal 1 | **Owner chose B's proposal (2026-10-14).** Goal 1 is now top-1% prize equity: expected dollars won from top-1% places after tie splits, as a share of the contest's top-1% pool. Raw top-1% probability stays as a reported diagnostic |
| B-I-02 (part 1) | Replace Goal 2 with "recover less than 25% of fees" | **Reject the goal change.** Keep the literal washout definition; report fee recovery, severe-loss probability and expected net return beside it (A-I-04); revisit the control's target after real nights | **Owner chose B's proposal (2026-10-14).** Goal 2 is now the probability of a severe-drawdown night: winnings below alpha (default 25%, a setting) of the night's total entry fees. Literal washout stays as a reported diagnostic |
| B-I-05 / Decision D1 | Make the personal-use posture (`nba_api` plus ESPN JSON) the default | **Permissive stays the default**; approve `nba_api` as a narrow backup for box scores and game logs only; ESPN JSON stays off. No permitted automated source gives confirmed starters, so a manual one-line command fills that gap (X-02) | **Owner chose the recommendation (2026-10-14):** permissive plus `nba_api` for box scores and game logs only |

**What the two goal changes do to the design (applied in Stage 2).** Both goals now run on money, so the per-contest payout curve and the field's copy rates enter the objective on night one instead of after a calibration gate. Decision D2 (when duplication switches on) is retired: duplication and equal-score ties are inside Goal 1 by definition, with the rank-aware dollar formula from entry 5, and the calibration tolerances in entry 6 now decide only when the brief stops labeling copy rates "unfitted". Contest payout facts (entry 1) move from an optional paste to the recommended week-1 input for every contest, cached by contest name, fee and size after the first night. The insurance control (entry 8) keeps its form: minimize Goal 2 subject to every contest keeping at least `(1 - epsilon)` of its best Goal 1, with the exact paired margin. Both goals are computed from the same per-scenario settlement: each of our entries' rank among the simulated field, the contest's payout at that rank, and the split for ties. The Floor release state does not compute either goal; the Baseline computes both with labeled payout-fact status.

### Where the critics agree, and where they contradict each other

**Agree:** the synthetic field is too weak and the R9 confidence is manufactured (A-I-02, A-I-06, B-I-06); the insurance margin in the spike is not the specified paired calculation (A-I-08, B-I-02); single-player replacement plans do not compose (A-I-09, B-I-04); the advisor must not run inside nightly runs (A-I-14, B-I-09); the volume ramp cannot be gated on two weeks of realized finishes (A-I-12, B-I-11); Monday-evening research misses game-day news (A-I-03, B-I-03); the free-data stack is weaker than the design's "works today" wording (A-I-13, B-I-05).

**Contradict:** on duplication, A says keep raw Goal 1 and report dollars separately, B says replace Goal 1 with prize equity (ruled with A, escalated); on confirmation after upload, A wants the real entry file reconciled before relying on any pending lineup, B wants post-upload re-downloads eliminated (ruled in the middle: commit on the read-back, re-download once before any late swap and once at the final check); on the field model, A wants a family of opponent behaviors tested before trusting anything, B wants a specific bottom-up simulator and specific calibration targets (both accepted: B's targets become stated configuration, A's sensitivity runs come after the MVP); on late news, A wants compatible-plan composition with a bounded rerun as the exception, B wants the rerun to be the only path (ruled with B).

### Shared blind spots

Neither critic noticed that the design's Phase 1 schedule had already expired (it assumed building on Oct 14 and rehearsing that night), that no permitted automated source gives confirmed starters in any posture, that the "original brief" with the advisor section was never saved to disk, or that a chunked build in fresh sessions needs real NBA DraftKings files on day one (X-01, X-02, X-04, X-06).

---

## Verification log

What I ran and what came back. Repo paths are relative to the project root.

| # | Claim checked | What I ran | What came back | Verdict |
|---|---|---|---|---|
| V1 | B-I-02: the spike's safety margin uses an unpaired relative standard error of the level | `sed -n '957,970p' spikes/night/night_spike.py` | `se_rel(c) = sqrt(p_(1-p_)/S)/p_` with `p_ = g1star[c]/S`; `thr = ceil((1 - eps + margin_k * se_rel(c)) * g1star[c])` | VERIFIED. It is the unpaired Monte Carlo error of G1*, not the paired error of a swap's change |
| V2 | B-I-02: at eps 2% and margin 2 the threshold exceeds G1* for contests with G1* under about 40% on 15,000 scenarios | `python -I -c` computing `(1 - 0.02 + 2*se_rel)` for G1* from 0.05 to 0.72 at S=15,000 | G1* 0.38: threshold 1.0009 x G1* (frozen); G1* 0.40: 1.0000; G1* 0.72: 0.9902 | VERIFIED arithmetic. B's "10 of 11 contests" is their reading of the per-contest G1* list, which I did not re-tabulate; the mechanism is confirmed |
| V3 | B-I-07: the spike's duplication adjustment is the flat E[1/(1+D)] that ADR-009 rejects | `sed -n '915,917p;1176,1183p' spikes/night/night_spike.py` | `greedy_weighted` docstring: "f[L] = E[1/(1+D_L)], D_L ~ Binomial(N', q_L)"; `share_factor` computes `(1 - (1-q)^(n+1)) / ((n+1) q)` | VERIFIED. R9's "kept 4, 1, 0 of 10 raw picks" describes the flat penalty, not the payout-table method |
| V4 | B-I-06: the spike draws team points first and back-solves two-point makes | `sed -n '364,380p' spikes/night/night_spike.py` | `Pt_eff = Pt[side] * ...`; `n2 = rint((Pt_eff + eps_t - 3*n3 - nF)/2)`; makes allocated by `_alloc` (multinomial, zero-sum within the team) | VERIFIED. ARCHITECTURE section 4 already specifies attempts-then-makes (bottom-up); the spike does not match the design |
| V5 | B-I-04: the narrow re-run is dominated by field-line recomputation | `sed -n '125,150p' docs/research/R9-night-benchmark.md` | Re-simulate 1.0 s; Classic field 6.2 s; **lines 73.1 s** of 103 s; candidates 2.4 s; 44 s total at 10,000 scenarios | VERIFIED as R9's measurement |
| V6 | B-I-05: a 2026 NBA salary export lacked `Status` and `Starting` | `grep -n -i "starting" docs/research/RR4-dfsos-nbabetting-lessons.md` | RR4 line 73: the 2026-04-15 NBA Classic salary file "has the 9 classic columns and no `Status` or `Starting` columns" | VERIFIED (RR4's inspection of a real file). Whether 2026-27 files carry them is open until the first export |
| V7 | B-I-05: `nba_api` plus ESPN JSON would give "live confirmed starters" | `grep -n -i "confirmed\|starters" docs/research/R4-data-sources.md` | R4 line 307: "Before tip the ESPN summary had no starters, and the stats.nba.com box score returned 0 players"; only RotoWire showed "Confirmed Lineup" 0 to 75 minutes before tip, and RotoWire bans scraping | **B's claim is wrong.** No permitted automated source gives confirmed starters before tip in any posture |
| V8 | A-D-04: ADR-020's "quarter-point-exact" wording is inconsistent with its 85.875 example | `python -I -c "print(1.5*57.25)"` | 85.875. UTIL totals are multiples of 0.25; 1.5 x a quarter point is an eighth point | VERIFIED. Captain totals need eighth-point precision |
| V9 | B-I-03: BOS at DET 3:00 pm ET on Tuesday Oct 20 may be a placeholder | Subagent web check: nba.com news post `nba-schedule-season-opener-2026-27`; ESPN schedule for 2026-10-20; NBC affiliate pages | nba.com: Pistons vs Celtics "tip off the action at 3 p.m. ET"; ESPN: BOS @ DET 3:00 PM, PHI @ NY 7:00 PM, OKC @ SA 9:30 PM; NBC: the same three times in ET | **B's placeholder guess is wrong.** The 3:00 pm ET tip is league-published |
| V10 | X-01: which preseason nights remain for live rehearsal | Same subagent, ESPN schedule pages for Oct 14, 15, 18 | Oct 14: 7 games; Oct 15: 2 games; Oct 16: 12 games; Oct 17, 18, 19: none | VERIFIED. After tonight only Oct 15 and Oct 16 remain |
| V11 | A-I-14, B-I-09: advisor behavior and cost | Subagent fetched `code.claude.com/docs/en/advisor` | "The advisor always receives the full conversation, and Claude controls the timing"; "Subagents inherit the configured advisor"; "each call consumes tokens at the advisor model's rates in addition to your main model's usage"; "There is no setting to cap or force advisor calls"; "Each advisor call processes the full transcript anew" | VERIFIED. Both critics' cost concerns hold |
| V12 | A-I-13: The Odds API free tier and props | Subagent fetched `the-odds-api.com` and the v4 guide | "500 credits per month"; cost = markets x regions per call; player props "one event at a time" via the event odds endpoint; historical odds paid-only; no statement that props are paid-only | VERIFIED. Props are available on the free tier, priced per event |
| V13 | A-I-05: DraftKings splits tied prizes | Subagent: DK Terms capture and DK-hosted contest rules | "In the event of a tie, prizes are divided evenly amongst the participants that have tied" | VERIFIED (the DK help article itself was blocked to the fetcher; the terms and contest rules say the same) |
| V14 | B-I-03: NBA injury report deadlines | Subagent fetched `official.nba.com/nba-injury-report-2025-26-season/`; the 2026-27 page returned 404 | Day-before by 5 pm local; game day 11 am to 1 pm local, 8 to 10 am for tips at or before 5 pm; "updated on a continual basis throughout the day" | VERIFIED for 2025-26 rules; the 2026-27 page is not yet published |
| V15 | A-I-07, B-I-01: scope of the greedy guarantee | Subagent fetched arXiv 1604.01455 (HTML v3) | Theorem 2.2: greedy achieves at least 1 - 1/e of the optimum for a non-decreasing submodular objective under a cardinality constraint (choose k lineups) | VERIFIED. The guarantee covers per-contest selection on a count limit only; it does not cover exposure caps or the insurance search |
| V16 | R2's record that a max-over-our-lineups objective stays submodular | `grep -n -i "facility" docs/research/R2-optimization-methods.md` | R2 line 93: "each scenario counts the best value among our lineups that hit it (a facility location objective), which is still monotone submodular" | SUPPORTED (standard result). B-I-01's math holds; A-I-05's objection is about what the value measures, not the math |
| V17 | Advisor availability in this session | Tool search for "advisor" among this session's tools | No advisor tool is exposed | VERIFIED. The advisor consultation for this adjudication is an independent Fable-model agent (X-03) |
| V18 | R9's 25-entry insurance run with margin 2 | `grep -n "margin2" spikes/night/out/20261013-1957_edge8_be1_edge0.1mix_S30000.txt` | `[small_margin2]` eps 0.02: P(W) 0.753% to 0.243%, mean loss 0.183%, max loss 2.013%, 6 swaps; `[spec_margin2]` (118 entries): 0 swaps at every budget | VERIFIED as measurements; they were taken with the V1 formula, so they are indicative only |

---

## Register

Each entry: who raised it, my verdict and timing, my own severity, why (tied to the goals, the deadline, cost and your workload), and the change made (document and section) or "none".

### 1. A-I-01 (with my addition X-05): tonight's payout facts cannot come from yesterday's history

- **Raised by:** A. B touches the same gap in B-I-12 (entry-history export weekly).
- **Verdict:** Modify. Labels and contest-type classification **before MVP**; the observed-entries capture **after MVP**.
- **Severity (mine):** Major for Goal 2 reporting, minor for Goal 1 (the top-1% line depends on field size, which the prize pool in the contest name estimates within a few percent for large GPPs; it matters most for small contests).
- **Why:** A is right that entry history gives exact facts only after settlement, and that a 23% paid-share default hides a 0.4% to 27.8% range that mixes contest types (R8). The fix is not a mandatory manual form for every contest (10 contests a night at 45 seconds each is 8 minutes of your time for facts that repeat), it is honesty about which facts are verified. Classifying the contest type from its name (double-up, satellite, "Top N", GPP) and using a type-specific default removes most of that range at zero workload. Goal 1: small improvement in thresholds for small contests. Goal 2: washout and cash probabilities stop being quoted as measured when they rest on defaults. Deadline: a few hours of build. Cost: none. Workload: unchanged in the MVP (pastes stay optional and cached); the optional observed-entries field adds about 10 seconds per contest you choose to fill.
- **Change:** ARCHITECTURE section 2 (paid places `m_c`: type-specific defaults; a `facts_status` of verified, template or default per contest), section 3 Component 4 (type classification; `facts_status`; optional observed entries and capacity with a timestamp), section 8 (the brief labels every probability that rests on template or default facts); BRIEF.md problem 7 replaced with A's wording, edited. ADR-004 consequences updated. Build plan: contest facts in chunk C04, the observed-entries capture in C14.

### 2. A-I-02: the simulated edge manufactures confidence in both goals

- **Raised by:** A. Shares ground with A-I-06, A-D-06 and B-I-06.
- **Verdict:** Accept. Wording **before MVP** (now); sensitivity reporting **after MVP**.
- **Severity (mine):** Major. The design's "treat any washout estimate at 50 or more entries as a lower bound" is unjustified and could switch off the one control meant for Goal 2 exactly when the model is most overconfident.
- **Why:** A's logic is correct: zero washouts in 30,000 synthetic draws bounds sampling noise inside an invented world, and the synthetic single entries cashed 31% to 44% against 22% paid where your real entries cashed 13% (R9, R8). Nothing in the design shows that real alternatives have greater risk, so "lower bound" is removed. Goal 2: the brief reports washout as a model estimate with a sensitivity range under three field-strength settings (no edge, stronger field, concentrated chalk) once the field model has settings for them. Goal 1: no change. Deadline: none now. Cost: three extra field draws in the reporting step, about a minute. Workload: none.
- **Change:** ARCHITECTURE section 2 ("lower bound" sentence replaced with A's replacement text, edited: simulation count controls numerical noise, not truth; synthetic tests establish speed and arithmetic only; washout sensitivity to field strength and shared errors is reported, and selection preserves the uncertainty), section 1 "Two things to know up front" rewritten. ADR-001 consequences. Build plan: sensitivity reporting in chunk C16.

### 3. A-I-03 and B-I-03: opening night can ship without the promised product; the schedule misses game-day news; the build scope repeats prior failures

- **Raised by:** both. A: two honest release states, rehearse after the last change, upload the baseline early. B: run the LLM researcher on game day; cut Phase 1 to a five-part walking skeleton; defer DuckDB, the per-entry ledger, the replacement composer, the Bluesky daemon and the three-layer edge model.
- **Verdict:** Modify. **Before MVP.**
- **Severity (mine):** Blocker for feasibility. Both are right, and the calendar is tighter than either assumed (X-01).
- **Why:** The design's own plan let Tier A launch alone while describing a product it does not deliver. Three release states fix the honesty problem (the third added on the advisor's read): **Floor** (parsers, validator, exporter, contest facts, injury-scrubbed lineups ranked on simple projections under the concentration cap, no simulation), **Baseline** (adds the simulation, field model, per-contest selection, the live re-solve, open-slot late swap, manual news commands and the brief) and **Optimizer** (adds the insurance control, QA, learning). The Floor is rehearsed with a real upload on Oct 15 and at scale on Oct 16; the Baseline cannot exist by Oct 16 (chunks C05 to C09 take until about Oct 17), so it is drilled on saved Oct 16 files and runs live for the first time on Monday Oct 19 evening with the Floor already uploaded, and a Baseline slip still leaves the Floor rehearsed (advisor's point, refined by the Stage 3 calendar). Every capability gets a feature flag with a `rehearsed_on` date, and the brief lists the ones that are off. On game-day research: B is right that Monday-evening research misses shootaround and game-day reports, which the league rule puts at 8 to 10 am local for a 3:00 pm ET tip (VERIFIED, V14); the 3:00 pm tip itself is real, not a placeholder (VERIFIED, V9). You are at your desk in the afternoon, so a capped researcher pass at about 12:45 pm CT, then a deterministic rebuild and upload by 1:30 pm, is the plan. On scope: B's walking skeleton is accepted with two adjustments. The ledger stays, simplified to one JSON per slate with each entry's committed and pending lineup and the night's news state, because A-I-09 and A-I-10 need it and the live re-solve (entry 10) reads it. DuckDB arrives with the learning chunk; MVP run artifacts are JSON and Parquet files. The replacement composer is deleted (entry 10), the watcher and the edge-uncertainty layer move after the MVP. A's "upload the baseline early" replaces "upload the fallback only if the full build looks at risk". Goal 1 and Goal 2: a rehearsed baseline beats an unrehearsed optimizer on opening night. Deadline: this is what makes it reachable. Cost: none. Workload: one extra upload early on opening night (about 2 minutes per slate), one 10-minute window at 12:45 pm CT.
- **Change:** ARCHITECTURE section 1 (release states), section 8 (opening-night table rewritten; early baseline upload; game-day researcher pass), section 13 replaced by a pointer to `docs/build/BUILD_PLAN.md`; BRIEF.md MVP paragraph replaced with A's text, edited; new ADR-023 (release states and feature flags) ; ADR-013 and ADR-017 amended (DuckDB after MVP). Build plan: C04 (baseline), C11 (opening-night runbook and flags).

### 4. A-I-04: both goals can improve while financial results deteriorate

- **Raised by:** A. B makes the same point inside B-I-01 and B-I-02.
- **Verdict:** Accept. Wording **before MVP**; the diagnostics **after MVP** (they need payout tables and the results pipeline).
- **Severity (mine):** Major for how you read results; it changes no lineup.
- **Why:** The two goals are yours and stay fixed, but A is right that a $1 cash on a $100 night is a non-washout and that adding cheap entries lowers washout mechanically. The brief and the results page will always show, next to the two goals: total fees, expected net return under stated assumptions, probability of recovering the night's fees, severe-loss probability (returning under 25% of fees), and probability of a meaningful prize (at least 10x the entry fee), with volume changes reported separately from skill changes. "Better median rank alone never justifies scaling" is folded into the volume-ramp gate (entry 13). Goal 1 and Goal 2: unchanged. Deadline: none. Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 2 (new subsection "Economic diagnostics beside the goals"), section 9 (readouts), section 14 D9; BRIEF.md goals section gains A's replacement paragraph; ADR-015 amended. Build plan: C18.

### 5. A-I-05, B-I-01 and B-I-07: duplication, prize equity and the definition of Goal 1

- **Raised by:** A (A-I-05: the prize-fraction score is neither a probability nor money) and B (B-I-01: replace Goal 1 with prize equity; B-I-07: the spike's flat penalty contradicts ADR-009).
- **Verdict:** B-I-01 **Escalate** (I recommended rejecting the goal change; **the owner chose B's proposal on 2026-10-14**, so Goal 1 is replaced). A-I-05 and B-I-07 **Accept**, modified into one mechanism, now **before MVP** because the dollar settlement is the objective itself. The ADR-009 evidence correction is **before MVP** (now).
- **Owner's decision and what it changes:** Goal 1 is "within each contest, maximize top-1% prize equity: the expected dollars our entries win from top-1% finishing places, after splitting tied payouts with opponent copies and equal scores, expressed as a share of the contest's top-1% prize pool; finishes outside the top 1% score zero". Every entry's top-1% winnings count, not only the best entry's. The per-scenario value is a joint settlement of all our entries in the contest (our own entries occupy ranks too), computed exactly for fields under 10,000 and additively above that, where the interaction is negligible. Selection stays greedy (the objective still has diminishing returns, SUPPORTED V16), reported as "best found". Raw top-1% probability is reported beside it as a diagnostic (A-I-05's point survives as reporting). The consequence I flagged stands: payout curves and copy rates enter the objective on night one, so their status is labeled on every number and the brief shows Goal 1 with and without duplication until the entry 6 tolerances pass.
- **Severity (mine):** Major for Goal 1 in Showdown and small fields; the mis-cited evidence is a documentation blocker.
- **Why:** Three facts drive this. First, the spike applied `E[1/(1+D)]` flat across the whole top 1% (VERIFIED, V3), so the numbers ADR-009 and Decision D2 cite ("kept 4, 1, 0 of 10 raw picks") describe the method ADR-009 rejects. Second, A's hypothetical is right: a score built on the *fraction* of a prize kept prefers a unique $100 over a $1,000 share of $10,000, so the design's `share_c` rewards uniqueness rather than money. Third, B's formula fixes both: in scenario `s`, for a lineup at opponent rank `r` with `D` opponent copies drawn from its copy rate, the value is the average of `W_c(r + j)` for `j = 0..D` divided by `(1 + D)`, in dollars, using a payout curve `W_c` from the exact table when present or a five-point curve otherwise. That is money after rank-aware tie splits, penalizes a tie for first heavily and a tie at the top-1% boundary barely, and remains a facility-location objective (SUPPORTED, V16). What B then proposes, making that the objective, changes Goal 1 as you defined it, so it is escalated. My recommendation is to keep raw top-1% probability as the objective and use dollar prize equity as a **bounded tie-breaker**: after greedy selection on raw Goal 1, a local-improvement pass accepts swaps that raise expected top-1% dollars only if raw Goal 1 does not fall by more than two paired standard errors, and the brief discloses both numbers. Reasons: your goals are fixed; a dollar objective needs calibrated payout tables and copy rates that will not exist for weeks (contest facts are often defaults, entry 1; copy rates are unfitted, entry 6); and the bounded tie-breaker captures most of the first-place upside B describes at almost no cost in raw odds. Switch-on tolerances for Decision D2 are pre-registered now (entry 6). Goal 1: unchanged as defined; the tie-breaker raises expected money within noise. Goal 2: none. Deadline: none in the MVP. Cost: one more scoring pass, seconds. Workload: none.
- **Change:** BRIEF.md goals rewritten (original wording kept for history); ARCHITECTURE section 2 rewritten around the settlement (Goal 1 as prize equity; duplication and ties inside it; evidence correction), section 6 (selection on the new objective; raw probability as a diagnostic), section 14 (D2 retired); ADR-009 superseded by ADR-024 (Goal 1 as top-1% prize equity, duplication inside the objective, owner decision); R9 correction note. Build plan: C08 (settlement and copy rates), C09 (selection).

### 6. A-I-06: the field can be wrong in ways ownership accuracy will not reveal

- **Raised by:** A. Overlaps B-I-06 (strawman field) and A-D-05.
- **Verdict:** Modify. Pre-registered tolerances **before MVP** (now, in configuration text); separate field checks and the cross-contest dependence sensitivity **after MVP**.
- **Severity (mine):** Major for both goals; it is the core calibration risk of the design.
- **Why:** A is right on all three points. Agreement among ownership, duplicates and thresholds drawn from one generator is internal consistency. "Private" is a hypothesis about informational advantage, not evidence of it. And section 2's independent-opponent binomial does not reconcile with section 5's user-clustered field; the design already planned a beta-binomial "once standings show clustering", which is the right fix and now has a trigger. Concretely: the field scorecard checks marginal ownership, player-pair co-occurrence, salary left unspent, Captain combinations, exact-duplicate counts, entrant portfolio clustering and realized score cutoffs as **separate** measures, each with its own baseline; the D2 switch-on tolerance is written now rather than after seeing results: predicted copy counts for the field's 20 most common lineups within a factor of 2 of observed on at least 4 of the first 5 standings files per format, and our own entries' predicted expected copies within 1.0 of observed on average; washout is reported with a shared-field sensitivity (the same simulated users entering every contest on a slate) beside the conditional-independence number. Goal 1: thresholds stop being trusted on ownership fit alone. Goal 2: dependence across contests is shown, not assumed. Deadline: none in the MVP. Cost: morning compute, seconds. Workload: none.
- **Change:** ARCHITECTURE section 2 (Goal 2 independence note; D2 tolerances), section 5 (qualification checks; "family of plausible opponent behaviors" wording), section 9 field scorecard rows, section 11; ADR-008 amended; BRIEF.md problem 6 adds A's replacement text, edited. Build plan: C14, C16.

### 7. A-I-07: the selection guarantee does not cover the proposed constraints

- **Raised by:** A.
- **Verdict:** Modify. **Before MVP** (the cap is built in the selection chunk).
- **Severity (mine):** Major for honesty, minor for results (the cap never bound on the synthetic night).
- **Why:** The guarantee is for greedy on a count limit (VERIFIED, V15), and the design adds a night-wide 60% cap and an insurance search on top. A's Showdown arithmetic is also right: six slots over nine credible players need 66.7% average exposure, so a universal 60% cap can be infeasible on a thin night or a one-game night. Ruling: the concentration cap becomes a per-format, feasibility-tested soft preference: the selector computes the minimum feasible cap for tonight's pools and entry counts, applies the stricter of that and the setting, and reports when it relaxed; it never blocks delivery. Every reported guarantee is labeled: the 63% bound applies to the per-contest greedy step on its candidate pool; the insurance search and local improvement are heuristic refinements reported as "best found" with in-sample and out-of-sample numbers. Goal 1: no silent loss to an infeasible cap. Goal 2: none. Deadline: an hour. Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 6 (guardrails rewritten; "search quality versus model quality" paragraph with A's replacement text, edited); ADR-007 amended. Build plan: C09.

### 8. A-I-08 and B-I-02 (part 3): the insurance safety margin is not a statistical guarantee, and the spike computed a different margin

- **Raised by:** both.
- **Verdict:** Accept. Specification **before MVP** (now); the search itself **after MVP** (chunk C12).
- **Severity (mine):** Blocker for the insurance claims as written; the control ships after the MVP anyway.
- **Why:** VERIFIED (V1, V2): the spike's margin is the unpaired relative error of the level, which at 15,000 scenarios makes the threshold exceed G1* for every contest with G1* under about 40%, so the R9 margin runs mostly swapped inside the 150-max. A is also right that a reporting set which triggers rollbacks is no longer untouched, and that one two-standard-error comparison does not protect many searched changes. The specification now reads: for a candidate portfolio `E_c` against the contest's best `E*_c`, `Delta_c = G1_c(E_c) - G1_c(E*_c)` on the validation set, with `SE_paired` the standard error of the per-scenario indicator differences of those two portfolios (cumulative from `E*_c`, never per incremental swap); accept only if `Delta_c - 2 x SE_paired >= -epsilon x G1_c(E*_c)` in every contest. There is no pre-freeze rule: a contest is labeled "frozen" after the search when no candidate swap in it satisfied the constraint, and the brief names those contests (advisor: a trigger phrased as "any single swap's error exceeds the budget" would freeze nearly everything and reproduce the spike's bug by another route). A test feeds a known case and checks the implementation reproduces the formula. The roll-back check stays a label on the reporting set; if a rollback is applied, the final numbers are recomputed on a fresh reporting draw (about 3 minutes, only in that case). The user-facing wording changes from "give up at most 2%" to "a model-based target under stated assumptions". Decision D3's default of 2% stands as a starting value and is re-measured with the corrected formula on the first real nights. Goal 1: contests are no longer frozen by an inflated margin. Goal 2: the control can act where it should. Deadline: none in the MVP. Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 2 (insurance subsection rewritten with the exact formula, freezing rule, rollback rule and the R9 caveat), section 14 D3; ADR-001 superseded by ADR-025 (insurance control: exact paired margin, model-based target, post-MVP); R9 gets a correction note. Build plan: C12.

### 9. B-I-02 (parts 1 and 2): Goal 2 is degenerate at 50 or more entries and ignores dollar loss

- **Raised by:** B. A makes the dollar point in A-I-04.
- **Verdict:** Part 1 **Escalate** (I recommended rejecting the goal change; **the owner chose B's proposal on 2026-10-14**, so Goal 2 is replaced). Part 2 **Accept** as a stated fact, **before MVP** (wording).
- **Owner's decision and what it changes:** Goal 2 is "across the night's portfolio, minimize the probability of a severe-drawdown night: total winnings across every contest, Classic and Showdown combined, below alpha of the night's total entry fees", with alpha a setting defaulting to 25% (alpha near zero recovers the literal zero-cash definition). It is computed from the same per-scenario settlement as Goal 1, over every paid place, not only the top 1%, so it needs each contest's payout curve and paid places; their status is labeled. At your volume this goal binds on many more nights than literal washout did, so the insurance control (entry 8) is expected to act regularly rather than rarely. Literal washout, unfilled entries and per-game concentration are reported beside it. The Floor prints "not estimated"; the Baseline prints a labeled, uncalibrated model estimate (entry 38).
- **Severity (mine):** Major for expectations, not for the build.
- **Why:** B's arithmetic is the design's own: at 50 entries the model found 1 washout scenario in 30,000, at 118 none (R9, V18). But the synthetic engine was far too skilled (entry 2), so the real washout rate at 50 entries is unknown, not zero, and the literal goal still binds on thin nights, during the ramp at 25 entries, and on any night the fill is low. Redefining Goal 2 as a fee-recovery floor is a goal change, so it is escalated with a recommendation to keep the literal definition and add the fee-recovery, severe-loss and expected-return diagnostics (entry 4). If, after real nights, you want the control to target severe loss rather than literal washout, that is one setting (`insurance.target = washout | severe_loss`) and ADR-025 leaves room for it. Goal 2: unchanged as defined. Goal 1: none. Deadline, cost, workload: none.
- **Change:** BRIEF.md Goal 2 rewritten (original kept for history); ARCHITECTURE sections 1 and 2 (Goal 2 as severe drawdown; the `goal2.alpha` setting; literal washout as a diagnostic); ADR-001 superseded by ADR-025. Build plan: C08 (settlement), C12 (control), C18 (diagnostics).

### 10. A-I-09, B-I-04 and B-D-06: late news, stored replacements, and the live re-solve

- **Raised by:** both (A: plans do not compose, recompute beneficiaries, reconcile after a lock; B: delete Component 15, live incremental re-solve; B-D-06: cache field scores to make it fast).
- **Verdict:** Accept B-I-04 and A-I-09, **before MVP**. B-D-06 **after MVP**, conditional on a measured need.
- **Severity (mine):** Blocker for correctness of the late-news path as designed.
- **Why:** B's collision case is real: two replacement tuples for the same Classic entry can both touch the same third player, both insert the same pivot, and together exceed the cap; the design's composition rule ("combine every confirmed change") has no answer for it, and A's joint-state argument says the same thing from the modeling side (two teammates out is not two one-out cases). The design built Component 15 to get "seconds" because the narrow re-run took 103 seconds at 30,000 scenarios, but the brief's requirement is to act on news 30 minutes before tip, and the measured re-run is 44 seconds at 10,000 scenarios (VERIFIED, V5) plus one upload. Ruling: Component 15 and `dfs apply` are deleted. `dfs out`, `dfs in` and `dfs start` (X-02) update the night's news state and run the narrow re-run on the **joint** state: re-simulate affected games, refresh the public view and fields for slates containing them, rebuild candidates, re-select before the first lock or re-optimize open slots after it (entry 17), validate, export a versioned file stamped "valid until", update the ledger. Budget 3 minutes at 10,000 scenarios. The 44-second figure is the spike's, and entry 16 discards the spike as a statistical oracle, so the budget is unmeasured for the rewritten engine until Drill B on the saved Oct 16 twelve-game files and the Oct 19 live run time it (advisor; calendar refined in Stage 3). The rehearsed fallback when the re-solve misses its budget or crashes is the validator's **legal repair**: remove the ruled-out player and insert the cheapest legal substitute by projection, exported in seconds, labeled as a repair; if Drill B or the Oct 19 run shows detection-to-confirmed-upload exceeding the window at 30, 10 or 2 minutes before tip, the legal repair is the opening-night late-news path and the re-solve ships flagged off. B-D-06's cached field scores with sparse deltas is the optimization if a 12-game slate exceeds the budget. The acceptance tests take A's list: two same-team absences, conflicting pivots, a status reversal, an unrostered scratch that changes our beneficiaries, a failed upload crossing a lock; the engine states "insufficient time to act" when a changed cell's game locks within a set number of minutes; rehearsal measures detection-to-upload time at 30, 10 and 2 minutes before tip. Goal 1 and Goal 2: every late-news file is built on the full current state. Deadline: removes the most complex MVP component. Cost: about a minute of compute per news event instead of seconds. Workload: the same commands; about 1 to 2 minutes longer per event.
- **Change:** ARCHITECTURE sections 1, 3 (Component 15 removed; Components 16 and 17 revised; data-flow diagrams), 6 (stored replacements subsection replaced by "Late news: the joint re-solve"), 8 (late-news path and runbook rows), 11 (tests), 12 (risk 6); ADR-011 superseded by ADR-026 (late news as a live re-solve on the joint state); ADR-019 amended. Build plan: C10 (re-solve), C20 (cache, conditional).

### 11. A-I-10: "only validity blocks" removes the distinction between usable and merely uploadable

- **Raised by:** A.
- **Verdict:** Accept. **Before MVP.**
- **Severity (mine):** Major.
- **Why:** A is right that an offline validator cannot guarantee platform acceptance, that DraftKings may correct a player pool after contests open (both rules files say so, VERIFIED in `docs/reference/`), and that the right fallback depends on what failed. The engine now tracks four states per slate separately: file validity (validator result against the identified input snapshot and lock time), news state (which statuses are applied), model status (which capabilities ran), and confirmed upload (your read-back). Known-OUT unlocked players are removed whenever a legal repair exists; identity or lock uncertainty stops an edit rather than shipping it; the "never hands me an invalid file" promise is restated as "every exported file passes the validator against its identified input snapshot and lock time; platform acceptance is confirmed separately". Goal 1 and Goal 2: fewer entries lost to the gap between valid and usable. Deadline: small. Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 3 (Components 2 and 16), section 8 (fallback ladder and the four-state status line), section 12; BRIEF.md constraint "Correct files, every time" reworded with A's replacement text, edited; ADR-010 and ADR-019 amended. Build plan: C03, C04.

### 12. A-I-11: the LLM's numerical confidence is being treated as statistical evidence

- **Raised by:** A. B's "what holds up" praises the belief-record boundary; both are compatible with this ruling.
- **Verdict:** Modify. **Before MVP.**
- **Severity (mine):** Major for Goal 1 on news-driven nights.
- **Why:** A's points stand: a player-outcome interval is not the uncertainty of an estimate of the mean; the LLM and the model share evidence; a true quote with unknown event time can still drive a harmful override. Ruling: the researcher's output splits into **fact records** (an announced starter, a restriction, an absence, a return, each with source, publish time and quote) and **inference records** (minutes and usage percentiles). In the MVP, only fact records with a verified quote and a known publish time inside 24 hours change the simulation, and code translates each fact type into a distribution with a fixed rule (for example "named starter" uses the role's starter minutes prior; "restriction, N minutes" sets a hard cap). Inference records are stored and scored in shadow; the precision-weighted blend with the 1.5 coverage factor switches on only after two weeks show their stated ranges cover actuals at the stated rate. Records with unknown publish time never change availability or role. A later fact about the same player supersedes an earlier one, so Monday's day-before report cannot outlive Tuesday's game-day report when overrides are reused (advisor). Goal 1: no unsupported 34-minute projection drives a portfolio. Goal 2: fewer correlated misses from one confident record. Deadline: simplifies the MVP researcher. Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 4 ("Where LLM overrides meet the model" rewritten), section 7 (override record split; checks; "time unknown" rule), section 9 (shadow scoring of inferences); ADR-003 amended; BRIEF.md problem 2 gains A's replacement text, edited. Build plan: C06 (schemas and rules), C11 (researcher).

### 13. A-I-12 and B-I-11: the learning rules allow premature victories; the ramp gate is noise

- **Raised by:** both.
- **Verdict:** Accept. **After MVP** (learning chunks); the gate wording **before MVP** (now).
- **Severity (mine):** Major for cost (scaling spend on noise).
- **Why:** Both are right and the design half-knew it: it says the night is the unit of evidence, then promises duplicate adjustment after five files, edge fitting after two weeks of cash rates, and a ramp gated on a two-week rank comparison that its own section 9 says needs about 88 slates. Ruling: every promotion claim states its independent nights, news regimes, interval and repeated-testing policy; challengers are frozen before their evaluation window; held-out nights are used once per challenger family; predictions are stored as they stood at decision time; late-swap replays reproduce when news became available and whether you could act; in flashback scoring, our historical entries are replaced, not added. The Nov 3 ramp gate becomes B's three conditions plus A-I-04's diagnostics: zero delivery failures over the window; minutes and ownership accuracy beating the named baselines with intervals excluding zero; positive flashback equity against the control and a random-entry benchmark on real fields; and the fee-recovery and expected-return diagnostics shown beside it. Realized finishing percentile is reported but is not the gate. Goal 1 and Goal 2: no change to lineups. Deadline: none. Cost: avoids scaling spend on a heater. Workload: none.
- **Change:** ARCHITECTURE section 9 (guardrails and readouts rewritten), section 14 D9; ADR-015 amended; ADR-022 scope narrowed (entry 16); BRIEF.md problem 12 gains A's replacement text, edited. Build plan: C13, C18.

### 14. A-I-13 and B-I-05: the free stack is not proven, and the posture question

- **Raised by:** both. A: "complete free stack works" is unsupported; verified-source labels; end-to-end source rehearsal. B: adopt the personal-use posture; never let the public view fall back to our baseline; props on only 7 nights.
- **Verdict:** A-I-13 **Accept**, before MVP. B-I-05 point 3 (public-view fallback) **Accept**, before MVP. B-I-05 posture **Escalate** as pending Decision D1 with my recommendation (**the owner chose the recommendation on 2026-10-14**: permissive plus `nba_api` for box scores and game logs only); point 1 corrected on the facts; point 2 handled by the `nba_api` backup; point 4 accepted as a stated limitation.
- **Severity (mine):** Major for feasibility.
- **Why:** A is right that the design's table contradicts its summary: The Odds API is untested with a key, Daily Fantasy Fuel returned no preseason projections, `Status` and `Starting` are a bet (and a real April 2026 NBA file lacked them, VERIFIED V6), the 2026-27 injury-report format is unknown. "Verified source" now means the chosen local path returned current data that parsed and passed freshness, with separate labels for documentation-only and historical probes; each required input names its fallback; pre-lock snapshots of lines and props are archived from the first night. B's strongest factual claim is wrong: no permitted automated source gives confirmed starters before tip in any posture (VERIFIED V7), so widening the posture would not buy them; `dfs start` (X-02) does. B's point 3 is right and accepted: the public view never falls back to our private baseline; when no consensus file exists it is built from a deterministic public formula (salary-implied value blended with the market-implied team share and trailing DraftKings points), so a private edge can never appear as simulated chalk. On the posture itself, the terms risk is yours, so D1 stays with you; my recommendation is permissive by default, with `nba_api` approved only as a backup for box scores and game logs (about five requests a night) when the sportsdataverse file lags more than 24 hours, and ESPN JSON off. Two consequences stated plainly (advisor): the sportsdataverse file was last updated September 9 (R4), so that trigger is already met and, under this recommendation, `nba_api` is the de facto source of current-season box scores from opening week unless the volunteer job resumes; and Daily Fantasy Fuel had no preseason projections, so the consensus path cannot be rehearsed and the opening-night public view is the deterministic public formula unless a Daily Fantasy Fuel file parses in a dry run first. Props: the free tier supports them per event (VERIFIED V12); the engine budgets them for the largest slates. Goal 1: honest inputs. Goal 2: fewer correlated misses from stale history. Deadline: none. Cost: free. Workload: none beyond the Odds API key.
- **Change:** ARCHITECTURE section 10 (summary sentence replaced; verified-source definition; fallback per input; public-view fallback rule), section 5 (public view table), section 14 D1; ADR-005 amended (recommendation and `nba_api` backup scope), ADR-008 amended (fallback rule); BRIEF.md constraints gain A's replacement text, edited. Build plan: C05 (history with the backup), C06 (market anchor), C08 (public view).

### 15. A-I-14 and B-I-09: the advisor has no enforceable budget and does not belong in nightly runs

- **Raised by:** both.
- **Verdict:** Accept. **Before MVP** (it is the session protocol).
- **Severity (mine):** Major for cost.
- **Why:** VERIFIED (V11): the advisor receives the full conversation on every call, subagents inherit it, it costs extra usage, and nothing caps it. A full-context advisor is also not an independent evaluator. Ruling: the advisor is used in build sessions (when a chunk is stuck, and once before a chunk is declared done), in this adjudication, and in the weekly results review; it is never called inside `/night`, `/news`, `/swap` or `/results`; each consultation names one decision and has a cap of one call; a concise log lives in `docs/research/advisor-log.md`; if the advisor is unavailable the deterministic path continues. Goal 1 and Goal 2: none. Deadline: protects the build-week allowance. Cost: bounded. Workload: none.
- **Change:** ARCHITECTURE section 7 (new subsection "Where the advisor fits"); ADR-013 amended; BRIEF.md advisor section (reconstructed, X-04) replaced with B's wording, edited; `CLAUDE.md` session protocol. Build plan: all chunks.

### 16. B-I-06: the reference simulator clamps team points before allocating baskets, and the field is a strawman

- **Raised by:** B. The strawman-field half overlaps A-I-02 and A-I-06.
- **Verdict:** Modify. **Before MVP** for the ADR-022 scope and the simulator structure; the calibration targets as stated configuration **before MVP**; the stronger field settings **after MVP**.
- **Severity (mine):** Major.
- **Why:** VERIFIED (V4): the spike draws team points and back-solves two-point makes, then allocates makes zero-sum within the team. The design text in section 4 already specifies the bottom-up order (attempts from possessions and usage share, makes from shrunk percentages), so the problem is ADR-022, which makes a top-down spike the "test oracle" for a bottom-up engine. Ruling: the engine simulator follows section 4 as written, with B's calibration targets stated in configuration and checked against last season before any slate (starter standard deviation 0.22 to 0.25 of the mean; most-owned Classic player 40% to 60% on the field model; overtime 5% to 6%; margin standard deviation about 13); ADR-022 is narrowed so the spike is a timing and bitset-mechanics benchmark and a regression oracle for the field scoring, threshold and selection arithmetic, never for the simulator's statistical outputs. B's rebounds-from-misses and assists-from-team-makes steps are already in section 4. Goal 1: tails and teammate correlations come from the stated structure, not from a clamp. Goal 2: same. Deadline: none (the engine was always a rewrite). Cost: none. Workload: none.
- **Change:** ARCHITECTURE section 4 (calibration targets), section 11 (simulator calibration list), section 13 pointer; ADR-022 superseded by ADR-027 (spike as a mechanics benchmark only); ADR-002 amended. Build plan: C07, C16.

### 17. B-I-08: Phase 1 late swap only swaps out ruled-out players

- **Raised by:** B. A-I-09 asks for beneficiaries to be recomputed even when the absent player is not rostered.
- **Verdict:** Modify. **Before MVP.**
- **Severity (mine):** Major for Goal 1 on nights with late-game scratches.
- **Why:** B is right that the biggest structural edge in NBA late swap is moving into the beneficiary of a late scratch, and that an entry which never held the scratched player is exactly the one that needs the swap. B is also right that the open-slot re-optimizer is simpler than a separate swap-out-only path: pin every `(LOCKED)` cell and every player whose game has started, subtract their salaries, and run the same candidate solver on the open slots. The MVP version re-optimizes each entry's open slots on the engine's current projections with locked games left at their pre-lock distributions (no live-score conditioning); per-entry diversity comes from the same perturbed-objective candidates. Scope rule (advisor): `/swap` rewrites an entry only when a news fact has changed since that entry's last exported file, or when the open-slot improvement clears a stated threshold (a setting, default 3 projected points); every other entry stays exactly as uploaded; the concentration cap is re-checked on the post-swap portfolio; and the brief shows the diff before you upload. Without this rule a per-entry re-optimizer drifts every entry toward the same beneficiary on every lock wave and produces a diff you cannot read. Conditioning on finished and in-progress games (and B-D-02's locked-field view) comes after the MVP. Goal 1: late-game value plays reach every entry with an open slot. Goal 2: more entries alive after a scratch. Deadline: replaces, not adds, a code path. Cost: seconds per entry. Workload: unchanged (re-download, `/swap`, upload).
- **Change:** ARCHITECTURE section 3 (Component 17), section 8 (runbook row and the narrow re-run step 6), section 12 risk 7; ADR-026 (entry 10) covers late swap. Build plan: C10, C23.

### 18. B-I-10: the QA adversary is split between tasks code does better and a bar that blocks qualitative checks

- **Raised by:** B.
- **Verdict:** Modify. **After MVP** (QA was already week 2).
- **Severity (mine):** Major for cost and workload, minor for results.
- **Why:** B's two arguments hold: the deterministic local-improvement pass already tests leverage swaps in under a second, and a 20-game evidence bar automatically rejects the kind of thing an LLM can actually catch an hour before lock (a stagger quote, a player who has not cleared physicals, a lineup pairing a guard with his own backup). Historical splits belong in the deterministic priors module (after the MVP, when history and errors exist). Ruling: QA becomes a single-pass **pre-lock coherence audit** (one iteration, 3 minutes, from week 2): it reads the top 15 players by exposure, the top 5 Captains, and the raw news digest, and files only missed-news challenges (with a cited, fetched source) and lineup-coherence flags; code judges both as before. Your brief's "up to three iterations" was a starting hypothesis, not a hard constraint, and the evidence bar survives in the form of a required citation. Goal 1: the audit catches the misses an LLM can see. Deadline: none. Cost: one short subagent run instead of three. Workload: none.
- **Change:** ARCHITECTURE section 7 (QA loop rewritten), section 3 (Component 24), section 8; ADR-012 superseded by ADR-028 (QA as a one-pass coherence audit); BRIEF.md vision step 4 and problem 10 edited. Build plan: C17.

### 19. B-I-12: manual file-juggling creates operator fatigue and re-download failure modes

- **Raised by:** B. A-I-10 argues for reconciling the real entry file after a lock; the ruling takes both.
- **Verdict:** Modify. Points 1 and 2 **before MVP**; point 3 **after MVP** (results chunk).
- **Severity (mine):** Major for workload, which is a feasibility risk.
- **Why:** B's count is about right and the prior engines' records (342 contests awaiting standings in MLB; 35 of 61 in NFL) show the pattern. Point 1: the entries file already carries the player pool (VERIFIED in R6, 158 of 158 IDs), so the salary export is optional from the start; rehearsal 1 records whether the 2026-27 NBA export carries `Status` or `Starting`, and only if it does is it worth a download at build time. Point 2, in the middle between B and A: an upload is **committed** when you confirm the read-back (`dfs uploaded <file>` or the one-line prompt in `/status`); a re-download is required before each Showdown's lock, before the main Classic slate's first lock, and before any post-lock `/swap` (the engine needs the `(LOCKED)` markers anyway); it is optional after intermediate uploads. The Showdown rule is the advisor's: a wrong-file upload (version 4 instead of 5) reads back as "N of N" and a Showdown has no swap and no second lock, so the only place to catch it is a re-download before that lock. On a four-slate night this is about four re-downloads timed to matter, instead of one after every upload. The ledger keeps the pending state in case you say an upload did not happen. Point 3: one flagship standings zip per slate is the required morning download (every player's points and a representative field); other contests' zips are optional; the weekly entry-history export supplies rank, winnings and exact facts for every contest. Goal 1 and Goal 2: fewer missed steps at lock. Deadline: none. Cost: none. Workload: afternoon downloads halve, re-downloads drop from about four to one or two, morning downloads drop from ten or more to three or four.
- **Change:** ARCHITECTURE section 1 (how a night runs), section 3 (Components 1, 2, 16), section 8 (runbook, "your time" table), section 9 (inputs table); ADR-004 and ADR-010 amended. Build plan: C02, C03, C13.

### 20. A-D-01: define a narrow, testable source of advantage

- **Raised by:** A.
- **Verdict:** Accept. Wording **before MVP**; measurement **after MVP**.
- **Severity (mine):** Major for how the backlog is prioritized.
- **Why:** "Emulate the secret sauce" is not a hypothesis. The living brief now names three: (1) execution reliability (no blank, late or rejected entries; falsified by any delivery failure); (2) late-news reaction (our entries reflect a scratch and its beneficiary before the field's stale share does; falsified if our news-driven ownership error is no better than the field's); (3) minutes and role on rotation changes (minutes error on news-affected players beats the 75/25 baseline; falsified if it does not after 30 such player-games). Every proposed feature after the MVP names which hypothesis it serves and what result would falsify it; commercial-platform feature replication is not a reason by itself. Goal 1 and Goal 2: focus. Deadline: none. Cost: avoids building unmeasurable features. Workload: none.
- **Change:** BRIEF.md new section "Where the edge is supposed to come from"; ARCHITECTURE section 1 and section 9. Build plan: milestone descriptions.

### 21. A-D-02: spend research and data quota where a decision can change

- **Raised by:** A.
- **Verdict:** Modify. The cheap version **before MVP**; the sensitivity version **after MVP**.
- **Severity (mine):** Minor to moderate.
- **Why:** Right in principle; the full version (compare plausible states of each unresolved fact and measure how much the portfolio changes) needs the re-solve machinery and time. The MVP news digest orders unresolved facts by exposure times fees at risk and tells the researcher to spend its search budget from the top, and it includes unrostered players whose status moves our beneficiaries. After the MVP, the digest adds "portfolio changes materially if this resolves" from a quick two-state re-solve for the top few facts, and a late-news reserve for searches and fetches is kept. Goal 1: research lands where it moves lineups. Cost: lower LLM usage. Workload: none.
- **Change:** ARCHITECTURE section 7 (news digest ordering; reserve); BRIEF.md problem 1 note. Build plan: C11, C21.

### 22. A-D-03: value the ability to change a lineup later

- **Raised by:** A.
- **Verdict:** Reject for now (backlog with a trigger).
- **Severity (mine):** Minor until late-swap scorecards exist.
- **Why:** A multi-stage evaluation of decision paths with operator availability is high effort, and the design already values flexibility through the simulation and the slot-assignment step. It would not move either goal in the opening weeks and would consume build time that execution reliability needs. Trigger to revisit: if the late-swap scorecard (after the MVP) shows our pre-lock portfolios regularly lacked an affordable pivot when news broke, this is the next design item.
- **Change:** none, except a backlog line in BUILD_PLAN.md.

### 23. A-D-04: audit what Showdown screening throws away; fix the scoring precision wording

- **Raised by:** A.
- **Verdict:** Accept. ADR-020 wording **before MVP** (now); the coverage audit **after MVP**.
- **Severity (mine):** Minor for the wording (the stored values were already exact), moderate for the audit.
- **Why:** VERIFIED (V8): Captain totals are eighth-point values, so "quarter-point-exact" was wrong wording though the example and the storage rule were right. The audit is cheap on Showdown's small universe: on saved slates, compare the screened shortlist with a full evaluation and record how often a candidate that scores well on fresh scenarios was discarded, without promoting hindsight winners. Full enumeration never justifies an optimality claim after screening. Goal 1: Showdown candidates are not lost to a mean-plus-spread shortlist. Cost: morning compute. Workload: none.
- **Change:** ADR-020 (eighth-point wording), ARCHITECTURE section 11 (scoring tests; Showdown coverage audit). Build plan: C05 (scoring), C16 (audit).

### 24. A-D-05: learn from joint failures before waiting for washouts

- **Raised by:** A.
- **Verdict:** Accept. **After MVP.**
- **Severity (mine):** Moderate for Goal 2 calibration.
- **Why:** Washouts are too rare to calibrate the model-error layer; near-washout diagnostics are not. The results step records errors grouped by game and by news event, the fraction of entries cashing, the best entry's distance from each cash line, and returns across the night, compared with the pre-lock prediction and bootstrapped by night; failures are attributed to a common assumption where one exists. These can reject a bad model; they never certify a tiny washout probability. Cost: morning compute. Workload: none.
- **Change:** ARCHITECTURE section 9 (model-error layer rows and the new diagnostics); ADR-015 amended. Build plan: C13, C16.

### 25. A-D-06: make the model survive deliberate attempts to fool it

- **Raised by:** A. Overlaps B-I-06's strawman-field point.
- **Verdict:** Accept. A few tiny examples **before MVP** inside the relevant chunks' tests; the full suite **after MVP**.
- **Severity (mine):** Major for trust in the numbers.
- **Why:** Small, fully countable examples give definite answers: exchangeable entrants (our edge must be zero), a stronger field plus a shared error against our preferred players, the same lineup and opponents repeated across contests (the independence product must be wrong and the shared-field sensitivity right), ties at a payout boundary with more tied entries than paid places, two same-team scratches and a failed upload across a lock, and a concentrated Showdown pool where the cap is infeasible. The arithmetic is checked independently of the spike. Cost: test time. Workload: none.
- **Change:** ARCHITECTURE section 11 (new "Adversarial examples" list). Build plan: C09 and C10 (a few), C16 (the suite).

### 26. A-D-07: put a stopping rule on architecture research itself

- **Raised by:** A.
- **Verdict:** Accept. Now.
- **Severity (mine):** Major for the deadline.
- **Why:** The design has 25 components and 22 decision records; more memos before opening night reduce no risk. Rule: research ends when it resolves a named decision or hits its time budget; no new research memos before Oct 20 except a spike a build chunk needs to settle a contract; established operational facts from the prior engines may be consulted at any time. Cost: protects the allowance. Workload: none.
- **Change:** BRIEF.md "How to run this" rule; `CLAUDE.md` session protocol. Build plan: each chunk's research budget.

### 27. B-D-01: post-contest "contest flashback" on real standings lineups

- **Raised by:** B.
- **Verdict:** Accept. **After MVP.**
- **Severity (mine):** Major for learning speed; it is the gate input for the volume ramp (entry 13).
- **Why:** Scoring our final, pre-override and control portfolios against the actual opponent lineups in a standings file, under pre-game projections and under hindsight-known roles, separates construction from projection and from one night's luck; the scorer already exists for selection. A-I-12's rule applies: our historical entries are replaced, not added. Cost: under a minute per slate. Workload: the flagship standings download already planned.
- **Change:** ARCHITECTURE section 9 ("Against real fields" rewritten), section 14 D9; ADR-015 amended. Build plan: C13.

### 28. B-D-02: late-swap locked-field conditioning from a mid-slate standings export

- **Raised by:** B.
- **Verdict:** Backlog (accepted in principle).
- **Severity (mine):** Moderate for Goal 1 on late-news Classic nights.
- **Why:** It needs the standings parser, the open-slot re-optimizer and live-score conditioning first, and it adds a manual mid-slate download to your night. Revisit after the late-swap scorecard shows how often late scratches changed our entries.
- **Change:** none now; BUILD_PLAN.md backlog line.

### 29. B-D-03: game-script rotation regimes from play-by-play stint data

- **Raised by:** B.
- **Verdict:** Backlog with a trigger.
- **Severity (mine):** Moderate for Showdown tails.
- **Why:** Discrete regimes (competitive, overtime, blowout mop-up, early exit) are a real improvement over a smooth blowout trim, and play-by-play exists in the sportsdataverse files; but it is medium effort and the simulator's calibration tests (section 11) will say whether blowout minutes are miscalibrated. Trigger: minutes coverage fails for starters or deep bench in games decided by 16 or more.
- **Change:** none now; BUILD_PLAN.md backlog line.

### 30. B-D-04: contest-entry assignment optimizer

- **Raised by:** B.
- **Verdict:** Reject.
- **Severity (mine):** Minor.
- **Why:** The design already selects lineups per contest against that contest's own field, threshold and entry count (greedy per contest, then the night-level search), so there is no shared pool assigned in CSV order; the assignment problem B describes is solved implicitly. Reuse across single-entry contests is Decision D5, which stands. Adding a matching step would add code without moving either goal.
- **Change:** none.

### 31. B-D-05: implied-minutes back-solver from free bookmaker player props

- **Raised by:** B.
- **Verdict:** Accept. **After MVP**, conditional on a permitted props source and the credit budget.
- **Severity (mine):** Moderate for Goal 1 (minutes are where NBA slates are decided).
- **Why:** Back-solving market-implied minutes from prop ladders and a shrunk per-minute rate is a cheap, well-founded prior, and the researcher should be told when the market disagrees with our depth chart by 4 or more minutes. The Odds API serves props on the free tier per event (VERIFIED V12), so the engine spends credits on the largest slates first; ESPN's ladders are available only if Decision D1 widens the posture. Cost: credits. Workload: none.
- **Change:** ARCHITECTURE section 4 (market anchor), section 10 (props row); ADR-016 amended. Build plan: C21.

### 32. X-01: the build calendar has already changed

- **Raised by:** me.
- **Verdict:** Accept. Now.
- **Why:** The design's Phase 1 schedule started building on Oct 14 and rehearsing that night. Today is Oct 14 and this session plans; the first build session starts after your approval. Live rehearsal nights left: Thursday Oct 15 (2 games) and Friday Oct 16 (12 games) (VERIFIED V10). So the first valid upload from real files must happen on Oct 15 or Oct 16, the optimizer rehearsal on Oct 16 or on saved Oct 16 files, and the "rehearse after the last substantive change" rule (entry 3) can only be met by a replay drill on saved files over Oct 17 to 19. The plan is built on that calendar, with the Baseline as the floor if the optimizer chunks slip.
- **Change:** BUILD_PLAN.md milestones; ARCHITECTURE section 13 pointer; section 8 opening-night table.

### 33. X-02: a manual confirmed-starters command

- **Raised by:** me (prompted by V7).
- **Verdict:** Accept. **Before MVP.**
- **Why:** No permitted automated source gives confirmed starters before tip in any posture, but you can read a lineups page in your own browser, which no terms forbid. `dfs start "Team: A, B, C, D, E"` records the confirmed five for a team as a fact record with you as the source and runs the re-solve; `dfs out` and `dfs in` already exist. Workload: about 30 seconds per game you choose to confirm, typically the one or two games with real uncertainty.
- **Change:** ARCHITECTURE section 3 (Component 22), section 8, section 10 (confirmed starters row). Build plan: C10.

### 34. X-03: no advisor tool in this session; how the advisor is consulted

- **Raised by:** me.
- **Verdict:** Accept. Now.
- **Why:** This session exposes no advisor tool (VERIFIED V17). The consultation required by the prompt is run as an independent Fable-model agent that reads the register cold and is asked for an unanchored read on the contested rulings; the log records that mechanism. Build sessions use `/advisor` where it is configured and the same independent-reviewer fallback where it is not.
- **Change:** `docs/research/advisor-log.md`; `CLAUDE.md` session protocol.

### 35. X-04: the original brief with the advisor section was never saved

- **Raised by:** me.
- **Verdict:** Accept. Now.
- **Why:** `NBA_DFS_Architecture_Prompt.md` is not on disk; `docs/brief/2026-10-13-architecture-brief.md` is the saved brief and both critics note it lacks the advisor section. `docs/BRIEF.md` is built from the saved brief, the goals and constraints restated in the adjudication prompt, and the advisor section as the critiques quote it, then edited by these rulings. If you still have the original prompt, paste it into the repo and the next session reconciles it.
- **Change:** `docs/BRIEF.md` created with a provenance note.

### 36. X-05: the build itself needs a usage budget per chunk

- **Raised by:** me (the design had a build-week rule written for a single continuous build).
- **Verdict:** Accept. Now.
- **Why:** Eleven MVP chunks in five days on a Pro plan plus a Team seat share the weekly window with opening night. Each chunk records usage at its end in PROGRESS.md; if the MVP's first four chunks use more than about 40% of a weekly window, the plan's "Baseline only" branch is taken and the optimizer chunks move after opening night.
- **Change:** BUILD_PLAN.md budget section; `CLAUDE.md` protocol; PROGRESS.md fields.

### 37. X-06: real NBA DraftKings files are needed on day one

- **Raised by:** me.
- **Verdict:** Accept. Now.
- **Why:** The chunked build tests every parser and the validator on fixtures, and the only real 2026-27 NBA files are the ones you export. Before chunk C02 runs, the engine needs: one Classic entries file and one Showdown entries file from a preseason slate with at least one $0.25 entry each, the matching salary exports, and, after the first lock, a re-downloaded entries file showing `(LOCKED)` cells. Decision D8's test entries are what make these exist.
- **Change:** BUILD_PLAN.md "What you provide and when".

### 38. X-07 (from the advisor's read): a Floor release state, an operational definition of "sensible", honest washout wording in the MVP brief, archiving from the first rehearsal

- **Raised by:** the advisor consultation.
- **Verdict:** Accept. **Before MVP.**
- **Why:** Four gaps in my own MVP definition. (1) The Baseline as first written was about a week of work with nothing named beneath it; the **Floor** (entry 3) is the Oct 15 target. (2) "Sensible" had no operational test, so validity was the Baseline's only acceptance criterion; the Floor and Baseline now pass a deterministic sanity check per slate: at least 95% of the cap used on average, no two identical lineups in one contest, the concentration cap honored or its relaxation reported, no lineup below a projection floor (a setting, default 85% of the slate's best single-lineup projection), and no player with `p_active` under 0.5 in any lineup unless you asked for him. (3) The Floor brief prints "Goal 2 not estimated" and shows unfilled entries and per-game concentration; the Baseline brief prints Goal 2 as a labeled model estimate with its assumptions beside it (payout-fact status per contest, field settings, "uncalibrated"), never as a bare number, until the calibration checks in entry 6 pass. (4) Every raw download and pre-lock snapshot (DraftKings files, injury reports, lines, props, projection pages) is archived from Oct 15 onward, so week 1 is learnable even though the results parser comes later. (5) The LLM news researcher is a flagged capability that may ship off; with three games and perhaps ten facts, `dfs out`, `dfs in` and `dfs start` are the rehearsed path.
- **Change:** ARCHITECTURE section 1 (release states), section 6 (sanity check), section 8 (brief wording), section 10 (archiving); ADR-023. Build plan: C04 (Floor and sanity check), C08 (brief wording), C02 (archiving), C11 (researcher flag).

### 39. X-08 (from the advisor's read): nobody asked whether the two rehearsal nights are possible

- **Raised by:** the advisor consultation.
- **Verdict:** Accept. Asked in the owner batch at the end of Stage 1. **Answered 2026-10-14: yes to Thursday Oct 15 evening, Friday Oct 16 evening, and Tuesday Oct 20 from 12:30 to 2:00 pm CT.**
- **Why:** The calendar (entry 32) and the fixtures (entry 37) rest on you being at the laptop on Thursday Oct 15 and Friday Oct 16 evenings with one $0.25 Classic and one $0.25 Showdown entry each night. With all three windows confirmed, the Floor is rehearsed live on Oct 15 and at scale on Oct 16, the Baseline runs live on Oct 19 evening with the Floor underneath, and opening night has its game-day research pass.
- **Change:** BUILD_PLAN.md calendar; Decision D7 and D8 recorded as answered.

---

## Escalation answers

Given by the owner on 2026-10-14 through the batched question.

| Question | Answer | Applied |
|---|---|---|
| Goal 1 (B-I-01) | Replace Goal 1 with top-1% prize equity in dollars (Critique B's proposal) | Entry 5; BRIEF.md; ARCHITECTURE section 2; ADR-024 |
| Goal 2 (B-I-02) | Replace Goal 2 with severe drawdown: winnings under 25% of fees | Entry 9; BRIEF.md; ARCHITECTURE section 2; ADR-025 |
| Data posture (D1) | Permissive plus `nba_api` for box scores and game logs only (the recommendation) | Entry 14; ADR-005; ARCHITECTURE section 10 |
| Availability | Thursday Oct 15 evening, Friday Oct 16 evening, Tuesday Oct 20 12:30 to 2:00 pm CT, all yes | Entry 39; BUILD_PLAN.md calendar; D7 and D8 |

Not yet answered: whether "QA runs at most three iterations" in the original vision was a requirement (entry 18). The ruling proceeds on the reading that the vision section was a starting hypothesis, as the brief itself says.


## Advisor consultation

Logged in full in `docs/research/advisor-log.md` (consultation 1, 2026-10-14). Mechanism: no advisor tool is exposed in this session, so an independent Fable-model agent read the register cold, with ARCHITECTURE sections 2, 6 and 8 and the two critiques, and was asked for an unanchored read of entries 3, 5, 8, 9, 10, 12, 14, 17, 18, 19 and the MVP scope.

| Entry | Advisor | Taken? |
|---|---|---|
| 3 | Adjust: add a Floor release state rehearsed Oct 15; Baseline rehearsed Oct 16 | Yes (entries 3 and 38) |
| 5 | Agree | |
| 8 | Adjust: the pre-freeze trigger as first written would freeze nearly everything; label frozen after the search instead | Yes |
| 9 | Agree | |
| 10 | Agree, with the timing caveat and a named fallback (legal repair) | Yes |
| 12 | Agree; add the supersession rule for facts | Yes |
| 14 | Adjust: state that `nba_api` becomes the de facto in-season box-score source and that the public-view consensus path cannot be rehearsed | Yes |
| 17 | Adjust: swap writes an entry only on a news change or a threshold improvement; re-check concentration | Yes |
| 18 | Agree; the owner should confirm "three iterations" was a hypothesis | Asked |
| 19 | Adjust: re-download before each Showdown lock and the Classic first lock | Yes |
| MVP scope | The researcher may ship off; define "sensible"; print "washout not estimated"; archive from Oct 15 | Yes (entry 38) |
| Riskiest ruling | Entry 10, on timing evidence from the discarded spike; Drill B and the Oct 19 live run decide | Recorded in entry 10 and the build plan |
| Gap | Rehearsal-night availability and test entries were never asked | Yes (entry 39) |
