# Advisor log

One entry per consultation. Each names the decision, what was asked, what came back, and what was taken. The advisor is consulted for consequential, unresolved decisions only: during design and adjudication, in build sessions when a chunk is stuck and once before it is declared done, and in the weekly results review. It is never called inside a nightly run (`/night`, `/news`, `/swap`, `/results`). One call per decision; if the advisor is unavailable, the deterministic path continues (ADJUDICATION entry 15).

**Mechanism note.** When a session exposes the Claude Code advisor (`/advisor fable`), that is the advisor. When it does not (as in the adjudication session on 2026-10-14, where no advisor tool was exposed), the consultation is an independent Fable-model agent that reads the material cold and is asked for an unanchored read. Either way the result is logged here.

---

## Consultation 1: adjudication rulings (2026-10-14)

**Decision:** whether the contested or high-impact rulings in `docs/review/ADJUDICATION.md` should stand before the owner is asked the escalations.

**Mechanism:** independent Fable-model agent (no advisor tool in the session). It read ADJUDICATION.md in full, ARCHITECTURE.md sections 2, 6 and 8, and the two critiques; it did not read the research memos or spikes. It was asked to agree, disagree or adjust entries 3, 5, 8, 9, 10, 12, 14, 17, 18, 19 and the MVP scope, then to answer: what is missing or unneeded in the MVP; which ruling is most likely wrong and what would show it; what gap nobody caught.

