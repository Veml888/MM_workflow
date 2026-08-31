#!/usr/bin/env python3
"""Detect layout drift / whitespace / isolation in a compiled CUMCM PDF.

Reads the actual PDF layout (text blocks + image rects) with PyMuPDF and flags:
  * LARGE VERTICAL BLANK GAP on a page  -> 排版不紧凑 / 为凑篇幅留下大空白;
  * ISOLATED FIGURE/TABLE PAGE          ->  图/表所在页几乎只有图+图题，没有正文解读
                                             (图表与相应文字不相邻).

Requires a compiled PDF. Output is ASCII-only (non-ASCII escaped). Run with
`PYTHONIOENCODING=utf-8` not required.
"""

from __future__ import annotations

import argparse
import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path


CAPTION_RE_TEXT = ("图 ", "表 ", "图　", "表　")
TOKEN_RE = None


def _ascii(value: object) -> str:
    # 保留可打印的中文/符号，仅对不可打印/控制字符转义（配合 UTF-8 输出保护，避免报错信息变成 \uXXXX）
    return "".join(ch if ch.isprintable() else ("\\u%04x" % ord(ch)) for ch in str(value))


def _content_intervals(page) -> list[tuple[float, float]]:
    """Return vertical intervals (y0,y1) of real content: text blocks + image rects."""
    intervals: list[tuple[float, float]] = []
    for block in page.get_text("blocks"):
        if not block or len(block) < 5:
            continue
        x0, y0, x1, y1 = block[:4]
        text = (block[4] or "").strip()
        if text:
            intervals.append((y0, y1))
    try:
        for info in page.get_image_info():
            if info.get("bbox"):
                x0, y0, x1, y1 = info["bbox"]
                pos = page.rect
                if (y1 - y0) > 0.04 * pos.height and (x1 - x0) > 0.04 * pos.width:
                    intervals.append((y0, y1))
    except Exception:
        pass
    if not intervals:
        return []
    intervals.sort()
    merged: list[tuple[float, float]] = [list(intervals[0])]
    for y0, y1 in intervals[1:]:
        if y0 <= merged[-1][1] + 2:
            merged[-1][1] = max(merged[-1][1], y1)
        else:
            merged.append([y0, y1])
    return [(a, b) for a, b in merged]


def _is_caption_text(text: str) -> bool:
    t = text.strip()
    for prefix in CAPTION_RE_TEXT:
        if t.startswith(prefix) and len(t) < 60:
            return True
    return False


