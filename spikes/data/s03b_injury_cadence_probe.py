# THROWAWAY SPIKE: not engine code. Purpose: probe a few injury-report PDF time slots (HEAD-style small GETs) to learn publication cadence (15/30/60 min) and whether preseason reports exist.
import json, time, datetime
from pathlib import Path
import requests

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}
BASE = "https://ak-static.cms.nba.com/referee/injury/Injury-Report_{}.pdf"
slots = [
    # regular season 2026-03-15 (Sunday): test 15-minute and half-hour slots
    "2026-03-15_05_15PM", "2026-03-15_05_45PM", "2026-03-15_06_00PM", "2026-03-15_11_00AM",
    # last preseason (2025-10-10, Friday) and opening night 2025-10-21
    "2025-10-10_05_30PM", "2025-10-10_06_00PM", "2025-10-21_05_30PM",
    # this preseason: yesterday and today
    "2026-10-12_05_30PM", "2026-10-13_05_30PM",
]
recs = []
for sl in slots:
    url = BASE.format(sl)
    t0 = time.time()
    try:
        r = requests.head(url, headers=H, timeout=20, allow_redirects=True)
        recs.append({"slot_ET": sl, "status": r.status_code, "bytes": r.headers.get("Content-Length"), "last_modified": r.headers.get("Last-Modified"), "latency_s": round(time.time() - t0, 2)})
    except Exception as e:
        recs.append({"slot_ET": sl, "error": str(e)[:200]})
    print(recs[-1], flush=True)
    time.sleep(1.2)
(OUT / f"{stamp}_injury_cadence_probe.json").write_text(json.dumps(recs, indent=1))
