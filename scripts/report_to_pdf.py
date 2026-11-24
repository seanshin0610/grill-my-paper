#!/usr/bin/env python3
"""Render a panel report written in Markdown as a PDF for reading and sharing.

Usage:
    python report_to_pdf.py <PANEL_REPORT.md> [--out FILE.pdf] [--paper a4|letter]

The PDF is written next to the Markdown file, with the same name, unless --out is
given. The Markdown file is only read; it stays the source, and the PDF is a copy
made from it. Run the script again after editing the report.

The script replaces an existing PDF only if this script made it. Any other file
with the output's name is left alone and the script stops, so it cannot overwrite
a paper or anything else that happens to share the name.

Needs two packages: pip install pymupdf markdown
"""

import argparse
import io
import re
import sys
from pathlib import Path

PRODUCER = "grill-my-paper report_to_pdf"

CSS = """
body { font-family: sans-serif; font-size: 10.5pt; line-height: 1.42; color: #1a1a1a; }
h1 { font-size: 17pt; margin-top: 0; margin-bottom: 8pt; }
h2 { font-size: 13pt; margin-top: 16pt; margin-bottom: 5pt; color: #12305a; }
h3 { font-size: 11.5pt; margin-top: 12pt; margin-bottom: 4pt; }
h4 { font-size: 10.5pt; margin-top: 10pt; margin-bottom: 3pt; }
p { margin-top: 0; margin-bottom: 6pt; }
ul { margin-top: 0; margin-bottom: 6pt; padding-left: 14pt; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; margin-top: 4pt; margin-bottom: 8pt; font-size: 9pt; }
th, td { border: 0.5pt solid #8a8a8a; padding: 3pt 4pt; text-align: left; vertical-align: top; }
th { border-bottom: 1.2pt solid #333333; }
code { font-family: monospace; font-size: 9pt; }
"""
# No background colour on table headers: the renderer repeats such a fill on later pages.


def _fitz():
    try:
        import pymupdf as fitz  # current name of the package's module
    except ImportError:
        import fitz  # older releases
    return fitz


def to_html(md_text: str) -> str:
    import markdown

    # The report's header is a few "**Label:** value" lines in one paragraph. Markdown would run them
    # together, so end each with a hard break. Only the part before the first section is touched.
    head, sep, rest = md_text.partition("\n## ")
    head = re.sub(r"\n(?=\*\*[A-Z][A-Za-z ]*:\*\*)", "  \n", head)
    return markdown.markdown(head + sep + rest, extensions=["tables", "sane_lists"])


def made_by_this_script(path: Path) -> bool:
    try:
        with _fitz().open(str(path)) as doc:
            return (doc.metadata or {}).get("producer") == PRODUCER
    except Exception:  # noqa: BLE001 - not a PDF we can read, so not ours
        return False


def render(html: str, out: Path, paper: str, title: str) -> int:
    fitz = _fitz()
    box = fitz.paper_rect(paper)
    where = box + (56, 54, -56, -62)  # margins; the bottom one leaves room for the page number
    story = fitz.Story(html=html, user_css=CSS)
    buf = io.BytesIO()
    writer = fitz.DocumentWriter(buf)
    more = 1
    while more:
        dev = writer.begin_page(box)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()

    doc = fitz.open("pdf", buf.getvalue())
    for i, page in enumerate(doc, start=1):
        r = page.rect
        page.insert_textbox(fitz.Rect(r.x0, r.y1 - 40, r.x1, r.y1 - 24), f"{i} / {doc.page_count}",
                            fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4), align=1)
    doc.set_metadata({"producer": PRODUCER, "title": title})
    doc.save(str(out), garbage=3, deflate=True)
    pages = doc.page_count
    doc.close()
    return pages


def main():
    ap = argparse.ArgumentParser(description="Render a Markdown panel report as a PDF.")
    ap.add_argument("report")
    ap.add_argument("--out", default=None, help="output file (default: same name with .pdf, next to the report)")
    ap.add_argument("--paper", default="a4", choices=["a4", "letter"])
    args = ap.parse_args()

    src = Path(args.report)
    if not src.is_file():
        sys.exit(f"Report not found: {src}")
    out = Path(args.out) if args.out else src.with_suffix(".pdf")
    if out.suffix.lower() != ".pdf":
        sys.exit(f"The output file must end in .pdf: {out}")
    try:
        if out.exists() and not made_by_this_script(out):
            sys.exit(f"Not overwriting {out}: it exists and this script did not make it. "
                     "Choose another name with --out.")
        text = src.read_text(encoding="utf-8")
        first = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        pages = render(to_html(text), out, args.paper, first.group(1).strip() if first else src.stem)
    except ImportError as e:
        sys.exit(f"Missing package ({e.name or e}). Install with: pip install pymupdf markdown")
    except AttributeError as e:
        sys.exit(f"This needs a newer PyMuPDF ({e}). Update with: pip install -U pymupdf")
    print(f"{out} ({pages} pages)")


if __name__ == "__main__":
    main()
