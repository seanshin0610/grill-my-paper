#!/usr/bin/env python3
"""Set up a review-panel run folder and extract the paper to text.

Usage:
    python extract_paper.py <paper.pdf|.tex|.txt|.md> [--run-dir DIR]

Creates <paper-folder>/grill_<paper-name>_<YYYY-MM-DD>/ (or DIR) with the
subfolders the panel uses, writes paper.txt inside it, and prints a JSON summary.

PDF pages are separated by "===== Page N =====" markers that match the PDF's
page numbers, so reviewers can cite pages and open the same page in the PDF.
TeX sources have \\input / \\include files inlined and comments stripped.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

PAGE_MARK = "\n\n===== Page {n} =====\n\n"
FILE_MARK = "\n\n===== File: {name} =====\n\n"


def extract_pdf(path: Path):
    """Return (list of page texts, backend name). Tries several libraries."""
    errors = []

    try:
        import fitz  # PyMuPDF

        with fitz.open(str(path)) as doc:
            return [page.get_text("text") for page in doc], "pymupdf"
    except Exception as e:  # noqa: BLE001 - fall through to the next backend
        errors.append(f"pymupdf: {e}")

    try:
        import pdfplumber

        with pdfplumber.open(str(path)) as pdf:
            return [(p.extract_text() or "") for p in pdf.pages], "pdfplumber"
    except Exception as e:  # noqa: BLE001
        errors.append(f"pdfplumber: {e}")

    for mod in ("pypdf", "PyPDF2"):
        try:
            reader_cls = __import__(mod).PdfReader
            reader = reader_cls(str(path))
            return [(p.extract_text() or "") for p in reader.pages], mod
        except Exception as e:  # noqa: BLE001
            errors.append(f"{mod}: {e}")

    raise RuntimeError(
        "Could not extract text from the PDF. Install a PDF library "
        "(pip install pymupdf) and retry.\n  " + "\n  ".join(errors)
    )


_INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def _strip_tex_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("%"):
            continue
        # cut at the first unescaped %
        out.append(re.sub(r"(?<!\\)%.*$", "", line))
    return "\n".join(out)


def flatten_tex(path: Path, seen=None) -> str:
    """Inline \\input/\\include files, depth first, with file markers."""
    seen = seen if seen is not None else set()
    real = path.resolve()
    if real in seen:
        return ""
    seen.add(real)
    text = _strip_tex_comments(path.read_text(encoding="utf-8", errors="replace"))

    def repl(match):
        name = match.group(1).strip()
        child = (path.parent / name)
        if not child.suffix:
            child = child.with_suffix(".tex")
        if not child.exists():
            return f"\n[extract_paper: could not find {name}]\n"
        return FILE_MARK.format(name=child.name) + flatten_tex(child, seen)

    return _INPUT_RE.sub(repl, text)


def find_heading_page(pages, pattern):
    """First page on which a line matches the heading pattern (1-based), else None."""
    rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for i, text in enumerate(pages, start=1):
        if rx.search(text):
            return i
    return None


def make_run_dir(paper: Path, run_dir):
    if run_dir:
        base = Path(run_dir)
    else:
        slug = re.sub(r"[^A-Za-z0-9]+", "-", paper.stem).strip("-")[:40] or "paper"
        stamp = datetime.date.today().isoformat()
        base = paper.parent / f"grill_{slug}_{stamp}"
        n = 2
        while base.exists() and any(base.iterdir()):
            base = paper.parent / f"grill_{slug}_{stamp}-{n}"
            n += 1
    for sub in ("prompts", "round1", "round2"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paper")
    ap.add_argument("--run-dir", default=None, help="use this folder instead of creating one next to the paper")
    args = ap.parse_args()

    paper = Path(args.paper).expanduser()
    if not paper.exists():
        sys.exit(f"Paper not found: {paper}")

    suffix = paper.suffix.lower()
    summary = {"paper": str(paper.resolve()), "type": suffix.lstrip(".")}
    warnings = []

    if suffix == ".pdf":
        pages, backend = extract_pdf(paper)
        body = "".join(PAGE_MARK.format(n=i) + t.strip() for i, t in enumerate(pages, start=1))
        words_per_page = [len(t.split()) for t in pages]
        thin = [i for i, w in enumerate(words_per_page, start=1) if w < 40]
        summary.update(
            backend=backend,
            pages=len(pages),
            # Headings on their own line; these are guesses to help reviewers navigate.
            references_start_page=find_heading_page(pages, r"^\s*(References|Bibliography)\s*$"),
            appendix_start_page=find_heading_page(
                pages, r"^\s*((Internet |Online )?Appendix\b.{0,60}|Appendix [A-Z]\b.{0,60})$"
            ),
            pages_with_little_text=thin[:60],
        )
        total = sum(words_per_page)
        if pages and total / len(pages) < 80:
            warnings.append(
                "Very little text per page: the PDF may be scanned. Reviewers should read the PDF pages directly."
            )
    elif suffix == ".tex":
        body = FILE_MARK.format(name=paper.name) + flatten_tex(paper)
        if "could not find" in body:
            warnings.append("Some \\input files were not found; see the markers in paper.txt.")
    elif suffix in (".txt", ".md"):
        body = paper.read_text(encoding="utf-8", errors="replace")
    else:
        sys.exit(f"Unsupported file type: {suffix}. Use .pdf, .tex, .txt or .md.")

    run_dir = make_run_dir(paper, args.run_dir)
    out = run_dir / "paper.txt"
    out.write_text(body.strip() + "\n", encoding="utf-8")

    words = len(body.split())
    summary.update(
        run_dir=str(run_dir.resolve()),
        paper_txt=str(out.resolve()),
        words=words,
        approx_tokens=int(words * 1.4),
        warnings=warnings,
    )
    # ASCII-only output so Windows consoles with legacy code pages do not choke.
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
