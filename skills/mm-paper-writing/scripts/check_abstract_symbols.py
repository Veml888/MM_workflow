#!/usr/bin/env python3
"""check_abstract_symbols.py — 摘要零数学符号 + 关键词数量机检（硬门禁，exit 0 才算 PASS）。

规范（mm-paper-writing references/chapters/00-摘要.md）：
  摘要正文不得出现行内/行间公式、独立字母变量、带上下标的变量、希腊字母、数学关系式；
  所有模型符号翻译成自然语言。白名单（不算符号）：纯阿拉伯数字、百分数、年份、
  常规计量单位、必要的化学式、首次写全称的模型英文缩写。
  关键词数量硬性为 4-5 个。

用法：python check_abstract_symbols.py <论文.tex>
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


def extract_abstract(tex):
    """摘要在 \\begin{document} 到首个 \\newpage 之间（摘要独占一页）。"""
    start = tex.find(r"\begin{document}")
    end = tex.find(r"\newpage", start)
    if start == -1:
        return ""
    if end == -1:
        end = tex.find(r"\section{", start)
    return tex[start:end] if end != -1 else tex[start:]


def check(tex):
    abstract = extract_abstract(tex)
    errs = []
    if not abstract.strip():
        errs.append("未定位到摘要区（\\begin{document} 到 \\newpage 之间为空）")
        return errs

    body = abstract
    # 剔除命令骨架（标题/字体/格式命令），保留可见文本
    visible = re.sub(r"\\(?:centering|vspace|heiti|songti|zihao|bfseries|noindent)\{[^}]*\}", "", body)
    visible = re.sub(r"\\textbf\{([^}]*)\}", r"\1", visible)
    visible = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", visible)

    # 1) 公式环境 / $...$ 行内公式
    if re.search(r"\\begin\{(equation|align\*?|eqnarray)\}", body):
        errs.append("摘要出现公式环境（equation/align）")
    dollar = re.findall(r"\$([^$]{1,40})\$", body)
    if dollar:
        errs.append(f"摘要出现 {len(dollar)} 处行内数学模式（$...$），首个为 ${dollar[0]}$")

    # 2) 希腊字母
    greek_cn = re.findall(r"[α-ωΑ-ΩΦΨΩλμσβγ]", body)
    if greek_cn:
        errs.append(f"摘要出现希腊字母：{''.join(set(greek_cn))[:20]}")

    # 3) 带下标/上标的变量（p_0、x_i、P_g、n_1 等）或 单字母紧跟数字/等号
    sub_var = re.findall(r"(?<![a-zA-Z])([a-zA-Z])[_^]\{?[a-zA-Z0-9]+\}?", visible)
    sub_var2 = re.findall(r"(?<![a-zA-Z])([a-zA-Z])\d+\s*[=≤≥→]", visible)
    if sub_var:
        errs.append(f"摘要出现带上下标的变量：{', '.join(set(sub_var))[:30]}")
    if sub_var2:
        errs.append(f"摘要出现单字母+下标/等号关系：{', '.join(set(sub_var2))[:30]}")

    # 4) 数学关系式：单字母=数字、<≤≥ 等（排除纯数字百分比）
    rel = re.findall(r"(?<![a-zA-Z0-9])([a-zA-Z])\s*[=≤≥<>→]\s*\d", visible)
    if rel:
        errs.append(f"摘要出现数学关系式（如 n=78）：{', '.join(set(rel))[:30]}")

    # 5) 关键词数量
    kw = re.search(r"关键词[:：]\s*(.+)", visible)
    if kw:
        cnt = len([x for x in re.split(r"[;；]", kw.group(1)) if x.strip()])
        if cnt < 4 or cnt > 5:
            errs.append(f"关键词数量 {cnt} 个，应为 4-5 个")
    else:
        errs.append("未找到关键词行")

    return errs


def main():
    if len(sys.argv) < 2:
        print("usage: python check_abstract_symbols.py <论文.tex>")
        return 2
    path = sys.argv[1]
    tex = load(path)
    errs = check(tex)
    if errs:
        print("abstract symbols check: FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("abstract symbols check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
