# THROWAWAY SPIKE: not engine code. Purpose: check robots.txt, then fetch ONE page each from free NBA projection / lineup / injury sites (Basketball Monster, DailyFantasyFuel, FantasyPros, DARKO, RotoWire news) and record whether usable data is in the static HTML.
import json, time, datetime, re
from pathlib import Path
from urllib import robotparser
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).parent / "out"
DL = OUT / "downloads" / "projection_pages"
DL.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
H = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}
pages = [
    ("basketballmonster_lineups", "https://basketballmonster.com/nbalineups.aspx"),
    ("basketballmonster_injuries", "https://basketballmonster.com/nbainjuries.aspx"),
    ("dff_nba_dk_projections", "https://www.dailyfantasyfuel.com/nba/projections/draftkings"),
    ("fantasypros_nba_dk_projections", "https://www.fantasypros.com/daily-fantasy/nba/draftkings-projections.php"),
    ("darko_home", "https://darko.app/"),
    ("rotowire_nba_news", "https://www.rotowire.com/basketball/news.php"),
]
res = {"run_started_local": datetime.datetime.now().isoformat(), "pages": []}
robots_cache = {}
s = requests.Session()
for name, url in pages:
    host = url.split("/")[2]
    rec = {"name": name, "url": url}
    if host not in robots_cache:
        rp = robotparser.RobotFileParser()
        try:
            rr = s.get(f"https://{host}/robots.txt", headers=H, timeout=20)
            rp.parse(rr.text.splitlines()) if rr.status_code == 200 else rp.parse([])
            robots_cache[host] = (rp, rr.status_code)
            (OUT / "downloads" / "terms" / f"{host}_robots.txt").write_text(rr.text[:20000], encoding="utf-8")
        except Exception as e:
            robots_cache[host] = (None, str(e)[:100])
        time.sleep(1.2)
    rp, rstat = robots_cache[host]
    rec["robots_status"] = rstat
    rec["robots_allows_generic_ua"] = rp.can_fetch("*", url) if rp else None
    if rp and not rp.can_fetch("*", url):
        rec["skipped"] = "robots.txt disallows"; res["pages"].append(rec); print(name, "robots disallow"); continue
    t0 = time.time()
    try:
        r = s.get(url, headers=H, timeout=30)
        rec.update(status=r.status_code, latency_s=round(time.time() - t0, 2), bytes=len(r.content), final_url=r.url)
        if r.status_code == 200:
            (DL / f"{stamp}_{name}.html").write_text(r.text, encoding="utf-8")
            soup = BeautifulSoup(r.text, "lxml")
            rec["title"] = soup.title.get_text(strip=True) if soup.title else None
            rec["n_tables"] = len(soup.find_all("table"))
            rec["n_tr"] = len(soup.find_all("tr"))
            rec["text_head"] = re.sub(r"\s+", " ", soup.get_text(" "))[:700]
            rec["mentions_login_or_premium"] = bool(re.search(r"(subscribe|premium|log ?in to view|members only)", r.text, re.I))
            rec["has_next_data"] = "__NEXT_DATA__" in r.text
            rec["script_json_hints"] = re.findall(r"(projections?[\w/.-]*\.json|/api/[\w/.-]+)", r.text)[:10]
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:200]
    print(name, rec.get("status"), rec.get("bytes"), rec.get("n_tr"), flush=True)
    res["pages"].append(rec)
    time.sleep(1.5)
(OUT / f"{stamp}_projection_pages.json").write_text(json.dumps(res, indent=1, default=str))
