#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据图文字重叠检查（论文级图交付前的强制校验，含文字-图形候选检测）。

用法：
  python check_figure_overlap.py fig1.pdf fig2.pdf ...
  python check_figure_overlap.py --dir figures/ --suffix .pdf
  python check_figure_overlap.py --dir figures/ --strict-data   # 文字-数据主体冲突也计 FAIL

分层判定：
  (1) 文字-文字重叠（硬性，FAIL 门槛不变）：
      任意两个文字 span 的包围盒满足
      水平重叠 > 2pt 且 垂直重叠 > 2pt 且 重叠面积 > 较小包围盒面积的 15%
      即判定为文字重叠；存在任一重叠则退出码为 1。
  (2) 文字-数据主体候选（新增，默认 COLUMN/候选，不 FAIL）：
      文字 span 与"数据主体"图元（曲线/柱/散点/误差带/热力色块等非空白图形）
      的细分几何深重叠时，输出该文字可能压住图形的候选提醒，提示"请人工回读确认"。
      数据主体定义：非白底、非网格线(低饱和浅灰)、非坐标轴/刻度细线(纯黑且细)的
      填充或描边图元；纯黑但非细线的【保留】为候选（可能是黑色数据，交人工判断）。
      用 --strict-data 可把这部分也计为 FAIL。
