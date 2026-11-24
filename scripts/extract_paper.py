#!/usr/bin/env python3
"""Set up a review-panel run folder and gather the paper's materials as text.

Usage:
    python extract_paper.py <paper.pdf|.tex|.txt|.md> [--also FILE ...]
                            [--run-dir DIR] [--no-git-exclude]

Creates <paper-folder>/grill_<paper-name>_<YYYY-MM-DD>/ (or DIR) with the
subfolders the panel uses, writes paper.txt inside it, and prints a JSON summary.

PDF sources: pages are separated by "===== Page N =====" markers that match the
PDF's page numbers, so reviewers cite pages.

TeX sources: there are no pages, so reviewers cite sections, labels, or line
numbers. Line N of paper.txt is line N of the .tex: comments are blanked, not
removed, and files pulled in with \\input / \\include are placed after the main
file as separate blocks instead of being spliced in. "line_map" in the summary
(and at the foot of paper.txt) says which lines belong to which file.
The script also gathers what the source points to:
  - \\externaldocument{...}  -> the online appendix, flattened to <name>.txt
  - \\includegraphics{...}   -> figure files, copied to figures/
  - \\bibliography / \\addbibresource -> .bib files, copied alongside

--also adds any other file (an appendix PDF, a second TeX file, a figure).

The paper and the files it points to are read and copied, never changed. Everything
is written inside the run folder, which must be new or empty (the default name gets
a -2, -3 suffix if needed; an explicit --run-dir that already holds files is refused).

If the run folder lands inside a git repository, the script adds it to that
repository's .git/info/exclude. That file is local to this machine, so the run
folder cannot be committed or pushed by accident and collaborators see nothing.
"""

import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

PAGE_MARK = "\n\n===== Page {n} =====\n\n"
FIGURE_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
FIGURE_ENV_RE = re.compile(r"\\begin\{(figure\*?|sidewaysfigure)\}(.*?)\\end\{\1\}", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
EXTDOC_RE = re.compile(r"\\externaldocument\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\s*\{([^}]+)\}")
BIBRES_RE = re.compile(r"\\addbibresource\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
# \newcommand{\bib}{master.bib} and \def\bib{master.bib}; macros with arguments are skipped.
MACRO_RE = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand)\s*\{?\\([A-Za-z]+)\}?\s*\{([^{}]*)\}"
    r"|\\def\s*\\([A-Za-z]+)\s*\{([^{}]*)\}"
)


# ---------- reading sources ----------

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


def _tex_lines(path: Path):
    """The file's lines with comments blanked.

    A comment-only line becomes an empty line; it is not dropped. Line N of the
    result is therefore line N of the file, which is what lets a reviewer's
    "line 103" be found in the author's editor.
    """
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return ["" if ln.lstrip().startswith("%") else re.sub(r"(?<!\\)%.*$", "", ln) for ln in lines]


def flatten_tex(path: Path):
    """Return (text, line_map) for a TeX source and the files it pulls in.

    The main file comes first, line for line, so line N of the text is always line N
    of the .tex the author edits. Files named by \\input, \\include or \\subfile are
    not spliced in where they are called, because that would shift every later line
    number. Each one follows the main file as a block of its own under a marker, in
    the order the paper calls them, and the calling line gets a note saying where
    its block starts.

    line_map has one entry per block: {"file", "first", "last", "subtract"}. A line
    number of the text minus "subtract" is the line number inside that file.
    """
    root_dir = path.parent.resolve()
    order, lines_of, calls = [], {}, {}

    def find(name: str, including: Path):
        # LaTeX resolves \input against the main file's folder; \subfile against the calling file's.
        for base in (root_dir, including.parent):
            child = base / name
            if not child.suffix:
                child = child.with_suffix(".tex")
            if child.exists():
                return child.resolve()
        return None

    def load(p: Path):  # depth first, so a section is followed by the tables it pulls in
        order.append(p)
        lines_of[p] = _tex_lines(p)
        calls[p] = {}
        for i, line in enumerate(lines_of[p]):
            for m in INPUT_RE.finditer(line):
                name = m.group(1).strip()
                child = find(name, p)
                calls[p].setdefault(i, []).append(child or name)
                if child and child not in lines_of:
                    load(child)

    def label(p: Path) -> str:
        try:
            return p.relative_to(root_dir).as_posix()
        except ValueError:
            return p.name

    load(path.resolve())

    first, n = {}, 0  # where each block starts: two lines (a blank and a marker) separate blocks
    for p in order:
        n += 2 if n else 0
        first[p] = n + 1
        n += len(lines_of[p])

    out, line_map = [], []
    for p in order:
        if out:
            out += ["", f"===== File: {label(p)} (pulled in by the paper; the next line is its line 1) ====="]
        for i, line in enumerate(lines_of[p]):
            notes = [f"[extract_paper: could not find {c}]" if isinstance(c, str)
                     else f"[extract_paper: {label(c)} starts at line {first[c]}]"
                     for c in calls[p].get(i, [])]
            out.append("  ".join([line, *notes]) if notes else line)
        line_map.append({"file": label(p), "first": first[p], "last": first[p] + len(lines_of[p]) - 1,
                         "subtract": first[p] - 1})
    if len(order) > 1:
        out += ["", "===== Line map (added by the extractor; not part of the paper) ====="]
        out += [f"lines {b['first']}-{b['last']}: {b['file']}"
                + (f" (subtract {b['subtract']} for its own line number)" if b["subtract"] else " (same line numbers)")
                for b in line_map]
    return "\n".join(out), line_map


