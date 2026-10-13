# R4: Free NBA data sources, verified from this machine

Status: research memo for design review (no engine code).
Written: Tuesday 2026-10-13, NBA preseason, one week before opening night, on the user's Windows 11 laptop over its home internet connection.
Evidence: every VERIFIED claim names a throwaway script in `spikes\data\` and its output in `spikes\data\out\`. Saved copies of terms pages are in `spikes\data\out\downloads\terms\`.

Labels used throughout:

* **VERIFIED**: I ran it on this laptop today and got real data back (or, for a terms quote, I matched it word for word against a saved copy of the page).
* **SUPPORTED**: credible documentation says so, or a research helper read it on a page I could not fetch myself. Not observed directly.
* **BET**: my judgment, or something I could not test today.

Jargon, defined once: an **endpoint** is one web address that returns data. **JSON** is the structured text format most of these return. A **slate** is the set of games in one DraftKings contest. A **prop** (player proposition) is a betting line on one player's stat. A **rate limit** is the most requests a site allows in a period. **Terms** means a site's Terms of Use. **robots.txt** is a small public file in which a site says which paths automated programs should not visit. **Lock** is the moment a DraftKings contest closes to changes.

---

## 1. The answer first

**1a. Technically, a complete free stack exists, and most of it answered from this laptop today.**

1. **stats.nba.com through the `nba_api` package**: schedule, box scores, play-by-play, rosters, lineups, history back to 1996-97. VERIFIED: 14 of 15 endpoints worked, most in under half a second.
2. **The NBA's official injury report PDF**: published every 15 minutes in the regular season, each file live about 4 seconds after its time slot. VERIFIED on archived reports; my parser produced clean rows. It does not exist in preseason.
3. **ESPN's public JSON**: DraftKings game lines, DraftKings player-prop ladders, injuries with news blurbs, depth charts, news, and historical lines back to 2014. VERIFIED.
4. **RotoWire's free NBA lineups page**: "Expected" and "Confirmed" starters with injury tags. VERIFIED reachable; tonight's timing is in section 4.9.
5. **sportsdataverse files on GitHub**: bulk ESPN box scores from 1994 and play-by-play from 2002, with no load on NBA servers. VERIFIED.

**1b. The terms finding is the headline, and it is broad.** Almost every free source either bans automated access or limits use to personal, non-commercial purposes:

* NBA.com Terms, Section 9 (dated July 13, 2026): "the NBA Statistics may not be used in connection with any fantasy game". VERIFIED word for word.
* ESPN (Disney Terms): no accessing the products "using a robot, spider, script, or other automated means". VERIFIED.
* RotoWire, Basketball Monster, Action Network, PrizePicks, Underdog, Pinnacle, Caesars (Nevada terms) and Bovada all ban bots or scraping in their terms (VERIFIED quotes in section 4). RotoWire has publicly sued a company for scraping its injury data (VERIFIED from its own statement page; that defendant was a commercial company, not a hobbyist).
* Two traps: ESPN's injury blurbs are RotoWire's text word for word (VERIFIED), so switching from RotoWire to ESPN does not escape RotoWire's content rights. And the sportsdataverse files carry a permissive license (CC BY 4.0), but that license cannot override ESPN's terms on the underlying data (BET, but a standard legal reading).

**Sources whose terms do not prohibit this use:** The Odds API (explicitly allows use in your own app; needs a free key the user signs up for), Bluesky's public read API (no login), Daily Fantasy Fuel (terms silent on scraping; free CSV button), pbpstats.com (no terms published, but its data comes from NBA.com), and the official injury PDF (NBA.com terms have no bot clause; whether Section 9's fantasy ban covers injury statuses rather than statistics is a BET).

**This is the user's decision, and I do not pick for them.** Two postures:

* **Strict posture** (only sources whose terms allow it): The Odds API for lines and a few prop nights a month, the official injury PDF, Daily Fantasy Fuel for salaries and projections, Bluesky for news, and history from sportsdataverse (with the ESPN caveat). It loses confirmed starting lineups (no free source with permissive terms provides them; Daily Fantasy Fuel may, BET), nightly ESPN props, and the richest box-score detail.
* **Low-volume personal-use posture** (the stack in 1a, a few hundred polite requests a night, nothing redistributed): best data, but in literal breach of several terms. BET: enforcement against one person's private, low-volume use is unlikely, but unlikely is not permitted.
* Also open (BET): whether entering paid DraftKings contests counts as "personal, non-commercial" use under these terms.

**1c. What failed or is off-limits from here (VERIFIED):** cdn.nba.com live JSON (bot protection blocks scripts), DraftKings Sportsbook JSON (blocked), Caesars (blocked), FanDuel and BetMGM (need keys embedded in their apps), PrizePicks (serves a CAPTCHA, a "prove you are human" check), Underdog (rejects old app versions), Reddit without login (blocked), NBA.com news RSS (blocked), and stats.nba.com GameRotation (server error). I did not try to get around any of these, and the design should not either.

**1d. Preseason is only partly representative.** Schedules, box scores, ESPN odds and injuries, and RotoWire lineups behave now as they will in the regular season. The official injury report, Pinnacle and Bovada lines, and most projection sites do not cover preseason, so their regular-season behavior is SUPPORTED or BET. The first chance to see the 2026-27 injury report is Monday Oct 19, because teams must file by 5 p.m. local time the day before a game.

---

## 2. Primary and fallback for each need

Primary and fallback below assume the low-volume personal-use posture; the "Strict option" column shows what remains if the user chooses the strict posture.

| Need | Primary | Fallback | Strict option | What it means |
|---|---|---|---|---|
| Schedule | stats.nba.com `ScheduleLeagueV2` (VERIFIED). Terms: NBA Section 9 | ESPN scoreboard by date (VERIFIED). Terms: Disney ban on bots | The Odds API events list (free, no quota cost, SUPPORTED) or sportsdataverse schedules | One request a day keeps the schedule current, including NBA Cup games added in December. |
| Box-score history | stats.nba.com `PlayerGameLogs` plus `BoxScore*V3` (VERIFIED). Terms: NBA Section 9 | sportsdataverse ESPN box-score parquet files (VERIFIED). Terms: CC BY 4.0, ESPN-derived | sportsdataverse files | A full season of player games is one request (26,651 rows in 0.4 s), so nightly updates take seconds. |
| Injuries and status | Official NBA injury report PDF (VERIFIED on archived reports). Terms: NBA, no bot clause | ESPN injuries JSON (VERIFIED). Terms: Disney ban; text is RotoWire's | Official PDF | The PDF is ground truth for Out, Doubtful, Questionable, Probable and Available, refreshed every 15 minutes. |
| Starting lineups | RotoWire lineups page, "Expected" then "Confirmed" (VERIFIED reachable). Terms: bans scraping | Basketball Monster lineups page (VERIFIED reachable). Terms: bans scraping | None confirmed (Daily Fantasy Fuel's "START" column, BET) | Starters are confirmed close to tip (timing in 4.9), so the engine must re-run in the final half hour. |
| Game lines (spread, total) | ESPN scoreboard and core odds, DraftKings lines with open and current (VERIFIED). Terms: Disney ban | The Odds API free key, 3 credits per pull (SUPPORTED; user must sign up). Terms: permits | The Odds API | Team totals for the projection model come free either way. |
| Player props | ESPN core `propBets`: DraftKings milestone ladders for points, rebounds, assists, threes (VERIFIED tonight). Terms: Disney ban | The Odds API free key: about 12 nights a month of props (SUPPORTED) | The Odds API, about 12 nights a month | Props are free only as same-day snapshots (ESPN deletes them after the game, VERIFIED), so archive a copy nightly from opening night. |
| Minutes and rotations | stats.nba.com `PlayByPlayV3` substitutions rebuilt into on-court stretches, plus box-score minutes (VERIFIED). Terms: NBA Section 9 | sportsdataverse ESPN play-by-play parquet (VERIFIED) | sportsdataverse files | The ready-made `GameRotation` endpoint is failing, so plan to compute rotations ourselves. |
| Priors (starting player ratings before data accumulates) | stats.nba.com season stats plus pbpstats.com possession data (VERIFIED). Terms: NBA Section 9; pbpstats silent | DARKO public ratings (VERIFIED page). Terms: no commercial use without permission | sportsdataverse history (compute our own) | Priors can be computed from free history; outside ratings are a cross-check, not a dependency. |
| Late news | ESPN injuries JSON (RotoWire blurbs, visible 0 to 18 minutes after the blurb's own timestamp, usually 5 to 12, VERIFIED on 10 updates tonight) plus the official PDF. Terms: Disney ban | RotoWire RSS, newest 5 items with minute timestamps (VERIFIED). Terms: RotoWire bans scraping (BET whether its RSS counts as an interface it offers) | Bluesky public API plus the official PDF | News that breaks 30 minutes before tip will usually reach the engine 5 to 20 minutes later through these free channels, so it can make lock most nights but not every night; X would be faster but is paid. |

---

## 3. Summary table

Evidence files are in `spikes\data\out\`; saved terms in `out\downloads\terms\`. "Terms" is the verdict for automated, private, fantasy-related use.

| Source | Provides | Cost | Access | Freshness | Terms | Verified (Y/N + evidence file) |
|---|---|---|---|---|---|---|
| stats.nba.com via nba_api | Schedule, game logs, box scores, PBP, rosters, lineups, on/off, play types, scoreboard | Free | `nba_api`, browser-like headers, no key | Last night's games present by afternoon; tonight in 4.9 | Restricts: no fantasy use; private non-commercial only | Y: `20261013-1632_nba_api.json`, `20261013-1635_nba_api_live_alternatives.json` |
| stats.nba.com GameRotation | Player on-court stints | Free | `stats/gamerotation` | n/a | as above | N: HTTP 500, `20261013-1636_gamerotation_raw.json` |
| cdn.nba.com JSON | Live scoreboard, box score, PBP, odds, schedule | Free | `cdn.nba.com/static/json/...` | Live | as NBA.com | N for scripts: Akamai 403, `20261013-1633_cdn_nba.json`; browser-only, `20261013-1636_cdn_nba_browser_context.json` |
| NBA official injury report | Official statuses and reasons, all games | Free | PDF, `ak-static.cms.nba.com/referee/injury/Injury-Report_<date>_<time>.pdf` | Every 15 min; file live about 4 s after slot | NBA terms, no bot clause | Y (archived): `20261013-1637_injury_cadence_probe*.json`, `20261013-1655_injury_pdf_parse_v3_*.json`. N for preseason (none exist) |
| ESPN site and core JSON | DK odds, injuries with blurbs, rosters, depth charts, news, props, historical lines | Free | `site.api.espn.com/...`, `sports.core.api.espn.com/...` | Injuries within minutes; cache 1 to 900 s | Prohibits bots and commercial use | Y: `20261013-1640_espn.json`, `20261013-1641_espn_props.json`, `20261013-1651_history_sources.json`, `20261013-1657_espn_vs_rotowire_text.json` |
| The Odds API | Lines and props, many US books | Free tier, 500 credits a month | REST API with key (user signs up) | Near real time | Permits (no resale of raw data) | N: docs only; `oddsapi_*.txt` |
| DraftKings Sportsbook JSON | Lines, props | Free | `sportsbook-nash.draftkings.com/api/...` | Live | Personal non-commercial only (SUPPORTED) | N: Akamai 403, `20261013-1648_sportsbooks_props.json` |
| FanDuel Sportsbook JSON | Lines, props | Free | `sbapi.<state>.sportsbook.fanduel.com/api/...` | Live | Odds use limited to using FanDuel itself | N: 400 without app key, same file |
| BetMGM JSON | Lines, props | Free | `sports.<state>.betmgm.com/cds-api/...` | Live | Personal entertainment use only | N: "Access id missing", same file |
| Caesars JSON | Lines, props | Free | `api.americanwagering.com/...` | Live | Prohibits bots (Nevada terms) | N: CloudFront 403, same file |
| Bovada JSON | Lines (offshore book) | Free | `bovada.lv/services/sports/...` | Live | Prohibits (UI-only clause) | Y: 18 regular-season games, no preseason, same file |
| Pinnacle guest JSON | Sharp lines incl. team totals | Free | `guest.api.arcadia.pinnacle.com/0.1/leagues/487/...` | Live | Prohibits automated access | Y: 12 games, 492 prices, `20261013-1648_props_followup.json` |
| Action Network JSON | Scoreboard odds, team totals | Free | `api.actionnetwork.com/web/v1/scoreboard/nba` | Live | Prohibits; API robots.txt `Disallow: /` | Y: 5 games, `20261013-1648_sportsbooks_props.json` |
| PrizePicks | Pick'em player lines | Free | `api.prizepicks.com/projections` | Live | Prohibits | N: CAPTCHA 403, same file |
| Underdog Fantasy | Pick'em player lines | Free | `api.underdogfantasy.com/beta/v5` and `v6` | Live | Prohibits | N: 426 "Upgrade required", same files |
| RotoWire lineups page | Expected and confirmed starters, injury tags | Free page | HTML | Minutes (4.9) | Prohibits scraping; robots.txt allows the page | Y: `20261013-1646_pretip_poller.jsonl` |
| RotoWire news page and RSS | Player news blurbs | Free (analysis paywalled) | HTML; RSS `rotowire.com/rss/news.php?sport=NBA` | Minutes | Prohibits scraping | Y: `20261013-1650_parse_saved_pages.json`, `20261013-1653_news_channels.json` |
| Basketball Monster lineups | Projected starters | Free page | HTML | Daily | Prohibits scraping | Y (page, showing opening night): `20261013-1649_projection_pages.json` |
| Daily Fantasy Fuel | DK salaries, free DK projections, CSV | Free page | HTML data attributes; CSV button | Timestamped on page | Silent on scraping | Y (page; projections empty in preseason): same file |
| FantasyPros | DFS projections (mostly paid) | Mostly paid | n/a | n/a | robots.txt blocks `/api/`, crawl delay 5 s | N: guessed URL 404 |
| DARKO (darko.app) | Player ratings, minutes per game, CSV | Free page | HTML | Updated after games (SUPPORTED) | No commercial use without permission | Y (page): same file |
| pbpstats.com API | Possession-level player and lineup totals | Free | `api.pbpstats.com/get-totals/nba` | Daily (BET) | Silent (data is NBA-derived) | Y: `20261013-1651_history_sources.json` |
| basketball-reference.com | Box scores, game logs | Free pages | HTML | Daily | Conditional bot ban; 20 requests a minute; robots.txt blocks game logs | Partial: policy and robots.txt read, no data pulled |
| sportsdataverse GitHub releases | ESPN player box 1994 to 2026, PBP 2002 to 2026, schedules | Free | GitHub release files (parquet, csv) | Season files updated in season (last Sep 9, 2026) | CC BY 4.0 (data is ESPN-derived) | Y: `20261013-1652_sportsdataverse_parquet.json` |
| Kaggle datasets | Box scores, historical odds | Free with account | Kaggle API token | Varies | Per-dataset licenses (not checked) | N: needs an account |
| SportsbookReviewsOnline archive | Historical NBA odds | Free | xlsx per season | Static, 2007-08 to 2022-23 | Not checked | Partial: archive page listed seasons, `20261013-1651_history_sources.json` |
| Bluesky public API | Reporter and mirror posts | Free, no login | `public.api.bsky.app/xrpc/...` | Seconds to minutes | Permits reading | Y: `20261013-1653_news_channels.json`, `20261013-1654_bluesky_mirrors.json` |
| Reddit r/nba | Community news | Free with OAuth app | `reddit.com/r/nba/new.json` | Minutes | OAuth required (SUPPORTED) | N: 403 without login |
| NBA.com news RSS | League news | Free | `nba.com/news/rss.xml` | n/a | RSS allowed with conditions | N: Akamai 403 |

---

## 4. Source details

### 4.1 stats.nba.com through the nba_api package

**What it provides.** The NBA's own statistics site, read through the free Python package `nba_api` (version 1.11.4 here): schedule, every player's game log, box scores (traditional, advanced, usage), play-by-play, rosters, five-man lineups, on/off splits, play types, team stats and the daily scoreboard.

**Cost and auth.** Free; no key or login. `nba_api` sends a fixed set of browser-like headers (`Host: stats.nba.com`, a Chrome User-Agent, `Referer: https://www.nba.com/`, `Accept`, `Accept-Language`, `Sec-Ch-Ua` and similar).

