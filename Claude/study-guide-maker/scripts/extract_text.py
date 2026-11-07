#!/usr/bin/env python3
"""Print the text of a PDF so it can be used to build a study guide.

Usage:
    python extract_text.py notes.pdf
    python extract_text.py notes.pdf --pages 1-5

Needs: pip install pypdf
Note: scanned PDFs (photos of pages) have no text to extract. If the
output is empty, ask the student to paste the text or upload clearer
notes.
"""

import argparse
import sys

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("pypdf is not installed. Run: pip install pypdf")


def parse_range(text, total):
    """Turn '3' or '2-5' into zero-based page indexes."""
    try:
        if "-" in text:
            start, end = text.split("-", 1)
            start, end = int(start), int(end)
        else:
            start = end = int(text)
    except ValueError:
        sys.exit("Use --pages like 3 or 2-5")
    start = max(start, 1)
    end = min(end, total)
    if start > end:
        sys.exit(f"That PDF has {total} pages.")
    return range(start - 1, end)


def main():
    parser = argparse.ArgumentParser(description="Extract text from a PDF.")
    parser.add_argument("pdf", help="Path to the PDF")
    parser.add_argument("--pages", help="Page or range, like 3 or 2-5")
    args = parser.parse_args()

    try:
        reader = PdfReader(args.pdf)
    except FileNotFoundError:
        sys.exit(f"Can't find {args.pdf}")
    except Exception as e:
        sys.exit(f"Couldn't open that PDF: {e}")

    total = len(reader.pages)
    pages = parse_range(args.pages, total) if args.pages else range(total)

    found_any = False
    for i in pages:
        text = (reader.pages[i].extract_text() or "").strip()
        if text:
            found_any = True
        print(f"--- Page {i + 1} ---")
        print(text)
        print()

    if not found_any:
        print("(No text found. This may be a scanned PDF.)", file=sys.stderr)


if __name__ == "__main__":
    main()
