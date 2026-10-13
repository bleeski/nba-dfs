# THROWAWAY SPIKE: not engine code. Purpose: fetch a few public pages (one-time research, ~1 request per 2 seconds) from non-DraftKings sources and save raw HTML plus extracted text. Usage: python fetch_page.py <source> <name> <url> [<name> <url> ...]
import sys, os, time, datetime, re
import requests
from bs4 import BeautifulSoup

OUT = os.path.join(os.path.dirname(__file__), "out")
src = sys.argv[1]
DL = os.path.join(OUT, "downloads", src)
os.makedirs(DL, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) personal-research (one-time, low rate)"
args = sys.argv[2:]
for i in range(0, len(args), 2):
    name, url = args[i], args[i + 1]
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    base = os.path.join(DL, f"{stamp}_{name}")
    open(base + ".html", "wb").write(r.content)
    s = BeautifulSoup(r.content, "lxml")
    for t in s(["script", "style"]):
        t.decompose()
    txt = re.sub(r"\n\s*\n+", "\n", s.get_text("\n"))
    open(base + ".txt", "w", encoding="utf-8").write(txt)
    print(name, r.status_code, len(r.content), base + ".txt")
    time.sleep(2)