def find_heading_page(pages, pattern):
    """First page on which a line matches the heading pattern (1-based), else None."""
    rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for i, text in enumerate(pages, start=1):
        if rx.search(text):
            return i
    return None


def read_source(path: Path):
    """Return (text, info) for a .pdf, .tex, .txt or .md file. info['anchor'] is 'pages' or 'lines'."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pages, backend = extract_pdf(path)
        body = "".join(PAGE_MARK.format(n=i) + t.strip() for i, t in enumerate(pages, start=1))
        words_per_page = [len(t.split()) for t in pages]
        info = {
            "anchor": "pages",
            "backend": backend,
            "pages": len(pages),
            # Headings on their own line; guesses to help reviewers navigate.
            "references_start_page": find_heading_page(pages, r"^\s*(References|Bibliography)\s*$"),
            "appendix_start_page": find_heading_page(
                pages, r"^\s*((Internet |Online )?Appendix\b.{0,60}|Appendix [A-Z]\b.{0,60})$"
            ),
            "pages_with_little_text": [i for i, w in enumerate(words_per_page, start=1) if w < 40][:60],
        }
        if pages and sum(words_per_page) / len(pages) < 80:
            info["warning"] = (
                f"{path.name}: very little text per page, so the PDF may be scanned. "
                "Reviewers should read the PDF pages directly."
            )
        return body, info
    if suffix == ".tex":
        body, line_map = flatten_tex(path)
        info = {"anchor": "lines", "line_map": line_map}
        if "[extract_paper: could not find" in body:
            info["warning"] = f"{path.name}: some \\input files were not found; see the notes in the text."
        return body, info
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace"), {"anchor": "lines"}
    raise ValueError(f"Unsupported file type: {suffix}. Use .pdf, .tex, .txt or .md.")


# ---------- what a TeX source points to ----------

def tex_macros(text: str) -> dict:
    macros = {}
    for m in MACRO_RE.finditer(text):
        name, value = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        macros[name] = value.strip()
    return macros


def _resolve_macro(arg: str, macros: dict) -> str:
    arg = arg.strip()
    if arg.startswith("\\"):
        return macros.get(arg[1:], arg)
    return arg


def find_external_documents(text: str, base: Path):
    """[(prefix, path)] for \\externaldocument[prefix]{name}."""
    out = []
    for m in EXTDOC_RE.finditer(text):
        p = base / m.group(2).strip()
        if not p.suffix:
            p = p.with_suffix(".tex")
        out.append((m.group(1) or "", p))
    return out


def find_bib_files(text: str, base: Path, macros: dict):
    names = []
    for m in BIB_RE.finditer(text):
        names += [_resolve_macro(n, macros) for n in m.group(1).split(",")]
    for m in BIBRES_RE.finditer(text):
        names.append(_resolve_macro(m.group(1), macros))
    paths = []
    for n in names:
        p = base / n
        if p.suffix.lower() != ".bib":
            p = p.with_name(p.name + ".bib")
        if p not in paths:
            paths.append(p)
    return paths


def _resolve_figure(name: str, base: Path):
    p = base / name.strip()
    if p.suffix and p.exists():
        return p
    for ext in FIGURE_EXTS:
        q = p.with_name(p.name + ext)
        if q.exists():
            return q
    return None


def find_figures(text: str, base: Path, label_prefix: str = ""):
    """[(resolved path or None, name as written, [labels])] in order of appearance."""
    found, spans = [], []
    for env in FIGURE_ENV_RE.finditer(text):
        spans.append(env.span())
        labels = [label_prefix + lab for lab in LABEL_RE.findall(env.group(2))]
        for m in INCLUDEGRAPHICS_RE.finditer(env.group(2)):
            found.append((_resolve_figure(m.group(1), base), m.group(1).strip(), labels))
    for m in INCLUDEGRAPHICS_RE.finditer(text):  # graphics outside figure environments
        if not any(a <= m.start() < b for a, b in spans):
            found.append((_resolve_figure(m.group(1), base), m.group(1).strip(), []))
    return found


# ---------- run folder ----------

def make_run_dir(paper: Path, run_dir):
    if run_dir:
        base = Path(run_dir)
        # Every file this script writes goes into the run folder. Starting from an empty one is what
        # guarantees that nothing already on disk (the paper, a figure, an earlier report) is replaced.
        if base.is_file() or (base.is_dir() and any(p.is_file() for p in base.rglob("*"))):
            sys.exit(f"The run folder must be new or empty, so that no existing file can be overwritten: {base}")
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


def _find_git(start: Path):
    """(work tree root, git dir holding info/exclude) for the repository containing start, else None."""
    for d in [start, *start.parents]:
        g = d / ".git"
        if g.is_dir():
            if (g / "HEAD").is_file():  # a stray empty .git folder is not a repository
                return d, g
            continue
        if g.is_file():  # worktree or submodule: a file that points at the git dir
            line = g.read_text(encoding="utf-8", errors="replace").strip()
            if line.startswith("gitdir:"):
                gd = Path(line.split(":", 1)[1].strip())
                if not gd.is_absolute():
                    gd = (d / gd).resolve()
                common = gd / "commondir"
                if common.is_file():
                    gd = (gd / common.read_text(encoding="utf-8").strip()).resolve()
                if (gd / "HEAD").is_file():
                    return d, gd
    return None


EXCLUDE_PATTERN = "grill_*/"


def git_exclude(run_dir: Path):
    """Keep the run folder out of the surrounding git repository, locally only.

    Adds one line, grill_*/, to that repository's .git/info/exclude (once). A run
    folder with another name (an explicit --run-dir) is left alone and only reported,
    so the exclude file never fills up with one-off paths.
    """
    try:
        found = _find_git(run_dir.resolve().parent)
        if not found:
            return None
        root, gitdir = found
        if not run_dir.name.startswith("grill_"):
            return {"repository": str(root), "added": False,
                    "note": "The run folder is inside this git repository and is NOT excluded, "
                            "because its name does not start with grill_."}
        exclude = gitdir / "info" / "exclude"
        existing = exclude.read_text(encoding="utf-8", errors="replace") if exclude.exists() else ""
        added = EXCLUDE_PATTERN not in [ln.strip() for ln in existing.splitlines()]
        if added:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            sep = "" if existing.endswith("\n") or not existing else "\n"
            with exclude.open("a", encoding="utf-8", newline="\n") as fh:
                fh.write(f"{sep}# grill-my-paper run folders (local only, not shared)\n{EXCLUDE_PATTERN}\n")
        return {"repository": str(root), "exclude_file": str(exclude),
                "pattern": EXCLUDE_PATTERN, "added": added}
    except (OSError, ValueError) as e:
        return {"error": f"could not update git exclude: {e}"}


def _unique_name(folder: Path, name: str, taken: dict, source: Path) -> str:
    """A file name inside folder that does not collide with a different source."""
    key = source.resolve()
    if taken.get(name, key) != key:
        name = f"{source.parent.name}_{name}"
    taken[name] = key
    return name


def main():
    ap = argparse.ArgumentParser(description="Set up a review-panel run folder and gather the paper's materials.")
    ap.add_argument("paper")
    ap.add_argument("--also", action="append", default=[], metavar="FILE",
                    help="another file reviewers should have (appendix, second source, figure); repeatable")
    ap.add_argument("--run-dir", default=None, help="use this folder instead of creating one next to the paper")
    ap.add_argument("--no-git-exclude", action="store_true",
                    help="do not add the run folder to the surrounding repository's .git/info/exclude")
    args = ap.parse_args()

    paper = Path(args.paper).expanduser()
    if not paper.exists():
        sys.exit(f"Paper not found: {paper}")
    try:
        body, info = read_source(paper)
    except ValueError as e:
        sys.exit(str(e))

    warnings, missing = [], []
    if "warning" in info:
        warnings.append(info.pop("warning"))

    def write_text(target: Path, text: str, src_info: dict):
        # Leading blank lines stay when locations are cited by line; removing them would shift every number.
        text = text.rstrip() if src_info.get("anchor") == "lines" else text.strip()
        with target.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")

    run_dir = make_run_dir(paper, args.run_dir)
    out = run_dir / "paper.txt"
    write_text(out, body, info)

    text_names = {"paper.txt": paper.resolve()}
    fig_names, companions, figures, bibs = {}, [], [], []
    fig_dir = run_dir / "figures"

    def add_text(source: Path, role: str, text: str, src_info: dict, prefix: str = ""):
        name = _unique_name(run_dir, source.stem + ".txt", text_names, source)
        write_text(run_dir / name, text, src_info)
        entry = {"role": role, "source": str(source.resolve()), "text": str((run_dir / name).resolve()),
                 "anchor": src_info.get("anchor"), "words": len(text.split())}
        if "line_map" in src_info:
            entry["line_map"] = src_info["line_map"]
        if prefix:
            entry["label_prefix"] = prefix
        if "pages" in src_info:
            entry["pages"] = src_info["pages"]
        companions.append(entry)

    def add_figures(text: str, base: Path, belongs_to: str, prefix: str = ""):
        for path, written, labels in find_figures(text, base, prefix):
            if path is None:
                missing.append(f"figure not found: {written} (in {belongs_to})")
                continue
            name = _unique_name(fig_dir, path.name, fig_names, path)
            fig_dir.mkdir(exist_ok=True)
            if not (fig_dir / name).exists():
                shutil.copy2(path, fig_dir / name)
            figures.append({"file": str((fig_dir / name).resolve()), "labels": labels, "in": belongs_to})

    def add_bibs(text: str, base: Path):
        for bib in find_bib_files(text, base, tex_macros(text)):
            if not bib.exists():
                missing.append(f"bibliography not found: {bib.name}")
            elif str(bib.resolve()) not in [b["source"] for b in bibs]:
                shutil.copy2(bib, run_dir / bib.name)
                bibs.append({"source": str(bib.resolve()), "file": str((run_dir / bib.name).resolve())})

    if paper.suffix.lower() == ".tex":
        add_figures(body, paper.parent, "paper")
        add_bibs(body, paper.parent)
        for prefix, ext in find_external_documents(body, paper.parent):
            if not ext.exists():
                missing.append(f"external document not found: {ext.name}")
                continue
            ext_body, ext_info = read_source(ext)
            if "warning" in ext_info:
                warnings.append(ext_info.pop("warning"))
            add_text(ext, "appendix", ext_body, ext_info, prefix)
            add_figures(ext_body, ext.parent, ext.name, prefix)
            add_bibs(ext_body, ext.parent)

    for extra in args.also:
        p = Path(extra).expanduser()
        if not p.exists():
            missing.append(f"--also file not found: {extra}")
            continue
        if p.suffix.lower() in (".pdf", ".tex", ".txt", ".md"):
            extra_body, extra_info = read_source(p)
            if "warning" in extra_info:
                warnings.append(extra_info.pop("warning"))
            add_text(p, "also", extra_body, extra_info)
            if p.suffix.lower() == ".tex":
                add_figures(extra_body, p.parent, p.name)
        else:  # an image or other file: hand it over as is
            name = _unique_name(fig_dir, p.name, fig_names, p)
            fig_dir.mkdir(exist_ok=True)
            shutil.copy2(p, fig_dir / name)
            figures.append({"file": str((fig_dir / name).resolve()), "labels": [], "in": "--also"})

    words = len(body.split())
    summary = {"paper": str(paper.resolve()), "type": paper.suffix.lower().lstrip("."), **info,
               "run_dir": str(run_dir.resolve()), "paper_txt": str(out.resolve()),
               "words": words, "approx_tokens": int(words * 1.4),
               "companions": companions, "figures": figures, "bibliography": bibs}
    if not args.no_git_exclude:
        excl = git_exclude(run_dir)
        if excl:
            summary["git_exclude"] = excl
    summary["missing"] = missing
    summary["warnings"] = warnings
    # ASCII-only output so Windows consoles with legacy code pages do not choke.
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
