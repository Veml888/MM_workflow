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


def check(tex, path, strict=False):
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


def check_list_indent(tex, path):
    """检测编号/项目列表是否配置了首行缩进（警告级，不硬 FAIL）。

    规范（common-paper-rules 第 17 条）：enumerate/itemize 列表项正文须首行缩进两字符。
    LaTeX 默认列表项不缩进，须用 enumitem 的 itemindent/leftmargin 或局部参数配置。
    此机检无法读取渲染结果，只能做静态启发式：若全文出现 enumerate/itemize 而
    未见任何 itemindent/leftmargin 缩进配置，则警告提示人工核对。
    """
    warns = []
    has_list_env = (r"\begin{enumerate}" in tex) or (r"\begin{itemize}" in tex)
    has_indent_cfg = ("itemindent" in tex) or (r"\setlist" in tex) or ("leftmargin" in tex and "enumitem" in tex)
    if has_list_env and not has_indent_cfg:
        warns.append(
            "检测到 enumerate/itemize 列表环境，但未见 itemindent/leftmargin/\\setlist 等缩进配置："
            "LaTeX 默认列表项正文顶格、无首行缩进。请用 \\usepackage{enumitem} + "
            "\\setlist[enumerate,1]{itemindent=2em,leftmargin=2em,...} 或局部列表参数配置，"
            "否则列表项首行不会缩进两字符（属人工冷读必查项，机检只能做静态提示）。"
        )
    return warns


def main():
    if len(sys.argv) < 2:
        print("usage: python check_noindent.py <论文.tex>")
        return 2
    path = sys.argv[1]
    tex = load(path)
    errs = check(tex, path)
    warns = check_list_indent(tex, path)
    for w in warns:
        print("  [WARN] (人工核对) ", w)
    if errs:
        print("no-indent check: FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("no-indent check: PASS%s" % ("（含 %d 条列表缩进人工核对提示）" % len(warns) if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
