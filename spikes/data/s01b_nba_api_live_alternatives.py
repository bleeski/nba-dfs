# THROWAWAY SPIKE: not engine code. Purpose: test stats.nba.com alternatives to the blocked cdn.nba.com feeds (ScoreboardV3, PlayByPlayV3, BoxScoreSummaryV3 inactives) and retry GameRotation with a longer timeout.
import json, time, datetime
from pathlib import Path
from nba_api.stats.endpoints import scoreboardv3, playbyplayv3, boxscoresummaryv3, gamerotation, scheduleleaguev2
import pandas as pd

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
res = {"run_started_local": datetime.datetime.now().isoformat(), "calls": []}


def call(name, fn, post=None):
    t0 = time.time(); rec = {"name": name}
    try:
        ep = fn(); rec["latency_s"] = round(time.time() - t0, 2); rec["ok"] = True
        d = ep.get_dict()
        rec["top_keys"] = list(d.keys())[:10]
        frames = ep.get_data_frames()
        rec["frames"] = [{"rows": len(f), "cols": list(f.columns)[:45]} for f in frames[:8]]
        if post: rec["detail"] = post(ep, d, frames)
    except Exception as e:
        rec["latency_s"] = round(time.time() - t0, 2); rec["ok"] = False; rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    print(name, rec["ok"], rec["latency_s"], rec.get("error", ""), flush=True)
    res["calls"].append(rec); time.sleep(1.6)


def sb_post(ep, d, frames):
    games = d["scoreboard"]["games"]
    return {"gameDate": d["scoreboard"].get("gameDate"), "games": [(g["gameId"], g["gameStatusText"], g["awayTeam"]["teamTricode"], g["homeTeam"]["teamTricode"]) for g in games],
            "game_keys": list(games[0].keys()) if games else []}


call("ScoreboardV3 today (stats.nba.com)", lambda: scoreboardv3.ScoreboardV3(game_date="2026-10-13", league_id="00", timeout=30), sb_post)


def pbp_post(ep, d, frames):
    a = frames[0]
    subs = a[a["actionType"].str.lower() == "substitution"] if "actionType" in a else a.iloc[0:0]
    return {"n_actions": len(a), "n_subs": len(subs), "sample_sub": subs.head(2).to_dict(orient="records")}


call("PlayByPlayV3 preseason 0012600044", lambda: playbyplayv3.PlayByPlayV3(game_id="0012600044", timeout=30), pbp_post)


def sum_post(ep, d, frames):
    bs = d.get("boxScoreSummary", {})
    inact = []
    for side in ("homeTeam", "awayTeam"):
        t = bs.get(side, {})
        for k in t:
            if "nactive" in k.lower():
                inact.append({k: t[k][:4]})
    return {"summary_keys": list(bs.keys())[:40], "inactives_sample": inact, "homeTeam_keys": list(bs.get("homeTeam", {}).keys())}


call("BoxScoreSummaryV3 0022501190", lambda: boxscoresummaryv3.BoxScoreSummaryV3(game_id="0022501190", timeout=30), sum_post)


def rot_post(ep, d, frames):
    f = frames[0]
    return {"sample": f.head(3).to_dict(orient="records")}


call("GameRotation 0022501190 retry (timeout 60)", lambda: gamerotation.GameRotation(game_id="0022501190", league_id="00", timeout=60), rot_post)


def sched_post(ep, d, frames):
    df = frames[0].copy()
    df["dt"] = pd.to_datetime(df["gameDateTimeUTC"], utc=True, errors="coerce")
    reg = df[df.gameId.astype(str).str.startswith("002")]
    pre = df[df.gameId.astype(str).str.startswith("001")]
    tbd = reg[reg.get("homeTeam_teamId", 0) == 0] if "homeTeam_teamId" in reg else reg.iloc[0:0]
    return {"first_regular_utc": str(reg.dt.min()), "last_regular_utc": str(reg.dt.max()), "regular_games": len(reg), "regular_tbd_teams": int(len(tbd)),
            "preseason": len(pre), "first_regular_games": reg.sort_values("dt").head(3)[["gameId", "gameDateTimeUTC", "awayTeam_teamTricode", "homeTeam_teamTricode"]].to_dict(orient="records"),
            "gameSubtype_counts": reg["gameSubtype"].value_counts().to_dict() if "gameSubtype" in reg else None,
            "gameLabel_counts": reg["gameLabel"].value_counts().head(8).to_dict() if "gameLabel" in reg else None}


call("ScheduleLeagueV2 2026-27 (parsed dates)", lambda: scheduleleaguev2.ScheduleLeagueV2(league_id="00", season="2026-27", timeout=30), sched_post)

path = OUT / f"{stamp}_nba_api_live_alternatives.json"
path.write_text(json.dumps(res, indent=1, default=str)[:200000])
print("wrote", path)
