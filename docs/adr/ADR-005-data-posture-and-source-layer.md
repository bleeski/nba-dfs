# ADR-005: A source layer with a data-posture switch; permissive by default

**Status:** Proposed; the posture itself is the user's call (Decision D1). **Date:** 2026-10-13.

## Context

The brief requires free data only and asks that any source whose terms prohibit our use be flagged. R4 verified from this laptop that a complete free stack works technically, and found that most of it is restricted: NBA.com's terms say "the NBA Statistics may not be used in connection with any fantasy game"; ESPN (Disney terms) bars access by "robot, spider, script, or other automated means"; RotoWire, Basketball Monster, Action Network, PrizePicks, Underdog, Pinnacle, Caesars and Bovada ban bots or scraping (all VERIFIED quotes). Permissive or silent: The Odds API (free key; use in your own app allowed), the official injury report PDF (no bot clause), Daily Fantasy Fuel (silent), Bluesky's public API, sportsdataverse files (CC BY 4.0, ESPN-derived). Several hosts block scripts technically (cdn.nba.com, sportsbooks, PrizePicks).

## Options considered

1. **Wider personal-use posture:** use everything reachable at low volume. Best data; literal breach of several terms.
2. **Permissive posture:** only sources whose terms allow this use, plus the user's manual DraftKings files.
3. **Hard-code one posture.** Simpler, but turns a product decision into a code change.

## Decision

A source layer where every adapter declares its terms status, and a `posture` setting selects which adapters may run. Default: **permissive**:

- History and priors: sportsdataverse ESPN box scores and play-by-play (bulk files, no load on NBA or ESPN servers).
- Status and starters: the official injury report every 15 minutes; DraftKings' `Status` and `Starting` columns from the user's salary re-export near lock (manual).
- Lines and props: The Odds API free key (lines twice daily; props on about 12 nights a month, prioritizing big slates).
- Public projections for the field's view: Daily Fantasy Fuel's free CSV.
- News: Bluesky public API and the LLM researcher's web searches.
- Never, in any posture: anything that defeats a technical block (bot protection, CAPTCHA, app keys), and anything on DraftKings.

## Consequences

- **Results:** opening-night projections rest on last season's box scores, market lines, and official statuses, which covers the essentials; the permissive posture gives up nightly props on about half the nights and richer play-by-play detail.
- **Cost:** free; the user signs up for a free The Odds API key (one-time, about 2 minutes).
- **Workload:** the near-lock salary re-export (about 1 minute per lock wave) replaces a scraped lineups feed.
- **Flagged uncertainty:** whether NBA.com's fantasy clause covers injury statuses, and whether ESPN's terms reach data republished under CC BY 4.0, are BETs, not legal advice.
