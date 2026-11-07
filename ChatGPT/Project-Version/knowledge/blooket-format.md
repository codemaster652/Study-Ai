# Blooket Set Format

Use this when I ask for a Blooket set (or a quiz or review game for Blooket). The goal is a CSV that imports cleanly using Blooket's "Import from Spreadsheet" option. An example file is in this project: **sample-blooket-set.csv**.

## Exact layout

**Row 1:** cell A1 contains `Blooket` then a line break then `Import Template`. All other cells in the row are empty (8 columns total).

**Row 2:** headers, exactly this text, in this order (a line break goes where shown):

1. `Question #`
2. `Question Text`
3. `Answer 1`
4. `Answer 2`
5. `Answer 3` (line break) `(Optional)`
6. `Answer 4` (line break) `(Optional)`
7. `Time Limit (sec)` (line break) `(Max: 300 Seconds)`
8. `Correct Answer(s)` (line break) `(Only Include Answer #)`

**Row 3 and down:** one question per row: the number, the question text, 2 to 4 answers (leave unused answer cells empty), the time in seconds (1 to 300, use 20 by default), and the correct answer's **number** (1 to 4).

## Rules

- The last column holds the answer's position number, NOT its text. For more than one correct answer, write them like `1,3` (the CSV needs quotes around it).
- Keep Answers 1 and 2 filled. Answers 3 and 4 are optional.
- Don't point the correct-answer number at an empty cell.
- Don't drop or reword the first two rows.
- Questions up to about 300 characters, each answer up to about 160.
- Maximum 98 questions per file. For bigger sets, split into parts of 98.
- UTF-8, comma-separated.
- Move the correct answer's position around so it isn't always Answer 1.

## Writing good questions

- Use fill-in-the-blank stems (`____`) or "which term" definitions.
- Wrong answers must be believable and from the same topic, never silly, and never also correct.
- Keep answers short, and mix question styles.
- If you can't read part of my notes, guess the likely term and **list your guesses at the end** so I can check them.
- If the source is graded work, write questions about the concepts, not the assigned problems.

## Delivering it

- If you can create files, give me the CSV to download. If not, put the CSV in a code block so I can copy it into a file named `something.csv` (or paste it into a spreadsheet and export as CSV).
- Tell me the question count and any guesses.
- Import steps: Blooket, then Create a Set, then Import from Spreadsheet, then upload the CSV.
- Blooket may change its import template. If the import fails, try downloading the current template from Blooket and match its headers.
