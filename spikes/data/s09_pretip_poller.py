# THROWAWAY SPIKE: not engine code. Purpose: poll tonight's preseason slate before and after tip to measure how fast injury status, starting lineups, and box scores appear on ESPN, stats.nba.com and RotoWire.
# Hosts and cadence (well under 1 request/second per host):
#   phase 1 (now until 7:15 pm ET): every 5 min ESPN injuries + ESPN summary + stats.nba.com scoreboard + boxscore; RotoWire lineups every 15 min.
#   phase 2 (until 9:45 pm ET): every 15 min stats.nba.com scoreboard + boxscore and ESPN summary only.
# Stops a host permanently on its first 403 or 429.
import json, time, datetime, re, sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from nba_api.stats.library.http import STATS_HEADERS

OUT = Path(__file__).parent / "out"
DL = OUT / "downloads" / "rotowire"
DL.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
LOG = OUT / f"{stamp}_pretip_poller.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}
TEAMS = {"CLE", "ORL", "NYK", "TOR", "IND", "OKC", "GSW", "LAL", "POR", "SAC"}
ESPN_EVENT = "401898403"   # CLE @ ORL, 7:00 pm ET
NBA_GAME = "0012600045"    # CLE @ ORL
UTC = datetime.timezone.utc
PHASE1_END = datetime.datetime(2026, 10, 13, 23, 15, tzinfo=UTC)   # 7:15 pm ET
PHASE2_END = datetime.datetime(2026, 10, 14, 1, 45, tzinfo=UTC)    # 9:45 pm ET
blocked = set()
s = requests.Session()
prev_inj = {}


def log(rec):
    rec["t_utc"] = datetime.datetime.now(UTC).isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    print(rec.get("kind"), rec.get("status"), str(rec.get("summary", ""))[:160], flush=True)


def fetch(host_key, url, headers, params=None):
    if host_key in blocked:
        return None, None
    t0 = time.time()
    try:
        r = s.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"[:200], "latency_s": round(time.time() - t0, 2)}
    meta = {"status": r.status_code, "latency_s": round(time.time() - t0, 2)}
    if r.status_code in (403, 429):
        blocked.add(host_key); meta["stopped_host"] = host_key
    time.sleep(1.2)
    return r, meta


def espn_injuries():
    r, m = fetch("espn", "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries", UA)
    if r is None or r.status_code != 200:
        log({"kind": "espn_injuries", **(m or {})}); return
    d = r.json(); rows = {}
    for t in d.get("injuries", []):
        for i in t.get("injuries", []):
            ab = (i.get("athlete", {}).get("team", {}) or {}).get("abbreviation") or t.get("displayName")
            rows[i.get("athlete", {}).get("displayName")] = {"team": t.get("displayName"), "status": i.get("status"), "date": i.get("date"), "short": (i.get("shortComment") or "")[:140]}
    tonight = {k: v for k, v in rows.items() if any(n in (v["team"] or "") for n in ("Cavaliers", "Magic", "Knicks", "Raptors", "Pacers", "Thunder", "Warriors", "Lakers", "Trail Blazers", "Kings"))}
    changes = [(k, prev_inj.get(k, {}).get("status"), v["status"], v["date"]) for k, v in tonight.items() if prev_inj.get(k, {}).get("status") != v["status"] or prev_inj.get(k, {}).get("date") != v["date"]]
    removed = [k for k in prev_inj if k not in tonight]
    prev_inj.clear(); prev_inj.update(tonight)
    newest = max((v["date"] for v in rows.values() if v["date"]), default=None)
    log({"kind": "espn_injuries", **m, "summary": {"n_all": len(rows), "n_tonight": len(tonight), "newest_date": newest, "changes": changes[:25], "removed": removed[:10]}})


def espn_summary():
    r, m = fetch("espn", "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary", UA, {"event": ESPN_EVENT})
    if r is None or r.status_code != 200:
        log({"kind": "espn_summary", **(m or {})}); return
    d = r.json()
    starters = []
    for team in d.get("boxscore", {}).get("players", []) or []:
        for st in team.get("statistics", []):
            for a in st.get("athletes", []):
                if a.get("starter"):
                    starters.append((team.get("team", {}).get("abbreviation"), a.get("athlete", {}).get("displayName")))
    rosters = d.get("rosters")
    roster_starters = []
    if rosters:
        for t in rosters:
            for p in t.get("roster", []):
                if p.get("starter"):
                    roster_starters.append((t.get("team", {}).get("abbreviation"), p.get("athlete", {}).get("displayName")))
    st = d.get("header", {}).get("competitions", [{}])[0].get("status", {}).get("type", {})
    log({"kind": "espn_summary", **m, "summary": {"status": st.get("description"), "keys": sorted(d.keys()), "box_starters": starters[:10], "roster_starters": roster_starters[:10],
                                                   "n_injury_blocks": len(d.get("injuries", []))}})


