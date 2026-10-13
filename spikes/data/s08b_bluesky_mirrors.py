# THROWAWAY SPIKE: not engine code. Purpose: check recency of two Bluesky accounts found in s08 search (a Shams mirror bot and nba.com) to judge Bluesky as a late-news channel.
import json, time, datetime, requests
from pathlib import Path
OUT = Path(__file__).parent / "out"; stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
res = []
for h in ("shamsbot.bsky.social", "nba.com"):
    r = requests.get("https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed", params={"actor": h, "limit": 5}, headers={"User-Agent": "nba-dfs-spike"}, timeout=30)
    rec = {"handle": h, "status": r.status_code, "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    if r.status_code == 200:
        rec["posts"] = [(f["post"]["record"].get("createdAt"), f["post"]["record"].get("text", "")[:120]) for f in r.json().get("feed", [])]
    res.append(rec); print(json.dumps(rec, ensure_ascii=True)[:900]); time.sleep(1.5)
    if r.status_code in (403, 429): break
(OUT / f"{stamp}_bluesky_mirrors.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
