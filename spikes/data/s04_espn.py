# THROWAWAY SPIKE: not engine code. Purpose: verify ESPN public JSON (scoreboard+odds, injuries, roster, depth chart, news, summary, core-API odds/props, historical odds) from this machine.
import json, time, datetime
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36", "Accept": "application/json"}
SITE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
CORE = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba"
res = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}
s = requests.Session()


def get(name, url, params=None):
    t0 = time.time(); rec = {"name": name, "url": url, "params": params}
    try:
        r = s.get(url, headers=H, params=params, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), cache_control=r.headers.get("Cache-Control"), age=r.headers.get("Age"))
        data = r.json() if r.status_code == 200 else None
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:300]; data = None
    print(name, rec.get("status"), rec.get("latency_s"), rec.get("bytes"), flush=True)
    res["calls"].append(rec); time.sleep(1.2)
    if rec.get("status") in (403, 429):
        raise SystemExit(f"stop on {rec['status']}")
    return rec, data


# 1 Scoreboard today with odds
rec, sb = get("scoreboard today", f"{SITE}/scoreboard", {"dates": "20261013"})
ev_today = None
if sb:
    evs = sb.get("events", [])
    rec["season"] = sb.get("season") or (sb.get("leagues") or [{}])[0].get("season")
    rec["n_events"] = len(evs)
    if evs:
        ev_today = evs[0]
        c = evs[0]["competitions"][0]
        rec["event0"] = {"id": evs[0]["id"], "name": evs[0]["name"], "date": evs[0]["date"], "seasonType": evs[0].get("season", {}).get("type")}
        rec["event0_odds"] = c.get("odds")
        rec["competitor_keys"] = list(c["competitors"][0].keys())
        rec["n_events_with_odds"] = sum(1 for e in evs if e["competitions"][0].get("odds"))

# 2 Injuries (league-wide)
rec, inj = get("injuries", f"{SITE}/injuries")
if inj:
    teams = inj.get("injuries", [])
    rec["n_teams"] = len(teams)
    rec["n_injuries"] = sum(len(t.get("injuries", [])) for t in teams)
    for t in teams:
        if t.get("injuries"):
            i0 = t["injuries"][0]
            rec["sample"] = {"team": t.get("displayName"), "status": i0.get("status"), "date": i0.get("date"), "shortComment": i0.get("shortComment"), "longComment": (i0.get("longComment") or "")[:200],
                             "type": i0.get("type"), "details": i0.get("details"), "athlete": i0.get("athlete", {}).get("displayName")}
            break
    rec["status_values"] = sorted({i.get("status") for t in teams for i in t.get("injuries", [])})
    rec["latest_dates"] = sorted([i.get("date") for t in teams for i in t.get("injuries", []) if i.get("date")])[-3:]

# 3 Roster (BOS = 2)
rec, ro = get("roster BOS", f"{SITE}/teams/2/roster")
if ro:
    ath = ro.get("athletes", [])
    rec["n_athletes"] = len(ath)
    if ath:
        a = ath[0]
        rec["athlete_keys"] = list(a.keys())
        rec["sample"] = {k: a.get(k) for k in ("id", "displayName", "position", "status", "injuries")}

# 4 Depth chart (core API, season year 2027 = 2026-27)
rec, dc = get("depthchart BOS (core)", f"{CORE}/seasons/2027/teams/2/depthcharts")
if dc:
    rec["count"] = dc.get("count"); items = dc.get("items", [])
    if items:
        pos = items[0].get("positions", {})
        rec["positions"] = list(pos.keys())
        k0 = list(pos.keys())[0] if pos else None
        rec["sample_pos"] = {k0: [ (x.get("rank"), x.get("athlete", {}).get("$ref", "")[-40:]) for x in pos[k0].get("athletes", [])[:3]]} if k0 else None

# 5 News
rec, nw = get("news", f"{SITE}/news", {"limit": 10})
if nw:
    arts = nw.get("articles", [])
    rec["n"] = len(arts)
    rec["sample"] = [(a.get("published"), a.get("type"), a.get("headline")) for a in arts[:6]]

# 6 Summary for today's first event (injuries, pickcenter, predictor)
if ev_today:
    rec, sm = get("summary today event0", f"{SITE}/summary", {"event": ev_today["id"]})
    if sm:
        rec["keys"] = list(sm.keys())
        rec["pickcenter"] = sm.get("pickcenter")
        rec["injuries_blocks"] = len(sm.get("injuries", []))
        rec["predictor"] = sm.get("predictor")

# 7 Core odds for today's event, and prop bets
if ev_today:
    eid = ev_today["id"]
    rec, od = get("core odds today event0", f"{CORE}/events/{eid}/competitions/{eid}/odds")
    prov = None
    if od:
        rec["count"] = od.get("count")
        rec["providers"] = [(i.get("provider", {}).get("id"), i.get("provider", {}).get("name"), i.get("details"), i.get("overUnder"), i.get("spread")) for i in od.get("items", [])]
        prov = od["items"][0]["provider"]["id"] if od.get("items") else None
    if prov:
        rec, pb = get("core propBets today event0", f"{CORE}/events/{eid}/competitions/{eid}/odds/{prov}/propBets", {"limit": 50})
        if pb:
            rec["count"] = pb.get("count"); its = pb.get("items", [])
            rec["sample"] = json.dumps(its[:2])[:1500]

# 8 Historical: a regular-season date last season, then core odds for one game (closing lines?)
rec, hsb = get("scoreboard 2026-03-15", f"{SITE}/scoreboard", {"dates": "20260315"})
if hsb and hsb.get("events"):
    he = hsb["events"][0]; hid = he["id"]
    rec["event0"] = (hid, he["name"]); rec["event0_odds_on_scoreboard"] = he["competitions"][0].get("odds")
    rec, hod = get("core odds 2026-03-15 event0", f"{CORE}/events/{hid}/competitions/{hid}/odds")
    if hod:
        rec["count"] = hod.get("count")
        its = hod.get("items", [])
        rec["providers"] = [(i.get("provider", {}).get("id"), i.get("provider", {}).get("name"), i.get("details"), i.get("overUnder"), i.get("spread")) for i in its]
        if its:
            i0 = its[0]
            rec["item0_keys"] = list(i0.keys())
            rec["item0_open_close"] = {k: i0.get(k) for k in ("open", "close", "current") if k in i0}
    # one older season to test depth
    rec, osb = get("scoreboard 2019-01-15", f"{SITE}/scoreboard", {"dates": "20190115"})
    if osb and osb.get("events"):
        oe = osb["events"][0]; oid = oe["id"]
        rec["event0"] = (oid, oe["name"])
        rec, ood = get("core odds 2019-01-15 event0", f"{CORE}/events/{oid}/competitions/{oid}/odds")
        if ood:
            rec["count"] = ood.get("count")
            rec["providers"] = [(i.get("provider", {}).get("id"), i.get("provider", {}).get("name"), i.get("details"), i.get("overUnder")) for i in ood.get("items", [])]

res["run_finished_local"] = datetime.datetime.now().isoformat()
p = OUT / f"{stamp}_espn.json"
p.write_text(json.dumps(res, indent=1, default=str)[:300000])
print("wrote", p)
