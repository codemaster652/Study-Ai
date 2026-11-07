#!/usr/bin/env python3
"""Combine several PDFs into one, in the order given.

Usage:
    python merge_pdfs.py combined.pdf guide.pdf answer-key.pdf

Needs: pip install pypdf
"""

import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("pypdf is not installed. Run: pip install pypdf")


def main():
    if len(sys.argv) < 4:
        sys.exit("Usage: python merge_pdfs.py output.pdf input1.pdf input2.pdf [...]")

    output, inputs = sys.argv[1], sys.argv[2:]
    writer = PdfWriter()

    for path in inputs:
        try:
            reader = PdfReader(path)
        except FileNotFoundError:
            sys.exit(f"Can't find {path}")
        except Exception as e:
            sys.exit(f"Couldn't open {path}: {e}")
        for page in reader.pages:
            writer.add_page(page)

    with open(output, "wb") as f:
        writer.write(f)
    print(f"Saved {output} ({len(writer.pages)} pages)")


if __name__ == "__main__":
    main()
