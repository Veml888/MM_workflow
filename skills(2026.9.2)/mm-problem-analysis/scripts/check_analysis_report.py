#!/usr/bin/env python3
"""check_analysis_report.py — 赛题分析报告机检（硬门禁，exit 0 才算 PASS）。

规范（mm-problem-analysis SKILL §三 Step 6 + references/analysis-report-template.md）：
  docs/01-analysis-report.md 必须包含八部分（## 0 阶段GATE ~ ## 8 输出契约与下游交接），
  每问有稳定 ID（REQ-###/P-##/DS-###/MC-P##-##），每个首选模型可证伪（有选择证据、局限与淘汰条件），
  且 Q-PA1~Q-PA5 门禁已填写（允许 N/A 仅限 Q-PA4）。

用法：python check_analysis_report.py <docs/01-analysis-report.md>
"""

from __future__ import annotations

import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 八部分标题（模板里的精确写法）
PARTS = [
    r"阶段 GATE",
    r"问题重述与要求追踪",
    r"数据概览与实验设计审计",
    r"数据审计",
    r"问题分类结论",
    r"建模方向与数学形态预演",
    r"可建模性与验证契约",
    r"子问题依赖关系",
    r"输出契约与下游交接",
]

ID_PATTERNS = {
    "REQ": re.compile(r"REQ-\d{3}"),
    "P": re.compile(r"P-\d{1,2}(?!\d)"),
    "DS": re.compile(r"DS-\d{3}"),
    "MC": re.compile(r"MC-P\d{1,2}-\d{1,2}"),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check(text, path):
    errs = []

    # 1) 八部分标题是否齐全（按模板 "## N. 标题" 前缀）
    for idx, title in enumerate(PARTS):
        # 标题前缀可能是 "## 0. 阶段 GATE" 等，宽容匹配 "## N. <title>" 或 "## <title>"
        pat = re.compile(r"^##\s+\d+\.\s*" + re.escape(title.split()[0]), re.M)
        if not pat.search(text):
            errs.append(f"缺第 {idx} 部分标题：'## {idx}. {title}'")
    # 0 部分标题是 "## 0. 阶段 GATE"，'阶段' 作为首词已匹配

    # 2) 稳定 ID 是否出现（报告应至少有一个 REQ / P / DS / MC）
    for key, pattern in ID_PATTERNS.items():
        if not pattern.search(text):
            errs.append(f"报告未出现稳定 ID {key}-xxx（应至少分配一个，用于下游追溯）")

    # 3) 每个首选候选是否可证伪：凡标"首选"的模型行，须有"淘汰条件"或"弃用/局限"字样
    #    在 "## 5. 建模方向" 区块里，检查"首选"是否伴随淘汰条件
    block5 = _section(text, "建模方向与数学形态预演")
    if block5:
        n_shared = len(re.findall(r"首选", block5))
        n_falsify = len(re.findall(r"淘汰|弃用|局限|证据.*出现|何时.*不用|触发.*弃", block5))
        if n_shared > 0 and n_falsify == 0:
            errs.append("建模方向区有'首选'候选，但未找到任何'淘汰条件/局限/何时弃用'表述（首选必须可被证据推翻）")
    else:
        errs.append("未找到 '## 5. 建模方向与数学形态预演' 区块")

    # 4) Q-PA 门禁：至少已填 Q-PA1~Q-PA5（允许 N/A 仅限 Q-PA4），未填为 FAIL
    _check_qpa(text, errs)

    return errs


def _section(text, title_word):
    """按 "## N. <title_word>" 切出一段，若找不到返回空串。"""
    m = re.search(r"^##\s+\d+\.\s*" + re.escape(title_word), text, re.M)
    if not m:
        return ""
    start = m.start()
    nxt = re.search(r"^##\s+\d+\.", text[m.end():], re.M)
    end = m.end() + (nxt.start() if nxt else len(text) - m.end())
    return text[start:end]


def _check_qpa(text, errs):
    # 门禁行形如：| Q-PA1 要求完整 | PASS/FAIL | <...> |
    for gate in ["Q-PA1", "Q-PA2", "Q-PA3", "Q-PA4", "Q-PA5"]:
        # 允许该门禁行状态为空缺（未填=Fail），"N/A" 仅 Q-PA4 合法
        m = re.search(re.escape(gate) + r"\s*[^|]*\|\s*(\S+)", text)
        if not m:
            errs.append(f"质量门禁 {gate} 未填写")
            continue
        state = m.group(1).strip()
        if state not in {"PASS", "FAIL"}:
            if gate == "Q-PA4" and state == "N/A":
                continue
            errs.append(f"质量门禁 {gate} 状态为 '{state}'，应填 PASS/FAIL（Q-PA4 可 N/A）")


def main():
    if len(sys.argv) < 2:
        print("usage: python check_analysis_report.py <docs/01-analysis-report.md>")
        return 2
    path = sys.argv[1]
    text = load(path)
    errs = check(text, path)
    if errs:
        print("analysis report check: FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("analysis report check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
