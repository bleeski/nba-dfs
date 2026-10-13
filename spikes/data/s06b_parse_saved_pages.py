# THROWAWAY SPIKE: not engine code. Purpose: parse (read only) the HTML pages saved by s06 to see what usable data each holds. Inputs are untrusted downloads; run with python -I.
import json, re, sys, datetime
from pathlib import Path
from bs4 import BeautifulSoup

D = Path(sys.argv[1])
OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
res = {}


def load(pattern):
    fs = sorted(D.glob(pattern))
    return BeautifulSoup(fs[-1].read_text(encoding="utf-8"), "lxml") if fs else None


# Basketball Monster lineups
s = load("*_basketballmonster_lineups.html")
if s:
    tables = s.find_all("table")
    out = []
    for t in tables[:3]:
        rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in t.find_all("tr")]
        out.append({"n_rows": len(rows), "rows": rows[:8]})
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    i = txt.find("Lineups")
    res["basketballmonster_lineups"] = {"tables": out, "status_words": sorted(set(re.findall(r"(Confirmed|Expected|Projected|Questionable|Out|GTD|Probable)", txt)))[:10],
                                        "text_mid": txt[i:i + 900]}

# DailyFantasyFuel projections
s = load("*_dff_nba_dk_projections.html")
if s:
    rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in s.find_all("tr")]
    data_attrs = [tr.attrs for tr in s.find_all("tr")[:4]]
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    i = txt.lower().find("projections")
    res["dff"] = {"rows": rows[:8], "tr_attrs_sample": data_attrs, "slate_text": re.findall(r"(No (?:slates|games|projections)[^.]{0,80})", txt, re.I)[:3], "text_mid": txt[i:i + 600]}

# DARKO
s = load("*_darko_home.html")
if s:
    rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in s.find_all("tr")]
    links = sorted({a["href"] for a in s.find_all("a", href=True) if a["href"].startswith("/") or "darko" in a["href"]})[:60]
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    res["darko"] = {"header_and_rows": rows[:5], "n_rows": len(rows), "links": links,
                    "mentions": {k: bool(re.search(k, txt, re.I)) for k in ("download", "csv", "api", "terms", "license", "daily", "minutes", "projection")}}

# RotoWire news
s = load("*_rotowire_nba_news.html")
if s:
    items = s.select("div.news-update") or s.select("[class*=news-update]")
    sample = []
    for it in items[:6]:
        sample.append(re.sub(r"\s+", " ", it.get_text(" "))[:260])
    times = re.findall(r"(\d{1,2}/\d{1,2}/\d{4},? ?\d{1,2}:\d{2} ?[AP]M|\d+ (?:minutes?|hours?) ago)", s.get_text(" "))[:10]
    res["rotowire_news"] = {"n_items": len(items), "sample": sample, "time_strings": times}

(OUT / f"{stamp}_parse_saved_pages.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False)[:9000])
