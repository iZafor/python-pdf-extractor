#!/usr/bin/env python3
"""
extract_pdf_pages.py

Usage:
  python extract_pdf_pages.py -i input.pdf -s 1 -e 3 -o output.pdf

This script extracts pages from `start` to `end` (inclusive, 1-based)
from the input PDF and writes them to the output PDF.

It prefers the modern `pypdf` package but falls back to `PyPDF2` if
`pypdf` is not available.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    # pypdf is the modern replacement for PyPDF2
    from pypdf import PdfReader, PdfWriter  # type: ignore
except Exception:
    try:
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter  # type: ignore
    except Exception:
        print(
            "Missing dependency: install pypdf (recommended) or PyPDF2\n"
            "Run: pip install pypdf\n",
            file=sys.stderr,
        )
        sys.exit(2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract a page range from a PDF into a new PDF file."
    )
    p.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Path to the input PDF file",
    )
    p.add_argument(
        "-s",
        "--start",
        required=False,
        type=int,
        default=None,
        help="Start page (1-based, inclusive). Defaults to first page if omitted.",
    )
    p.add_argument(
        "-e",
        "--end",
        required=False,
        type=int,
        default=None,
        help=("End page (1-based, inclusive). Defaults to last page if omitted."),
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Output PDF path. If omitted, a filename will be generated next to the input"
        ),
    )
    p.add_argument(
        "--split",
        action="store_true",
        help=(
            "Extract each page as a separate PDF file instead of a single combined file"
        ),
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    input_path: Path = args.input
    start: int | None = args.start
    end: int | None = args.end
    output_path: Path | None = args.output
    split: bool = args.split

    if not input_path.exists():
        print(f"Input file does not exist: {input_path}", file=sys.stderr)
        return 2

    # If start was provided, ensure it's valid; otherwise we'll default later
    if start is not None and start < 1:
        print("Start page must be >= 1", file=sys.stderr)
        return 2

    # Read input PDF
    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:  # pragma: no cover - runtime error handling
        print(f"Failed to open input PDF: {exc}", file=sys.stderr)
        return 2

    # pypdf exposes .pages and len(reader.pages); PyPDF2 exposes .getNumPages()
    try:
        num_pages = len(reader.pages)  # type: ignore
    except Exception:
        try:
            num_pages = reader.getNumPages()  # type: ignore
        except Exception as exc:  # pragma: no cover
            print(f"Unable to determine page count: {exc}", file=sys.stderr)
            return 2

    # Apply fallbacks: default start to first page, end to last page
    if start is None:
        start = 1
    if end is None:
        end = num_pages

    if start < 1:
        print("Start page must be >= 1", file=sys.stderr)
        return 2
    if end > num_pages:
        print(
            f"End page ({end}) exceeds document page count ({num_pages})",
            file=sys.stderr,
        )
        return 2
    if end < start:
        print("End page must be >= start page", file=sys.stderr)
        return 2

    # When splitting, create separate PDFs for each page
    if split:
        stem = input_path.stem
        parent = input_path.parent if output_path is None else output_path.parent

        created_files = []
        for pnum in range(start - 1, end):
            writer = PdfWriter()

            try:
                # pypdf uses reader.pages[pnum]
                page = reader.pages[pnum]  # type: ignore
                writer.add_page(page)  # type: ignore
            except Exception:
                # PyPDF2 older API
                try:
                    page = reader.getPage(pnum)  # type: ignore
                    writer.addPage(page)  # type: ignore
                except Exception as exc:  # pragma: no cover
                    print(f"Failed to extract page {pnum + 1}: {exc}", file=sys.stderr)
                    return 2

            # Generate output filename for this page
            page_output = parent / f"{stem}_page_{pnum + 1}.pdf"

            try:
                with open(page_output, "wb") as outf:
                    writer.write(outf)  # type: ignore
                created_files.append(page_output)
            except Exception as exc:
                print(f"Failed to write page {pnum + 1}: {exc}", file=sys.stderr)
                return 2

        print(f"Extracted {len(created_files)} pages as separate files:")
        for file_path in created_files:
            print(f"  {file_path}")
        return 0

    # Default output filename if not provided (non-split mode)
    if output_path is None:
        stem = input_path.stem
        parent = input_path.parent
        output_path = parent / f"{stem}_pages_{start}-{end}.pdf"

    writer = PdfWriter()

    # Add requested pages (convert to 0-based)
    for pnum in range(start - 1, end):
        try:
            # pypdf uses reader.pages[pnum]
            page = reader.pages[pnum]  # type: ignore
            writer.add_page(page)  # type: ignore
        except Exception:
            # PyPDF2 older API
            try:
                page = reader.getPage(pnum)  # type: ignore
                writer.addPage(page)  # type: ignore
            except Exception as exc:  # pragma: no cover
                print(f"Failed to extract page {pnum + 1}: {exc}", file=sys.stderr)
                return 2

    # Write output
    try:
        with open(output_path, "wb") as outf:
            try:
                # pypdf PdfWriter has write(fileobj)
                writer.write(outf)  # type: ignore
            except Exception:
                # PyPDF2 PdfFileWriter uses write as well, keep fallback
                writer.write(outf)  # type: ignore
    except Exception as exc:
        print(f"Failed to write output PDF: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote pages {start}-{end} to {output_path}")
    return 0


def cli() -> None:
    """Console entry point for packaging (calls main and exits)."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