"""
from __future__ import annotations

import argparse
import colorsys
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path

import fitz

# 判定阈值（与文字-文字重叠一致）
OX_MIN = 2.0
OY_MIN = 2.0
RATIO = 0.15

# 非数据元素颜色阈值
WHITE_T = 0.95        # 白底/接近白
GRID_SAT = 0.13       # 网格线/浅灰背景 饱和度上限
GRID_VAL = 0.85       # 网格线/浅灰背景 亮度下限
AXIS_NUM = 0.10       # 纯黑(坐标轴/刻度) RGB 分量总和阈值


def _rgb_key(col):
    return tuple(round(x, 2) for x in col)


def _is_white(col) -> bool:
    return all(x > WHITE_T for x in col)


def _is_grid(col) -> bool:
    """网格线 / 浅灰背景：低饱和、浅色。"""
    h, s, v = colorsys.rgb_to_hsv(*col)
    return s < GRID_SAT and v > GRID_VAL


def _is_pure_black(col) -> bool:
    return sum(col) < AXIS_NUM * 3


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


def _item_point_pairs(item):
    """把 drawing 的一个图元拆成可判交的 (type, 点集) 列表。

    item = (kind, ...)，kind ∈ {'l'线段, 'c'贝塞尔, 're'矩形}。
    贝塞尔用其 4 个控制点近似；矩形用角点。返回结构化元组，便于求交。
    """
    kind = item[0]
    pts = []
    if kind == "l":
        pts = [item[1], item[2]]
    elif kind == "c":
        pts = list(item[1:5])
    elif kind == "re":
        r = item[1]
        pts = [r.tl, r.tr, r.br, r.bl]
    else:
        # 兜底：3D 曲面/散点的 item 是 Quad 等，未必带 Point 坐标。
        # 尝试提取 rect 角点；失败则跳过该图元（不崩溃，文字-文字检测不受影响）。
        try:
            r = getattr(item[1], "rect", None) or (item[1].x0, item[1].y0, item[1].x1, item[1].y1)
            if r is not None and len(r) == 4:
                pts = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
        except Exception:
            pts = []
    out = []
    for p in pts:
        try:
            out.append((p.x, p.y))
        except AttributeError:
            try:
                out.append((float(p[0]), float(p[1])))
            except (TypeError, IndexError, ValueError):
                pass
    return out


def _pt_in_bbox(p, bbox, pad=0.0):
    x0, y0, x1, y1 = bbox
    return (x0 - pad) <= p[0] <= (x1 + pad) and (y0 - pad) <= p[1] <= (y1 + pad)


def _seg_bbox_hit(bbox, pts):
    """判断点序列与 文字 bbox 是否深重叠：
    任一点落在 bbox 内（加了 1pt 容差），或 bbox 中心落在点范围的包围盒内，
    都视为"文字可能压到该图元"。返回 True/False。"""
    if not pts:
        return False
    # 点落在 bbox 内
    for p in pts:
        if _pt_in_bbox(p, bbox, pad=1.0):
            return True
    # bbox 中心落在顶点范围盒内（覆盖跨越 bbox 的长线）
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx = (bbox[0] + bbox[2]) / 2.0
    cy = (bbox[1] + bbox[3]) / 2.0
    if min(xs) <= cx <= max(xs) and min(ys) <= cy <= max(ys):
        return True
    return False


def is_data_mark(d):
    """判断 drawing 是否为"数据主体"图元（曲线/柱/散点/误差带/热力色块等）。

    非数据元素（返回 False）：
      - 白底 / 接近白；
      - 网格线 / 浅灰背景（低饱和浅灰）；
      - 坐标轴 / 刻度线（纯黑且极细：min(w,h)<2）。
    其余（含纯黑但非细的、各种高饱和填充/描边）都视为数据主体候选，交人工判断。
    """
    fill = d.get("fill")
    color = d.get("color")
    typ = d.get("type")
    if fill is not None and _is_white(fill):
        return False
    # 网格线/浅灰：看 fill 和 color 是否都浅灰
    for col in (fill, color):
        if col is not None and _is_grid(col):
            return False
    # 纯黑且细线（刻度/坐标轴）：排除；纯黑但不细的保留（可能为数据）
    r = d.get("rect")
    w = r[2] - r[0]; h = r[3] - r[1]
    for col in (fill, color):
        if col is not None and _is_pure_black(col) and min(w, h) < 2.0:
            return False
    # 其余：无任何非白填充，也无 color 的纯 type=f 白→已排除；纯 s 有 color 的数据曲线保留
    return True


def collect_drawings(page):
    """返回 [drawing, ...] 中所有"数据主体"drawing（带 items 点集展开）。"""
    out = []
    for d in page.get_drawings():
        if not is_data_mark(d):
            continue
        segs = []
        for item in d.get("items", []):
            segs.append(_item_point_pairs(item))
        out.append({"rect": d.get("rect"), "color": d.get("fill") or d.get("color"),
                    "type": d.get("type"), "segs": segs})
    return out


def text_to_data_hits(spans, drawings, ox_min=OX_MIN, oy_min=OY_MIN):
    """返回 [(text, bbox, color, n_seg_hits), ...]：文字可能压到数据主体图元。"""
    cands = []
    for text, bbox in spans:
        for dw in drawings:
            hit_segs = 0
            for seg in dw["segs"]:
                if _seg_bbox_hit(bbox, seg):
                    hit_segs += 1
            if hit_segs > 0:
                cands.append((text[:22], [round(v, 1) for v in bbox],
                              _rgb_key(dw["color"]) if dw["color"] else None,
                              dw["type"], hit_segs))
                break  # 一个文字给一个候选即可
    return cands


def find_overlaps(spans, ox_min=OX_MIN, oy_min=OY_MIN, ratio=RATIO):
    """返回文字-文字重叠对列表。"""
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


def check_pdf(path: Path, strict_data: bool = False):
    doc = fitz.open(path)
    all_overlaps = []
    all_cands = []
    for page in doc:
        spans = collect_spans(page)
        all_overlaps.extend(find_overlaps(spans))
        drawings = collect_drawings(page)
        all_cands.extend(text_to_data_hits(spans, drawings))
    doc.close()
    fail = bool(all_overlaps) or (strict_data and bool(all_cands))
    return {"overlaps": all_overlaps, "cands": all_cands, "fail": fail}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", help="一个或多个 PDF 文件")
    parser.add_argument("--dir", help="扫描目录下的所有 PDF")
    parser.add_argument("--suffix", default=".pdf", help="配合 --dir 使用的后缀")
    parser.add_argument("--strict-data", action="store_true",
                        help="把文字-数据主体候选也计为 FAIL（默认仅提示，交人工回读）")
    args = parser.parse_args()

    files = [Path(p) for p in args.pdfs]
    if args.dir:
        d = Path(args.dir)
        files += sorted(d.glob(f"*{args.suffix}"))
    files = [f for f in files if f.exists()]
    if not files:
        print("[FAIL] 未找到任何 PDF 文件")
        return 1

    total_overlap = 0
    total_cand = 0
    failed = False
    for f in files:
        res = check_pdf(f, strict_data=args.strict_data)
        overlaps, cands, fail = res["overlaps"], res["cands"], res["fail"]
        total_overlap += len(overlaps)
        total_cand += len(cands)
        if fail:
            failed = True
        print(f"--- {f.name}: 文字重叠 {len(overlaps)} 处, 文字-数据候选 {len(cands)} 处 ---")
        for t1, a, t2, b in overlaps[:20]:
            print(f"    [OVERLAP] {t1!r} {a} <-> {t2!r} {b}")
        for text, bbox, col, typ, nhit in cands[:20]:
            colstr = f"RGB{col}" if col else "无填充色"
            print(f"    [DATA-CAND] {text!r} {bbox} 可能压到颜色{colstr} "
                  f"(type={typ}) 图元 {nhit} 次; 请人工回读确认是否真遮挡")

    print(f"\n总计：{len(files)} 个文件，文字重叠 {total_overlap} 处，文字-数据候选 {total_cand} 处")
    if failed:
        if total_overlap and strict_data:
            print("[FAIL] 存在文字重叠；且 --strict-data 开启，部分文字疑似压到数据图形，必须返工后重扫+回读")
        else:
            print("[FAIL] 存在文字重叠，禁止进入 docs/04 与论文；必须返工后重扫")
        return 1
    if total_cand > 0:
        print("[PASS] 文字-文字重叠为 0（硬性通过）；但存在文字-数据图元重叠候选，请人工回读确认是否真遮挡")
        return 0
    print("[PASS] 全部数据图文字重叠为 0，无可疑文字-图形候选，可进入 docs/04 与论文")
    return 0


if __name__ == "__main__":
    sys.exit(main())