**What came back (condensed, the advisor's words where quoted):**

- **Entry 3, adjust.** The Baseline as defined is about a week of work with nothing named beneath it. "Add a third state, Floor: parser, validator, exporter, projection-ranked injury-scrubbed lineups under the concentration cap, no simulation, rehearsed with a real upload on Oct 15; Baseline is rehearsed on Oct 16."
- **Entry 5, agree.** The escalation is correct and the bounded dollar tie-breaker captures B's first-place point without changing the objective. B's NHL evidence (0 of 135 top-1%) indicts that engine's projections, not the coverage objective.
- **Entry 8, adjust.** The freeze trigger as first written ("2 x SE_paired(any single swap) > epsilon x G1*") is ill-defined: every contest has some high-variance swap, so it would freeze nearly everything and reproduce the spike's bug by another route. "Replace with: no pre-freeze; a contest is labeled frozen when no candidate swap satisfied the constraint, and the brief names those contests."
- **Entry 9, agree.** B's $0.25 example argues for a diagnostic, not for redefining a goal before any real night has been played.
- **Entry 10, agree with an addition.** The 44-second figure comes from the spike that entry 16 discards as a statistical oracle, so the 3-minute budget is unmeasured for the rewritten engine and must be timed on the Oct 16 slate. "Name the fallback when the re-solve misses budget or crashes: the validator's legal repair (remove the OUT player, insert the cheapest legal substitute by projection), exported in seconds."
- **Entry 12, agree.** Add that a later fact about the same player supersedes an earlier one, so Monday's day-before report cannot outlive Tuesday's game-day report when overrides are reused.
- **Entry 14, adjust.** State two implicit consequences: the `nba_api` backup trigger (sportsdataverse lagging over 24 hours) is already met (last update Sept 9), so under the recommended answer `nba_api` is the de facto source of current-season box scores from opening week; and Daily Fantasy Fuel had no preseason projections, so the consensus path cannot be rehearsed and the opening-night public view is the deterministic formula unless a file parses in a dry run first.
- **Entry 17, adjust.** A per-entry re-optimizer on perturbed objectives "drifts every entry toward the same beneficiary and rewrites entries that had no reason to change", concentrating exposure and producing an unreadable diff on every lock wave. "Swap writes an entry only when a news fact changed since its last file or the open-slot change clears a stated improvement threshold; the concentration cap is re-checked on the post-swap portfolio; everything else stays as uploaded."
- **Entry 18, agree.** The owner should confirm that "up to three iterations" was a hypothesis, since the adjudicator reinterpreted the owner's own text.
- **Entry 19, adjust.** A wrong-file upload read back as "N of N" is invisible until the pre-swap re-download, and a Showdown has no swap and no second lock. "Change to: once before each Showdown's lock and before the main Classic's first lock."
- **MVP scope, adjust.** Not needed as a required capability: the LLM researcher (three games, perhaps ten facts; the manual commands are the rehearsed path; it can only be rehearsed on live news). Missing: a named Floor; an operational definition of "sensible"; a rule that the MVP brief prints "washout not estimated" and shows concentration and unfilled entries instead of a near-zero number from uncalibrated layers; archiving every raw download and pre-lock snapshot from Oct 15 onward.
- **Riskiest ruling: entry 10.** It makes the live re-solve the only late-news path on timing evidence from discarded code, in a rewrite, where a Showdown gets no second chance. Evidence it is wrong: detection-to-confirmed-upload exceeding the window at T-30, T-10 or T-2 on Oct 16, or any crash during the drill. If so, the legal repair is the rehearsed late-news path for opening night and the re-solve ships flagged off.
- **Gap nobody caught:** whether the owner will be at the laptop on Oct 15 and Oct 16 evenings, and whether $0.25 Classic and Showdown entries exist for those slates. "If the answer is no for either night, the calendar collapses to replay drills on files that do not exist."

**What was taken:** every adjustment, verbatim in substance (ADJUDICATION entries 3, 8, 10, 12, 14, 17, 19, and new entries 38 and 39). The two "confirm with the owner" items (QA iterations; rehearsal-night availability) went into the owner's question batch.

**Usage:** one agent run, about 141,000 tokens, 13 tool uses, under 5 minutes.

---

## Consultation 2: the build plan (2026-10-14)

**Decision:** whether `docs/build/BUILD_PLAN.md`, `CONTRACTS.md` and chunks C01 to C22 are ready for the owner's approval.

**Mechanism:** independent Fable-model agent (no advisor tool in the session). It read BUILD_PLAN.md, CONTRACTS.md, C01 to C11 in full, C12 to C22 for ordering, CLAUDE.md, the run-chunk command and PROGRESS.md, and answered eight questions.

**What came back (condensed):**

1. **Sizing.** Reachable at three sessions a day, but the plan must say who starts the daytime Thursday sessions and which seat runs them. C04 is the likeliest overrun (three ported parsers, the solver, the cap test, the sanity check, the Floor command, brief-lite, a timing test); cut the payout-paste parser and facts cache first, then the injury adapter. C11 is an L mislabeled M.
2. **Reading lists.** C06 cited a 63 KB Odds API dump (about 15,700 tokens) for two endpoints and one header; replace with three lines. C01 would read the 95 KB spike to serialize the synthetic night; move that fixture to its first consumer.
3. **Order.** "Nothing builds a way to run a past night": every weekend drill runs on saved Oct 16 files, but locks would be in the past and the started-game and insufficient-time rules would drop every row. Add a saved-night mode (`--night`, `--as-of`) to C03. The C05 parallel claim is false (shared `cli.py`, settings, `pyproject.toml`, `PROGRESS.md`); run it sequentially. One solver owner, not two ports.
4. **M1.** Valid, yes; "sensible" and "injury-scrubbed" are weaker on Oct 15 (no preseason injury reports; last-season minutes). Unguarded: a 2-game Thursday may have no Classic slate; `dfs repair` cannot fill a reserved blank entry; a 5:00 pm parser failure leaves no fix time. Cheap guard: hand-build the test lineups in the browser so a validate-and-export round trip exists even without the Floor.
5. **Contracts.** Sufficient; the weakest is `lineup_hash` (undefined; two chunks could hash differently and duplicate detection would silently return zero). Also `settlement_fn` has no signature and `cdf_grid` does not say what Q indexes.
6. **Owner checks.** Most are recognizable. C06's check ruled out a real player on a live night without restoring him; C10's swap check could not point at the Oct 15 file; the launcher drill had the same gap; `dfs history status` and `dfs digest` were not stubbed.
7. **Fallback.** The flag-off late-news path was unspecified (Floor rebuild versus repair). What the owner runs at 1:15 pm on Oct 20 if news breaks and the re-solve is off: `uv run dfs out "Name" --no-run`, `uv run dfs repair --slate <slate>`, upload in the browser, `uv run dfs uploaded <file>`, `uv run dfs status`; rehearse it in Drill B on a Baseline file and put it on the "engine is down" card; make `dfs out` run the repair whenever `resolve` is off.
8. **Change before approval:** the saved-night mode. **Do not change:** the Floor-first rule (upload and commit the Floor every night, replace it only when the Baseline passes the sanity check and the drill bar), even to save ten minutes.

**What was taken:** all eight. Saved-night mode added to CONTRACTS 1.1 and C03 and used by every drill; `lineup_hash`, `settlement_fn` and `cdf_grid` defined; C05 sequential and the whole plan declared non-parallel (the independent verifier found every chunk shares `cli.py` and `CONTRACTS.md`); C04 re-ordered with M1 first and the solver port owned there; C11 relabeled L; the Odds API facts inlined in C06; the synthetic fixture moved to C07; the flag-off path defined as the repair in CONTRACTS 4.4, ADR-026, ARCHITECTURE and C04, C06, C10; the five fallback lines on the "engine is down" card and in Drill B; the Oct 15 guards (lobby check, hand-built lineups, Wednesday-night exports) in the calendar; the Team seat for build sessions and the Pro plan for rehearsals; the missing CLI stubs added.

**Usage:** one agent run, about 159,000 tokens, 18 tool uses, under 6 minutes.

## Consultation 3: round 2 stop-the-line rulings and contract changes (2026-10-14)

**Decision:** whether the proposed rulings on the round 2 stop-the-line items (A-R2-I-01, I-02, I-03, I-05; B-R2-I-01, I-02, I-04) and the contract-changing rulings (A-R2-I-04, I-06, I-07, I-08, I-09, D-01 to D-04) should stand before the full register is written.

**Mechanism:** the Claude Code advisor tool (`/advisor fable`), live in this session. It received the whole conversation: both round 2 reviews, the build documents read so far, the verification runs V-R2-1 to V-R2-9, and the working draft of `docs/review/ADJUDICATION-R2.md`. This is the first consultation that used the real advisor rather than a stand-in agent (round 1 X-03).

**Asked:** (1) is the C04 and C11 split the right fix for the Floor-only route, and is the calendar realistic; (2) is deleting the additive mode and dropping the 63% claim except for first-place-only contests correct, and is exact greedy affordable; (3) is one joint realization per scenario enough for Goal 2; (4) is turning the eight-minute drop into a label consistent with the owner's constraints; (5) what is wrong or missing.

**What came back (condensed):**

1. The split is right; change the dependencies. C11a depends on C04a only; `dfs status --apply` moves into C04b (which owns the injury adapter); on Friday run C11a first, then C04b, which may slip to Saturday. Do not schedule C10 for Monday: hard cut on Sunday evening, after which C10 moves past opening night and the repair is the late-news path. C11b goes after opening night outright. Measure the usage trigger at M1 (C01 to C04a).
2. Correct. State the condition exactly: the greedy bound holds when the payout curve extended with its drop to zero at k+1 is convex, which in practice means k = 1 (fields under 200). Exact incremental updates work because adding an entry changes another candidate's gain only in scenarios where the added entry finishes in the top 1%. C09 measures the runtime; lazy greedy is the labeled fallback. Record the false fact under the round 1 exception (V16, entry 7).
3. One realization is enough, but drawing opponent counts between our sorted scores re-randomizes every draw when the portfolio changes and breaks C12's paired standard error. Use a portfolio-independent realization: per (scenario, contest), draw opponent counts top-down on a fixed score lattice, each bin keyed by (seed, set, scenario, contest, bin); copies keyed by `lineup_hash`. Contract test: two portfolios that differ by one entry give every unchanged entry the same realized rank apart from the swapped entry's push.
4. Consistent. "Lock uncertainty" means an unresolved lock time, which still stops an edit. The validator treats a cell as locked when it shows `(LOCKED)` or its game has started by the clock. Update C10's `--at 2` expectation.
5. Misses: the slate key and validator rely on a draft group ID the entries file does not contain (R6 line 132), so define the slate by a fingerprint; identity collisions must not stop ingest (disambiguate, disable the history join, require pick-by-number, warn); Thursday scope is piling up, so keep drill isolation and the basic temp-file-then-rename write in C03 and move the slot-reassignment repair and the extra interrupted-write tests to C11a. Process: reversals of ADR-024, ADR-025 and ADR-026 get new decision records; ADR-007 and ADR-008 bullet fixes are edits; mark B-R2-I-02 closed in round 1 rather than spending the owner's question on it; keep the field-tail contract to the interface with C08 free to ship first place labeled "tail unfitted"; add the new tiny fixtures and settings keys to CONTRACTS so C01 builds from it alone; simulate the Floor-only branch in the scripted gate.

**What was taken:** all of it. See `docs/review/ADJUDICATION-R2.md` entries 1, 2, 4, 5, 6, 8, 9, 15, 17, 26 and X-R2-03.

## Consultation 4: the owner's real DraftKings files of Oct 14 (2026-10-14)

**Decision:** what the owner's four real files (one $0.25 Classic entry on the 7-game slate, one $0.25 Showdown entry on DEN@LAC, both salary files) change in the plan, and whether the public repository changes the fixture plan.

**Mechanism:** the advisor tool, live in this session. It saw the analysis outputs (V-R2-12 to V-R2-19 in `docs/review/ADJUDICATION-R2.md`) and the draft proposal.

**What came back (condensed):** (1) Tell the owner first: both entries are blank reservations, so a post-lock re-download would show no locked cells; fill the lineups before 6:30 pm CT (Classic mixing early games with at least two DEN@LAC players), re-download the Classic entries file between about 6:45 and 9:15 pm CT and the salary file about 15 minutes before the first tip. (2) Showdown: prune our candidates by availability and a projected-minutes floor with a cap C09 measures (22 and 26), labeled as searched over a subset; do not prune the field; sample the Showdown field by popularity with cap and both-teams rejection, like Classic. (3) Real-file tests that silently skip defeat the definition of done: fail with a message on this laptop, skip only behind an explicit flag; never commit the standings salt; this lands in C01, which runs tonight. (4) Read the newest salary file for a fingerprint, not "newer than the entries file"; map out codes explicitly; only truly unknown codes default to questionable. (5) Settle the triple-double rule now with the `AvgPointsPerGame` harness. (6) Ship the Floor on `AvgPointsPerGame` at C04a checkpoint 2 and move the history join and the self-check to checkpoint 3; keep the fallback order. (7) Repository visibility is the owner's setting: a recommendation, not an escalation; correct the "private repo" claims; the push stays authorized. (8) Record it as one entry, R2-33.

**What was taken:** all of it. The triple-double check ran (V-R2-17: both bonuses, 14 of 16 players). See ADJUDICATION-R2 entry R2-33.

## Consultation 5: final gate review of the complete design (2026-10-14)

**Decision:** whether the final state (both rounds of rulings, ARCHITECTURE v5.1, the contracts, the build plan, the chunks, the owner checklist) is consistent and whether C01 is safe to start.

**Mechanism:** the advisor tool, live in this session, after both final-gate audits' findings were fixed and `scripts/check_docs.py` passed (401 reading-list references resolved).

**What came back (condensed):** C01 is safe to start once two blocking fixes land; the rest is coherent and needs no second round. (1) C01 is oversized for an M chunk (the contracts alone are about 33,000 tokens, plus `lineup_hash`, the fixture builder, the `realfiles` marker and twelve hand-written fixtures): drop `scripts/check_docs.py` from its reading list, relabel it L, and let the tiny fixtures move to the start of C08 if it runs long, keeping the fixture builder C02 needs in C01. (2) Define a degenerate tiny field exactly (`p_above` and `p_equal` 0 or 1 at every score our entries take; ten opponents with three above is a binomial case, not rank 4); compute binomial hand values with a standalone script that does not import the engine; have the settings test skip the `[field.<family>]` placeholder. (3) Drill mode runs only built capabilities regardless of their flags; a stub falls back as in live mode. (4) Trace every "final audit" changelog line to entry R2-34. (5) Update the ADR index rows for the records that gained round 2 markers. Optional: a Monday line for a capability left stale by a parser fix. Then commit, annotated tag `design-final`, push `master` and the tag, checking that nothing under `data/` or `fixtures/` and no secret or salt is staged. Open risks for the summary: Thursday's load, the untested Showdown subset size, the first-place tail fit, the re-solve budget, whether `Starting` fills near tip, and the public repository.

**What was taken:** all of it, including the optional line.
