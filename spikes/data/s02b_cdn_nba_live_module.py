# THROWAWAY SPIKE: not engine code. Purpose: one diagnostic request to cdn.nba.com liveData using nba_api's own live-module headers, after s02 got Akamai 403s with custom headers.
import json, time, datetime
from pathlib import Path
from nba_api.live.nba.endpoints import scoreboard

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
rec = {"run_local": datetime.datetime.now().isoformat(), "name": "nba_api.live ScoreBoard (cdn.nba.com todaysScoreboard_00.json)"}
t0 = time.time()
try:
    sb = scoreboard.ScoreBoard(timeout=20)
    d = sb.get_dict()
    rec.update(ok=True, latency_s=round(time.time() - t0, 2), gameDate=d["scoreboard"]["gameDate"],
               games=[(g["gameId"], g["gameStatusText"], g["awayTeam"]["teamTricode"], g["homeTeam"]["teamTricode"]) for g in d["scoreboard"]["games"]])
except Exception as e:
    rec.update(ok=False, latency_s=round(time.time() - t0, 2), error=f"{type(e).__name__}: {str(e)[:400]}")
print(json.dumps(rec, indent=1))
(OUT / f"{stamp}_cdn_nba_live_module.json").write_text(json.dumps(rec, indent=1))
