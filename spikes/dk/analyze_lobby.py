# THROWAWAY SPIKE: not engine code. Purpose: analyze the ONE already-downloaded DK NBA lobby JSON (no new requests) for contest fields, field sizes, max-entries-per-user, entry fees, implied rake, and payoutDescriptionMetadata depth, by game type and entry-limit bucket.
import json, sys, os, re, collections, datetime, statistics, glob

OUT = os.path.join(os.path.dirname(__file__), "out")
src = sorted(glob.glob(os.path.join(OUT, "downloads", "draftkings", "*_lobby_nba.json")))[-1]
d = json.load(open(src, encoding="utf-8"))
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
def p(*a): L.append(" ".join(str(x) for x in a))

C = d["Contests"]
p("source:", os.path.basename(src), "contests:", len(C))
p("all contest keys:", sorted(C[0].keys()))
# key meanings by inspection of examples
ex = [c for c in C if c["gameTypeId"] in (70, 81)][:3]
for c in ex:
    p("example:", {k: c[k] for k in ("n", "id", "dg", "gameType", "m", "mec", "a", "po", "nt", "ec", "uc", "tmpl", "sdstring", "attr", "pd")})
pdm = collections.Counter(len(c.get("payoutDescriptionMetadata") or []) for c in C)
p("payoutDescriptionMetadata list lengths:", dict(pdm))
longest = max(C, key=lambda c: len(c.get("payoutDescriptionMetadata") or []))
p("longest payoutDescriptionMetadata example:", longest["n"], json.dumps(longest["payoutDescriptionMetadata"])[:600])

def bucket(c):
    mec, m = c["mec"], c["m"]
    if m == 2: return "H2H (2)"
    if m <= 20 and mec == 1: return "small SE (<=20)"
    if mec == 1: return "single-entry"
    if mec <= 3: return "3-max"
    if mec <= 20: return "<=20-max"
    if mec <= 150: return "<=150-max"
    return ">150-max"

rows = collections.defaultdict(list)
for c in C:
    if c["gameTypeId"] not in (70, 81):
        continue
    rows[(c["gameType"], bucket(c))].append(c)
p("\n=== Classic(70) and Showdown(81) contests by entry-limit bucket: count | field size m (min/median/max) | entry fee a (min/median/max) | implied rake 1-po/(m*a) median (only cash prize pools, a>0)")
for k in sorted(rows):
    cs = rows[k]
    ms = [c["m"] for c in cs]; fees = [c["a"] for c in cs]
    rk = [1 - c["po"] / (c["m"] * c["a"]) for c in cs if c["a"] > 0 and c["po"] and not c.get("tix")]
    p(k, len(cs), "| m", min(ms), int(statistics.median(ms)), max(ms), "| a", min(fees), statistics.median(fees), max(fees),
      "| rake med", round(statistics.median(rk), 3) if rk else None, "| rake min/max", (round(min(rk), 3), round(max(rk), 3)) if rk else None)

p("\n=== Largest Classic and Showdown GPPs (by prize pool), per draft group")
for gt in (70, 81):
    top = sorted([c for c in C if c["gameTypeId"] == gt], key=lambda c: -c["po"])[:8]
    for c in top:
        p(gt, c["dg"], c["sdstring"], "|", c["n"], "| m", c["m"], "mec", c["mec"], "a", c["a"], "po", c["po"], "| top prize:", (c.get("payoutDescriptionMetadata") or [{}])[0].get("PayoutDescription"))

p("\n=== Opening-night related contest names (contain 'Opening' or '10-20')")
for c in C:
    if re.search(r"Opening|10-20", c["n"]):
        p(c["id"], c["dg"], c["gameType"], c["n"], "m", c["m"], "mec", c["mec"], "a", c["a"], "po", c["po"], "nt", c["nt"])
p("\n=== attr keys seen:", dict(collections.Counter(k for c in C for k in (c.get("attr") or {}))))
p("=== WNBA contests in sport=NBA lobby:", sum(1 for c in C if "WNBA" in c["n"]))
outp = os.path.join(OUT, f"{stamp}_lobby_analysis.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))

# --- appended: top-prize share from contest names like "[$200K to 1st]" (no new requests)
def money(s):
    s = s.replace(",", "").replace("$", "")
    mult = 1000 if s.endswith("K") else (1_000_000 if s.endswith("M") else 1)
    return float(s.rstrip("KM")) * mult
L2 = ["\n=== Top-prize share of prize pool, from names containing '[$X to 1st]' (Classic=70, Showdown=81)"]
for c in sorted(C, key=lambda c: -c["po"]):
    m = re.search(r"\[\$([\d.,]+[KM]?) to 1st\]", c["n"])
    if m and c["gameTypeId"] in (70, 81) and c["po"]:
        first = money(m.group(1))
        L2.append(f"{c['gameTypeId']} | {c['n'].strip()[:70]:70s} | m={c['m']:6d} mec={c['mec']:3d} fee={c['a']:>6} pool={c['po']:>9.0f} | 1st={first:>8.0f} = {first / c['po']:.1%} of pool, {first / c['a']:.0f}x fee")
open(outp.replace("_lobby_analysis", "_lobby_top_prize_share"), "w", encoding="utf-8").write("\n".join(L2))
print("\n".join(L2))
