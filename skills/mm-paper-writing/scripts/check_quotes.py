#!/usr/bin/env python3
"""check_quotes.py — 中文引号方向机检（硬门禁，exit 0 才算 PASS）。

规范（common-paper-rules 第 18 条）：中文引号必须成对使用弯引号——
开启用 “（U+201C）、闭合用 ”（U+201D），禁止两端同向的直引号 "（U+0022）。

本脚本强制两条硬性检查：
  (1) 全文禁止 ASCII 直引号 U+0022（唯一合法豁免区见白名单）；
  (2) 中文弯引号必须成对：左弯引号 U+201C 数量 == 右弯引号 U+201D 数量。

白名单（跳过，不在其中计 U+0022 或判断成对）：
  - \\texttt{...} 参数（文件名/路径/代码标识）
  - \\verb ... \\verb 或 \\verb|...|（原样输出）
  - \\begin{lstlisting} ... \\end{lstlisting} 块（源码，string 引号合法）
  - 行内 LaTeX 命令区（\\command 及其参数等纯语法，不含中文内容）

用法：python check_quotes.py <论文.tex>
"""

from __future__ import annotations

import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ASCII_Q = "\u0022"      # "
LEFT_Q = "\u201c"       # “
RIGHT_Q = "\u201d"      # ”

# 白名单区域正则（从文本中剔除，不在这些区域内统计引号）
LST = re.compile(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", re.S)
TT = re.compile(r"\\texttt\{[^{}]*\}", re.S)
VERB = re.compile(r"\\verb(\W)(.*?)\1", re.S)         # \verb|...| 或 \verb ... 形式
# 行内命令区：\\command（含 \\begin{env}、\\includegraphics[...]{...}、\\subsection{...} 等
CMD = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_whitelist(text):
    """剔除白名单区域，返回需参与引号检查的正文片段。"""
    # 先剔除大块 lstlisting（否则 \\begin 命令会先被 CMD 吞掉破坏匹配）
    out = LST.sub("", text)
    out = VERB.sub("", out)
    out = TT.sub("", out)
    out = CMD.sub("", out)
    return out


def check(tex):
    body = strip_whitelist(tex)
    errs = []
    n_ascii = body.count(ASCII_Q)
    n_left = body.count(LEFT_Q)
    n_right = body.count(RIGHT_Q)
    if n_ascii:
        errs.append(
            f"中文正文出现 {n_ascii} 处 ASCII 直引号 \u0022（U+0022）："
            "应为中文弯引号 “（U+201C）与 ”（U+201D），禁止两端同向。"
        )
    if n_left != n_right:
        errs.append(
            f"中文弯引号不成对：左引号 “（U+201C）{n_left} 个，右引号 ”（U+201D）{n_right} 个，"
            "应为成对且左右交替。"
        )
    return errs, body


def main():
    if len(sys.argv) < 2:
        print("usage: python check_quotes.py <论文.tex>")
        return 2
    path = sys.argv[1]
    tex = load(path)
    errs, _body = check(tex)
    if errs:
        print("quote check: FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("quote check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
