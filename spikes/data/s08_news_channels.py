# THROWAWAY SPIKE: not engine code. Purpose: test free late-news channels other than X: Bluesky public AppView, Reddit r/nba JSON, RotoWire RSS, NBA.com news RSS. One or two requests each; stop a host on first 403/429.
import json, time, datetime, re
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
res = {"run_local": datetime.datetime.now().isoformat(), "calls": []}
blocked = set()
s = requests.Session()


def get(name, url, params=None, headers=None):
    host = url.split("/")[2]
    rec = {"name": name, "url": url, "params": params}
    if host in blocked:
        rec["skipped"] = "host blocked"; res["calls"].append(rec); return rec, None
    t0 = time.time()
    try:
        r = s.get(url, params=params, headers=headers or {"User-Agent": UA}, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), ctype=r.headers.get("Content-Type"),
                   ratelimit=(r.headers.get("ratelimit-limit"), r.headers.get("ratelimit-remaining"), r.headers.get("x-ratelimit-remaining")))
        if r.status_code in (403, 429):
            blocked.add(host); rec["body_head"] = r.text[:300]
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:200]; r = None
    print(name, rec.get("status"), rec.get("bytes"), flush=True)
    res["calls"].append(rec); time.sleep(1.3)
    return rec, r


BSKY = "https://public.api.bsky.app/xrpc"
rec, r = get("bluesky searchActors 'nba injury'", f"{BSKY}/app.bsky.actor.searchActors", {"q": "nba injuries", "limit": 15})
if r is not None and r.status_code == 200:
    rec["actors"] = [(a.get("handle"), a.get("displayName"), a.get("followersCount")) for a in r.json().get("actors", [])]
for handle in ("underdognba.bsky.social", "shamscharania.bsky.social"):
    rec, r = get(f"bluesky profile {handle}", f"{BSKY}/app.bsky.actor.getProfile", {"actor": handle})
    if r is not None and r.status_code == 200:
        p = r.json(); rec["profile"] = {k: p.get(k) for k in ("handle", "displayName", "followersCount", "postsCount")}
        rec2, r2 = get(f"bluesky feed {handle}", f"{BSKY}/app.bsky.feed.getAuthorFeed", {"actor": handle, "limit": 5})
        if r2 is not None and r2.status_code == 200:
            rec2["posts"] = [(f["post"]["record"].get("createdAt"), f["post"]["record"].get("text", "")[:140]) for f in r2.json().get("feed", [])]
    else:
        rec["body_head"] = r.text[:200] if r is not None else None

rec, r = get("reddit r/nba new.json (unauthenticated)", "https://www.reddit.com/r/nba/new.json", {"limit": 5}, headers={"User-Agent": "windows:nba-dfs-spike:0.1 (personal research)"})
if r is not None and r.status_code == 200:
    try:
        rec["posts"] = [(c["data"].get("created_utc"), c["data"].get("title", "")[:120]) for c in r.json()["data"]["children"]]
    except Exception as e:
        rec["parse_error"] = str(e)[:100]; rec["body_head"] = r.text[:200]
elif r is not None:
    rec["body_head"] = r.text[:300]

for name, url in (("rotowire rss nba", "https://www.rotowire.com/rss/news.php?sport=NBA"), ("nba.com news rss", "https://www.nba.com/news/rss.xml")):
    rec, r = get(name, url)
    if r is not None and r.status_code == 200:
        items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
        rec["n_items"] = len(items)
        rec["sample"] = [(re.search(r"<pubDate>(.*?)</pubDate>", i).group(1) if re.search(r"<pubDate>(.*?)</pubDate>", i) else None,
                          (re.search(r"<title>(.*?)</title>", i, re.S).group(1) if re.search(r"<title>(.*?)</title>", i, re.S) else "")[:120]) for i in items[:5]]
    elif r is not None:
        rec["body_head"] = r.text[:200]

(OUT / f"{stamp}_news_channels.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res, indent=1, default=str, ensure_ascii=True)[:6000])
