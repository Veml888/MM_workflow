#!/usr/bin/env python3
"""校验 SVG，并按目标物理宽度渲染带 600 dpi 元数据的 PNG。"""
from __future__ import annotations

import argparse
import math
import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
import xml.etree.ElementTree as ET
from pathlib import Path


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.match(r"\s*([0-9.]+)", value)
    return float(match.group(1)) if match else None


def computed_attr(el: ET.Element, name: str, parents: dict[ET.Element, ET.Element]) -> str | None:
    current: ET.Element | None = el
    while current is not None:
        style = current.get("style", "")
        for declaration in style.split(";"):
            if ":" not in declaration:
                continue
            key, value = declaration.split(":", 1)
            if key.strip() == name:
                return value.strip()
        value = current.get(name)
        if value is not None:
            return value
        current = parents.get(current)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg")
    parser.add_argument("--png")
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--width-cm", type=float, default=14.5)
    parser.add_argument("--min-font", type=float, help="兼容旧用法：SVG 源坐标中的最小字号")
    parser.add_argument("--min-font-pt", type=float, default=8.0, help="最终论文物理尺寸下的最小字号")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    svg_path = Path(args.svg)
    png_path = Path(args.png) if args.png else svg_path.with_name(svg_path.stem + "_600dpi.png")
    errors: list[str] = []
    warnings: list[str] = []

    try:
        root = ET.parse(svg_path).getroot()
    except Exception as exc:
        print(f"[FAIL] SVG XML 解析失败: {exc}")
        return 1

    parents = {child: parent for parent in root.iter() for child in parent}
    viewbox = root.get("viewBox", "").split()
    source_width = float(viewbox[2]) if len(viewbox) == 4 else number(root.get("width")) or 1600.0
    scale_to_pt = args.width_cm / source_width * 72.0 / 2.54
    ids = {el.get("id") for el in root.iter() if el.get("id")}
    text_nodes = [el for el in root.iter() if local(el.tag) in {"text", "tspan"}]
    if not text_nodes:
        warnings.append("没有发现文字节点")

    contains_cjk = False
    font_chain = " ".join(computed_attr(el, "font-family", parents) or "" for el in root.iter())
    for el in text_nodes:
        content = "".join(el.itertext())
        contains_cjk |= bool(re.search(r"[\u3400-\u9fff]", content))
        size = number(computed_attr(el, "font-size", parents))
        if size is None:
            warnings.append(f"文字缺少可计算字号: {content[:12]!r}")
        elif args.min_font is not None and size < args.min_font:
            warnings.append(f"源字号 {size:g} 小于 {args.min_font:g}: {content[:12]!r}")
        elif size * scale_to_pt < args.min_font_pt:
            warnings.append(
                f"最终字号 {size * scale_to_pt:.2f} pt 小于 {args.min_font_pt:g} pt: {content[:12]!r}"
            )

    if contains_cjk and not any(name in font_chain for name in ("Microsoft YaHei", "SimHei", "Noto Sans CJK", "Source Han Sans")):
        warnings.append("包含中文，但未声明推荐中文字体族")

    for el in root.iter():
        for attr in ("marker-end", "marker-start", "marker-mid"):
            ref = el.get(attr)
            if not ref:
                continue
            match = re.fullmatch(r"url\(#([^)]+)\)", ref)
            if not match or match.group(1) not in ids:
                errors.append(f"无效 marker 引用: {ref}")

    if args.dpi < 300:
        errors.append("论文 PNG 的 dpi 不得低于 300")
    target_px = max(1, round(args.width_cm / 2.54 * args.dpi))
    scale = target_px / source_width

    try:
        import fitz
        from PIL import Image

        doc = fitz.open(svg_path)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        pix.save(png_path)
        with Image.open(png_path) as image:
            image.save(png_path, dpi=(args.dpi, args.dpi), optimize=True)
            rendered_size = image.size
        actual_width_cm = rendered_size[0] / args.dpi * 2.54
        if not math.isclose(actual_width_cm, args.width_cm, abs_tol=0.05):
            warnings.append(f"物理宽度偏差: {actual_width_cm:.2f} cm")
    except Exception as exc:
        errors.append(f"渲染失败: {exc}")
        rendered_size = (0, 0)

    for item in warnings:
        print(f"[WARN] {item}")
    for item in errors:
        print(f"[FAIL] {item}")
    if errors or (args.strict and warnings):
        return 1
    print(f"[OK] {png_path} | {rendered_size[0]}×{rendered_size[1]} px | {args.dpi} dpi | {args.width_cm:.2f} cm")
    print("visual_review: pending（必须回读 PNG 后确认）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
