# extract-pdf-pages

A small command-line utility to extract a page range from a PDF file and
write the result to a new PDF.

Features
- Extract contiguous page ranges from a PDF (start and end page).
- Extract specific non-contiguous pages in any order.
- Invert selection to extract all pages except the ones specified.
- Optionally split pages into separate PDF files with configurable part sizes.
- Small, single-purpose CLI suitable for scripts and automation.

Installation

Install from the project root using pip:

```bash
pip install .
```

Options

```text
# Flag           Type   Required?  Default
-i, --input     PATH   Yes        (none)         -- Path to the input PDF file
-s, --start     INT    No         first page     -- Start page (1-based, inclusive)
-e, --end       INT    No         last page      -- End page (1-based, inclusive)
-p, --pages     LIST   No         (none)         -- Specific page numbers to extract (e.g. 1 4 3). Overrides start/end
--invert        FLAG   No         False          -- Invert selection (extract all pages EXCEPT those specified)
-o, --output    PATH   No         <input>_pages_<start>-<end>.pdf -- Output path; generated next to input if omitted
--split         FLAG   No         False          -- Extract each page as a separate PDF file
--part-size     INT    No         1              -- Number of pages per part when splitting (only used with --split)
```

Examples

Extract pages 2 through 5 from example.pdf:

```bash
extract-pdf-pages -i example.pdf -s 2 -e 5 -o pages_2-5.pdf
```

Extract specific non-contiguous pages:

```bash
extract-pdf-pages -i example.pdf -p 1 5 3 10
```

Extract all pages EXCEPT 1, 3, and 5:

```bash
extract-pdf-pages -i example.pdf -p 1 3 5 --invert
```

Extract pages 1 through 10 as separate PDF files (one page per file):

```bash
extract-pdf-pages -i example.pdf -s 1 -e 10 --split
```

This will create: example_page_1.pdf, example_page_2.pdf, ..., example_page_10.pdf

Extract pages 1 through 20 split into parts of 5 pages each:

```bash
extract-pdf-pages -i example.pdf -s 1 -e 20 --split --part-size 5
```

This will create: example_part_1_pages_1-5.pdf, example_part_2_pages_6-10.pdf, example_part_3_pages_11-15.pdf, example_part_4_pages_16-20.pdf
 
