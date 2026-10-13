# THROWAWAY SPIKE: not engine code. Purpose: inspect generic DK salary CSVs in Downloads for column layout, multi-position format, Game Info format, Status/Starting values, and Showdown CPT/UTIL dual-ID and 1.5x salary rounding.
import csv, glob, os, re, sys, collections, datetime, json

DL = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\benja\Downloads"
PAT = sys.argv[2] if len(sys.argv) > 2 else "DKSalaries*.csv"
OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
lines = []
def p(*a):
    s = " ".join(str(x) for x in a)
    lines.append(s)

headers = collections.Counter()
gi_patterns = collections.Counter()
status_vals = collections.Counter()
starting_vals = collections.Counter()
rp_vals = collections.Counter()
ratio_rows = []
pair_summary = []
for f in sorted(glob.glob(os.path.join(DL, PAT))):
    with open(f, encoding="utf-8-sig", newline="") as fh:
        raw = fh.read()
    has_bom = False
    with open(f, "rb") as fb:
        has_bom = fb.read(3) == b"\xef\xbb\xbf"
    rows = list(csv.DictReader(raw.splitlines()))
    if not rows:
        continue
    hdr = tuple(rows[0].keys())
    headers[hdr] += 1
    for r in rows:
        gi = r.get("Game Info", "")
        pat = re.sub(r"[A-Z]{2,4}@[A-Z]{2,4}", "AAA@BBB", gi)
        pat = re.sub(r"\d", "9", pat)
        gi_patterns[pat] += 1
        status_vals[r.get("Status", "<no col>")] += 1
        starting_vals[r.get("Starting", "<no col>")] += 1
        rp_vals[r.get("Roster Position")] += 1
        # Name + ID consistency
        if r["Name + ID"] != f'{r["Name"]} ({r["ID"]})':
            p("NAME+ID MISMATCH", os.path.basename(f), r["Name + ID"], r["Name"], r["ID"])
    # Showdown CPT/UTIL pairing
    rps = set(r["Roster Position"] for r in rows)
    if "CPT" in rps:
        by = collections.defaultdict(dict)
        for r in rows:
            key = (r["Name"], r["TeamAbbrev"])
            by[key].setdefault(r["Roster Position"], []).append(r)
        n_pair = 0; n_same_id = 0; ratios = collections.Counter(); id_gap = collections.Counter()
        for key, d in by.items():
            if "CPT" in d and ("UTIL" in d or "FLEX" in d):
                u = d.get("UTIL", d.get("FLEX"))[0]; c = d["CPT"][0]
                n_pair += 1
                if c["ID"] == u["ID"]:
                    n_same_id += 1
                us, cs = int(u["Salary"]), int(c["Salary"])
                exact = us * 1.5
                ratios["exact" if cs == exact else f"diff={cs-exact:+.0f}"] += 1
                id_gap[int(u["ID"]) - int(c["ID"])] += 1
                ratio_rows.append((os.path.basename(f), us, cs))
        pair_summary.append((os.path.basename(f), sorted(rps), len(rows), n_pair, n_same_id, dict(ratios), dict(collections.Counter({k: v for k, v in id_gap.most_common(3)}))))

p("=== Header variants (count of files)")
for h, n in headers.most_common():
    p(n, "|", ",".join(h))
p("\n=== Game Info patterns (top 15)")
for k, n in gi_patterns.most_common(15):
    p(n, "|", k)
p("\n=== Status values"); p(dict(status_vals.most_common(20)))
p("\n=== Starting values"); p(dict(starting_vals.most_common(20)))
p("\n=== Roster Position values (top 30)"); p(dict(rp_vals.most_common(30)))
p("\n=== Showdown files: file, roster positions, rows, CPT/UTIL pairs, pairs with same ID, CPT vs 1.5*UTIL salary, top UTIL-CPT ID gaps")
for s in pair_summary:
    p(s)
# rounding: UTIL salaries ending not in 00 or odd hundreds
odd = [(f, u, c) for f, u, c in ratio_rows if (u * 3) % 2 != 0]
p("\n=== UTIL salaries where 1.5x is not an integer:", len(odd), odd[:5])
odd100 = [(f, u, c) for f, u, c in ratio_rows if (u // 100) % 2 == 1]
p("=== UTIL salaries with odd hundreds (1.5x ends in 50):", len(odd100), odd100[:8])

outp = os.path.join(OUT, f"{stamp}_salary_csv_inspect_{os.path.basename(DL)}.txt")
with open(outp, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print(outp)
print("\n".join(lines))
