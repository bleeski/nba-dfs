# THROWAWAY SPIKE: not engine code. Purpose: compare ESPN injuries blurbs with RotoWire's free news blurbs for the same players (is ESPN a RotoWire mirror, and how far behind?).
import json, re, sys, datetime, requests
from pathlib import Path
from bs4 import BeautifulSoup
OUT = Path(__file__).parent / "out"; stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
names = ["Vucevic", "Bane", "Anthony Black", "Isaac", "Bittle", "Graves"]
r = requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}, timeout=30)
espn = {}
for t in r.json().get("injuries", []):
    for i in t.get("injuries", []):
        n = i.get("athlete", {}).get("displayName", "")
        if any(x in n for x in names):
            espn[n] = {"date": i.get("date"), "status": i.get("status"), "short": i.get("shortComment")}
rw_file = sorted((OUT / "downloads" / "projection_pages").glob("*_rotowire_nba_news.html"))[-1]
soup = BeautifulSoup(rw_file.read_text(encoding="utf-8"), "lxml")
rw = {}
for it in soup.select("div.news-update"):
    txt = re.sub(r"\s+", " ", it.get_text(" ")).strip()
    for x in names:
        if x in txt and x not in rw:
            rw[x] = txt[:240]
res = {"espn_fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "espn": espn, "rotowire_page_file": rw_file.name, "rotowire": rw}
(OUT / f"{stamp}_espn_vs_rotowire_text.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=True))
