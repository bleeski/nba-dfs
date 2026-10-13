# THROWAWAY SPIKE: not engine code. Purpose: find the sportsdataverse ESPN NBA box score / pbp release assets and download ONE small parquet (read with pyarrow, never executed) to confirm columns, seasons, and freshness.
import json, time, datetime
from pathlib import Path
import requests
import pyarrow.parquet as pq

OUT = Path(__file__).parent / "out"
DL = OUT / "downloads" / "sportsdataverse"; DL.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
GH = {"User-Agent": "nba-dfs-spike", "Accept": "application/vnd.github+json"}
res = {"run_local": datetime.datetime.now().isoformat(), "tags": {}}
for tag in ("espn_nba_player_boxscores", "espn_nba_pbp", "espn_nba_schedules"):
    r = requests.get(f"https://api.github.com/repos/sportsdataverse/sportsdataverse-data/releases/tags/{tag}", headers=GH, timeout=30)
    rec = {"status": r.status_code, "ratelimit_remaining": r.headers.get("x-ratelimit-remaining")}
    if r.status_code == 200:
        a = sorted(r.json().get("assets", []), key=lambda x: x["name"])
        rec.update(n_assets=len(a), first=[x["name"] for x in a[:3]], last=[(x["name"], round(x["size"] / 1e6, 2), x["updated_at"]) for x in a[-5:]])
        res["tags"][tag] = rec
        if tag == "espn_nba_player_boxscores":
            pick = [x for x in a if x["name"].endswith(".parquet") and "2026" in x["name"]]
            if pick and pick[0]["size"] < 40e6:
                time.sleep(1.5)
                url = pick[0]["browser_download_url"]
                d = requests.get(url, headers={"User-Agent": "nba-dfs-spike"}, timeout=120)
                p = DL / pick[0]["name"]; p.write_bytes(d.content)
                t = pq.read_table(p)
                df = t.to_pandas()
                res["parquet"] = {"url": url, "status": d.status_code, "mb": round(len(d.content) / 1e6, 2), "rows": t.num_rows, "columns": t.column_names[:60],
                                  "date_min": str(df["game_date"].min()) if "game_date" in df else None, "date_max": str(df["game_date"].max()) if "game_date" in df else None,
                                  "season_types": df["season_type"].value_counts().to_dict() if "season_type" in df else None,
                                  "has_starter": "starter" in df.columns, "has_minutes": "minutes" in df.columns,
                                  "sample": json.loads(df.head(2).to_json(orient="records", default_handler=str))}
    else:
        res["tags"][tag] = rec
    print(tag, rec.get("status"), rec.get("n_assets"), flush=True)
    time.sleep(1.5)
(OUT / f"{stamp}_sportsdataverse_parquet.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in res.items() if k != "parquet"}, indent=1, default=str)[:3000])
print(json.dumps({k: v for k, v in res.get("parquet", {}).items() if k != "sample"}, indent=1, default=str)[:3000])
