# THROWAWAY SPIKE: not engine code. Purpose: verify free historical sources for backtests and priors: ESPN closing-line coverage by season, pbpstats API, sportsdataverse (hoopR) GitHub releases, basketball-reference bot policy, SBR odds archive page.
import json, time, datetime, collections, re
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
TERMS = OUT / "downloads" / "terms"; TERMS.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36", "Accept": "application/json, text/html;q=0.9"}
res = {"run_started_local": datetime.datetime.now().isoformat(), "espn_odds_coverage": [], "calls": []}
blocked = set()
s = requests.Session()


def get(name, url, params=None, keep_text=False, headers=None):
    host = url.split("/")[2]
    rec = {"name": name, "url": url, "params": params}
    if host in blocked:
        rec["skipped"] = "host blocked"; return rec, None
    t0 = time.time()
    try:
        r = s.get(url, headers=headers or H, params=params, timeout=40)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), ratelimit_remaining=r.headers.get("x-ratelimit-remaining"))
        if r.status_code in (403, 429):
            blocked.add(host)
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:200]; r = None
    print(name, rec.get("status"), rec.get("bytes"), flush=True)
    time.sleep(1.3)
    return rec, r


# 1 ESPN odds coverage: one mid-January date per season
SITE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
CORE = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba"
for d in ("20120115", "20140115", "20160115", "20180115", "20200115", "20210215", "20220115", "20230115", "20240115", "20250115"):
    rec, r = get(f"espn scoreboard {d}", SITE, {"dates": d})
    cov = {"date": d}
    if r is not None and r.status_code == 200:
        evs = r.json().get("events", [])
        cov["n_events"] = len(evs)
        if evs:
            eid = evs[0]["id"]
            rec2, r2 = get(f"espn core odds {d} {eid}", f"{CORE}/events/{eid}/competitions/{eid}/odds")
            if r2 is not None and r2.status_code == 200:
                its = r2.json().get("items", [])
                cov["event"] = evs[0]["name"]
                cov["providers"] = [i.get("provider", {}).get("name") for i in its]
                cov["has_open_close"] = [bool(i.get("open")) and bool(i.get("close")) for i in its]
                cov["lines"] = [(i.get("details"), i.get("overUnder")) for i in its[:3]]
            else:
                cov["odds_status"] = rec2.get("status")
    res["espn_odds_coverage"].append(cov)

# 2 pbpstats API
rec, r = get("pbpstats totals Player 2025-26", "https://api.pbpstats.com/get-totals/nba", {"Season": "2025-26", "SeasonType": "Regular Season", "Type": "Player"})
if r is not None and r.status_code == 200:
    j = r.json(); rows = j.get("multi_row_table_data", [])
    rec["n_rows"] = len(rows); rec["keys_sample"] = list(rows[0].keys())[:50] if rows else None
res["calls"].append(rec)
rec, r = get("pbpstats lineups BOS 2025-26", "https://api.pbpstats.com/get-totals/nba", {"Season": "2025-26", "SeasonType": "Regular Season", "Type": "Lineup", "TeamId": "1610612738"})
if r is not None and r.status_code == 200:
    rows = r.json().get("multi_row_table_data", [])
    rec["n_rows"] = len(rows); rec["sample"] = {k: rows[0].get(k) for k in list(rows[0].keys())[:12]} if rows else None
res["calls"].append(rec)

# 3 sportsdataverse releases (GitHub REST API, unauthenticated 60 req/hour)
GH = {"User-Agent": "nba-dfs-spike", "Accept": "application/vnd.github+json"}
for repo in ("sportsdataverse/sportsdataverse-data", "sportsdataverse/hoopR-nba-data"):
    rec, r = get(f"github releases {repo}", f"https://api.github.com/repos/{repo}/releases", {"per_page": 100}, headers=GH)
    if r is not None and r.status_code == 200:
        rels = r.json()
        nba = [x for x in rels if "nba" in (x.get("tag_name") or "").lower()]
        rec["n_releases"] = len(rels); rec["nba_tags"] = [(x["tag_name"], x.get("published_at"), len(x.get("assets", []))) for x in nba][:30]
        for x in nba:
            if x["tag_name"] in ("espn_nba_player_boxscores", "espn_nba_pbp", "espn_nba_schedules", "espn_nba_team_boxscores"):
                names = sorted(a["name"] for a in x.get("assets", []))
                rec.setdefault("assets", {})[x["tag_name"]] = {"n": len(names), "first": names[:3], "last": names[-4:],
                                                                "sizes_mb_last": [round(a["size"] / 1e6, 1) for a in sorted(x["assets"], key=lambda a: a["name"])[-4:]],
                                                                "updated_last": [a["updated_at"] for a in sorted(x["assets"], key=lambda a: a["name"])[-2:]]}
    res["calls"].append(rec)

# 4 basketball-reference robots + Sports Reference bot policy page (saved as text for quote checks)
for name, url in (("bbref_robots", "https://www.basketball-reference.com/robots.txt"), ("sr_bot_traffic", "https://www.sports-reference.com/bot-traffic.html"),
                  ("sbr_nba_archive", "https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba/nbaoddsarchives.htm")):
    rec, r = get(name, url, headers={"User-Agent": H["User-Agent"]})
    if r is not None and r.status_code == 200:
        from bs4 import BeautifulSoup
        txt = re.sub(r"\s+", " ", BeautifulSoup(r.text, "lxml").get_text(" ")) if "html" in r.headers.get("Content-Type", "") else r.text
        (TERMS / f"{name}.txt").write_text(f"URL: {url}\nFETCHED: {datetime.datetime.now().isoformat()}\n\n{txt}", encoding="utf-8")
        rec["text_head"] = txt[:500]
        if name == "sbr_nba_archive":
            rec["season_links"] = re.findall(r"nba odds (\d{4}-\d{2})", txt, re.I)[:30] or re.findall(r"(20\d\d-\d\d)", txt)[:30]
    res["calls"].append(rec)

res["blocked"] = sorted(blocked)
(OUT / f"{stamp}_history_sources.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res["espn_odds_coverage"], indent=0)[:3000])
