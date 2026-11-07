---
name: study-guide-maker
description: Use when a student wants a study guide, review sheet, cheat sheet, or practice questions from notes, a chapter, or a topic, even as a PDF. Builds it around concepts, not assignment answers.
---

# Study Guide Maker

Build a clear, well-organized study guide a student can actually study from. The goal is understanding and recall, not a pile of facts to copy.

## Ground rules

- **Never put the answers to the student's graded or assigned work in the guide.** If they paste a worksheet or homework and ask for a guide, make a guide on the *concepts and skills* it covers, with new example problems. Do not solve the assigned problems.
- **Use the student's own material first.** If they give notes, a chapter, or a PDF, build from that. Don't invent facts the notes don't support. If you add something from general knowledge, say so, and tell them to check it against their textbook or teacher.
- **Say when you are unsure.** If something looks wrong or missing in the notes, flag it rather than quietly fixing it.
- **Keep it short.** A good guide is usually 1 to 4 pages. Leave out filler.

## Step 1: Find out what the student needs

Ask at most one or two quick questions, and only if you can't tell from the request:

- What subject, unit, or test is it for?
- Do they have notes or a chapter to build from?

If they gave enough already, don't ask. Just build it.

## Step 2: Read the source material (if there is any)

If the student uploaded a PDF of notes, extract the text first:

```bash
python scripts/extract_text.py notes.pdf
```

(Use the script path relative to this skill's folder. If a script can't run in your environment, do the same work by hand and tell the student what you did.)

## Step 3: Plan the guide

Pick the parts that fit the subject. Not every guide needs every part.

- **Sections** by topic, each with a one or two sentence summary and the key points
- **Key terms** with short definitions in plain words
- **Worked example** with new numbers or a new scenario, shown step by step (math, science)
- **Practice questions** (5 to 10), mixing easy and hard, with an answer key
- **Common mistakes** or things to watch out for
- **Memory tips** only when they genuinely help (a pattern, a diagram description, a mnemonic)

Make the guide something the student can use to *test themselves*, not just reread. Put the practice questions near the end and the answers on their own page so they can cover them up.

## Step 4: Build the guide

Write the guide as JSON in this shape, then turn it into a PDF with the script:

```json
{
  "title": "Unit 3 Review: Photosynthesis",
  "subject": "Biology",
  "intro": "Optional one or two sentences on what this guide covers.",
  "sections": [
    {
      "heading": "Light reactions",
      "summary": "Where and why the plant captures light energy.",
      "key_points": ["Happens in the thylakoid membranes", "Makes ATP and NADPH"],
      "terms": [{"term": "Chlorophyll", "definition": "The green pigment that absorbs light."}],
      "example": {
        "problem": "A short worked example, with new numbers or a new scenario.",
        "steps": ["First step", "Second step", "Final result"]
      },
      "mistakes": ["Mixing up what goes in and what comes out"]
    }
  ],
  "practice": [
    {"question": "What is the job of chlorophyll?", "answer": "It absorbs light energy."}
  ],
  "tips": ["Draw the whole process from memory, then check it."]
}
```

Only `title` and `sections` are required. Every field inside a section is optional.

In any text field you may use these simple tags: `<b>bold</b>`, `<i>italic</i>`, `<sub>2</sub>` for subscripts (H<sub>2</sub>O), and `<super>2</super>` for exponents (x<super>2</super>). Do **not** use Unicode subscript or superscript characters (like ₂ or ²). They show up as black boxes in the PDF.

Save the JSON, then run:

```bash
python scripts/make_pdf.py guide.json study-guide.pdf
```

Useful options:

- `--no-answers` leaves the answer key out (for a self-quiz sheet)
- `--answers-only` makes just the answer key (to print separately)

## Step 5: Share it and follow up

- Give the student the PDF, plus a one or two sentence summary of what's in it.
- If you added anything that wasn't in their notes, say so.
- Offer to quiz them on it, or to make a shorter cheat sheet or a Blooket or flashcard version. Quizzing them is often more useful than rereading.

A complete working example is in `examples/sample-guide.json`.

## Other helper scripts

- `scripts/extract_text.py notes.pdf` prints the text of a PDF (use `--pages 1-5` for part of it)
- `scripts/merge_pdfs.py out.pdf a.pdf b.pdf` combines PDFs (for example, a guide plus an answer key)

## If the PDF tools aren't available

If you can't run scripts, give the study guide directly in the chat using clear headings and short lists. Offer to format it for copying into a document.
