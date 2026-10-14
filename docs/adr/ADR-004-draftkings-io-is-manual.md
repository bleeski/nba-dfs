# ADR-004: Every DraftKings interaction is manual

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entries 1 and 19): the salary export is optional because the entries file carries the player pool; rehearsal 1 records whether the 2026-27 NBA export has `Status` or `Starting`. The payout paste is recommended for every new contest in week 1 because both goals now run on money (ADR-024, ADR-025); contests are classified by type from their name with type-specific paid-share defaults, and every contest carries a `facts_status` (verified, template, default) that the brief shows. One flagship standings zip per slate is the required morning download; other contests' zips are optional. An upload is committed on the owner's read-back (ADR-026).

## Context

The engine needs four things from DraftKings each night: the player pool with IDs, our entries, contest details (field size, payouts), and next-day standings. The brief already rules out automating actions on the DraftKings site. Research found DraftKings' Daily Fantasy Terms of Use (updated 06/30/2026) go further: improper conduct includes using automated means "to obtain, collect or access any information on the Website", and the penalty can include disqualification and forfeited prizes (R6, section 3.2, VERIFIED). Public JSON endpoints exist (lobby, contest detail, draftables), but reading them by script fits that wording.

## Options considered

1. **Read DraftKings JSON by script** (lobby, contest detail, draftables). Exact field sizes and payouts at zero user effort. Puts the user's real-money account at risk.
2. **Ask DraftKings for written permission** for a few read-only requests per night. Unknown answer and timeline.
3. **Manual files only.** The user downloads entries files and standings, and optionally pastes payout tables. The engine estimates what it lacks.

## Decision

Option 3. All DraftKings data enters through an `inbox/` folder the user fills by hand:

- `inbox/entries/` one DKEntries CSV per slate (required). It already contains that slate's full player list with IDs, salaries, and eligibility (R6, VERIFIED 158 of 158 IDs match the salary file).
- `inbox/salaries/` DKSalaries CSV (optional; the only source of the `Status` column).
- `inbox/payouts/<contestId>.txt` pasted payout table (optional, about 45 seconds per new contest).
- `inbox/standings/` next-day standings zips (needed for learning).
- `inbox/history/` DraftKings entry-history export (optional, weekly; gives exact field size and places paid after the fact, R8).

Without a payout paste, the engine estimates field size as prize pool / (fee x 0.85) and uses the paid-share default for the contest class (about 23%, VERIFIED on the user's 394 past NBA Classic entries, R8). Claude Code's settings deny web fetches to `draftkings.com` so no agent can reach the site by accident.

Option 2 stays open: if the user ever gets written permission, a contest-detail adapter can be added without changing anything else.

## Consequences

- **Results:** field size and payout depth are estimates on nights without pastes; estimation error is small for big GPPs (rake is a steady 15 to 16%) and largest for small contests, where a paste matters most.
- **Cost:** none.
- **Workload:** the DraftKings file handling itself (entries and salary downloads per slate, uploads, re-downloads, payout pastes for new contests, next-morning standings) is most of the user's 30 to 45 minutes a night (ARCHITECTURE section 8); auto-filing from Downloads removes the filing step. Recurring contests are cached by name, fee, and size, so pastes shrink after the first week.
