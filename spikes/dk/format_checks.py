# THROWAWAY SPIKE: not engine code. Purpose: one rerunnable record of small DK file-format checks cited in R6 (BOM/line endings, LOCKED cells in a mid-slate DKEntries file, standings Points = sum of FPTS, ragged standings rows, accented names, salary increments, and DKEntries embedded player list vs DKSalaries for the same slate). Entry IDs and usernames are never printed.
import csv, glob, io, os, re, zipfile, datetime, collections

DL = r"C:\Users\benja\Downloads"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
def p(*a): L.append(" ".join(str(x) for x in a))

# 1. BOM and line endings
p("=== 1. BOM and line endings")
for f in ["DKEntries (6).csv", "DKEntries_showdown.csv", "DKSalaries_showdown.csv", "DKSalaries_Classic.csv"]:
    b = open(os.path.join(DL, f), "rb").read()
    p(f"{f}: BOM={b[:3] == b'\xef\xbb\xbf'} CRLF={b.count(b'\r\n')} LF={b.count(b'\n')}")
z = zipfile.ZipFile(os.path.join(DL, "contest-standings-196048725.zip")); b = z.read(z.namelist()[0])
p(f"contest-standings-196048725.csv: BOM={b[:3] == b'\xef\xbb\xbf'} CRLF={b.count(b'\r\n')} LF={b.count(b'\n')}")

# 2. LOCKED cells in a mid-slate DKEntries download
p("\n=== 2. LOCKED cells in DKEntries (5).csv (downloaded mid-slate)")
rows = list(csv.reader(open(os.path.join(DL, "DKEntries (5).csv"), encoding="utf-8-sig")))
hdr = rows[0]; end = hdr.index("Instructions") - 1
ent = [r for r in rows[1:] if r and r[0].strip()]
kinds = collections.Counter()
for r in ent:
    for c in r[4:end]:
        kinds["Name (ID) (LOCKED)" if re.fullmatch(r".+ \(\d+\) \(LOCKED\)", c) else "Name (ID)" if re.fullmatch(r".+ \(\d+\)", c) else "blank" if not c.strip() else "other"] += 1
p(f"slots per row={end - 4}, entries={len(ent)}, cell formats={dict(kinds)}")
p("example cell:", next(c for r in ent for c in r[4:end] if "(LOCKED)" in c))

# 3/4. Standings: Points == sum of right-table FPTS; ragged rows
p("\n=== 3. Standings: Points vs sum of FPTS, and row widths")
SLOTS = r"CPT|FLEX|UTIL|GK|C|W|D|G|M|F"
for f in ["contest-standings-194542293.zip", "contest-standings-196048727.zip", "contest-standings-195958188.zip"]:
    z = zipfile.ZipFile(os.path.join(DL, f))
    rs = list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode("utf-8-sig"))))
    body = rs[1:]
    fp = {(r[7], r[8]): float(r[10]) for r in body if len(r) > 10 and r[7]}
    n = bad = 0
    for r in body:
        if not r or not r[0] or not r[5]:
            continue
        toks = re.split(rf"(?:^| )({SLOTS}) ", " " + r[5])
        pairs = [(toks[i], toks[i + 1].strip()) for i in range(1, len(toks) - 1, 2)]
        try:
            s = sum(fp[(nm, sl)] for sl, nm in pairs)
        except KeyError:
            continue
        n += 1; bad += abs(s - float(r[4])) > 0.011
    p(f"{f}: lineups checked={n}, Points != sum(FPTS)={bad}, row widths={dict(collections.Counter(len(r) for r in body))}")

# 5. Accented names and salary increments in salary files
p("\n=== 5. Salary files: accented names, salary increments")
acc = collections.Counter(); inc = collections.Counter()
files = glob.glob(os.path.join(DL, "DKSalaries*.csv")) + glob.glob(os.path.join(HERE, "out", "downloads", "github", "*.csv")) + glob.glob(os.path.join(HERE, "out", "downloads", "github", "classic", "*.csv"))
for f in files:
    rs = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    sd = "CPT" in {r["Roster Position"] for r in rs}
    for r in rs:
        if any(ord(ch) > 127 for ch in r["Name"]):
            acc[os.path.basename(f)] += 1
        s = int(r["Salary"])
        inc[("showdown " + r["Roster Position"] if sd else "classic", "mult100" if s % 100 == 0 else "NOT100", "mult200" if s % 200 == 0 else "not200")] += 1
p(f"files={len(files)}, files with accented names={dict(acc) or 'none'}")
for k, v in sorted(inc.items()):
    p("  ", k, v)

# 6. DKEntries embedded player list vs DKSalaries, same slate (CHI @ VGK NHL Showdown)
p("\n=== 6. DKEntries_showdown.csv embedded player list vs DKSalaries_showdown.csv")
rows = list(csv.reader(open(os.path.join(DL, "DKEntries_showdown.csv"), encoding="utf-8-sig")))
start = next(i for i, r in enumerate(rows) if "TeamAbbrev" in r)
col = rows[start].index("Position")
emb = {r[col + 3]: (r[col + 4], r[col + 5], r[col + 2]) for r in rows[start + 1:] if len(r) > col + 5 and r[col + 3]}
sal = {r["ID"]: (r["Roster Position"], r["Salary"], r["Name"]) for r in csv.DictReader(open(os.path.join(DL, "DKSalaries_showdown.csv"), encoding="utf-8-sig"))}
p(f"embedded players={len(emb)}, salary-file players={len(sal)}, IDs only in entries={len(set(emb) - set(sal))}, only in salaries={len(set(sal) - set(emb))}")
diff = [(i, emb[i], sal[i]) for i in set(emb) & set(sal) if emb[i] != sal[i]]
p(f"IDs whose (Roster Position, Salary, Name) differ: {len(diff)} {diff[:3]}")
p("embedded player-list header:", rows[start][col:])

outp = os.path.join(OUT, f"{stamp}_format_checks.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))
