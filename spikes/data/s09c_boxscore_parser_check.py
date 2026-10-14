# THROWAWAY SPIKE: not engine code. Purpose: run the poller's exact raw BoxScoreTraditionalV3 request and parser on a FINISHED game (0012600044) to check that the empty in-game result tonight was real and not a parser bug.
import json, datetime, requests
from pathlib import Path
from nba_api.stats.library.http import STATS_HEADERS
OUT = Path(__file__).parent / "out"; stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
gid = "0012600044"
r = requests.get("https://stats.nba.com/stats/boxscoretraditionalv3", headers=STATS_HEADERS,
                 params={"GameID": gid, "LeagueID": "00", "StartPeriod": 0, "EndPeriod": 0, "StartRange": 0, "EndRange": 0, "RangeType": 0}, timeout=30)
res = {"gid": gid, "status": r.status_code, "bytes": len(r.content)}
if r.status_code == 200:
    bx = r.json()["boxScoreTraditional"]
    ps = []
    for side in ("awayTeam", "homeTeam"):
        for p in bx.get(side, {}).get("players", []):
            ps.append((bx[side].get("teamTricode"), p.get("familyName"), p.get("position"), p.get("comment"), p.get("statistics", {}).get("minutes")))
    starters = [p for p in ps if p[2]]
    res.update(n_players=len(ps), n_with_position=len(starters), starters=starters[:10], sample=ps[:3])
print(json.dumps(res, indent=1))
(OUT / f"{stamp}_boxscore_parser_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
