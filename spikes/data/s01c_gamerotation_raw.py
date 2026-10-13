# THROWAWAY SPIKE: not engine code. Purpose: one raw request to stats.nba.com gamerotation to see why nba_api's GameRotation fails (timeout, then empty body).
import json, time, datetime, requests
from pathlib import Path
from nba_api.stats.library.http import STATS_HEADERS
OUT = Path(__file__).parent / "out"; stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
recs = []
for gid in ("0022501190", "0012600044"):
    t0 = time.time()
    try:
        r = requests.get("https://stats.nba.com/stats/gamerotation", params={"GameID": gid, "LeagueID": "00"}, headers=STATS_HEADERS, timeout=45)
        rec = {"gid": gid, "status": r.status_code, "latency_s": round(time.time()-t0, 2), "bytes": len(r.content), "ctype": r.headers.get("Content-Type"), "head": r.text[:300]}
    except Exception as e:
        rec = {"gid": gid, "error": f"{type(e).__name__}: {e}"[:300], "latency_s": round(time.time()-t0, 2)}
    print(rec, flush=True); recs.append(rec); time.sleep(2)
(OUT / f"{stamp}_gamerotation_raw.json").write_text(json.dumps(recs, indent=1))
