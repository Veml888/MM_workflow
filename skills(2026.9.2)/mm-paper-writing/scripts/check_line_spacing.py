#!/usr/bin/env python3
"""check_line_spacing.py — 实测论文正文行距（硬门禁，exit 0 才算 PASS）。

规范：正文（摘要页之后、附录之前）行距必须为 linespread 1.2 的排版效果，
即 12pt 字号下相邻两行基线距约 17pt；实测中位数须落在 [15.5, 18.5] pt 内。
附录保持单倍行距，不参与本检查。

用法：python check_line_spacing.py <论文.pdf> [--min-pt 15.5] [--max-pt 18.5] [--output out.json]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ABSTRACT_RE = re.compile(r"^摘\s*要$")
APPENDIX_RE = re.compile(r"^附\s*录$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="measure CUMCM body line spacing")
    parser.add_argument("pdf", nargs="?", default="paper/论文.pdf", type=Path)
    parser.add_argument("--min-pt", type=float, default=15.5)
    parser.add_argument("--max-pt", type=float, default=18.5)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def normalized_lines(text: str) -> list[str]:
    return [re.sub(r"[ \t\u3000]+", "", ln.strip()) for ln in text.splitlines() if ln.strip()]


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        import fitz  # type: ignore
    except ImportError:
        print("PyMuPDF (fitz) is not installed")
        return 2
    if not args.pdf.exists():
        print(f"pdf not found: {args.pdf}")
        return 2

    document = fitz.open(str(args.pdf))
    # 定位附录页：附录总标题单独成行（去空白后恰为"附录"）；兼容被拆为"附"/"录"两行的情况。
    # 正文范围 = 第 2 页起（摘要独占第一页是固定版式）至附录前一页。
    appendix_index = None
    for index in range(document.page_count):
        lines = normalized_lines(document[index].get_text())
        hit = any(ln == "附录" for ln in lines)
        if not hit:
            for k in range(len(lines) - 1):
                if lines[k] == "附" and lines[k + 1] == "录":
                    hit = True
                    break
        if index > 0 and hit:
            appendix_index = index
            break
    body_first = 1
    body_last = (appendix_index if appendix_index is not None else document.page_count) - 1

    pitches: list[float] = []
    for pno in range(body_first, body_last + 1):
        for blk in document[pno].get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            lines = blk["lines"]
            for i in range(1, len(lines)):
                dy = lines[i]["bbox"][3] - lines[i - 1]["bbox"][3]
                if 8.0 < dy < 40.0:
                    pitches.append(dy)
    document.close()

    if len(pitches) < 30:
        errors.append(f"too few line samples collected ({len(pitches)}); cannot judge")
    else:
        median = statistics.median(pitches)
        if not (args.min_pt <= median <= args.max_pt):
            errors.append(
                f"median line pitch {median:.1f}pt outside [{args.min_pt}, {args.max_pt}]pt "
                f"(12pt 正文应约 17pt，即 \\linespread{{1.2}}；禁止单倍行距)"
            )

    result = {
        "status": "pass" if not errors else "fail",
        "pdf": str(args.pdf),
        "body_page_range": [body_first + 1, body_last + 1],
        "samples": len(pitches),
        "median_line_pitch_pt": round(statistics.median(pitches), 2) if pitches else None,
        "allowed_range_pt": [args.min_pt, args.max_pt],
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
