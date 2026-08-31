#!/usr/bin/env python3
"""审查论文流程图 SVG 的物理字号、语义标记、节点与正交连线。"""
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
from dataclasses import dataclass
from pathlib import Path


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def number(value: str | None, default: float | None = None) -> float | None:
    if value is None:
        return default
    match = re.match(r"\s*(-?[0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else default


def parse_hex(color: str | None) -> tuple[int, int, int] | None:
    if not color:
        return None
    value = color.strip().lower()
    value = {"black": "#000000", "white": "#ffffff"}.get(value, value)
    if value in {"none", "transparent"}:
        return None
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", value):
        return None
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


def computed_attr(el: ET.Element, name: str, parents: dict[ET.Element, ET.Element]) -> str | None:
    """Resolve a presentation attribute through inline style and ancestor inheritance."""
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


def luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for channel in rgb:
        c = channel / 255.0
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(rgb: tuple[int, int, int]) -> float:
    lum = luminance(rgb)
    return (1.0 + 0.05) / (lum + 0.05)


@dataclass(frozen=True)
class Box:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def overlaps(self, other: "Box", epsilon: float = 0.5) -> bool:
        return not (
            self.right <= other.left + epsilon
            or other.right <= self.left + epsilon
            or self.bottom <= other.top + epsilon
            or other.bottom <= self.top + epsilon
        )


def element_box(el: ET.Element) -> Box | None:
    tag = local(el.tag)
    if tag == "rect":
        x, y = number(el.get("x"), 0.0), number(el.get("y"), 0.0)
        width, height = number(el.get("width")), number(el.get("height"))
        if None not in (x, y, width, height):
            return Box(x, y, x + width, y + height)
    if tag == "circle":
        cx, cy, radius = number(el.get("cx")), number(el.get("cy")), number(el.get("r"))
        if None not in (cx, cy, radius):
            return Box(cx - radius, cy - radius, cx + radius, cy + radius)
    if tag == "ellipse":
        cx, cy = number(el.get("cx")), number(el.get("cy"))
        rx, ry = number(el.get("rx")), number(el.get("ry"))
        if None not in (cx, cy, rx, ry):
            return Box(cx - rx, cy - ry, cx + rx, cy + ry)
    if tag in {"polygon", "polyline"}:
        values = [float(v) for v in re.findall(r"-?[0-9]+(?:\.[0-9]+)?", el.get("points", ""))]
        if len(values) >= 4:
            xs, ys = values[0::2], values[1::2]
            return Box(min(xs), min(ys), max(xs), max(ys))
    return None


def path_points(el: ET.Element) -> list[tuple[float, float]] | None:
    tag = local(el.tag)
    if tag == "line":
        values = [number(el.get(key)) for key in ("x1", "y1", "x2", "y2")]
        return [(values[0], values[1]), (values[2], values[3])] if None not in values else None
    if tag == "polyline":
        values = [float(v) for v in re.findall(r"-?[0-9]+(?:\.[0-9]+)?", el.get("points", ""))]
        return list(zip(values[0::2], values[1::2])) if len(values) >= 4 else None
    if tag != "path":
        return None
    tokens = re.findall(r"[MLHVZmlhvz]|-?[0-9]+(?:\.[0-9]+)?", el.get("d", ""))
    if not tokens or any(token in "mlhvz" for token in tokens if token.isalpha()):
        return None
    points: list[tuple[float, float]] = []
    x = y = 0.0
    index = 0
    command = ""
    try:
        while index < len(tokens):
            if tokens[index].isalpha():
                command = tokens[index]
                index += 1
                if command == "Z":
                    break
            if command in {"M", "L"}:
                x, y = float(tokens[index]), float(tokens[index + 1])
                index += 2
            elif command == "H":
                x = float(tokens[index])
                index += 1
            elif command == "V":
                y = float(tokens[index])
                index += 1
            else:
                return None
            points.append((x, y))
    except (ValueError, IndexError):
        return None
    return points if len(points) >= 2 else None


def segments(points):
    return list(zip(points, points[1:]))


def boundary_distance(point: tuple[float, float], box: Box) -> float:
    x, y = point
    if box.left <= x <= box.right and box.top <= y <= box.bottom:
        return min(abs(x - box.left), abs(x - box.right), abs(y - box.top), abs(y - box.bottom))
    dx = max(box.left - x, 0.0, x - box.right)
    dy = max(box.top - y, 0.0, y - box.bottom)
    return math.hypot(dx, dy)


def segment_hits_box(segment, box: Box) -> bool:
    (x1, y1), (x2, y2) = segment
    if math.isclose(y1, y2):
        lo, hi = sorted((x1, x2))
        return box.top < y1 < box.bottom and max(lo, box.left) < min(hi, box.right)
    if math.isclose(x1, x2):
        lo, hi = sorted((y1, y2))
        return box.left < x1 < box.right and max(lo, box.top) < min(hi, box.bottom)
    return False


def orthogonal_cross(first, second) -> bool:
    (a1, a2), (b1, b2) = first, second
    ah, av = math.isclose(a1[1], a2[1]), math.isclose(a1[0], a2[0])
    bh, bv = math.isclose(b1[1], b2[1]), math.isclose(b1[0], b2[0])
    if not ((ah or av) and (bh or bv)) or ah == bh:
        return False
    h1, h2 = (a1, a2) if ah else (b1, b2)
    v1, v2 = (b1, b2) if ah else (a1, a2)
    hx1, hx2 = sorted((h1[0], h2[0]))
    vy1, vy2 = sorted((v1[1], v2[1]))
    x, y = v1[0], h1[1]
    return hx1 < x < hx2 and vy1 < y < vy2 and not {a1, a2}.intersection({b1, b2})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg")
    parser.add_argument("--width-cm", type=float, default=14.5)
    parser.add_argument("--min-font-pt", type=float, default=8.0)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        root = ET.parse(Path(args.svg)).getroot()
    except Exception as exc:
        print(f"[FAIL] SVG XML 解析失败: {exc}")
        return 1

    viewbox = root.get("viewBox", "").split()
    if len(viewbox) != 4:
        print("[FAIL] 根元素必须提供四项 viewBox")
        return 1
    vx, vy, width, height = map(float, viewbox)
    if width <= 0 or height <= 0:
        print("[FAIL] viewBox 宽高必须为正数")
        return 1
    canvas = Box(vx, vy, vx + width, vy + height)
    parents = {child: parent for parent in root.iter() for child in parent}

    effects = sorted({local(el.tag) for el in root.iter() if local(el.tag) in {"filter", "linearGradient", "radialGradient"}})
    if effects:
        errors.append("论文版禁止 PPT 式效果: " + ", ".join(effects))
    if any(local(el.tag) == "image" for el in root.iter()):
        warnings.append("发现嵌入位图；确认不是照片背景或装饰插画")

    nodes: dict[str, Box] = {}
    node_elements = [el for el in root.iter() if el.get("data-node") == "true"]
    for index, el in enumerate(node_elements, 1):
        ident = el.get("id")
        box = element_box(el)
        if not ident:
            errors.append(f"第 {index} 个 data-node 缺少唯一 id")
        elif ident in nodes:
            errors.append(f"重复节点 id: {ident}")
        elif box is None:
            warnings.append(f"节点 {ident} 的形状无法计算边界")
        else:
            nodes[ident] = box
    if not node_elements:
        warnings.append("未发现 data-node 语义标记")

    node_items = list(nodes.items())
    for index, (first_id, first_box) in enumerate(node_items):
        for second_id, second_box in node_items[index + 1 :]:
            if first_box.overlaps(second_box):
                errors.append(f"节点重叠: {first_id} 与 {second_id}")

    edge_records = []
    edge_elements = [el for el in root.iter() if el.get("data-edge") == "true"]
    for index, el in enumerate(edge_elements, 1):
        ident = el.get("id", f"edge-{index}")
        source, target = el.get("data-source"), el.get("data-target")
        if source not in nodes or target not in nodes:
            errors.append(f"边 {ident} 的 source/target 不存在: {source!r} -> {target!r}")
        if not computed_attr(el, "marker-end", parents):
            errors.append(f"边 {ident} 缺少 marker-end")
        points = path_points(el)
        if points is None:
            warnings.append(f"边 {ident} 不是可审查的直线或正交 M/L/H/V 路径")
            continue
        turns = max(0, len(points) - 2)
        if turns > 2:
            warnings.append(f"边 {ident} 有 {turns} 个转折，超过建议上限 2")
        if source in nodes and boundary_distance(points[0], nodes[source]) > 12:
            warnings.append(f"边 {ident} 起点未贴近源节点 {source}")
        if target in nodes and boundary_distance(points[-1], nodes[target]) > 16:
            warnings.append(f"边 {ident} 终点未贴近目标节点 {target}")
        for node_id, box in nodes.items():
            if node_id not in {source, target} and any(segment_hits_box(seg, box) for seg in segments(points)):
                errors.append(f"边 {ident} 穿过非端点节点 {node_id}")
        edge_records.append((ident, source, target, points))
    if nodes and not edge_elements:
        warnings.append("有节点但没有 data-edge 语义标记")

    crossings = 0
    for index, (first_id, first_source, first_target, first_points) in enumerate(edge_records):
        for second_id, second_source, second_target, second_points in edge_records[index + 1 :]:
            if {first_source, first_target}.intersection({second_source, second_target}):
                continue
            if any(orthogonal_cross(a, b) for a in segments(first_points) for b in segments(second_points)):
                crossings += 1
                warnings.append(f"检测到边交叉: {first_id} × {second_id}")
    if crossings > 2:
        errors.append(f"交叉边共 {crossings} 处，应拆图或重排")

    font_chain = " ".join(computed_attr(el, "font-family", parents) or "" for el in root.iter())
    if not any(name in font_chain for name in ("Microsoft YaHei", "SimHei", "Noto Sans CJK", "Source Han Sans")):
        warnings.append("未声明推荐中文字体族")

    scale_to_pt = args.width_cm / width * 72.0 / 2.54
    for el in root.iter():
        if local(el.tag) != "text":
            continue
        content = "".join(el.itertext()).strip()
        size = number(computed_attr(el, "font-size", parents))
        if size is None:
            warnings.append(f"文字缺少显式字号: {content[:16]!r}")
        elif size * scale_to_pt < args.min_font_pt:
            errors.append(f"最终字号 {size * scale_to_pt:.2f} pt 小于 {args.min_font_pt:g} pt: {content[:16]!r}")
        rgb = parse_hex(computed_attr(el, "fill", parents))
        if rgb and contrast(rgb) < 4.5:
            warnings.append(f"文字对白底对比度 {contrast(rgb):.2f} 偏低: {content[:16]!r}")

    if nodes:
        content_box = Box(
            min(box.left for box in nodes.values()),
            min(box.top for box in nodes.values()),
            max(box.right for box in nodes.values()),
            max(box.bottom for box in nodes.values()),
        )
        margins = {
            "左": (content_box.left - canvas.left) / width,
            "右": (canvas.right - content_box.right) / width,
            "上": (content_box.top - canvas.top) / height,
            "下": (canvas.bottom - content_box.bottom) / height,
        }
        for side, ratio in margins.items():
            if ratio > 0.25:
                warnings.append(f"{side}侧外部留白占画布 {ratio:.0%}，检查是否为无效留白")

    semantic_colors = set()
    for el in node_elements:
        rgb = parse_hex(computed_attr(el, "fill", parents))
        if rgb and max(rgb) - min(rgb) > 12 and rgb != (255, 255, 255):
            semantic_colors.add(rgb)
    if len(semantic_colors) > 3:
        warnings.append(f"节点使用 {len(semantic_colors)} 个彩色填充，超过建议的 3 个语义色")

    for item in warnings:
        print(f"[WARN] {item}")
    for item in errors:
        print(f"[FAIL] {item}")
    print(
        f"[SUMMARY] nodes={len(nodes)} edges={len(edge_records)} crossings={crossings} "
        f"target_width={args.width_cm:g}cm min_font={args.min_font_pt:g}pt"
    )
    if errors or (args.strict and warnings):
        return 1
    print("[OK] 自动结构审查通过；仍须回读最终 PNG 完成人工视觉验收")
    return 0


if __name__ == "__main__":
    sys.exit(main())
