#!/usr/bin/env python3
"""Audit CUMCM abstract typography and first-page vertical occupancy."""

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
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
TITLE_RE = re.compile(
    r"\{(?=[^\n]*\\zihao\{3\})(?=[^\n]*\\heiti)(?=[^\n]*\\bfseries)"
    r"(?![^\n]*摘(?:\\quad|\s)*要)[^\n]*\\par\s*\}"
)
ABSTRACT_HEADING_RE = re.compile(
    r"\{(?=[^\n]*\\zihao\{3\})(?=[^\n]*\\heiti)(?=[^\n]*\\bfseries)"
    r"[^\n]*摘(?:\\quad|\s)*要[^\n]*\\par\s*\}"
)
ABSTRACT_BODY_STYLE_RE = re.compile(
    r"\\songti\s*\\zihao\{-4\}|\\zihao\{-4\}\s*\\songti"
)
KEYWORDS_STYLE_RE = re.compile(
    r"\\noindent(?=[\s\S]{0,300}\\heiti)(?=[\s\S]{0,300}\\zihao\{-4\})"
    r"[\s\S]{0,300}关键词[\s\S]{0,300}\\songti[\s\S]{0,120}\\zihao\{-4\}",
)
FORBIDDEN_FILL_RE = re.compile(
    r"\\vfill|\\vspace\*?\{[^}]*fill[^}]*\}|\\enlargethispage",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--abstract-tex", required=True, type=Path)
    parser.add_argument("--pdftotext", type=Path)
    parser.add_argument("--margin-cm", type=float, default=2.54)
    parser.add_argument("--min-fill", type=float, default=0.78)
    parser.add_argument("--max-fill", type=float, default=0.90)
    parser.add_argument("--min-han", type=int, default=800)
    parser.add_argument("--max-han", type=int, default=1000)
    parser.add_argument(
        "--allow-title-override",
        action="store_true",
        help="Accept title sizes supplied by an official template or explicit user rule.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def find_pdftotext(explicit: Path | None) -> str:
    if explicit:
        return str(explicit)
    found = shutil.which("pdftotext") or shutil.which("pdftotext.exe")
    if not found:
        raise FileNotFoundError("pdftotext not found; pass --pdftotext")
    return found


def first_page_words(pdf: Path, pdftotext: str) -> tuple[float, float, list[dict[str, object]]]:
    with tempfile.TemporaryDirectory(prefix="cumcm-abstract-") as tmp:
        bbox = Path(tmp) / "page.xml"
        subprocess.run(
            [pdftotext, "-f", "1", "-l", "1", "-bbox-layout", str(pdf), str(bbox)],
            check=True,
            capture_output=True,
        )
        root = ET.parse(bbox).getroot()

    page = next(node for node in root.iter() if node.tag.endswith("page"))
    width = float(page.attrib["width"])
    height = float(page.attrib["height"])
    words: list[dict[str, object]] = []
    for node in page.iter():
        if not node.tag.endswith("word"):
            continue
        text = "".join(node.itertext()).strip()
        if not text:
            continue
        words.append(
            {
                "text": text,
                "x_min": float(node.attrib["xMin"]),
                "y_min": float(node.attrib["yMin"]),
                "x_max": float(node.attrib["xMax"]),
                "y_max": float(node.attrib["yMax"]),
            }
        )
    return width, height, words


def group_lines(words: list[dict[str, object]], tolerance: float = 2.0) -> list[list[dict[str, object]]]:
    """Group bbox words into visual lines so title/keyword boundaries are measurable."""
    lines: list[list[dict[str, object]]] = []
    for word in sorted(words, key=lambda item: (float(item["y_min"]), float(item["x_min"]))):
        y_min = float(word["y_min"])
        target = next(
            (
                line
                for line in lines
                if abs(y_min - min(float(item["y_min"]) for item in line)) <= tolerance
            ),
            None,
        )
        if target is None:
            lines.append([word])
        else:
            target.append(word)
    for line in lines:
        line.sort(key=lambda item: float(item["x_min"]))
    return lines


def main() -> int:
    args = parse_args()
    pdftotext = find_pdftotext(args.pdftotext)
    _, page_height, words = first_page_words(args.pdf, pdftotext)
    tex = args.abstract_tex.read_text(encoding="utf-8")

    # Ignore the isolated footer page number when locating abstract content.
    content_words = [
        word
        for word in words
        if not (
            float(word["y_min"]) > page_height * 0.90
            and re.fullmatch(r"\d+", str(word["text"]))
        )
    ]
    margin_pt = args.margin_cm * 72.0 / 2.54
    printable_height = page_height - 2.0 * margin_pt
    content_bottom = max(float(word["y_max"]) for word in content_words)
    fill_ratio = (content_bottom - margin_pt) / printable_height
    text = "".join(str(word["text"]) for word in content_words)
    lines = group_lines(content_words)
    heading_line = next(
        (
            line
            for line in lines
            if re.sub(r"\s+", "", "".join(str(word["text"]) for word in line)) == "摘要"
        ),
        None,
    )
    keyword_line = next(
        (
            line
            for line in lines
            if re.sub(r"\s+", "", "".join(str(word["text"]) for word in line)).startswith("关键词")
        ),
        None,
    )
    body_bounds_found = heading_line is not None and keyword_line is not None
    if body_bounds_found:
        body_top = max(float(word["y_max"]) for word in heading_line)
        body_bottom = min(float(word["y_min"]) for word in keyword_line)
        abstract_body_words = [
            word
            for word in content_words
            if float(word["y_min"]) > body_top and float(word["y_max"]) < body_bottom
        ]
    else:
        body_top = None
        body_bottom = None
        abstract_body_words = []
    abstract_body_text = "".join(str(word["text"]) for word in abstract_body_words)
    han_count = len(HAN_RE.findall(abstract_body_text))

    checks = {
        "title_size_three": args.allow_title_override or bool(TITLE_RE.search(tex)),
        "abstract_heading_size_three": args.allow_title_override
        or bool(ABSTRACT_HEADING_RE.search(tex)),
        "abstract_body_smallfour_song": bool(ABSTRACT_BODY_STYLE_RE.search(tex)),
        "keywords_heiti_label_song_content": bool(KEYWORDS_STYLE_RE.search(tex)),
        "han_count_in_range": args.min_han <= han_count <= args.max_han,
        "fill_ratio_in_range": args.min_fill <= fill_ratio <= args.max_fill,
        "keywords_on_first_page": "关键词" in text,
        "abstract_body_bounds_found": body_bounds_found,
        "no_forbidden_fill_macro": not bool(FORBIDDEN_FILL_RE.search(tex)),
    }
    result = {
        "status": "pass" if all(checks.values()) else "fail",
        "pdf": str(args.pdf),
        "abstract_tex": str(args.abstract_tex),
        "page_height_pt": round(page_height, 3),
        "margin_cm": args.margin_cm,
        "content_bottom_pt": round(content_bottom, 3),
        "fill_ratio": round(fill_ratio, 4),
        "fill_range": [args.min_fill, args.max_fill],
        "han_count": han_count,
        "han_range": [args.min_han, args.max_han],
        "abstract_body_top_pt": round(body_top, 3) if body_top is not None else None,
        "abstract_body_bottom_pt": round(body_bottom, 3) if body_bottom is not None else None,
        "title_override": args.allow_title_override,
        "checks": checks,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