**VERIFIED today** (`s01_nba_api.py` writing `20261013-1632_nba_api.json`; `s01b_nba_api_live_alternatives.py` writing `20261013-1635_nba_api_live_alternatives.json`):

| Endpoint | Result | Latency |
|---|---|---|
| ScheduleLeagueV2 2026-27 | 1,274 games: 67 preseason, 1,206 regular season (6 are NBA Cup knockout games with teams blank). First regular-season games Oct 20: BOS at DET 19:00 UTC, PHI at NYK 23:00 UTC, OKC at SAS 01:30 UTC | 2.4 s |
| LeagueGameLog, 2026-27 Pre Season | 41 completed games, Oct 3 to Oct 12, so last night's games were present this afternoon | 0.1 s |
| PlayerGameLogs, 2025-26 regular season | 26,651 player-game rows, 582 players, Oct 21 2025 to Apr 12 2026, with minutes and `NBA_FANTASY_PTS` | 0.4 s |
| BoxScoreTraditionalV3 | Player rows with minutes, box stats, `position` (filled only for starters) and `comment` (why a player sat) | 0.1 s |
| BoxScoreAdvancedV3, BoxScoreUsageV3 | Usage rate, pace, possessions, ratings per player | 0.1 to 0.4 s |
| BoxScoreSummaryV3 | `inactives` list per team (for example Towns, Anunoby, Hart in a 2025-26 Knicks game) | 0.2 s |
| ScoreboardV3, today | Tonight's 5 preseason games with status text | 0.4 s |
| PlayByPlayV3, last night | 552 events, 54 substitutions ("SUB: Bailey FOR Hayes") | 0.2 s |
| CommonTeamRoster, BOS 2026-27 | 21 players, 7 coaches | 0.4 s |
| LeagueDashLineups 2025-26 | 2,000 five-man lineups | 2.4 s |
| TeamPlayerOnOffSummary, BOS 2025-26 | On and off net rating for 21 players | 1.1 s |
| SynergyPlayTypes 2025-26, isolation | 284 player rows | 0.2 s |
| LeagueDashTeamStats 2025-26, Advanced | 30 teams with pace and ratings | 0.1 s |
| PlayerGameLogs 1996-97; LeagueGameLog 1983-84 player rows | 23,757 and 19,544 rows | 6.1 s, 0.1 s |
| **GameRotation** | **Failed**: 30-second timeout, then HTTP 500 with an empty body on two games (`s01c_gamerotation_raw.py`, `20261013-1636_gamerotation_raw.json`) | n/a |

