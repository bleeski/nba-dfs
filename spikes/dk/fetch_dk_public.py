# THROWAWAY SPIKE: not engine code. Purpose: make a handful of read-only GET requests (about 1 per second) to public DraftKings pages/JSON and save raw responses for the R6 memo. Usage: python fetch_dk_public.py <name> <url> [<name> <url> ...]
import sys, os, time, datetime, json
import requests

OUT = os.path.join(os.path.dirname(__file__), "out")
DL = os.path.join(OUT, "downloads", "draftkings")
os.makedirs(DL, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-spike (personal, read-only, ~1 req/s)"
log = []
args = sys.argv[1:]
for i in range(0, len(args), 2):
    name, url = args[i], args[i + 1]
    t0 = time.time()
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json, text/html;q=0.9"}, timeout=20)
        ctype = r.headers.get("content-type", "")
        ext = "json" if "json" in ctype else ("html" if "html" in ctype else "txt")
        path = os.path.join(DL, f"{stamp}_{name}.{ext}")
        with open(path, "wb") as fh:
            fh.write(r.content)
        log.append({"name": name, "url": url, "status": r.status_code, "ctype": ctype, "bytes": len(r.content), "saved": path,
                    "ratelimit_headers": {k: v for k, v in r.headers.items() if "rate" in k.lower() or "retry" in k.lower()}})
    except Exception as e:
        log.append({"name": name, "url": url, "error": repr(e)})
    time.sleep(max(0, 1.2 - (time.time() - t0)))
logp = os.path.join(OUT, f"{stamp}_fetchlog_{args[0]}.json")
with open(logp, "w") as fh:
    json.dump(log, fh, indent=1)
print(json.dumps(log, indent=1))
