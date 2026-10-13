# THROWAWAY SPIKE: not engine code. Purpose: cross-check DK's own recorded FPTS (public NBA contest-standings CSV for 2017-03-29, contest 39051001, from GitHub) against RotoGuru stat lines for the same date, and score each line under formula A (TD=+3) and B (TD=+4.5). Shows whether RotoGuru matches DK and which bonus rule DK used.
import csv, os, re, sys, glob, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")

def parse(s):
    d = collections.Counter()
    for n, k in re.findall(r"(\d+)(pt|rb|as|st|bl|to|trey)\b", s):
        d[k] += int(n)
    return d

def dk(d, td_bonus):
    base = d["pt"] + 0.5 * d["trey"] + 1.25 * d["rb"] + 1.5 * d["as"] + 2 * d["st"] + 2 * d["bl"] - 0.5 * d["to"]
    tens = sum(d[k] >= 10 for k in ("pt", "rb", "as", "st", "bl"))
    return base, (td_bonus if tens >= 3 else 1.5 if tens == 2 else 0), tens

rows = list(csv.reader(open(os.path.join(OUT, "downloads", "github", "standings", "royh21k_39051001.csv"), encoding="utf-8-sig")))
h = rows[0]; pi = h.index("Player")
dkfp = {r[pi]: float(r[pi + 2]) for r in rows[1:] if len(r) > pi + 2 and r[pi]}
rg = {}
for f in glob.glob(os.path.join(OUT, "downloads", "rotoguru", "*_scsv_20170329.txt")):
    for line in open(f, encoding="utf-8"):
        p = line.strip().split(";")
        if len(p) >= 14 and p[0] == "20170329":
            last, first = [x.strip() for x in p[3].split(",", 1)]
            rg[f"{first} {last}"] = (float(p[5]), p[13])
L = ["player | DK standings FPTS | RotoGuru DK Pts | formula A (TD=+3) | formula B (TD=+4.5) | stat line"]
for name, fp in sorted(dkfp.items(), key=lambda t: -t[1]):
    if name in rg:
        rgp, stat = rg[name]
        d = parse(stat)
        b, bonA, tens = dk(d, 3.0)
        _, bonB, _ = dk(d, 4.5)
        L.append(f"{name} | {fp} | {rgp} | {b + bonA} | {b + bonB} | {stat}")
L.append(f"players in DK standings right table: {len(dkfp)}; matched to RotoGuru rows (guards only in that file): {sum(n in rg for n in dkfp)}; DK==RotoGuru for all matched: {all(abs(dkfp[n] - rg[n][0]) < 0.01 for n in dkfp if n in rg)}")
outp = os.path.join(OUT, f"{stamp}_dk_vs_rotoguru_20170329.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))