Excerpt from the run log:

```
PlayerGameLogs 2025-26 Regular Season: ok=True latency=0.44s [26651]
GameRotation 0022501190: ok=False latency=30.01s ReadTimeout ...
{'gid': '0022501190', 'status': 500, 'latency_s': 0.56, 'bytes': 0}
```

**Blocking and rate limits.** Not blocked from this laptop: every request except GameRotation succeeded, plus the scoreboard and box-score polls in 4.9. No published rate limit; I kept to one request every 1.6 seconds or slower. BET: stats.nba.com is widely reported to refuse cloud data-center addresses, a reason to keep the nightly run on this laptop.

**Freshness.** Last night's preseason games were complete this afternoon; tonight's timing is in 4.9. The post-game lag (how soon after the final buzzer the full box score is complete) was not measured.

**Rotations.** Rebuild each player's on-court stretches from PlayByPlayV3 substitution events. This is ordinary data processing, not a workaround of any block.

**Schedule note (BET).** The 1,206 regular-season games should grow to 1,230 in December when the NBA Cup group stage ends and the remaining games are filled in, so refresh the schedule daily.

**Terms.** NBA.com Terms of Use, Section 9 (last updated July 13, 2026): use is limited to "private, non-commercial purposes", and "the NBA Statistics may not be used in connection with any fantasy game". VERIFIED word for word. https://www.nba.com/termsofuse

