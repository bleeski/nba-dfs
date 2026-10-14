# ADR-005: A source layer with a data-posture switch; permissive by default

**Status:** Accepted; Decision D1 answered by the owner on 2026-10-14. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entry 14; Decision D1 answered): the owner chose **permissive plus `nba_api` for box scores and game logs only** (about five requests a night). Because the sportsdataverse file was last updated September 9, `nba_api` is the de facto source of current-season box scores from opening week unless the volunteer job resumes. ESPN JSON stays off. No permitted automated source gives confirmed starters before tip in any posture (ADJUDICATION V7), so `dfs start` records them from the owner's own browser (ADR-026). "Verified source" means the chosen local path returned current data that parsed and passed freshness checks; documentation-only and historical probes carry separate labels; every required input names its fallback. The public view never falls back to our private baseline (ADR-008). Every raw download and pre-lock snapshot is archived from Oct 15.

## Context

The brief requires free data only and asks that any source whose terms prohibit our use be flagged. R4 verified from this laptop that a complete free stack works technically, and found that most of it is restricted: NBA.com's terms say "the NBA Statistics may not be used in connection with any fantasy game"; ESPN (Disney terms) bars access by "robot, spider, script, or other automated means"; RotoWire, Basketball Monster, Action Network, PrizePicks, Underdog, Pinnacle, Caesars and Bovada ban bots or scraping (all VERIFIED quotes). Permissive or silent: The Odds API (free key; use in your own app allowed), the official injury report PDF (no bot clause), Daily Fantasy Fuel (silent), Bluesky's public API, sportsdataverse files (CC BY 4.0, ESPN-derived). Several hosts block scripts technically (cdn.nba.com, sportsbooks, PrizePicks).

## Options considered

1. **Wider personal-use posture:** use everything reachable at low volume. Best data; literal breach of several terms.
2. **Permissive posture:** only sources whose terms allow this use, plus the user's manual DraftKings files.
3. **Hard-code one posture.** Simpler, but turns a product decision into a code change.

## Decision

A source layer where every adapter declares its terms status, and a `posture` setting selects which adapters may run. Default: **permissive**:

- History and priors: sportsdataverse ESPN box scores and play-by-play (bulk files, no load on NBA or ESPN servers).
- Status and starters: the official injury report (every 15 minutes, or an hourly file early in the season); DraftKings' `Status` and `Starting` columns from each salary export the user downloads (manual; BET for NBA until the first export); news the user sees first, entered with `dfs out` or `dfs in`.
- Lines and props: The Odds API free key (lines twice daily, about 180 of 500 monthly credits; props on about 7 nights a month at about 40 credits per 10-game night, prioritizing big slates; the engine reads the remaining-credit header and keeps a reserve).
- Public projections for the field's view: Daily Fantasy Fuel's free CSV.
- News: Bluesky public API and the LLM researcher's web searches.
- Never, in any posture: anything that defeats a technical block (bot protection, CAPTCHA, app keys), and anything on DraftKings.

### The two terms bets inside the permissive posture (stated plainly, per red-team round 1, RT1 rank 12)

1. The official injury report has no bot clause, but NBA.com's Section 9 bars using "the NBA Statistics" with any fantasy game; whether statuses count as statistics is a BET.
2. sportsdataverse files are CC BY 4.0, but the underlying box scores are ESPN's, whose terms ban automated access; whether that reaches republished data is a BET.

The user accepts or rejects each (Decision D1). If either is rejected, the engine runs without it.

### Other details

- The researcher fetches pages only through `dfs research fetch`, which enforces an allowlist by domain (official.nba.com; nba.com team and league news; Bluesky posts through the public API) and saves each page for the quote check. ESPN, RotoWire and paywalled news sites are never fetched, because their terms ban automated access.
- DraftKings `Status` and `Starting` are BET for NBA until the user's first NBA salary export (they appear in 2026 exports for other sports).
- `nba_api` can be approved by the user as a backup history source if sportsdataverse's daily job stalls.

## Consequences

- **Results:** opening-night projections rest on last season's box scores, market lines, and official statuses; the permissive posture gives up nightly props on about half the nights and richer play-by-play detail.
- **Cost:** free; the user creates a free The Odds API key (about 2 minutes, on Oct 14).
- **Workload:** none beyond the manual DraftKings downloads; occasionally a manual Daily Fantasy Fuel CSV download.
- **Not legal advice:** both bets are judgment calls the user makes.