def check(pdf_path: Path, gap_ratio: float, min_body_chars: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        import fitz  # type: ignore
    except ImportError:
        return [f"PyMuPDF (fitz) not installed", ], []
    if not pdf_path.exists():
        return [f"pdf not found: {pdf_path}"], []
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        return [f"cannot open pdf: {exc}"], []

    # token occurrences: "图 N" / "表 N" -> list of (page, y0, y1, textlen)
    token_occ: dict[str, list[tuple[int, float, float, int]]] = {}
    page_has_image: dict[int, bool] = {}
    for pno in range(doc.page_count):
        page = doc[pno]
        page_has_image[pno] = False
        try:
            if page.get_image_info():
                page_has_image[pno] = True
        except Exception:
            pass
        for block in page.get_text("blocks"):
            if not block or len(block) < 5:
                continue
            text = (block[4] or "").strip()
            for m in re.finditer(r"(图|表)\s*(\d+)", text):
                token = f"{m.group(1)}{m.group(2)}"
                bucket = token_occ.setdefault(token, [])
                # avoid counting the same block twice: dedup by (page, y0)
                if not any(abs(a - pno) < 1 and abs(b - block[1]) < 2 for (a, b, _, _) in bucket):
                    bucket.append((pno, block[1], block[3], len(text)))

        # whitespace + isolation checks (existing)
        height = page.rect.height
        intervals = _content_intervals(page)
        if not intervals:
            warnings.append(f"page {pno + 1}: no detectable text/image content")
            continue

        # largest vertical gap between consecutive content intervals
        largest_gap = 0.0
        for i in range(1, len(intervals)):
            gap = intervals[i][0] - intervals[i - 1][1]
            if gap > largest_gap:
                largest_gap = gap
        if largest_gap > height * gap_ratio:
            errors.append(
                f"page {pno + 1}: large vertical blank gap ({largest_gap:.1f}pt, "
                f"~{largest_gap / height * 100:.0f}% page height) — not compact / blank padding"
            )

        # isolated figure/table page (image dominates, almost no body text)
        image_area = 0.0
        try:
            for info in page.get_image_info():
                if info.get("bbox"):
                    x0, y0, x1, y1 = info["bbox"]
                    image_area += max(0.0, (x1 - x0) * (y1 - y0))
        except Exception:
            image_area = 0.0
        body_chars = 0
        for block in page.get_text("blocks"):
            if not block or len(block) < 5:
                continue
            text = (block[4] or "").strip()
            if text and not _is_caption_text(text):
                body_chars += len(text)
        page_area = page.rect.width * page.rect.height
        if image_area > 0.45 * page_area and body_chars < min_body_chars:
            errors.append(
                f"page {pno + 1}: isolate figure/table page (image ~{image_area / page_area * 100:.0f}%"
                f" of page, body text only {body_chars} chars) figure/table not adjacent to text"
            )

    # proximity: figure/table must be tightly close to its narrative (SPATIAL distance, not page count)
    page_height = (doc[0].rect.height if doc.page_count else 842.0)
    for token, occs in token_occ.items():
        # placement page = first page of this token that has an image
        place = next((o for o in occs if page_has_image.get(o[0])), None)
        if place is None:
            continue
        p_page = place[0]
        # vertical extent occupied by the figure on its placement page (image bbox union)
        fig_y0, fig_y1 = None, None
        try:
            for info in doc[p_page].get_image_info():
                if info.get("bbox"):
                    x0, y0, x1, y1 = info["bbox"]
                    if fig_y0 is None or y0 < fig_y0:
                        fig_y0 = y0
                    if fig_y1 is None or y1 > fig_y1:
                        fig_y1 = y1
        except Exception:
            pass
        if fig_y0 is None:
            fig_y0, fig_y1 = place[1], place[2]

        best_eff = None
        best_ref = None
        for pno, y0, y1, tlen in occs:
            if pno == p_page and tlen < 60:
                continue  # caption line, not a narrative reference
            if pno == p_page:
                if fig_y0 <= y1 and y0 <= fig_y1:
                    eff = 0.0  # narrative overlaps / immediately beside the figure
                elif y1 < fig_y0:
                    eff = max(0.0, fig_y0 - y1)
                else:
                    eff = max(0.0, y0 - fig_y1)
            elif abs(pno - p_page) == 1:
                eff = 0.18 * page_height  # immediately adjacent page -> considered close
            else:
                eff = abs(pno - p_page) * page_height
            if best_eff is None or eff < best_eff:
                best_eff = eff
                best_ref = (pno, y0)
        if best_ref is not None and best_eff > 0.75 * page_height:
            errors.append(
                f"{token}: figure/table not adjacent to its narrative — placement page {p_page + 1}, "
                f"closest narrative ~{best_eff / page_height:.2f} page-height away (page {best_ref[0] + 1})"
            )
    doc.close()
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="detect layout drift / blank / isolation")
    parser.add_argument("pdf", nargs="?", default="paper/论文.pdf")
    parser.add_argument("--gap-ratio", type=float, default=0.22, help="max allowed blank gap fraction of page height")
    parser.add_argument("--min-body-chars", type=int, default=200, help="min body text chars on a figure page")
    args = parser.parse_args()

    errors, warnings = check(Path(args.pdf), args.gap_ratio, args.min_body_chars)
    for warning in warnings:
        print("WARN: " + _ascii(warning))
    if errors:
        print("layout check: FAIL")
        for error in errors:
            print("- " + _ascii(error))
        return 1
    print("layout check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
