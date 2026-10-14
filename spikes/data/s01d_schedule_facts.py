# THROWAWAY SPIKE: not engine code. Purpose: one ScheduleLeagueV2 request to pull (1) the full Oct 20, 2026 opening-night schedule with ET tip times and (2) the remaining preseason dates Oct 13 to Oct 19 with game counts.
import json, datetime
from pathlib import Path
import pandas as pd
from nba_api.stats.endpoints import scheduleleaguev2

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
fetched = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
df = scheduleleaguev2.ScheduleLeagueV2(league_id="00", season="2026-27", timeout=30).get_data_frames()[0]
df["utc"] = pd.to_datetime(df["gameDateTimeUTC"], utc=True, errors="coerce")
df["et_from_utc"] = (df["utc"] - pd.Timedelta(hours=4)).dt.strftime("%Y-%m-%d %I:%M %p")  # EDT (UTC-4) applies through Nov 1, 2026
cols = ["gameId", "gameCode", "gameStatusText", "gameDateEst", "gameTimeEst", "gameDateTimeEst", "gameDateTimeUTC", "et_from_utc",
        "awayTeam_teamTricode", "homeTeam_teamTricode", "arenaName", "arenaCity", "gameLabel", "gameSubLabel", "postponedStatus"]
cols = [c for c in cols if c in df.columns]
gid = df["gameId"].astype(str)
reg = df[gid.str.startswith("002")].copy()
opening = reg[reg["et_from_utc"].str.startswith("2026-10-20")].sort_values("utc")
pre = df[gid.str.startswith("001")].copy()
pre["et_date"] = pre["et_from_utc"].str[:10]
remaining = pre[(pre["et_date"] >= "2026-10-13")].sort_values("utc")
res = {
    "fetched_utc": fetched,
    "opening_night_2026_10_20": opening[cols].to_dict(orient="records"),
    "regular_season_first_10": reg.sort_values("utc").head(10)[["gameId", "gameDateTimeUTC", "et_from_utc", "awayTeam_teamTricode", "homeTeam_teamTricode"]].to_dict(orient="records"),
    "preseason_counts_by_et_date_from_oct13": remaining.groupby("et_date").size().to_dict(),
    "preseason_games_from_oct13": remaining[["gameId", "et_from_utc", "gameStatusText", "awayTeam_teamTricode", "homeTeam_teamTricode", "arenaCity"]].to_dict(orient="records"),
    "last_preseason_game": remaining.tail(1)[["gameId", "et_from_utc", "awayTeam_teamTricode", "homeTeam_teamTricode"]].to_dict(orient="records"),
    "all_preseason_first_last_et": (pre.sort_values("utc")["et_from_utc"].iloc[0], pre.sort_values("utc")["et_from_utc"].iloc[-1]),
}
(OUT / f"{stamp}_schedule_facts.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res, indent=1, default=str))
