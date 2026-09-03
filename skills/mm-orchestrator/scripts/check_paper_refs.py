#!/usr/bin/env python3
"""Machine-check the paper's figure/table integrity from actual .tex + figures/.

Checks that are objective (no self-report):
  * every \\includegraphics resolves to an existing file;
  * figure/table caption numbering is a continuous 1..N sequence (no gap/dup);
  * no Q1/Q2/q1/q2 or 问题一 prefix in figure filenames or captions;
  * a figure declared in docs/04 or docs/05 reports is actually included in the tex
    (catches "created but unused / stacked" figures).
Output is ASCII-only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path


def _ascii(value: object) -> str:
    # 保留可打印的中文/符号，仅对不可打印/控制字符转义（配合 UTF-8 输出保护，避免报错信息变成 \uXXXX）
    return "".join(ch if ch.isprintable() else ("\\u%04x" % ord(ch)) for ch in str(value))


FIG_EXT = {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
Q_PREFIX = re.compile(r"(^|[\\/])[qQ]\d+|问题[一二三四五]", re.UNICODE)
INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption\{(.*?)\}")


def resolve(root: Path, tex_dir: Path, name: str) -> Path | None:
    name = name.strip()
    if not name:
        return None
    if name.startswith("figures/"):
        name = name[len("figures/"):]
    if not Path(name).suffix:
        for ext in FIG_EXT:
            cand = tex_dir / (name + ext)
            if cand.exists():
                return cand
            cand = root / "figures" / (name + ext)
            if cand.exists():
                return cand
        return None
    for base in (tex_dir, root / "figures"):
        cand = base / name
        if cand.exists():
            return cand
    return None


def report_figures(p: Path) -> set[str]:
    if not p.exists():
        return set()
    text = p.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"figures/([A-Za-z0-9_\-\u4e00-\u9fa5\.]+)", text))


def check(root: Path, tex_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not tex_path.exists():
        return [f"paper tex not found: {tex_path}"], []
    text = tex_path.read_text(encoding="utf-8", errors="ignore")
    tex_dir = tex_path.parent

    refs = INCLUDE_RE.findall(text)
    resolved: set[str] = set()
    for name in refs:
        path = resolve(root, tex_dir, name)
        if path is None:
            errors.append(f"includegraphics file missing: {name}")
        else:
            resolved.add(path.name)
        if Q_PREFIX.search(name):
            errors.append(f"figure filename has question-number prefix: {name}")
    captions = CAPTION_RE.findall(text)
    for caption in captions:
        if Q_PREFIX.search(caption):
            errors.append(f"caption uses question-number wording: {caption}")

    # every figure/table label must be referenced by at least one \ref (no orphan)
    for m in re.finditer(r"\\label\{(fig|tab):([^}]+)\}", text):
        key = f"{m.group(1)}:{m.group(2)}"
        if not re.search(r"\\ref\{" + re.escape(key) + r"\}", text):
            errors.append(f"figure/table '{key}' has a \\label but is never \\ref'd in text (orphan)")

    # numbering continuity (arabic only)
    for kind in ("图", "表"):
        nums: list[int] = []
        for caption in captions:
            match = re.search(rf"{kind}\s*(\d+)", caption)
            if match:
                nums.append(int(match.group(1)))
        if nums:
            nums = sorted(nums)
            uniq = sorted(set(nums))
            expected = list(range(1, max(uniq) + 1))
            if uniq != expected or len(nums) != len(uniq):
                errors.append(f"{kind} numbering gap/dup: found {nums}")

    # orphan figures: declared in reports but not in tex
    declared: set[str] = set()
    for rel in ("docs/04-figures-report.md", "docs/05-diagrams-report.md", "docs/05-visual-report.md"):
        declared |= report_figures(root / rel)
    for name in sorted(declared):
        if name not in resolved:
            errors.append(f"figure declared in report but not included in tex: {name}")

    fig_dir = root / "figures"
    if fig_dir.exists():
        for p in fig_dir.iterdir():
            if p.is_file() and p.suffix.lower() in FIG_EXT and p.name not in resolved and p.name not in declared:
                warnings.append(f"figure in figures/ not referenced (check if intentional): {p.name}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="machine-check paper figure/table integrity")
    parser.add_argument("tex", nargs="?", default="paper/论文.tex")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    tex_path = root / args.tex
    errors, warnings = check(root, tex_path)
    for warning in warnings:
        print("WARN: " + _ascii(warning))
    if errors:
        print("paper references check: FAIL")
        for error in errors:
            print("- " + _ascii(error))
        return 1
    print("paper references check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
