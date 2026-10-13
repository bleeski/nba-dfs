# THROWAWAY SPIKE: not engine code. Purpose: check whether ESPN core API keeps prop markets for a PAST regular-season game (2026-03-15 MIN@OKC) (player points/reb/ast?) and whether athlete ids are attached.
import json, time, datetime, collections
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36", "Accept": "application/json"}
eid = "401810831"
url = f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/{eid}/competitions/{eid}/odds/100/propBets"
r = requests.get(url, headers=H, params={"limit": 1000}, timeout=30)
d = r.json()
items = d.get("items", [])
types = collections.Counter(i.get("type", {}).get("name") for i in items)
with_ath = [i for i in items if i.get("athlete")]
samp = [{"type": i["type"]["name"], "athlete": i.get("athlete", {}).get("$ref", "")[-60:], "target": i.get("current", {}).get("target", {}).get("displayValue"),
         "american": i.get("odds", {}).get("american"), "lastUpdated": i.get("lastUpdated")} for i in with_ath[:8]]
res = {"run_local": datetime.datetime.now().isoformat(), "url": url, "status": r.status_code, "count": d.get("count"), "pageCount": d.get("pageCount"),
       "n_items": len(items), "type_counts": dict(types), "n_with_athlete": len(with_ath), "sample_player_props": samp}
print(json.dumps(res, indent=1))
(OUT / f"{stamp}_espn_props_historical.json").write_text(json.dumps(res, indent=1))
