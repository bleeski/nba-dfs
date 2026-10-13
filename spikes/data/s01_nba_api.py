# THROWAWAY SPIKE: not engine code. Purpose: verify stats.nba.com (via nba_api) endpoints respond from this machine, measure latency, record fields and row counts.
import json, time, datetime, traceback, sys
from pathlib import Path

from nba_api.stats.endpoints import (
    scheduleleaguev2, leaguegamelog, playergamelogs, boxscoretraditionalv3,
    boxscoreadvancedv3, boxscoreusagev3, gamerotation, commonteamroster,
    leaguedashlineups, teamplayeronoffsummary, synergyplaytypes, leaguedashteamstats,
)

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
results = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}
SLEEP = 1.6  # stay under ~1 request/second


def call(name, fn):
    t0 = time.time()
    rec = {"name": name}
    try:
        ep = fn()
        rec["latency_s"] = round(time.time() - t0, 2)
        frames = ep.get_data_frames()
        rec["ok"] = True
        rec["frames"] = []
        for i, df in enumerate(frames[:4]):
            rec["frames"].append({
                "index": i, "rows": int(len(df)), "columns": list(df.columns)[:60],
                "sample": json.loads(df.head(2).to_json(orient="records", default_handler=str)),
            })
        rec["_df0"] = frames[0] if frames else None
    except Exception as e:
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["ok"] = False
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    print(f"{name}: ok={rec['ok']} latency={rec['latency_s']}s " + (str([f['rows'] for f in rec.get('frames', [])]) if rec['ok'] else rec['error']), flush=True)
    results["calls"].append(rec)
    time.sleep(SLEEP)
    return rec


T = 30
# 1. Schedule for the new season
r = call("ScheduleLeagueV2 2026-27", lambda: scheduleleaguev2.ScheduleLeagueV2(league_id="00", season="2026-27", timeout=T))
if r["ok"] and r["_df0"] is not None:
    df = r["_df0"]
    gid = df["gameId"].astype(str)
    r["summary"] = {
        "preseason_games(001)": int(gid.str.startswith("001").sum()),
        "regular_games(002)": int(gid.str.startswith("002").sum()),
        "first_regular_date": str(df.loc[gid.str.startswith("002"), "gameDate"].min()),
    }

# 2. Preseason league game log (this season) to see how fast completed games appear
r = call("LeagueGameLog 2026-27 Pre Season (team rows)", lambda: leaguegamelog.LeagueGameLog(season="2026-27", season_type_all_star="Pre Season", timeout=T))
pre_game = None
if r["ok"] and r["_df0"] is not None and len(r["_df0"]):
    df = r["_df0"]
    r["summary"] = {"min_date": str(df.GAME_DATE.min()), "max_date": str(df.GAME_DATE.max()), "games": int(df.GAME_ID.nunique())}
    pre_game = str(df.sort_values("GAME_DATE").iloc[-1].GAME_ID)

# 3. Last regular season player game logs (the core history table)
r = call("PlayerGameLogs 2025-26 Regular Season", lambda: playergamelogs.PlayerGameLogs(season_nullable="2025-26", season_type_nullable="Regular Season", timeout=60))
reg_game = None
if r["ok"] and r["_df0"] is not None and len(r["_df0"]):
    df = r["_df0"]
    r["summary"] = {"rows": int(len(df)), "players": int(df.PLAYER_ID.nunique()), "min_date": str(df.GAME_DATE.min()), "max_date": str(df.GAME_DATE.max()),
                    "has_MIN": "MIN" in df.columns, "has_NBA_FANTASY_PTS": "NBA_FANTASY_PTS" in df.columns}
    reg_game = str(df.sort_values("GAME_DATE").iloc[-1].GAME_ID)

# 4. Box scores for most recent preseason game (posting speed) and a regular game
for gid_label, gid in (("preseason", pre_game), ("regular", reg_game)):
    if not gid:
        continue
    call(f"BoxScoreTraditionalV3 {gid_label} {gid}", lambda gid=gid: boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=gid, timeout=T))
    if gid_label == "regular":
        call(f"BoxScoreAdvancedV3 {gid}", lambda gid=gid: boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=gid, timeout=T))
        call(f"BoxScoreUsageV3 {gid}", lambda gid=gid: boxscoreusagev3.BoxScoreUsageV3(game_id=gid, timeout=T))
        call(f"GameRotation {gid}", lambda gid=gid: gamerotation.GameRotation(game_id=gid, timeout=T))

# 5. Roster, lineups, on/off, play types, team stats
call("CommonTeamRoster BOS 2026-27", lambda: commonteamroster.CommonTeamRoster(team_id=1610612738, season="2026-27", timeout=T))
call("LeagueDashLineups 2025-26 5-man", lambda: leaguedashlineups.LeagueDashLineups(season="2025-26", group_quantity=5, timeout=60))
call("TeamPlayerOnOffSummary BOS 2025-26", lambda: teamplayeronoffsummary.TeamPlayerOnOffSummary(team_id=1610612738, season="2025-26", timeout=T))
call("SynergyPlayTypes 2025-26 Isolation offense players", lambda: synergyplaytypes.SynergyPlayTypes(season="2025-26", play_type_nullable="Isolation", player_or_team_abbreviation="P", type_grouping_nullable="offensive", season_type_all_star="Regular Season", timeout=T))
call("LeagueDashTeamStats 2025-26 Advanced", lambda: leaguedashteamstats.LeagueDashTeamStats(season="2025-26", measure_type_detailed_defense="Advanced", timeout=T))

# 6. History depth
r = call("PlayerGameLogs 1996-97 (history depth)", lambda: playergamelogs.PlayerGameLogs(season_nullable="1996-97", season_type_nullable="Regular Season", timeout=60))
r = call("LeagueGameLog 1983-84 player rows (history depth)", lambda: leaguegamelog.LeagueGameLog(season="1983-84", player_or_team_abbreviation="P", timeout=60))

for c in results["calls"]:
    c.pop("_df0", None)
results["run_finished_local"] = datetime.datetime.now().isoformat()
path = OUT / f"{stamp}_nba_api.json"
path.write_text(json.dumps(results, indent=1, default=str)[:400000])
print("wrote", path)
