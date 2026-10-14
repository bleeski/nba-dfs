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