def nba_scoreboard_and_box():
    r, m = fetch("stats", "https://stats.nba.com/stats/scoreboardv3", STATS_HEADERS, {"GameDate": "2026-10-13", "LeagueID": "00"})
    if r is not None and r.status_code == 200:
        g = [x for x in r.json()["scoreboard"]["games"] if x["gameId"] == NBA_GAME]
        g = g[0] if g else {}
        log({"kind": "nba_scoreboardv3", **m, "summary": {"gameStatus": g.get("gameStatus"), "text": g.get("gameStatusText"), "period": g.get("period"), "clock": g.get("gameClock"),
                                                         "score": (g.get("awayTeam", {}).get("score"), g.get("homeTeam", {}).get("score"))}})
    else:
        log({"kind": "nba_scoreboardv3", **(m or {})})
    r, m = fetch("stats", "https://stats.nba.com/stats/boxscoretraditionalv3", STATS_HEADERS,
                 {"GameID": NBA_GAME, "LeagueID": "00", "StartPeriod": 0, "EndPeriod": 0, "StartRange": 0, "EndRange": 0, "RangeType": 0})
    if r is not None and r.status_code == 200:
        try:
            bx = r.json()["boxScoreTraditional"]
            ps = []
            for side in ("awayTeam", "homeTeam"):
                for p in bx.get(side, {}).get("players", []):
                    ps.append((bx[side].get("teamTricode"), p.get("familyName"), p.get("position"), p.get("comment"), p.get("statistics", {}).get("minutes")))
            starters = [p for p in ps if p[2]]
            log({"kind": "nba_boxscore", **m, "summary": {"n_players": len(ps), "n_with_position(starters)": len(starters), "starters": starters[:10],
                                                         "dnp_comments": [p for p in ps if p[3]][:8], "minutes_sample": [p[4] for p in ps[:5]]}})
        except Exception as e:
            log({"kind": "nba_boxscore", **m, "summary": f"parse error {e}", "head": r.text[:200]})
    else:
        log({"kind": "nba_boxscore", **(m or {}), "head": (r.text[:200] if r is not None else None)})


rw_first = True


def rotowire():
    global rw_first
    r, m = fetch("rotowire", "https://www.rotowire.com/basketball/nba-lineups.php", UA)
    if r is None or r.status_code != 200:
        log({"kind": "rotowire_lineups", **(m or {})}); return
    if rw_first:
        (DL / f"{stamp}_nba-lineups.html").write_text(r.text, encoding="utf-8"); rw_first = False
    soup = BeautifulSoup(r.text, "lxml")
    games = []
    for g in soup.select("div.lineup.is-nba"):
        abbr = [a.get_text(strip=True) for a in g.select(".lineup__abbr")]
        sides = []
        for ul in g.select("ul.lineup__list"):
            st = ul.select_one(".lineup__status")
            players = [li.select_one("a").get("title") or li.select_one("a").get_text(strip=True) for li in ul.select("li.lineup__player") if li.select_one("a")]
            inj = [li.get_text(" ", strip=True)[:40] for li in ul.select("li.lineup__player") if li.select_one(".lineup__inj")]
            sides.append({"status": st.get_text(" ", strip=True) if st else None, "status_class": " ".join(st.get("class", [])) if st else None, "first5": players[:5], "inj_tagged": inj[:6]})
        games.append({"teams": abbr[:2], "sides": sides})
    log({"kind": "rotowire_lineups", **m, "summary": {"n_games": len(games), "games": games[:6]}, "bytes": len(r.content)})


cycle = 0
log({"kind": "start", "summary": "poller started"})
while True:
    now = datetime.datetime.now(UTC)
    if now > PHASE2_END or len(blocked) >= 3:
        break
    if now <= PHASE1_END:
        espn_injuries(); espn_summary(); nba_scoreboard_and_box()
        if cycle % 3 == 0:
            rotowire()
        cycle += 1
        time.sleep(300)
    else:
        nba_scoreboard_and_box(); espn_summary()
        if cycle % 99 == 0:
            espn_injuries()
        cycle += 1
        time.sleep(900)
log({"kind": "end", "summary": {"blocked": sorted(blocked)}})
