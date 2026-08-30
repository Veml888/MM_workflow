#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据图文字重叠检查（论文级图交付前的强制校验）。

用法：
  python check_figure_overlap.py fig1.pdf fig2.pdf ...
  python check_figure_overlap.py --dir figures/ --suffix .pdf

判定：任意两个文字 span 的包围盒满足
  水平重叠 > 2pt 且 垂直重叠 > 2pt 且 重叠面积 > 较小包围盒面积的 15%
即判定为文字重叠；存在任一重叠则退出码为 1。

输出：逐文件列出重叠对（文本前 22 字符 + 坐标），最后给出总数。
"""
from __future__ import annotations

import argparse
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path

import fitz


def collect_spans(page):
    """返回 [(text, bbox), ...]，bbox 为 [x0, y0, x1, y1]。"""
    spans = []
    d = page.get_text("dict")
    for block in d["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                text = s["text"].strip()
                if text:
                    spans.append((text, s["bbox"]))
    return spans


def find_overlaps(spans, ox_min=2.0, oy_min=2.0, ratio=0.15):
    """返回重叠对列表。"""
    overlaps = []
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            t1, a = spans[i]
            t2, b = spans[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox <= ox_min or oy <= oy_min:
                continue
            area_a = (a[2] - a[0]) * (a[3] - a[1])
            area_b = (b[2] - b[0]) * (b[3] - b[1])
            if ox * oy > ratio * min(area_a, area_b):
                overlaps.append((t1[:22], [round(v, 1) for v in a], t2[:22], [round(v, 1) for v in b]))
    return overlaps


def check_pdf(path: Path):
    doc = fitz.open(path)
    all_overlaps = []
    for page in doc:
        all_overlaps.extend(find_overlaps(collect_spans(page)))
    doc.close()
    return all_overlaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", help="一个或多个 PDF 文件")
    parser.add_argument("--dir", help="扫描目录下的所有 PDF")
    parser.add_argument("--suffix", default=".pdf", help="配合 --dir 使用的后缀")
    args = parser.parse_args()

    files = [Path(p) for p in args.pdfs]
    if args.dir:
        d = Path(args.dir)
        files += sorted(d.glob(f"*{args.suffix}"))
    files = [f for f in files if f.exists()]
    if not files:
        print("[FAIL] 未找到任何 PDF 文件")
        return 1

    total = 0
    failed = False
    for f in files:
        overlaps = check_pdf(f)
        total += len(overlaps)
        if overlaps:
            failed = True
            print(f"[OVERLAP] {f.name} ({len(overlaps)} 处)")
            for t1, a, t2, b in overlaps[:20]:
                print(f"    {t1!r} {a} <-> {t2!r} {b}")
        else:
            print(f"[OK] {f.name}")

    print(f"总计：{len(files)} 个文件，文字重叠 {total} 处")
    if failed:
        print("[FAIL] 存在文字重叠，禁止进入 docs/04 与论文；必须返工后重扫")
        return 1
    print("[PASS] 全部数据图文字重叠为 0，可进入 docs/04 与论文")
    return 0


if __name__ == "__main__":
    sys.exit(main())
