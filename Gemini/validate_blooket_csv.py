#!/usr/bin/env python3
"""Check a Blooket CSV: template rows, 8 columns, correct-answer numbers point at filled answers."""
import csv, sys
rows = list(csv.reader(open(sys.argv[1], encoding="utf-8", newline="")))
errs = []
if not rows[0][0].startswith("Blooket"): errs.append("Row 1 must be the 'Blooket Import Template' title cell")
if not rows[1][0].startswith("Question #"): errs.append("Row 2 must be the header row")
for n, r in enumerate(rows[2:], 3):
    if len(r) != 8: errs.append(f"Row {n}: {len(r)} columns, need 8"); continue
    ans = r[2:6]
    if not r[1].strip(): errs.append(f"Row {n}: empty question")
    if sum(bool(a.strip()) for a in ans) < 2: errs.append(f"Row {n}: needs at least 2 answers")
    for c in r[7].split(","):
        if not c.strip().isdigit() or not 1 <= int(c) <= 4 or not ans[int(c)-1].strip():
            errs.append(f"Row {n}: correct answer '{r[7]}' does not point to a filled answer")
    if not r[6].isdigit() or not 1 <= int(r[6]) <= 300: errs.append(f"Row {n}: bad time '{r[6]}'")
print("OK" if not errs else "\n".join(errs)); sys.exit(1 if errs else 0)
