# THROWAWAY SPIKE: not engine code. Purpose: find the official NBA injury report PDF pattern and cadence, test if preseason reports exist, and test pdfplumber parsing on one archived and one current PDF.
import json, re, time, datetime, sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).parent / "out"
DL = OUT / "downloads" / "nba_injury_pdf"
DL.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}
res = {"run_started_local": datetime.datetime.now().isoformat(), "pages": [], "probes": [], "parsed": []}
s = requests.Session()


def get(url, **kw):
    t0 = time.time()
    try:
        r = s.get(url, headers=H, timeout=30, **kw)
        return r, round(time.time() - t0, 2)
    except Exception as e:
        return e, round(time.time() - t0, 2)
    finally:
        time.sleep(1.2)


links_all = []
for page in ("https://official.nba.com/nba-injury-report-2026-27-season/", "https://official.nba.com/nba-injury-report-2025-26-season/"):
    r, lat = get(page)
    rec = {"url": page, "latency_s": lat}
    if isinstance(r, Exception):
        rec["error"] = str(r)[:200]
    else:
        rec["status"] = r.status_code
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            links = [a["href"] for a in soup.find_all("a", href=True) if "Injury-Report" in a["href"] or a["href"].lower().endswith(".pdf")]
            rec["n_pdf_links"] = len(links)
            rec["first_links"] = links[:8]
            rec["last_links"] = links[-8:]
            txt = soup.get_text(" ", strip=True)
            m = re.search(r".{0,300}(updated|publish|every|hour|minute).{0,300}", txt, re.I)
            rec["cadence_text"] = m.group(0)[:600] if m else None
            links_all += links
    res["pages"].append(rec)
    print(rec.get("url"), rec.get("status"), rec.get("n_pdf_links"), flush=True)

# Learn the time-slot pattern from the links (e.g. 15-minute or hourly)
times = {}
for l in links_all:
    m = re.search(r"Injury-Report_(\d{4}-\d{2}-\d{2})_(\d{2})_?(\d{2})?(AM|PM)", l)
    if m:
        times.setdefault(m.group(1), []).append(f"{m.group(2)}:{m.group(3) or '00'}{m.group(4)}")
res["dates_seen"] = len(times)
res["sample_dates"] = {k: sorted(set(v))[:40] for k, v in list(times.items())[:3]}
res["latest_dates"] = sorted(times)[-5:]
res["minute_values_seen"] = sorted({t.split(":")[1][:2] for v in times.values() for t in v})

# Probe: today's (preseason) report at a few plausible slots, and a known archived regular-season slot
probes = []
today = datetime.date.today().isoformat()
for slot in ("01_00PM", "05_00PM", "03_30PM"):
    probes.append(f"https://ak-static.cms.nba.com/referee/injury/Injury-Report_{today}_{slot}.pdf")
pdf_to_parse = []
for url in probes:
    r, lat = get(url, stream=False)
    rec = {"url": url, "latency_s": lat}
    if isinstance(r, Exception):
        rec["error"] = str(r)[:200]
    else:
        rec.update(status=r.status_code, bytes=len(r.content), ctype=r.headers.get("Content-Type"), last_modified=r.headers.get("Last-Modified"))
        if r.status_code == 200 and r.content[:4] == b"%PDF":
            p = DL / url.rsplit("/", 1)[1]; p.write_bytes(r.content); pdf_to_parse.append(str(p))
    res["probes"].append(rec)
    print(url, rec.get("status"), rec.get("bytes"), flush=True)

# One archived regular-season PDF from the page links (pick a mid-season 5 PM-ish one), else a guessed URL
arch = [l for l in links_all if "2026-0" in l or "2025-1" in l]
pick = None
for l in arch:
    if "2026-03-1" in l and ("05_00PM" in l or "05_30PM" in l or "06_00PM" in l):
        pick = l; break
pick = pick or (arch[len(arch) // 2] if arch else "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-03-15_05_30PM.pdf")
r, lat = get(pick)
rec = {"url": pick, "latency_s": lat}
if not isinstance(r, Exception):
    rec.update(status=r.status_code, bytes=len(r.content), last_modified=r.headers.get("Last-Modified"))
    if r.status_code == 200 and r.content[:4] == b"%PDF":
        p = DL / pick.rsplit("/", 1)[1]; p.write_bytes(r.content); pdf_to_parse.append(str(p))
res["probes"].append(rec)
print(pick, rec.get("status"), rec.get("bytes"), flush=True)

(OUT / f"{stamp}_injury_report_fetch.json").write_text(json.dumps(res, indent=1, default=str))
print("pdfs:", pdf_to_parse)
