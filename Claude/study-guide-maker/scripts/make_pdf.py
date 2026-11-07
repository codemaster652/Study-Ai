#!/usr/bin/env python3
"""Turn a study guide written as JSON into a clean PDF.

Usage:
    python make_pdf.py guide.json study-guide.pdf
    python make_pdf.py guide.json quiz-sheet.pdf --no-answers
    python make_pdf.py guide.json answer-key.pdf --answers-only

Needs: pip install reportlab
(On systems that block global installs, add --break-system-packages
or use a virtual environment.)

The JSON format is described in SKILL.md. Only "title" and "sections"
are required.
"""

import argparse
import json
import re
import sys
from xml.sax.saxutils import escape

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        KeepTogether,
        ListFlowable,
        ListItem,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:
    sys.exit("reportlab is not installed. Run: pip install reportlab")


ACCENT = colors.HexColor("#2F5D8A")
SOFT = colors.HexColor("#EAF1F8")
GREY = colors.HexColor("#555555")

# Tags students/Claude may use inside text. Everything else is escaped.
ALLOWED_TAGS = ["b", "i", "u", "sub", "super"]


def fmt(text):
    """Make text safe for ReportLab while keeping a few simple tags."""
    text = escape(str(text))
    for tag in ALLOWED_TAGS:
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>")
        text = text.replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    # Unicode sub/superscripts render as black boxes in the built-in fonts.
    text = re.sub(r"[\u2070-\u209f\u00b2\u00b3\u00b9]", "?", text)
    return text


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "GuideTitle", parent=base["Title"], fontSize=24, leading=28,
            textColor=ACCENT, alignment=TA_LEFT, spaceAfter=4,
        ),
        "subject": ParagraphStyle(
            "GuideSubject", parent=base["Normal"], fontSize=12, leading=15,
            textColor=GREY, spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "GuideH1", parent=base["Heading1"], fontSize=16, leading=20,
            textColor=ACCENT, spaceBefore=14, spaceAfter=4,
        ),
        "h2": ParagraphStyle(
            "GuideH2", parent=base["Heading2"], fontSize=12, leading=15,
            textColor=colors.black, spaceBefore=8, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "GuideBody", parent=base["Normal"], fontSize=10.5, leading=14.5,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "GuideSmall", parent=base["Normal"], fontSize=9, leading=12,
            textColor=GREY,
        ),
        "cell": ParagraphStyle(
            "GuideCell", parent=base["Normal"], fontSize=10, leading=13,
        ),
    }


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(fmt(i), style), leftIndent=14) for i in items],
        bulletType="bullet", start="\u2022", leftIndent=14,
    )


def numbered(items, style):
    return ListFlowable(
        [ListItem(Paragraph(fmt(i), style), leftIndent=18) for i in items],
        bulletType="1", leftIndent=18,
    )


def terms_table(terms, s):
    rows = [
        [Paragraph(f"<b>{fmt(t.get('term', ''))}</b>", s["cell"]),
         Paragraph(fmt(t.get("definition", "")), s["cell"])]
        for t in terms
    ]
    table = Table(rows, colWidths=[1.6 * inch, 4.9 * inch])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [SOFT, colors.white]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def example_box(example, s):
    parts = [Paragraph("<b>Worked example</b>", s["h2"])]
    if example.get("problem"):
        parts.append(Paragraph(fmt(example["problem"]), s["body"]))
    if example.get("steps"):
        parts.append(numbered(example["steps"], s["body"]))
    box = Table([[parts]], colWidths=[6.5 * inch])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("BOX", (0, 0), (-1, -1), 0.5, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return box


def section_flowables(sec, s):
    out = [Paragraph(fmt(sec.get("heading", "Untitled")), s["h1"])]
    if sec.get("summary"):
        out.append(Paragraph(f"<i>{fmt(sec['summary'])}</i>", s["body"]))
    if sec.get("key_points"):
        out.append(bullets(sec["key_points"], s["body"]))
    if sec.get("terms"):
        out += [Spacer(1, 6), Paragraph("Key terms", s["h2"]), terms_table(sec["terms"], s)]
    if sec.get("example"):
        out += [Spacer(1, 8), KeepTogether([example_box(sec["example"], s)])]
    if sec.get("mistakes"):
        out += [Paragraph("Watch out for", s["h2"]), bullets(sec["mistakes"], s["body"])]
    return out


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(0.75 * inch, 0.5 * inch, doc.title or "")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def practice_flowables(practice, s, show_answers_inline=False):
    out = [Paragraph("Practice questions", s["h1"])]
    out.append(Paragraph(
        "Try each one on your own first. Answers are at the end.",
        s["small"]))
    out.append(Spacer(1, 4))
    out.append(numbered([p.get("question", "") for p in practice], s["body"]))
    return out


def answer_key_flowables(practice, s):
    out = [Paragraph("Answer key", s["h1"])]
    out.append(Paragraph(
        "Check your work. If you got one wrong, find the step where it went "
        "off before looking at the next one.", s["small"]))
    out.append(Spacer(1, 4))
    out.append(numbered([p.get("answer", "") for p in practice], s["body"]))
    return out


def build(data, out_path, no_answers=False, answers_only=False):
    s = build_styles()
    title = data.get("title", "Study Guide")
    doc = SimpleDocTemplate(
        out_path, pagesize=letter, title=title,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.85 * inch,
    )
    practice = data.get("practice") or []
    story = []

    if answers_only:
        if not practice:
            sys.exit("No practice questions in the JSON, so there is no answer key.")
        story.append(Paragraph(fmt(title), s["title"]))
        story.append(HRFlowable(width="100%", color=ACCENT, thickness=1.5))
        story += answer_key_flowables(practice, s)
    else:
        story.append(Paragraph(fmt(title), s["title"]))
        if data.get("subject"):
            story.append(Paragraph(fmt(data["subject"]), s["subject"]))
        story.append(HRFlowable(width="100%", color=ACCENT, thickness=1.5))
        if data.get("intro"):
            story += [Spacer(1, 6), Paragraph(fmt(data["intro"]), s["body"])]

        sections = data.get("sections") or []
        if not sections:
            sys.exit('The JSON needs at least one entry in "sections".')
        for sec in sections:
            story += section_flowables(sec, s)

        if data.get("tips"):
            story += [Paragraph("Study tips", s["h1"]), bullets(data["tips"], s["body"])]

        if practice:
            story.append(PageBreak())
            story += practice_flowables(practice, s)
            if not no_answers:
                story.append(PageBreak())
                story += answer_key_flowables(practice, s)

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)


def main():
    parser = argparse.ArgumentParser(description="Turn study guide JSON into a PDF.")
    parser.add_argument("json_file", help="Path to the study guide JSON")
    parser.add_argument("output_pdf", help="Where to save the PDF")
    parser.add_argument("--no-answers", action="store_true",
                        help="Leave out the answer key")
    parser.add_argument("--answers-only", action="store_true",
                        help="Make only the answer key")
    args = parser.parse_args()

    try:
        with open(args.json_file, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Can't find {args.json_file}")
    except json.JSONDecodeError as e:
        sys.exit(f"That JSON file has a mistake near line {e.lineno}: {e.msg}")

    build(data, args.output_pdf, args.no_answers, args.answers_only)
    print(f"Saved {args.output_pdf}")


if __name__ == "__main__":
    main()