### 4.2 cdn.nba.com (static and liveData JSON)

**What it would provide.** The files behind NBA.com's game pages: `scheduleLeagueV2.json`, `todaysScoreboard_00.json`, `boxscore_<gameId>.json`, `playbyplay_<gameId>.json` and `odds_todaysGames.json`.

**VERIFIED: blocked for scripts.** Every scripted request got the Akamai bot-protection page "Access Denied" (HTTP 403):

```
python s02_cdn_nba.py
scheduleLeagueV2 403 0.34 425 None
todaysScoreboard_00 403 0.42 445 None
odds_todaysGames 403 0.32 436 None
```

The `nba_api` live module, with its own headers, failed the same way (`s02b_cdn_nba_live_module.py`, `20261013-1634_cdn_nba_live_module.json`).

**VERIFIED: works only inside a real browser page.** Opening the JSON address directly in a browser also showed "Access Denied", but the nba.com Games page's own requests to the same files returned 200 (`20261013-1636_cdn_nba_browser_context.json`). Fields seen: the scoreboard has `gameStatus`, `gameStatusText`, `gameClock`, `period`, teams and `pbOdds`; the odds feed lists mostly non-US books (Sportradar ids, decimal odds with opening odds).

**Recommendation: do not use cdn.nba.com.** Getting past bot protection (faking a browser's network fingerprint, or driving a browser to harvest the files) would defeat a technical access control. Nothing is lost: stats.nba.com `ScoreboardV3`, `PlayByPlayV3`, `BoxScoreTraditionalV3` and `BoxScoreSummaryV3` cover the same data.

**Process note.** My first spike sent four requests before stopping, then I sent two single diagnostic requests (curl and the `nba_api` live module) to tell an address block from a client block. Every later script stops a host at its first 403 or 429.

### 4.3 The official NBA injury report

**What it provides.** For every upcoming game, each team's players with an official status (Out, Doubtful, Questionable, Probable, Available) and a reason, for example "Injury/Illness - Right Knee; Soreness" or "G League - Two-Way". Teams that have not filed show "NOT YET SUBMITTED".

**The league rule (VERIFIED against the saved page).** Teams must file "By 5 p.m. local time the day before a game", except the second day of a back-to-back (1 p.m. local on game day). Game-day reports are due between 11 a.m. and 1 p.m. local (8 to 10 a.m. for tip-offs at 5 p.m. or earlier), and the page says reports are updated continually through the day. https://official.nba.com/nba-injury-report-2025-26-season/ (the 2026-27 page returned 404 today).

**Publication pattern (VERIFIED by probing archived files with `s03b`, `s03c`, `s03d`; outputs `20261013-1637_injury_cadence_probe.json`, `..._probe2.json`, `20261013-1638_injury_cadence_probe3.json`).**

| Period | File name pattern | Behavior observed |
|---|---|---|
| Jan to Apr 2026 | `Injury-Report_2026-03-15_05_15PM.pdf`, `_05_30PM`, `_05_45PM`, `_06_00PM` | One file per 15-minute slot; each file's Last-Modified time is 4 to 6 seconds after its slot |
| Oct to at least Dec 20, 2025 | `Injury-Report_2025-11-15_05PM.pdf` | One file per hour, overwritten within the hour (Last-Modified 5:30 PM and 5:45 PM ET on two "05PM" files); 15-minute names did not exist |

Times in file names are US Eastern; base address `https://ak-static.cms.nba.com/referee/injury/`.

```
{'slot_ET': '2026-03-15_05_15PM', 'status': 200, 'bytes': '87881', 'last_modified': 'Sun, 15 Mar 2026 21:15:04 GMT'}
{'slot_ET': '2025-10-21_05PM', 'status': 200, 'bytes': '71674', 'last_modified': 'Tue, 21 Oct 2025 21:30:04 GMT'}
{'slot_ET': '2025-10-21_05_30PM', 'status': 403, 'bytes': '1'}
```

A 403 from this host means "no such file", not "blocked": it is the storage service's standard reply for a missing file, and real files on the same host returned 200 in the same runs.

**Preseason (VERIFIED): none published.** No file exists for 2025-10-10, 2026-10-12 or 2026-10-13 in either pattern, so the 2026-27 naming cannot be known yet. BET: the first reports appear Monday Oct 19 for opening night; the engine should try both patterns.

**Parsing (VERIFIED, `s03g_injury_pdf_parse_v3.py`, outputs `20261013-1655_injury_pdf_parse_v3_*.json`).** pdfplumber's ruled-table mode found nothing because the PDF has no table lines (`s03e`). Reading words by horizontal position and attaching wrapped text to the vertically nearest row worked:

* 5:30 PM ET report, Mar 15 2026: 151 rows across 15 games (Out 101, Available 26, Questionable 12, Probable 2, Doubtful 1, NOT YET SUBMITTED 9 for next-day games); 0 rows with an unrecognized status; wrapped reasons stitched correctly.
* 11:00 AM ET report, same day (downloaded with `curl` into the same folder): 108 rows (Out 50, Questionable 29, Doubtful 4, Probable 3, Available 4, NOT YET SUBMITTED 18). Players moved during the day: Anthony Edwards was Questionable at 11:00 AM and Available at 5:30 PM, exactly the signal the engine needs.

An earlier version (`s03f`) attached one wrapped reason to the wrong player, so the engine's parser needs tests against several saved reports. Status accuracy matters more than reason text.

**Terms.** No terms specific to the report. NBA.com terms apply; they contain no bot or scraping clause (VERIFIED by searching the saved copy: the only "automated" mention concerns text messages). Whether Section 9's fantasy ban reaches injury statuses is a BET.

### 4.4 ESPN public JSON

**What it provides (VERIFIED, `s04_espn.py`, `20261013-1640_espn.json`), no key:**

| Endpoint | Result today |
|---|---|
| `site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20261013` | 5 games, each with DraftKings odds ("CLE -1.5", total 228.5, moneylines with open and close); season type Preseason |
| `.../injuries` | 135 entries for 30 teams with status, timestamp and news blurb; newest stamp 21:28 UTC at a 21:40 fetch |
| `.../teams/2/roster` | 21 players with position, status and current injury |
| core `.../seasons/2027/teams/2/depthcharts` | Depth chart by position with rank |
| `.../news?limit=10` | Articles with publish times |
| `.../summary?event=<id>` | Pick center (DraftKings spread, total, moneyline, prices), injuries, team stats |
| core `.../events/<id>/competitions/<id>/odds` | Providers and lines; open and close for past games |
| core `.../odds/100/propBets` | 123 DraftKings items for CLE at ORL: Points, Rebounds, Assists and 3-Pointer "Milestones" (ladders such as 15+, 18+, 20+), 119 tied to a player id (`s04b_espn_props.py`, `20261013-1641_espn_props.json`) |

**Props caveats (VERIFIED).** These are milestone ladders, not the usual over/under lines (BET: regular-season games may add over/under lines; check on opening night). The same request for a finished March 2026 game returned 404 (`s04c_espn_props_historical.py`), so ESPN keeps no prop history. Two fields are unreliable: `lastUpdated` read about two hours ahead of the server clock, and every rung showed the same `open` price.

**Historical lines (VERIFIED, `s07_history_sources.py`).** One January date per season: odds exist from 2014 (none for the 2012 sample), with 2 to 16 books per game (Westgate, Caesars, DraftKings, MGM, consensus and others). Separate open and close values appear from 2024; earlier seasons have one line per book. This is the best free source of historical game lines found.

**ESPN injuries are RotoWire's blurbs, word for word (VERIFIED, `s04d_espn_vs_rotowire_text.py`, `20261013-1657_espn_vs_rotowire_text.json`).** For all four Orlando and Toronto players listed by both (Vucevic, Anthony Black, Jonathan Isaac, Nate Bittle) the ESPN text matched RotoWire's exactly, and the timestamps agree within a minute (RotoWire RSS 2:29 PM PDT, which is 21:29 UTC, for Anthony Black; ESPN 21:28 UTC). Two cautions: ESPN marked players ruled out tonight as "Day-To-Day", so the game-day status must come from the blurb text or the official report; and players cleared to play drop off the list (Desmond Bane disappeared between two polls).

**Rate limits.** None published. Cache lifetimes are short (`max-age` 1 to 8 seconds on site endpoints, 66 to 900 seconds on core endpoints), so polling faster than once a minute gains nothing.

**Terms.** The Disney Terms of Use name ESPN and prohibit access "using a robot, spider, script, or other automated means"; the license is for personal, non-commercial use, and commercial or business use is barred. VERIFIED word for word. https://disneytermsofuse.com/english/

### 4.5 Betting lines and player props

**The Odds API (docs only; no key).**

* Free plan: 500 credits a month (SUPPORTED, pricing page). Each request costs markets times regions; listing sports and events costs nothing (VERIFIED in the saved docs).
* Props: per-event endpoint `/v4/sports/basketball_nba/events/{eventId}/odds` with keys such as `player_points`, `player_rebounds`, `player_assists`, `player_threes` and combos (SUPPORTED; a research helper read the market list). Available on the free plan (SUPPORTED).
* Historical odds: the docs say "only available on paid usage plans" (VERIFIED). The homepage table seemed to list them for the free plan; a research helper found that entry is struck through (SUPPORTED).
* Quota math (BET on game counts): lines for all games in one call cost 3 credits; twice a day for a month is 180 credits, which fits. Props for 4 markets on a 10-game night cost about 40 credits, so 500 credits cover about 12 nights. **The free tier covers game lines, not nightly props.**
* Terms: "Do not resell, repackage, or redistribute our data as a standalone data product." Use in your own app is allowed. VERIFIED. https://the-odds-api.com/terms-and-conditions.html

**Sportsbook and pick'em JSON (VERIFIED, one request each, `s05_sportsbooks_props.py`, `20261013-1648_sportsbooks_props.json`; follow-ups `s05b_props_followup.py`, `20261013-1648_props_followup.json`).**

| Source | What came back | Usable? | Terms (quote VERIFIED unless marked) |
|---|---|---|---|
| DraftKings Sportsbook (`sportsbook-nash.draftkings.com`) | Akamai "Access Denied" 403 | No | Sportsbook terms are separate, per-state documents at `sportsbook.draftkings.com/legal/...`; they returned 403 to us. The Massachusetts House Rules limit data to private, non-commercial use (SUPPORTED, read by a helper) |
| FanDuel (`sbapi.nj.sportsbook.fanduel.com`) | 400 `{"error":true}`: needs an app key from their web code | No (would mean lifting their key) | Ohio terms: odds may be used "only as strictly required for your permitted personal" purpose of using FanDuel |
| BetMGM (`sports.nj.betmgm.com/cds-api`) | 400 "Access id missing" | No (same reason) | Massachusetts terms: "for Your personal, entertainment use" |
| Caesars (`api.americanwagering.com`) | CloudFront 403 "Request blocked" | No | Nevada terms: "Use any robot, spider, scraper or other automated means to access" is prohibited (New Jersey terms are silent, SUPPORTED) |
| Bovada (`bovada.lv`) | 200: 18 regular-season games, no preseason | Technically yes | "must be executed by players via the supplied user interface" (also bars use from several states, SUPPORTED) |
| Pinnacle (`guest.api.arcadia.pinnacle.com`) | 200 with no key: 12 regular-season games, 492 prices (spreads 132, totals 192, moneylines 48, team totals 120), 96 season-long specials; no preseason | Technically yes | "no automated access, scraping, crawling, data extraction, or similar activity is authorized". Its official API is "closed for the general public since July 23rd, 2025", though it offers help to pregame handicapping projects by email. US customers are restricted (SUPPORTED) |
| Action Network (`api.actionnetwork.com`) | 200: tonight's 5 games with moneyline, spread, total, team totals; props path 404 | Technically yes | 'You may not use any "deep-link", "page-scrape", "robot", "spider"'; the API host's robots.txt is `Disallow: /` |
| PrizePicks (`api.prizepicks.com`) | 403 with a DataDome CAPTCHA link | No (never bypass a CAPTCHA) | "use any robot, spider, or other automatic device, process, or means" is prohibited |
| Underdog (`api.underdogfantasy.com`, v5 and v6) | 426 "A new version is required to continue" | No | Terms (effective Mar 17, 2026) bar users who "scrape, access, monitor, index, frame, link, or copy any content" automatically |

### 4.6 Free projections, lineups and news pages

Fetched once each after checking robots.txt (`s06_projection_pages.py`, `20261013-1649_projection_pages.json`; parsed read-only by `s06b_parse_saved_pages.py`, `20261013-1650_parse_saved_pages.json`).

* **RotoWire NBA lineups** (`rotowire.com/basketball/nba-lineups.php`), VERIFIED. Each game card shows "Expected Lineup" or "Confirmed Lineup" per team, five starters, and injury tags such as "F J. Butler Out". robots.txt allows the page. Terms (effective Sep 19, 2026) forbid using 'manual or automated software, devices, or other processes to "crawl," "scrape," or "spider"' its pages (VERIFIED); a separate article requires access only through interfaces RotoWire offers. RotoWire's statement page describes its lawsuit against Swish Analytics for scraping its injury data (VERIFIED). https://www.rotowire.com/termsandconditions.php
* **RotoWire news page and RSS**, VERIFIED. 25 free blurbs on the page (the "ANALYSIS" part is for subscribers), dates only. The RSS feed returns only the newest 5 items, with minute timestamps ("Tue, 13 Oct 2026 2:49:00 PM PDT, Desmond Bane: Will play Tuesday").
* **Basketball Monster** (`basketballmonster.com/nbalineups.aspx`), VERIFIED page. Already shows projected opening-night lineups ("Projected", with "Q" and "P" injury letters), not tonight's preseason games; its injuries URL redirected to an error page. Terms: "You may not scrape or otherwise copy our Content without permission." (VERIFIED) https://basketballmonster.com/TermsOfUse.aspx
* **Daily Fantasy Fuel** (`dailyfantasyfuel.com/nba/projections/draftkings`), VERIFIED page. Tonight's DraftKings "5 GAME SLATE" with salaries in the page's data attributes (for example `data-salary="5700"` for Jimmy Butler, marked Out), a "START" column, a free "Download CSV" button, and an "Updated At: Tue, Oct 13, 2026, 5:49 PM ET" stamp. Projections were still 0.0 at fetch time, and a second fetch at 22:08 UTC (`s06c_dff_recheck.py`, `20261013-1708_dff_recheck.json`) showed the same: the page's raw HTML holds only 5 rows (all players marked Out), with the stamp moved to 5:57 PM ET. BET: the full table is filled in by the page's JavaScript, so the free CSV button is the intended way to take the data. Terms (last updated June 7, 2026) cover subscriptions and say nothing about scraping (VERIFIED by search of the saved copy); robots.txt blocks only `/lineup/*`.
* **FantasyPros**: the URL I guessed returned 404. robots.txt blocks `/api/` and asks for a 5-second crawl delay (VERIFIED). Daily NBA projections are mostly paid, and its API allows 100 calls a day for approved personal use (SUPPORTED).
* **DARKO** (`darko.app`), VERIFIED page: player ratings (DPM, a plus-minus style impact rating), offensive and defensive splits, minutes per game and pace, a "Download CSV" button, a "Fantasy Lab". Terms (its assistant terms): "Commercial use of DARKO charts, data, ratings or other outputs is prohibited" without permission (VERIFIED); non-commercial chart reuse with credit is welcome. It also offers a public assistant connection at `darko.app/mcp` (SUPPORTED).
* **NumberFire**: now redirects to FanDuel Research; not a DraftKings projection source (SUPPORTED).
* **Others** (Stokastic, SaberSim, LineStar, FTN, SportsLine): free tiers are partial previews or trials; none offers a full free DraftKings projection or ownership feed (SUPPORTED, lightly checked).

### 4.7 Historical data for backtests and priors

* **nba_api history (VERIFIED, 4.1).** Player game logs with minutes back to 1996-97; basic player box rows back to at least 1983-84.
* **pbpstats.com API (VERIFIED).** `api.pbpstats.com/get-totals/nba` returned 500 player rows for 2025-26 (possessions, shot zones, second-chance and penalty splits) and 500 Boston lineups. BET: 500 is a per-call cap; filter by team to get everything. No terms or rate limit published (SUPPORTED); its data comes from NBA.com, so Section 9 is relevant.
* **basketball-reference.com (VERIFIED from saved pages).** robots.txt disallows `*/gamelog/`, `*/lineups/`, `*/on-off/`, `*/splits/` and sets `Crawl-delay: 3`. The bot policy blocks anyone requesting "more often than twenty requests in a minute", with a block of up to a day. The terms bar bots and scrapers used "in a manner that adversely impacts site performance or access" (a conditional ban). Recommendation: do not scrape it; the same data is available above. https://www.sports-reference.com/bot-traffic.html
* **sportsdataverse ESPN data on GitHub (VERIFIED, `s07b_sportsdataverse_parquet.py`).** Release `espn_nba_player_boxscores` has season files from 1994 to 2026 (103 files); `player_box_2026.parquet` is 0.61 MB with 34,883 rows, Oct 21 2025 to Jun 13 2026 (regular season, playoffs, NBA Cup), including `minutes`, `starter`, `did_not_play` and `reason`. Release `espn_nba_pbp` has play-by-play from 2002 (2026 file 22 MB). Season files last updated Sep 9, 2026. License: Creative Commons Attribution 4.0 (VERIFIED from the repository's license file); a daily update job runs during the season (SUPPORTED).
* **Kaggle.** Downloads need a Kaggle account and API token the user would create (SUPPORTED). Notable datasets: an NBA betting dataset covering 2007 to 2026 and a box-score dataset from 1947 (SUPPORTED; licenses not checked).
* **Free historical odds.** ESPN core odds per past game (4.4), VERIFIED from 2014. The SportsbookReviewsOnline archive page listed NBA seasons 2007-08 to 2022-23 when I fetched it (VERIFIED; a helper later got a 404 there, so it may be unstable).
* **Historical DraftKings salaries and ownership.** Not fetched (RotoGuru and RotoGrinders belong to another agent). Daily Fantasy Fuel shows the current slate's salaries only.

### 4.8 Late-news channels without paying for X

| Channel | VERIFIED result | Speed |
|---|---|---|
| ESPN injuries JSON | RotoWire's blurbs verbatim, each stamped with RotoWire's publish minute. Tonight, 10 new or updated entries for tonight's teams appeared between 0 and 18 minutes after their stamp (Vucevic 0 to 4, Holmgren 1 to 6, Topic 7 to 12, Jaylin Williams 13 to 18), measured with 5-minute polls. Players cleared to play are removed (five OKC players including Shai Gilgeous-Alexander dropped off at 22:53 UTC) | Usually 5 to 12 minutes behind RotoWire, worst case seen 18 |
| ESPN news JSON | Headlines with publish times | Slower: the Pritchard extension at 20:35 to 20:42 UTC, versus a Shams mirror post at 19:50 and RotoWire RSS at 19:58 |
| RotoWire RSS | Newest 5 items, minute timestamps | Same minute RotoWire publishes; only 5 items, so poll often |
| RotoWire news page | 25 items, dates only | Same as RSS |
| Bluesky public API (no login) | A Shams Charania mirror bot (`shamsbot.bsky.social`) was current (posts at 19:50 and 19:53 UTC); Underdog NBA last posted Mar 4, 2026; Shams' own account last posted in 2024 | Seconds, but the mirror is unofficial and could stop any day |
| Reddit r/nba | 403 without login | n/a |
| NBA.com news RSS | Akamai 403 | n/a |

Terms: Bluesky's developer guidelines target spam ("Generating automated or bulk interactions"), not reading public posts (VERIFIED); `public.api.bsky.app` is the address Bluesky asks apps to use for public reads, with no published number for its limit (SUPPORTED). Reddit requires an OAuth app, with about 100 requests a minute reported (SUPPORTED, secondary sources). NBA.com allows RSS reuse with branding and non-commercial conditions (Section 7, SUPPORTED by a helper's read; the clause exists in the saved copy).

### 4.9 Tonight's timing test (one preseason game, first tips 7:00 PM ET)

TIMING-PENDING

---

## 5. Is today representative of the regular season?

| Observation | Representative? |
|---|---|
| stats.nba.com endpoints, speed, no blocking | Yes (BET: regular-season load is higher, so expect occasional timeouts) |
| Last night's box scores present today | Yes |
| Official injury report | No: none in preseason; 2026-27 naming unknown until about Oct 19 |
| ESPN odds and props | Partly: DraftKings lines and milestone ladders tonight; regular-season prop menus are usually wider (BET) |
| ESPN injuries and RotoWire news | Yes, though preseason news is mostly rest days |
| RotoWire lineups page | Yes in structure; preseason starters are less predictable |
| Pinnacle, Bovada | No: regular-season games only |
| Projection sites | No: Daily Fantasy Fuel had a preseason DK slate with empty projections; Basketball Monster already shows opening night |

---

## 6. Request budget for a typical night (BET)

About 200 to 400 requests a night across five hosts, never faster than one per second per host: stats.nba.com about 50 (yesterday's box scores, play-by-play, game logs), ESPN about 150 (injuries, scoreboard, props every 2 to 5 minutes in the last 90 minutes), the injury PDF about 30 (one per 15-minute slot), RotoWire about 20 (lineups every 5 to 10 minutes near lock), sportsdataverse a few files a week. This is a tiny load for any of these hosts, and it fits a laptop.

---

## 7. Process notes

* Every spike sent at most a few requests per endpoint, about one per second or slower; total for the day was a few hundred requests across about 25 hosts.
* cdn.nba.com: see the process note in 4.2.
* ak-static.cms.nba.com 403 replies were missing-file replies (4.3), so probing other time slots was not a breach of the stop-on-403 rule.
* Downloaded files (PDFs, HTML pages, one parquet file) are saved under `spikes\data\out\downloads\<source>\` and were only read, never executed; parsers ran in Python's isolated mode (`-I`).
* Terms quotes were matched word for word against saved copies with `s10_terms_capture.py --grep`. Claims that only a research helper could read (pages that refused my fetcher) are marked SUPPORTED.

---

## 8. Open questions

1. **Which terms posture does the user choose** (section 1b): strict, or low-volume personal use with the stated risk? This decides several primary sources.
2. **Does entering paid DraftKings contests count as "personal, non-commercial" use** under these terms? (BET: arguable either way; not legal advice.)
3. **Which US state is the user in?** Several sportsbook terms differ by state (Caesars New Jersey is silent, Nevada bans bots; Bovada bars several states), and the FanDuel and BetMGM endpoints are state-specific.
4. **Will the user sign up for a free The Odds API key?** It is the only lines source whose terms clearly permit this use, and it covers about 12 prop nights a month.
5. **Injury PDF naming for 2026-27**: confirm hourly or 15-minute file names on Monday Oct 19, and confirm the first reports appear then.
6. **ESPN's regular-season prop menu**: check on opening night whether over/under lines appear alongside the milestone ladders.
7. **Where DraftKings salaries and contest data come from**: owned by another agent (DraftKings DFS endpoints); Daily Fantasy Fuel's page carries current salaries as a cross-check.
8. **Starting-lineup confirmation timing in the regular season**: tonight is one preseason data point; repeat the poller on opening night.
9. **Will GameRotation recover?** If it does, it saves rotation-building code; the design should not depend on it.

---

## 9. Implications for the architecture

* **Run the nightly job on this laptop, not in the cloud.** stats.nba.com worked from this home connection; it is widely reported to refuse cloud addresses (BET). This also keeps the user's workload at "leave the laptop on".
* **Put every source behind a small adapter with a common output shape** (schedule, box score, status, lineup, line, prop, news item). The terms posture can then swap sources without touching the model, and a blocked source can fail over to its fallback.
* **One polite request gate per host**: at most one request per second, a lower cap where published (20 a minute for Sports Reference if ever used), and an automatic stop for the night at the first 403 or 429, with a clear message to the user. Never retry around bot protection or CAPTCHAs.
* **Archive what disappears**: save each night's ESPN props, lines and injury PDFs locally, because props vanish after the game and the free tiers have no history. After one season this becomes the user's own free backtest set.
* **Injury PDF poller**: every 15 minutes on game days, trying both file-name patterns, stopping when a slot's file is missing ("no such file" 403s are expected and are not a block).
* **Two-speed schedule**: a full refresh in the morning (schedule, history, priors, game lines), then a tight loop in the 90 minutes before lock (ESPN injuries and props, RotoWire lineups, the PDF) every 2 to 5 minutes, re-running projections and lineups when anything changes. Free news arrives 5 to 20 minutes after it breaks (4.8), so the final re-run should be as close to lock as the user's routine allows, and the engine should flag any player whose status is still uncertain at lock rather than silently trusting the last value.
* **Compute rotations from play-by-play** rather than relying on GameRotation.
* **Refresh the schedule daily** (NBA Cup games are added in December; postponements happen).
* **Treat the injury blurb text as data**: ESPN's status field says "Day-To-Day" for players ruled out tonight, so a small text classifier (or the official PDF) must set the game status.

---

## 10. Sources

Terms and policies (saved copies in `spikes\data\out\downloads\terms\`):

* NBA.com Terms of Use: https://www.nba.com/termsofuse
* NBA injury report page: https://official.nba.com/nba-injury-report-2025-26-season/
* Disney Terms of Use (covers ESPN): https://disneytermsofuse.com/english/
* The Odds API docs: https://the-odds-api.com/liveapi/guides/v4/ ; terms: https://the-odds-api.com/terms-and-conditions.html ; pricing: https://the-odds-api.com/
* RotoWire terms: https://www.rotowire.com/termsandconditions.php ; lawsuit statement: https://www.rotowire.com/swish-lawsuit ; robots.txt: https://www.rotowire.com/robots.txt
* Basketball Monster terms: https://basketballmonster.com/TermsOfUse.aspx
* Daily Fantasy Fuel terms: https://www.dailyfantasyfuel.com/terms-of-service
* FantasyPros robots.txt: https://www.fantasypros.com/robots.txt
* DARKO assistant terms: https://www.darko.app/assistant-terms
* Sports Reference terms: https://www.sports-reference.com/termsofuse.html ; bot policy: https://www.sports-reference.com/bot-traffic.html ; basketball-reference robots.txt: https://www.basketball-reference.com/robots.txt
* hoopR data license: https://github.com/sportsdataverse/hoopR-nba-data (LICENSE.md)
* Action Network terms: https://www.actionnetwork.com/terms ; API robots.txt: https://api.actionnetwork.com/robots.txt
* PrizePicks terms: https://www.prizepicks.com/help-center/terms-of-service
* Underdog terms: https://legal.underdogsports.com/?g=42203
* Bovada terms: https://www.bovada.lv/contents/terms_of_service_bvd.pdf
* Pinnacle terms (Malta): https://www.pinnacle.com/en/future/termsandconditions/malta ; API status: https://github.com/pinnacleapi/pinnacleapi-documentation
* FanDuel Sportsbook Ohio terms: https://d38ayms4az88sz.cloudfront.net/SB/OH/2026-03-09T12-48-00.html
* BetMGM Massachusetts terms: https://help.ma.betmgm.com/en/general-information/legal-matters/general-terms-and-conditions
* Caesars Sportsbook Nevada terms: https://www.caesars.com/sportsbook-and-casino/nv/support/terms-and-conditions-privacy/
* Bluesky developer guidelines: https://github.com/bluesky-social/bsky-docs (docs/support/developer-guidelines.md)

Data endpoints tested (see section 4 for exact paths): stats.nba.com (via nba_api 1.11.4), cdn.nba.com, ak-static.cms.nba.com, site.api.espn.com, sports.core.api.espn.com, sportsbook-nash.draftkings.com, sbapi.nj.sportsbook.fanduel.com, sports.nj.betmgm.com, api.americanwagering.com, bovada.lv, guest.api.arcadia.pinnacle.com, api.actionnetwork.com, api.prizepicks.com, api.underdogfantasy.com, rotowire.com, basketballmonster.com, dailyfantasyfuel.com, fantasypros.com, darko.app, api.pbpstats.com, api.github.com and github.com (sportsdataverse), sportsbookreviewsonline.com, public.api.bsky.app, reddit.com, nba.com.

Spike scripts: `spikes\data\s01_nba_api.py` through `s10_terms_capture.py`.
