# THROWAWAY SPIKE: not engine code. Purpose: verify cdn.nba.com static and liveData JSON (schedule, scoreboard, boxscore, play-by-play, odds) from this machine and record fields.
import json, time, datetime
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
     "Referer": "https://www.nba.com/", "Origin": "https://www.nba.com", "Accept": "application/json, text/plain, */*"}
res = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}
s = requests.Session()


def get(name, url):
    t0 = time.time()
    rec = {"name": name, "url": url}
    try:
        r = s.get(url, headers=H, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content),
                   last_modified=r.headers.get("Last-Modified"), cache_control=r.headers.get("Cache-Control"),
                   age=r.headers.get("Age"), date=r.headers.get("Date"))
        data = r.json() if r.status_code == 200 else None
    except Exception as e:
        rec.update(error=f"{type(e).__name__}: {e}"[:300]); data = None
    print(name, rec.get("status"), rec.get("latency_s"), rec.get("bytes"), rec.get("last_modified"), flush=True)
    res["calls"].append(rec)
    time.sleep(1.2)
    return rec, data


# Schedule
rec, sched = get("scheduleLeagueV2", "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json")
done_games, today_games = [], []
if sched:
    ls = sched["leagueSchedule"]
    rec["seasonYear"] = ls.get("seasonYear")
    allg = [g for d in ls["gameDates"] for g in d["games"]]
    rec["total_games"] = len(allg)
    rec["by_prefix"] = {p: sum(1 for g in allg if g["gameId"].startswith(p)) for p in ("001", "002", "003", "004", "005", "006")}
    rec["game_keys"] = list(allg[0].keys())
    rec["sample_game"] = {k: allg[0][k] for k in list(allg[0].keys())[:20] if not isinstance(allg[0][k], (dict, list))}
    reg = [g for g in allg if g["gameId"].startswith("002")]
    rec["first_regular"] = (reg[0]["gameDateTimeUTC"], reg[0]["awayTeam"]["teamTricode"], reg[0]["homeTeam"]["teamTricode"]) if reg else None
    done_games = [g for g in allg if g.get("gameStatus") == 3]
    rec["completed_games"] = len(done_games)
    rec["last_completed"] = (done_games[-1]["gameId"], done_games[-1]["gameDateTimeUTC"]) if done_games else None
    rec["broadcasters_key_present"] = "broadcasters" in allg[0]

# Today's scoreboard
rec, sb = get("todaysScoreboard_00", "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json")
if sb:
    games = sb["scoreboard"]["games"]
    rec["gameDate"] = sb["scoreboard"].get("gameDate")
    rec["games"] = [(g["gameId"], g["gameStatusText"], g["awayTeam"]["teamTricode"], g["homeTeam"]["teamTricode"]) for g in games]
    rec["game_keys"] = list(games[0].keys()) if games else []
    today_games = games

# Odds feed on cdn.nba.com
rec, odds = get("odds_todaysGames", "https://cdn.nba.com/static/json/liveData/odds/odds_todaysGames.json")
if odds:
    rec["top_keys"] = list(odds.keys())
    gs = odds.get("games", [])
    rec["n_games"] = len(gs)
    if gs:
        g = gs[0]
        rec["sample"] = json.dumps(g)[:1500]

# Box score + pbp for most recent completed game
if done_games:
    gid = done_games[-1]["gameId"]
    rec, bx = get(f"boxscore_{gid}", f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json")
    if bx:
        gm = bx["game"]
        p = gm["homeTeam"]["players"]
        rec["player_keys"] = list(p[0].keys())
        rec["stat_keys"] = list(p[0]["statistics"].keys())
        rec["sample_players"] = [{k: q.get(k) for k in ("name", "starter", "position", "status", "notPlayingReason", "notPlayingDescription", "played", "oncourt")} | {"minutes": q["statistics"].get("minutes"), "points": q["statistics"].get("points")} for q in p[:7]]
        rec["n_players_home"] = len(p)
        rec["n_inactive_or_dnp"] = sum(1 for q in p if q.get("status") != "ACTIVE" or q.get("played") == "0")
    rec, pbp = get(f"playbyplay_{gid}", f"https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{gid}.json")
    if pbp:
        acts = pbp["game"]["actions"]
        rec["n_actions"] = len(acts)
        rec["action_keys"] = list(acts[0].keys())
        subs = [a for a in acts if a.get("actionType") == "substitution"]
        rec["n_substitutions"] = len(subs)
        rec["sample_sub"] = subs[0] if subs else None

# Last season final regular game box score still on CDN?
rec, bx = get("boxscore_0022501230 (2025-26 last regular)", "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_0022501230.json")
if bx:
    rec["gameTimeUTC"] = bx["game"].get("gameTimeUTC"); rec["teams"] = (bx["game"]["awayTeam"]["teamTricode"], bx["game"]["homeTeam"]["teamTricode"])

res["run_finished_local"] = datetime.datetime.now().isoformat()
path = OUT / f"{stamp}_cdn_nba.json"
path.write_text(json.dumps(res, indent=1, default=str))
print("wrote", path)
