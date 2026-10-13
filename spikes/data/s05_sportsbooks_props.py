# THROWAWAY SPIKE: not engine code. Purpose: one request each to public sportsbook / pick'em JSON endpoints (DK Sportsbook, FanDuel, BetMGM, Caesars, Bovada, Pinnacle, Action Network, PrizePicks, Underdog) to record whether they answer from this machine. No keys, no logins. Stop a host on first 403/429.
import json, time, datetime
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
H = {"User-Agent": UA, "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9"}
targets = [
    ("dk_sportsbook_nba_league", "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648", {}),
    ("fanduel_nba_page", "https://sbapi.nj.sportsbook.fanduel.com/api/content-managed-page", {"page": "CUSTOM", "customPageId": "nba", "pbHorizontal": "false", "timezone": "America/New_York"}),
    ("betmgm_fixtures_no_key", "https://sports.nj.betmgm.com/cds-api/bettingoffer/fixtures", {"lang": "en-us", "country": "US", "sportIds": "7"}),
    ("caesars_schedule", "https://api.americanwagering.com/regions/us/locations/nj/brands/czr/sb/v4/sports/basketball/events/schedule", {}),
    ("bovada_nba_coupon", "https://www.bovada.lv/services/sports/event/coupon/events/A/description/basketball/nba", {"marketFilterId": "def", "preMatchOnly": "true", "lang": "en"}),
    ("pinnacle_arcadia_no_key", "https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/matchups", {}),
    ("actionnetwork_scoreboard", "https://api.actionnetwork.com/web/v1/scoreboard/nba", {"period": "game", "date": "20261013"}),
    ("prizepicks_projections", "https://api.prizepicks.com/projections", {"league_id": "7", "per_page": "250", "single_stat": "true"}),
    ("underdog_over_under_v5", "https://api.underdogfantasy.com/beta/v5/over_under_lines", {}),
]
res = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}
blocked_hosts = set()
s = requests.Session()
for name, url, params in targets:
    host = url.split("/")[2]
    if host in blocked_hosts:
        continue
    t0 = time.time(); rec = {"name": name, "url": url, "params": params}
    try:
        r = s.get(url, headers=H, params=params, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), ctype=r.headers.get("Content-Type"), server=r.headers.get("Server"),
                   cf=r.headers.get("cf-ray") is not None, body_head=r.text[:400])
        if r.status_code in (403, 429):
            blocked_hosts.add(host)
        if r.status_code == 200 and "json" in (r.headers.get("Content-Type") or ""):
            d = r.json()
            rec["top_keys"] = list(d.keys())[:15] if isinstance(d, dict) else f"list[{len(d)}]"
            # light per-source summaries
            if name.startswith("dk_"):
                rec["n_events"] = len(d.get("events", [])); rec["n_markets"] = len(d.get("markets", [])); rec["n_selections"] = len(d.get("selections", []))
                rec["events_sample"] = [(e.get("name"), e.get("startEventDate")) for e in d.get("events", [])[:5]]
            if name.startswith("prizepicks"):
                rec["n_projections"] = len(d.get("data", []))
                rec["sample"] = [{k: p["attributes"].get(k) for k in ("stat_type", "line_score", "start_time", "description")} for p in d.get("data", [])[:5]]
            if name.startswith("underdog"):
                rec["n_lines"] = len(d.get("over_under_lines", []))
                rec["sample"] = [(l.get("over_under", {}).get("title"), l.get("stat_value")) for l in d.get("over_under_lines", [])[:5]]
            if name.startswith("actionnetwork"):
                gs = d.get("games", []); rec["n_games"] = len(gs)
                if gs:
                    rec["game0_keys"] = list(gs[0].keys())[:40]; rec["odds_sample"] = json.dumps(gs[0].get("odds", [])[:2])[:800]
            if name.startswith("bovada"):
                evs = d[0].get("events", []) if isinstance(d, list) and d else []
                rec["n_events"] = len(evs); rec["events_sample"] = [e.get("description") for e in evs[:5]]
    except Exception as e:
        rec.update(error=f"{type(e).__name__}: {e}"[:300], latency_s=round(time.time() - t0, 2))
    print(name, rec.get("status"), rec.get("bytes"), rec.get("error", ""), flush=True)
    res["calls"].append(rec)
    time.sleep(1.5)
res["blocked_hosts"] = sorted(blocked_hosts)
(OUT / f"{stamp}_sportsbooks_props.json").write_text(json.dumps(res, indent=1, default=str))
