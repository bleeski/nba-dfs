# THROWAWAY SPIKE: not engine code. Purpose: in local DK Showdown standings files, test whether CPT FPTS == 1.5 x FLEX/UTIL FPTS exactly for every player listed at both slots (cross-sport evidence for whether the Captain multiplier also applies to bonuses).
import zipfile, glob, io, csv, os, sys, datetime

DL = r"C:\Users\benja\Downloads"
OUT = os.path.join(os.path.dirname(__file__), "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
for f in sorted(glob.glob(os.path.join(DL, "contest-standings-*.zip"))):
    z = zipfile.ZipFile(f)
    rows = list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode("utf-8-sig"))))
    right = [r[7:11] for r in rows[1:] if len(r) > 10 and r[7]]
    slots = {r[1] for r in right}
    if "CPT" not in slots:
        continue
    fp = {}
    for name, slot, pct, pts in right:
        fp.setdefault(name, {})[slot] = float(pts)
    p(f"=== {os.path.basename(f)}")
    exact = off = 0
    for name, d in sorted(fp.items(), key=lambda t: -max(t[1].values())):
        if "CPT" in d and ("FLEX" in d or "UTIL" in d):
            u = d.get("FLEX", d.get("UTIL"))
            ok = abs(d["CPT"] - 1.5 * u) < 0.006
            exact += ok; off += (not ok)
            p(f"  {name:28s} UTIL/FLEX={u:7.2f} CPT={d['CPT']:7.2f} 1.5x={1.5*u:7.3f} {'EXACT' if ok else 'DIFF ' + str(round(d['CPT'] - 1.5*u, 3))}")
    p(f"  exact={exact} differs={off}")
outp = os.path.join(OUT, f"{stamp}_captain_ratio_check.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))
