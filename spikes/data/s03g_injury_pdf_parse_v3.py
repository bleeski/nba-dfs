# THROWAWAY SPIKE: not engine code. Purpose: third parsing attempt on official injury PDFs: word x-bands for columns, and wrapped Reason fragments attached to the vertically nearest player row (cells are vertically centered). Inputs are untrusted downloads; run with python -I.
import json, sys, datetime, re
from pathlib import Path
import pdfplumber

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
COLS = ["Game Date", "Game Time", "Matchup", "Team", "Player Name", "Current Status", "Reason"]
STATUSES = {"Out", "Questionable", "Doubtful", "Probable", "Available"}


def header_bounds(words):
    hw = [w for w in words if w["top"] < 130]
    hdr = {}
    for i, w in enumerate(hw):
        nxt = hw[i + 1]["text"] if i + 1 < len(hw) else ""
        pair = f"{w['text']} {nxt}"
        if pair in COLS:
            hdr[pair] = w["x0"]
        elif w["text"] in ("Matchup", "Team", "Reason"):
            hdr[w["text"]] = w["x0"]
    return hdr


def parse(pdf_path):
    rows, frags, nys = [], [], []
    bounds = None
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=1.2, y_tolerance=2)
            h = header_bounds(words)
            if len(h) == 7:
                bounds = sorted(h.items(), key=lambda kv: kv[1])
                body_top = max(w["bottom"] for w in words if w["top"] < 130 and w["text"] in ("Game", "Reason", "Team"))
            else:
                body_top = 60
            lines = {}
            for w in words:
                if w["top"] <= body_top + 1:
                    continue
                lines.setdefault(round(w["top"], 0), []).append(w)
            for top in sorted(lines):
                cells = {c: [] for c in COLS}
                for w in sorted(lines[top], key=lambda w: w["x0"]):
                    col = bounds[0][0]
                    for c, x in bounds:
                        if w["x0"] >= x - 3:
                            col = c
                    cells[col].append(w["text"])
                ln = {c: " ".join(v) for c, v in cells.items()}
                joined = " ".join(ln.values())
                if re.fullmatch(r"\s*Page \d+ of \d+\s*", joined) or re.match(r"\d+ of \d+$", joined.strip()) or ln["Player Name"].startswith("of "):
                    continue
                key = (pno, top)
                if "NOT YET SUBMITTED" in joined.upper():
                    nys.append({"key": key, **ln})
                elif ln["Player Name"]:
                    rows.append({"key": key, **ln})
                elif any(ln[c] for c in COLS):
                    frags.append({"key": key, **ln})
    # attach fragments to nearest player row on same page (game/team header fragments too)
    for f in frags:
        same = [r for r in rows if r["key"][0] == f["key"][0]]
        if not same:
            continue
        r = min(same, key=lambda r: (abs(r["key"][1] - f["key"][1]), -r["key"][1]))
        r.setdefault("_frags", []).append(f)
    out, last = [], {c: "" for c in COLS[:4]}
    for r in sorted(rows + nys, key=lambda r: r["key"]):
        parts = sorted([r] + r.get("_frags", []), key=lambda x: x["key"][1])
        rec = {}
        for c in COLS:
            rec[c] = " ".join(p[c] for p in parts if p[c]).strip()
        for c in COLS[:4]:
            if rec[c]:
                last[c] = rec[c]
            else:
                rec[c] = last[c]
        out.append(rec)
    return out


pdf_path = Path(sys.argv[1])
out = parse(pdf_path)
status_counts = {}
for r in out:
    st = r["Current Status"] if r["Current Status"] in STATUSES else ("NOT YET SUBMITTED" if "NOT YET SUBMITTED" in json.dumps(r).upper() else f"OTHER:{r['Current Status']}")
    status_counts[st] = status_counts.get(st, 0) + 1
res = {"file": pdf_path.name, "n_rows": len(out), "status_counts": status_counts,
       "check_rows": [r for r in out if any(n in r["Player Name"] for n in ("Hartenstein", "Sorber", "Edwards, Anthony"))][:4],
       "nys_rows": [r for r in out if "NOT YET SUBMITTED" in json.dumps(r).upper()][:4],
       "other_status_rows": [r for r in out if r["Current Status"] not in STATUSES and "NOT YET SUBMITTED" not in json.dumps(r).upper()][:5],
       "matchups": sorted({r["Matchup"] for r in out}), "sample": out[:6]}
(OUT / f"{stamp}_injury_pdf_parse_v3_{pdf_path.stem}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: res[k] for k in ("file", "n_rows", "status_counts", "check_rows", "nys_rows", "other_status_rows", "matchups")}, indent=1))
