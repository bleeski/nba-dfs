# THROWAWAY SPIKE: not engine code. Purpose: re-fetch Daily Fantasy Fuel's free DK NBA projections page once (closer to tip) to see whether projections, the START column and the updated stamp fill in. One request per run.
import json, re, datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).parent / "out"
DL = OUT / "downloads" / "projection_pages"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
r = requests.get("https://www.dailyfantasyfuel.com/nba/projections/draftkings", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}, timeout=30)
res = {"fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "status": r.status_code, "bytes": len(r.content)}
if r.status_code == 200:
    (DL / f"{stamp}_dff_nba_dk_projections.html").write_text(r.text, encoding="utf-8")
    s = BeautifulSoup(r.text, "lxml")
    rows = s.find_all(attrs={"data-salary": True})
    proj = [x for x in rows if float(x.get("data-ppg_proj") or 0) > 0]
    attrs = sorted({a for x in rows for a in x.attrs if a.startswith("data-")})
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    m = re.search(r"Updated At:[^|]{0,40}", txt)
    res.update(n_rows=len(rows), n_with_projection=len(proj), updated=m.group(0) if m else None, data_attrs=attrs,
               start_like={a: sorted({x.get(a) for x in rows})[:8] for a in attrs if any(k in a for k in ("start", "depth", "inj", "confirm"))},
               sample=[{k: x.get(k) for k in ("data-name", "data-team", "data-salary", "data-ppg_proj", "data-inj", "data-depth_rank", "data-ou", "data-spread")} for x in (proj or rows)[:6]])
print(json.dumps(res, indent=1))
(OUT / f"{stamp}_dff_recheck.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
