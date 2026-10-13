# THROWAWAY SPIKE: not engine code. Purpose: second parsing attempt on the official injury PDF using word x-positions (column bands) instead of ruled-table detection.
import json, sys, datetime, re
from pathlib import Path
import pdfplumber

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
pdf_path = Path(sys.argv[1])
COLS = ["Game Date", "Game Time", "Matchup", "Team", "Player Name", "Current Status", "Reason"]
lines_all = []
with pdfplumber.open(pdf_path) as pdf:
    for pno, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1.2, y_tolerance=2, keep_blank_chars=False)
        # header x positions: learn from the first page that has the header row, reuse for the rest
        hdr = {}
        hw = [w for w in words if w["top"] < 130]
        texts = [w["text"] for w in hw]
        for i, w in enumerate(hw[:-1]):
            pair = w["text"] + " " + hw[i + 1]["text"]
            if pair in COLS and pair not in hdr:
                hdr[pair] = w["x0"]
            if w["text"] == "Team" and "Team" not in hdr:
                hdr["Team"] = w["x0"]
            if w["text"] == "Matchup":
                hdr["Matchup"] = w["x0"]
            if w["text"] == "Reason":
                hdr["Reason"] = w["x0"]
        if hw and hw[-1]["text"] == "Reason":
            hdr["Reason"] = hw[-1]["x0"]
        if len(hdr) == 7:
            HDR = hdr; hdr_bottom = max(w["bottom"] for w in hw if w["text"] in ("Game", "Reason"))
        else:
            hdr_bottom = 60
        bounds = sorted(HDR.items(), key=lambda kv: kv[1])
        # group words into lines by 'top'
        rows = {}
        for w in words:
            if w["top"] <= hdr_bottom + 1 or w["text"].startswith("Page"):
                continue
            key = round(w["top"] / 2.5)
            rows.setdefault(key, []).append(w)
        for key in sorted(rows):
            cells = {c: [] for c in COLS}
            for w in sorted(rows[key], key=lambda w: w["x0"]):
                col = bounds[0][0]
                for c, x in bounds:
                    if w["x0"] >= x - 3:
                        col = c
                cells[col].append(w["text"])
            line = {c: " ".join(v) for c, v in cells.items()}
            line["_top"] = key; line["_page"] = pno
            lines_all.append(line)

# Stitch: forward-fill game/team columns; attach reason-only lines to the player row with empty reason (above/below wrap)
out, last = [], {c: "" for c in COLS[:4]}
pending_frag = []
for ln in lines_all:
    if re.match(r"Injury Report:", ln.get("Game Date", "")):
        continue
    for c in COLS[:4]:
        if ln[c]:
            last[c] = ln[c]
    if ln["Player Name"]:
        rec = {c: (ln[c] or last.get(c, "")) for c in COLS}
        if not rec["Reason"] and pending_frag:
            rec["Reason"] = " ".join(pending_frag)
        pending_frag = []
        out.append(rec)
    elif ln["Reason"] and not ln["Player Name"]:
        if out and (out[-1]["Reason"] == "" or out[-1].get("_needs_tail")):
            out[-1]["Reason"] = (out[-1]["Reason"] + " " + ln["Reason"]).strip()
        elif out and pending_frag == [] and out[-1]["Reason"].endswith(("Surgical", "Injury/Illness", "-", ";")):
            out[-1]["Reason"] += " " + ln["Reason"]
        else:
            pending_frag.append(ln["Reason"])
    elif "NOT YET SUBMITTED" in " ".join(ln[c] for c in COLS).upper():
        out.append({**{c: last.get(c, "") for c in COLS[:4]}, "Player Name": "", "Current Status": "NOT YET SUBMITTED", "Reason": ""})
status_counts = {}
for r in out:
    status_counts[r["Current Status"]] = status_counts.get(r["Current Status"], 0) + 1
bad = [r for r in out if r["Current Status"] not in ("Out", "Questionable", "Doubtful", "Probable", "Available", "NOT YET SUBMITTED")]
res = {"file": pdf_path.name, "n_rows": len(out), "status_counts": status_counts, "n_rows_with_unexpected_status": len(bad), "unexpected_sample": bad[:5],
       "games": sorted({r["Matchup"] for r in out}), "sample": out[:14]}
(OUT / f"{stamp}_injury_pdf_parse_words_{pdf_path.stem}.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: res[k] for k in ("file", "n_rows", "status_counts", "n_rows_with_unexpected_status", "games")}, indent=1))
for r in out[:14]:
    print(r)
print("unexpected:", bad[:5])
