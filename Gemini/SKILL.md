---
name: blooket-set-builder
description: Build Blooket question sets as CSV files that import cleanly through Blooket's "Import from Spreadsheet" option. Use whenever the user mentions Blooket, a Blooket set, Blooket CSV or spreadsheet import, or wants study questions, vocab, guided notes, a worksheet, a unit review or a textbook chapter turned into a game, quiz or review set for Blooket (or Gimkit/Kahoot-style class games, offering Blooket format), even if they never say "CSV". Also use to shorten, split or fix an existing Blooket import file.
---

# Blooket Set Builder

Turns notes, vocab lists, PDFs or images of worksheets into a Blooket import CSV. Always produce the file with the bundled script so the format is exact, then validate it.

## Exact Blooket import format

Blooket's "Import from Spreadsheet" matches the official **Blooket Import Template** (a Google Sheet; download as CSV). Layout:

| Row | Contents |
|---|---|
| 1 | Cell A1 = `Blooket` + newline + `Import Template`. All other cells empty (8 columns total). |
| 2 | Headers (exact text, in this order): `Question #` · `Question Text` · `Answer 1` · `Answer 2` · `Answer 3` + newline + `(Optional)` · `Answer 4` + newline + `(Optional)` · `Time Limit (sec)` + newline + `(Max: 300 Seconds)` · `Correct Answer(s)` + newline + `(Only Include Answer #)` |
| 3+ | One question per row: number, question text, 2–4 answers (unused answer cells left empty), time in seconds (1–300, default 20), correct answer **number** (1–4) |

Rules:
- Correct Answer column holds the answer's position number, not its text. Multiple correct answers: `1,3` (quoted by the CSV writer automatically).
- Keep Answers 1 and 2 filled; 3 and 4 optional.
- Conservative length limits: question ≤ 300 characters, each answer ≤ 160 (the script warns).
- The template sheet has 98 question rows. The script splits larger sets into parts of 98 so each file safely imports; the user can still try combining.
- UTF-8, comma delimited, header cells contain real line breaks (the csv module quotes them).
- Rotate the correct answer's position (the script does) so it is not always Answer 1.

If the user supplies a Google Sheets template link, try `web_fetch` on it to confirm the header text still matches; if it can't be read, use the layout above.

## Workflow

1. **Read the source.** If the content is handwritten or partly unreadable, infer the likely textbook term and **list those guesses to the user** at the end so they can verify them.
2. **Pick the content.** Full set: every term/concept. If the user wants a "short" or "hard terms" set: ~40–60 questions focused on vocabulary that is easy to confuse (similar pairs such as patent/trademark/copyright, value creation vs. capture, vision vs. mission, C-corp vs. S-corp), numbers/rules (e.g. the 40% rule), ordered sequences, and frameworks.
3. **Write questions into a JSON file** (see format below). Make fill-in-the-blank stems (`____`) or "which term" definitions. Distractors must be plausible and from the same topic, never silly, and never also correct. Keep answers short; mix question styles.
4. **Run the script:**
   ```bash
   python /mnt/skills/user/blooket-set-builder/scripts/make_blooket_csv.py questions.json /mnt/user-data/outputs/Set_Name.csv --time 20
   python /mnt/skills/user/blooket-set-builder/scripts/validate_blooket_csv.py /mnt/user-data/outputs/Set_Name.csv
   ```
   (If the skill lives elsewhere, use its actual `scripts/` path.) Check the validator prints `OK` for each output file, including each `_partN` file if split.
5. **Deliver** with `present_files`. Mention question counts, any splits, and the guessed terms. Import steps: Blooket → Create a Set → Import from Spreadsheet → upload the CSV.

### questions.json

```json
[
  {"q": "The ____ Rule says you may have PMF if more than this % of customers would be very disappointed without your product.",
   "correct": "40%", "wrong": ["14%", "25%", "60%"]},
  {"q": "Which are barriers to entry? (pick all)", "correct": ["Patents", "Economies of scale"],
   "wrong": ["Low taxes"], "time": 30}
]
```

`wrong` has 1–3 items. `time` is optional.

## Direct code (if the script is unavailable)

```python
import csv
H=["Question #","Question Text","Answer 1","Answer 2","Answer 3\n(Optional)","Answer 4\n(Optional)",
   "Time Limit (sec)\n(Max: 300 Seconds)","Correct Answer(s)\n(Only Include Answer #)"]
with open("set.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["Blooket\nImport Template"]+[""]*7)
    w.writerow(H)
    for i,(q,correct,*wrong) in enumerate(data):   # data = [(question, correct, w1, w2, w3), ...]
        pos=i%4; a=wrong[:3]; a.insert(pos,correct)
        w.writerow([i+1,q,*a,20,pos+1])
```

## Common mistakes
- Putting the answer text (not its number) in the last column.
- Dropping the title row or the header row, or rewording the headers.
- More than one blank in Answers 1–2, or a correct-answer number pointing at an empty cell.
- Leaving distractors that are also technically right.
