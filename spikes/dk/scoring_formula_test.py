# THROWAWAY SPIKE: not engine code. Purpose: discriminating test of DK NBA double-double / triple-double bonus stacking. For every player line in saved RotoGuru DK daily files, compute DK points under formula A (TD gets +3 only) and formula B (TD gets +1.5 DD AND +3 TD = +4.5), and report which matches RotoGuru's recorded DK Pts. Also checks 3PM, turnovers, and that only PTS/REB/AST/STL/BLK count toward DD/TD.
import glob, os, re, sys, datetime, collections

OUT = os.path.join(os.path.dirname(__file__), "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
def p(*a): L.append(" ".join(str(x) for x in a))

def parse(statline):
    d = collections.Counter()
    for num, key in re.findall(r"(\d+)(pt|rb|as|st|bl|to|trey)\b", statline):
        d[key] += int(num)
    return d

def score(d, mode):
    base = d["pt"] + 0.5 * d["trey"] + 1.25 * d["rb"] + 1.5 * d["as"] + 2 * d["st"] + 2 * d["bl"] - 0.5 * d["to"]
    tens = sum(1 for k in ("pt", "rb", "as", "st", "bl") if d[k] >= 10)
    if mode == "A":   # TD replaces DD
        bonus = 3 if tens >= 3 else (1.5 if tens == 2 else 0)
    elif mode == "B":  # TD stacks on DD
        bonus = 4.5 if tens >= 3 else (1.5 if tens == 2 else 0)
    elif mode == "none":
        bonus = 0
    return base, bonus, tens

tally = collections.Counter()
for f in sorted(glob.glob(os.path.join(OUT, "downloads", "rotoguru", "*_scsv_*.txt"))):
    for line in open(f, encoding="utf-8"):
        parts = line.strip().split(";")
        if len(parts) < 14 or not parts[0].isdigit():
            continue
        date, name, dkpts, stat = parts[0], parts[3], parts[5], parts[13]
        if not dkpts or stat in ("DNP", "NA", ""):
            continue
        try:
            rec = float(dkpts)
        except ValueError:
            continue
        d = parse(stat)
        bA, bonA, tens = score(d, "A")
        _, bonB, _ = score(d, "B")
        mA = abs(bA + bonA - rec) < 0.01
        mB = abs(bA + bonB - rec) < 0.01
        cat = "TD" if tens >= 3 else ("DD" if tens == 2 else "none")
        tally[(cat, mA, mB)] += 1
        if cat == "TD" or (cat == "DD" and tally[("DDshown",)] < 4) or (not (mA or mB)):
            if cat == "DD":
                tally[("DDshown",)] += 1
            p(f"{date} {name:24s} {cat:4s} recorded={rec:6.2f} base={bA:6.2f} A(TD=+3)={bA+bonA:6.2f} B(TD=+4.5)={bA+bonB:6.2f} match={'A' if mA else ''}{'B' if mB else ''}{'NONE' if not (mA or mB) else ''} | {stat}")
p("\n=== tally (category, matches formula A, matches formula B): count")
for k, v in sorted(tally.items(), key=str):
    p(k, v)
outp = os.path.join(OUT, f"{stamp}_scoring_formula_test.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))
