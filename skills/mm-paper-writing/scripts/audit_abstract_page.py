#!/usr/bin/env python3
"""Audit CUMCM abstract typography and first-page vertical occupancy."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
TITLE_RE = re.compile(
    r"\{\s*\\zihao\{3\}\s*\\bfseries\s*"
    r"(?!摘(?:\\quad|\s)*要)[^{}\n]+\\par\s*\}"
)
ABSTRACT_HEADING_RE = re.compile(
    r"\\zihao\{3\}\s*\\bfseries\s*摘(?:\\quad|\s)*要"
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
    parser.add_argument("--min-han", type=int, default=550)
    parser.add_argument("--max-han", type=int, default=1100)
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
    han_count = len(HAN_RE.findall(text))

    checks = {
        "title_size_three": args.allow_title_override or bool(TITLE_RE.search(tex)),
        "abstract_heading_size_three": args.allow_title_override
        or bool(ABSTRACT_HEADING_RE.search(tex)),
        "han_count_in_range": args.min_han <= han_count <= args.max_han,
        "fill_ratio_in_range": args.min_fill <= fill_ratio <= args.max_fill,
        "keywords_on_first_page": "关键词" in text,
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
