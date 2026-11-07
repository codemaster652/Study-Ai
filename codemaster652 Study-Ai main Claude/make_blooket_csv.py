#!/usr/bin/env python3
"""Build a Blooket-importable CSV from a JSON list of questions.

Usage:
  python make_blooket_csv.py questions.json out.csv [--time 20] [--max-rows 98] [--no-rotate]

questions.json = list of objects:
  {"q": "Question text", "correct": "Right answer", "wrong": ["w1","w2","w3"], "time": 20}
  - "wrong" has 1-3 items (so 2-4 answers total). "time" is optional.
  - Multiple correct answers: use "correct": ["A","B"].

Output matches the official "Blooket Import Template" layout exactly:
  Row 1: A1 = "Blooket\nImport Template" (rest empty)
  Row 2: column headers (below)
  Row 3+: Question #, text, Answer 1-4, time limit, correct answer number(s)
Large sets are split into parts of --max-rows questions (template has 98 rows).
"""
import csv, json, sys, argparse, os

HEADERS = ["Question #", "Question Text", "Answer 1", "Answer 2",
           "Answer 3\n(Optional)", "Answer 4\n(Optional)",
           "Time Limit (sec)\n(Max: 300 Seconds)",
           "Correct Answer(s)\n(Only Include Answer #)"]
MAX_Q, MAX_A = 300, 160  # conservative limits; warn if exceeded

def build_rows(items, default_time=20, rotate=True):
    rows, warns = [], []
    for i, it in enumerate(items):
        q = it["q"].strip()
        corr = it["correct"] if isinstance(it["correct"], list) else [it["correct"]]
        wrong = list(it["wrong"])
        answers_n = len(corr) + len(wrong)
        if not 2 <= answers_n <= 4:
            raise ValueError(f"Q{i+1}: needs 2-4 total answers, has {answers_n}")
        allans = corr + wrong
        if len(set(a.lower() for a in allans)) != len(allans):
            raise ValueError(f"Q{i+1}: duplicate answers {allans}")
        # place correct answers; rotate position so it is not always Answer 1
        slots = [None] * answers_n
        start = (i % answers_n) if rotate else 0
        order = [(start + k) % answers_n for k in range(answers_n)]
        for a, pos in zip(corr, order[:len(corr)]):
            slots[pos] = a
        it_w = iter(wrong)
        for s in range(answers_n):
            if slots[s] is None:
                slots[s] = next(it_w)
        correct_nums = sorted(p + 1 for p in order[:len(corr)])
        t = int(it.get("time", default_time))
        if not 1 <= t <= 300:
            raise ValueError(f"Q{i+1}: time {t} outside 1-300")
        if len(q) > MAX_Q: warns.append(f"Q{i+1}: question {len(q)} chars (> {MAX_Q})")
        for a in slots:
            if len(a) > MAX_A: warns.append(f"Q{i+1}: answer >{MAX_A} chars: {a[:30]}...")
        padded = slots + [""] * (4 - answers_n)   # blank optional answer cells
        rows.append([i + 1, q, *padded, t, ",".join(map(str, correct_nums))])
    return rows, warns

def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Blooket\nImport Template"] + [""] * 7)
        w.writerow(HEADERS)
        for r in rows:
            w.writerow(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_in"); ap.add_argument("csv_out")
    ap.add_argument("--time", type=int, default=20)
    ap.add_argument("--max-rows", type=int, default=98)
    ap.add_argument("--no-rotate", action="store_true")
    a = ap.parse_args()
    items = json.load(open(a.json_in, encoding="utf-8"))
    rows, warns = build_rows(items, a.time, not a.no_rotate)
    for w in warns: print("WARNING:", w)
    base, ext = os.path.splitext(a.csv_out)
    if len(rows) <= a.max_rows:
        write_csv(a.csv_out, rows); print(f"{a.csv_out}: {len(rows)} questions")
    else:
        for n, s in enumerate(range(0, len(rows), a.max_rows), 1):
            chunk = [[j + 1] + r[1:] for j, r in enumerate(rows[s:s + a.max_rows])]
            p = f"{base}_part{n}{ext}"; write_csv(p, chunk)
            print(f"{p}: {len(chunk)} questions")

if __name__ == "__main__":
    main()
