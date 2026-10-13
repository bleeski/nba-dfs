# THROWAWAY SPIKE: not engine code. Purpose: characterize DK contest-standings CSV format (Lineup string grammar, LOCKED placeholders, (n/m) multi-entry suffix, right-hand %Drafted/FPTS table, CPT vs UTIL ownership) with usernames and entry IDs redacted.
import zipfile, glob, io, csv, re, os, sys, collections, datetime

DL = r"C:\Users\benja\Downloads"
OUT = os.path.join(os.path.dirname(__file__), "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
def p(*a): L.append(" ".join(str(x) for x in a))

SLOT_RE = re.compile(r"\b(CPT|FLEX|UTIL|P|C|1B|2B|3B|SS|OF|QB|RB|WR|TE|DST|G|F|D|W|M|GK|PG|SG|SF|PF|LW|RW)\b ")
for f in sorted(glob.glob(os.path.join(DL, "contest-standings-*.zip"))):
    z = zipfile.ZipFile(f)
    name = z.namelist()[0]
    rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
    hdr, body = rows[0], rows[1:]
    left = [r for r in body if r and r[0] != ""]
    right = [r for r in body if len(r) > 7 and r[7] != ""]
    names = [r[2] for r in left]
    suffix = sum(1 for n in names if re.search(r" \(\d+/\d+\)$", n))
    tr = collections.Counter(r[3] for r in left)
    locked = sum(1 for r in left if "LOCKED" in r[5])
    empty = sum(1 for r in left if r[5].strip() == "")
    slots = collections.Counter()
    for r in left[:200]:
        toks = re.findall(r"(?:^| )(CPT|FLEX|UTIL|P|C|1B|2B|3B|SS|OF|QB|RB|WR|TE|DST|G|F|D|W|M|GK|PG|SG|SF|PF) ", r[5])
        slots[" ".join(toks)] += 1
    rp = collections.Counter(r[8] for r in right)
    # redacted sample
    def red(n):
        m = re.search(r"( \(\d+/\d+\))$", n)
        return "<USER>" + (m.group(1) if m else "")
    sample = left[0]
    p(f"=== {os.path.basename(f)}: entries={len(left)} right-table rows={len(right)} names with (n/m) suffix={suffix} LOCKED lineups={locked} empty lineups={empty}")
    p("  TimeRemaining values:", dict(tr.most_common(4)))
    p("  slot token sequence (first 200 lineups):", dict(slots.most_common(2)))
    p("  right-table Roster Position values:", dict(rp))
    p("  sample row:", [sample[0], "<ENTRYID>", red(sample[2]), sample[3], sample[4], sample[5][:160]])
    if right:
        p("  right-table sample:", right[0][7:11], right[1][7:11] if len(right) > 1 else "")
    # duplicate player names in right table (CPT and UTIL listed separately?)
    pc = collections.Counter(r[7] for r in right)
    dups = [k for k, v in pc.items() if v > 1]
    p("  players listed >1 time in right table:", len(dups), dups[:3])
    if dups:
        for r in right:
            if r[7] == dups[0]:
                p("   ", r[7:11])
    # Check Points == sum of FPTS of lineup players (Classic) using right table
    fp = {}
    for r in right:
        fp[(r[7], r[8])] = float(r[10]) if r[10] else 0.0
    # Rank ties
    ranks = [r[0] for r in left]
    p("  tied ranks present:", len(ranks) != len(set(ranks)))
    # LOCKED example
    lk = [r for r in left if "LOCKED" in r[5]]
    if lk:
        p("  LOCKED example:", lk[0][5][:200], "| Points:", lk[0][4], "| TimeRemaining:", lk[0][3])

outp = os.path.join(OUT, f"{stamp}_standings_inspect.txt")
open(outp, "w", encoding="utf-8").write("\n".join(L))
print(outp); print("\n".join(L))
