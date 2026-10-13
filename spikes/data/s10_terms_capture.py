# THROWAWAY SPIKE: not engine code. Purpose: save terms-of-use pages as text (one request each) and grep for exact phrases so memo quotes are verified word for word.
# Usage: python -I s10_terms_capture.py <name>=<url> ... ; then: python -I s10_terms_capture.py --grep <name> "<phrase>"
import sys, re, time, json, datetime
from pathlib import Path

TERMS = Path(__file__).parent / "out" / "downloads" / "terms"
TERMS.mkdir(parents=True, exist_ok=True)


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


if sys.argv[1] == "--grep":
    name, phrase = sys.argv[2], sys.argv[3]
    txt = (TERMS / f"{name}.txt").read_text(encoding="utf-8")
    i = txt.lower().find(norm(phrase).lower())
    print(json.dumps({"name": name, "phrase": phrase, "found": i >= 0, "context": txt[max(0, i - 150): i + len(phrase) + 150] if i >= 0 else None}, indent=1))
    sys.exit(0)

import requests
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}
for arg in sys.argv[1:]:
    name, url = arg.split("=", 1)
    try:
        r = requests.get(url, headers=H, timeout=30)
        ct = r.headers.get("Content-Type", "")
        if "pdf" in ct or r.content[:4] == b"%PDF":
            import pdfplumber, io
            (TERMS / f"{name}.pdf").write_bytes(r.content)
            with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                txt = norm(" ".join((pg.extract_text() or "") for pg in pdf.pages))
        elif "html" in ct:
            txt = norm(BeautifulSoup(r.text, "lxml").get_text(" "))
        else:
            txt = norm(r.text)
        (TERMS / f"{name}.txt").write_text(f"URL: {url}\nFETCHED: {datetime.datetime.now().isoformat()}\nSTATUS: {r.status_code}\n\n" + txt, encoding="utf-8")
        print(name, r.status_code, len(txt))
    except Exception as e:
        print(name, "ERROR", e)
    time.sleep(1.5)
