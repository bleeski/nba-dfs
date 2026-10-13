# THROWAWAY SPIKE: not engine code. Purpose: offline consistency check of lobby JSON field meanings (mec vs "[N Entry Max]"/"[Single Entry]" name tags; mec vs 3% of field m; po vs m*a) using the one saved lobby file; no new requests.
import json, glob, os, re, collections, datetime
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
d = json.load(open(sorted(glob.glob(os.path.join(OUT, "downloads", "draftkings", "*_lobby_nba.json")))[-1], encoding="utf-8"))
C = [c for c in d["Contests"] if c["gameTypeId"] in (70, 81)]
L = []
tag = collections.Counter()
for c in C:
    m = re.search(r"\[(\d+) Entry Max\]", c["n"]); se = "[Single Entry]" in c["n"]
    if m: tag[("N Entry Max tag", int(m.group(1)) == c["mec"])] += 1
    if se: tag[("Single Entry tag", c["mec"] == 1)] += 1
L.append(f"name-tag vs mec agreement: {dict(tag)}")
three = collections.Counter()
for c in C:
    if c["mec"] > 1 and c["m"] > 20:
        three[("mec == min(150, floor(0.03*m))", c["mec"] == min(150, int(0.03 * c["m"])))] += 1
L.append(f"multi-entry contests, mec rule check: {dict(three)}")
bad = [(c["n"], c["m"], c["mec"]) for c in C if c["mec"] > 1 and c["m"] > 20 and c["mec"] != min(150, int(0.03 * c["m"]))][:8]
L.append(f"exceptions sample: {bad}")
nt_le_m = sum(c["nt"] <= c["m"] for c in C)
L.append(f"nt <= m for {nt_le_m} of {len(C)} contests (nt = entries so far)")
open(os.path.join(OUT, datetime.datetime.now().strftime("%Y%m%d-%H%M") + "_lobby_field_semantics.txt"), "w").write("\n".join(L))
print("\n".join(L))
