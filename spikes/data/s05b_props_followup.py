# THROWAWAY SPIKE: not engine code. Purpose: follow-up on endpoints that answered in s05: Pinnacle (matchup types, player-prop specials, prices), Action Network (props), Underdog (newer API version). Stop a host on first 403/429.
import json, time, datetime, collections
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36", "Accept": "application/json"}
res = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}
blocked = set()
s = requests.Session()


def get(name, url, params=None):
    host = url.split("/")[2]
    rec = {"name": name, "url": url, "params": params}
    if host in blocked:
        rec["skipped"] = "host blocked earlier"; res["calls"].append(rec); return rec, None
    t0 = time.time()
    try:
        r = s.get(url, headers=H, params=params, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), body_head=r.text[:300] if r.status_code != 200 else None)
        if r.status_code in (403, 429):
            blocked.add(host)
        d = r.json() if r.status_code == 200 else None
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:300]; d = None
    print(name, rec.get("status"), rec.get("bytes"), flush=True)
    res["calls"].append(rec); time.sleep(1.5)
    return rec, d


rec, m = get("pinnacle matchups NBA (487)", "https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/matchups")
if m:
    rec["n"] = len(m)
    rec["type_counts"] = dict(collections.Counter(x.get("type") for x in m))
    specials = [x for x in m if x.get("type") == "special"]
    rec["special_categories"] = dict(collections.Counter((x.get("special") or {}).get("category") for x in specials))
    rec["special_sample"] = [{"desc": (x.get("special") or {}).get("description"), "units": x.get("units"), "participants": [p.get("name") for p in x.get("participants", [])][:3], "startTime": x.get("startTime")} for x in specials[:6]]
    rec["matchup_sample"] = [{"id": x["id"], "participants": [p.get("name") for p in x.get("participants", [])], "startTime": x.get("startTime")} for x in m if x.get("type") == "matchup"][:4]
rec, mk = get("pinnacle straight markets NBA (487)", "https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/markets/straight")
if mk:
    rec["n"] = len(mk)
    rec["type_counts"] = dict(collections.Counter(x.get("type") for x in mk))
    rec["sample"] = mk[:3]

rec, an = get("actionnetwork props points (core_bet_type_27_points)", "https://api.actionnetwork.com/web/v1/leagues/4/props/core_bet_type_27_points", {"date": "20261013"})
if an:
    rec["top_keys"] = list(an.keys())[:20] if isinstance(an, dict) else type(an).__name__
    rec["sample"] = json.dumps(an)[:1200]

rec, ud = get("underdog over_under_lines v6", "https://api.underdogfantasy.com/beta/v6/over_under_lines")
if ud:
    rec["top_keys"] = list(ud.keys())[:20]
    lines = ud.get("over_under_lines", [])
    rec["n_lines"] = len(lines)
    apps = {a["id"]: a for a in ud.get("appearances", [])}
    players = {p["id"]: p for p in ud.get("players", [])}
    nba = []
    for l in lines:
        ou = l.get("over_under", {}); st = ou.get("appearance_stat", {})
        ap = apps.get(st.get("appearance_id"), {}); pl = players.get(ap.get("player_id"), {})
        if pl.get("sport_id") == "NBA":
            nba.append({"player": f"{pl.get('first_name')} {pl.get('last_name')}", "stat": st.get("display_stat"), "line": l.get("stat_value"), "status": l.get("status")})
    rec["n_nba_lines"] = len(nba)
    rec["nba_sample"] = nba[:10]
    rec["sports_seen"] = dict(collections.Counter(p.get("sport_id") for p in players.values()))

(OUT / f"{stamp}_props_followup.json").write_text(json.dumps(res, indent=1, default=str)[:200000])
print(json.dumps([{k: v for k, v in c.items() if k in ("name", "status", "n", "type_counts", "special_categories", "special_sample", "n_nba_lines", "nba_sample", "sports_seen", "top_keys", "body_head")} for c in res["calls"]], indent=1, default=str)[:6000])
