# THROWAWAY SPIKE: not engine code. Purpose: list the Position -> Roster Position mapping, salary range/increments, and Game Info formats in public NBA Classic DKSalaries files (GitHub examples) to document multi-position eligibility format.
import csv, glob, os, sys, collections, datetime
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
for f in sorted(glob.glob(os.path.join(D, "*.csv"))):
    rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    m = collections.Counter((r["Position"], r["Roster Position"]) for r in rows)
    sal = [int(r["Salary"]) for r in rows]
    games = sorted({r["Game Info"].split(" ")[0] for r in rows})
    L.append(f"== {os.path.basename(f)} rows={len(rows)} games={len(games)} salary min={min(sal)} max={max(sal)} all multiples of 100={all(s % 100 == 0 for s in sal)} dates={sorted({r['Game Info'].split(' ')[1] for r in rows})}")
    for (pos, rp), n in sorted(m.items()):
        L.append(f"   Position={pos:8s} Roster Position={rp:18s} n={n}")
    dup = collections.Counter(r["Name"] for r in rows)
    L.append(f"   names appearing more than once: {[k for k, v in dup.items() if v > 1][:5]}")
    L.append(f"   AvgPointsPerGame sample: {[r['AvgPointsPerGame'] for r in rows[:3]]}")
open(os.path.join(OUT, f"{stamp}_nba_classic_positions.txt"), "w").write("\n".join(L))
print("\n".join(L))
