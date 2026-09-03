#!/usr/bin/env python3
"""Count CUMCM body pages between the abstract page and appendix."""

from __future__ import annotations

import argparse
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
import json
import re
import shutil
import subprocess
from pathlib import Path


ABSTRACT_RE = re.compile(r"^摘\s*要$")
APPENDIX_RE = re.compile(r"^附\s*录$")
SECTION_RE = re.compile(r"^([一二三四五六七八九十]+)、\s*(.+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="check CUMCM PDF body page count")
    parser.add_argument("pdf", nargs="?", default="paper/论文.pdf", type=Path)
    parser.add_argument("--min-pages", type=int, default=27)
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--appendix-min-pages", type=int, default=9)
    parser.add_argument("--appendix-max-pages", type=int, default=11)
    parser.add_argument("--draft", action="store_true", help="allow missing abstract/appendix boundaries")
    parser.add_argument("--pdftotext", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def normalized_lines(text: str) -> list[str]:
    return [re.sub(r"[ \t\u3000]+", "", line.strip()) for line in text.splitlines() if line.strip()]


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        import fitz  # type: ignore
    except ImportError:
        errors.append("PyMuPDF (fitz) is not installed")
        fitz = None

    if not args.pdf.exists():
        errors.append(f"pdf not found: {args.pdf}")

    page_texts: list[str] = []
    if not errors and fitz is not None:
        try:
            document = fitz.open(str(args.pdf))
            page_count = document.page_count
            document.close()
            pdftotext = str(args.pdftotext) if args.pdftotext else (
                shutil.which("pdftotext") or shutil.which("pdftotext.exe")
            )
            if not pdftotext:
                errors.append("pdftotext not found; pass --pdftotext")
            else:
                completed = subprocess.run(
                    [pdftotext, "-layout", "-enc", "UTF-8", str(args.pdf), "-"],
                    check=True,
                    capture_output=True,
                )
                extracted = completed.stdout.decode("utf-8", errors="replace").split("\f")
                if extracted and not extracted[-1].strip():
                    extracted.pop()
                if len(extracted) == page_count:
                    page_texts = extracted
                else:
                    # Fallback for pdftotext builds that omit form-feed page separators.
                    for page_number in range(1, page_count + 1):
                        page_result = subprocess.run(
                            [
                                pdftotext,
                                "-f",
                                str(page_number),
                                "-l",
                                str(page_number),
                                str(args.pdf),
                                "-",
                            ],
                            check=True,
                            capture_output=True,
                        )
                        page_texts.append(page_result.stdout.decode("utf-8", errors="replace"))
        except Exception as exc:
            errors.append(f"cannot open PDF: {exc}")

    abstract_index = None
    appendix_index = None
    section_starts: list[dict[str, object]] = []
    for index, text in enumerate(page_texts):
        lines = normalized_lines(text)
        if abstract_index is None and any(ABSTRACT_RE.fullmatch(line) for line in lines):
            abstract_index = index
        if appendix_index is None and any(APPENDIX_RE.fullmatch(line) for line in lines):
            appendix_index = index
        for line in lines:
            match = SECTION_RE.fullmatch(line)
            if match:
                section_starts.append({"page": index + 1, "title": f"{match.group(1)}、{match.group(2)}"})
            elif line in {"AI工具使用声明", "参考文献"}:
                section_starts.append({"page": index + 1, "title": line})

    if args.draft:
        body_start = abstract_index + 1 if abstract_index is not None else 0
        body_end = appendix_index if appendix_index is not None else len(page_texts)
    else:
        if abstract_index is None:
            errors.append("abstract heading not found")
        if appendix_index is None:
            errors.append("appendix heading not found")
        body_start = abstract_index + 1 if abstract_index is not None else 0
        body_end = appendix_index if appendix_index is not None else len(page_texts)
        if abstract_index is not None and appendix_index is not None and appendix_index <= abstract_index:
            errors.append("appendix must appear after abstract and body")

    body_pages = max(0, body_end - body_start)
    if not args.draft and not (args.min_pages <= body_pages <= args.max_pages):
        errors.append(
            f"body page count {body_pages} outside allowed range [{args.min_pages}, {args.max_pages}]"
        )

    appendix_pages = max(0, len(page_texts) - appendix_index) if appendix_index is not None else 0
    if not args.draft and appendix_index is not None and not (
        args.appendix_min_pages <= appendix_pages <= args.appendix_max_pages
    ):
        errors.append(
            f"appendix page count {appendix_pages} outside allowed range "
            f"[{args.appendix_min_pages}, {args.appendix_max_pages}]"
        )

    result = {
        "status": "pass" if not errors else "fail",
        "mode": "draft" if args.draft else "final",
        "pdf": str(args.pdf),
        "total_pdf_pages": len(page_texts),
        "abstract_page": abstract_index + 1 if abstract_index is not None else None,
        "body_start_page": body_start + 1 if page_texts else None,
        "appendix_page": appendix_index + 1 if appendix_index is not None else None,
        "body_pages": body_pages,
        "appendix_pages": appendix_pages,
        "allowed_range": [args.min_pages, args.max_pages],
        "appendix_allowed_range": [args.appendix_min_pages, args.appendix_max_pages],
        "section_starts": section_starts,
        "errors": errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
