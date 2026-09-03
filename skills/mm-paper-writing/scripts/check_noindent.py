#!/usr/bin/env python3
"""check_noindent.py — 扫描论文源文件中的 \\noindent（首行缩进硬门禁）。

规范（common-paper-rules 第 17 条）：每个正文新段落必须首行缩进两字符，
不得用 \\noindent 消除首行缩进。唯一的合法例外是"摘要之关键词行"
（形如 \\noindent{...关键词：...}），其余所有 \\noindent 一律 FAIL。

用法：python check_noindent.py <论文.tex>
"""

from __future__ import annotations

import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check(tex, path):
    lines = tex.split("\n")
    errs = []
    for idx, line in enumerate(lines, start=1):
        if r"\noindent" not in line:
            continue
        # 合法例外：含 "关键词" 的关键词行
        if "关键词" in line and ("关键词：" in line or "关键词：" in line):
            continue
        errs.append(
            f"第 {idx} 行含 \\noindent：正文新段落必须首行缩进两字符，"
            f"禁止用 \\noindent 消除缩进（合法例外仅为摘要之关键词行）：\n"
            f"    {line[:80]}"
        )
    return errs


def main():
    if len(sys.argv) < 2:
        print("usage: python check_noindent.py <论文.tex>")
        return 2
    path = sys.argv[1]
    tex = load(path)
    errs = check(tex, path)
    if errs:
        print("no-indent check: FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("no-indent check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
