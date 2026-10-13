# THROWAWAY SPIKE: not engine code. Purpose: test whether pdfplumber can turn an official NBA injury report PDF (untrusted download, read only) into clean rows.
import json, sys, datetime, re
from pathlib import Path
import pdfplumber

OUT = Path(__file__).parent / "out"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
pdf_path = Path(sys.argv[1])
res = {"file": pdf_path.name}
rows = []
with pdfplumber.open(pdf_path) as pdf:
    res["pages"] = len(pdf.pages)
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
        if i == 0:
            res["page0_text_head"] = (page.extract_text() or "")[:600]
            res["page0_n_tables_lines_strategy"] = len(tables)
        for t in tables:
            rows.extend(t)
    # Fallback: text strategy on page 1 for comparison
    t2 = pdf.pages[0].extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
    res["page0_text_strategy_tables"] = len(t2)
    res["page0_text_strategy_sample"] = t2[0][:6] if t2 else None
res["n_raw_rows"] = len(rows)
res["header_row"] = rows[0] if rows else None
res["sample_rows"] = rows[1:15]
# Forward-fill the merged cells (Game Date, Game Time, Matchup, Team) the way a parser would
cols = None
clean = []
last = {}
for r in rows:
    if r and r[0] and "Game Date" in str(r[0]):
        cols = [c.replace("\n", " ") if c else c for c in r]
        continue
    if not cols:
        continue
    rec = {}
    for c, v in zip(cols, r):
        v = (v or "").replace("\n", " ").strip()
        if not v and c in ("Game Date", "Game Time", "Matchup", "Team"):
            v = last.get(c, "")
        rec[c] = v
    for c in ("Game Date", "Game Time", "Matchup", "Team"):
        last[c] = rec.get(c, "")
    clean.append(rec)
res["n_clean_rows"] = len(clean)
res["clean_sample"] = clean[:12]
res["status_counts"] = {}
for rec in clean:
    st = rec.get("Current Status", "")
    res["status_counts"][st] = res["status_counts"].get(st, 0) + 1
res["not_yet_submitted_rows"] = sum(1 for r in clean if "NOT YET SUBMITTED" in json.dumps(r).upper())
out = OUT / f"{stamp}_injury_pdf_parse_{pdf_path.stem}.json"
out.write_text(json.dumps(res, indent=1))
print(json.dumps({k: res[k] for k in ("file", "pages", "n_raw_rows", "n_clean_rows", "status_counts", "not_yet_submitted_rows", "header_row")}, indent=1))
print(json.dumps(res["clean_sample"][:6], indent=1))
