#!/usr/bin/env python3
"""Reject process-oriented and empty-template language from paper TeX sources."""

from __future__ import annotations

import argparse
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
import re
from pathlib import Path


RULES = {
    "生成过程与工具身份": [
        "AI", "人工智能", "大语言模型", "ChatGPT", "Codex", "Agent", "智能体",
        "提示词", "Prompt", "skill", "工作流", "阶段", "上游", "下游", "GATE",
        "manifest", "artifact", "调用", "生成", "自动生成", "用户", "本助手",
    ],
    "对话与执行口吻": [
        "根据你的要求", "下面给出", "如果需要可以", "接下来", "下面由", "已完成此阶段", "我/我们为你",
    ],
    "空泛模板与无证据自评": [
        "本文将", "值得注意的是", "需要指出的是", "综上所述", "总而言之", "形成闭环",
        "完整回答", "显著提升", "有效赋能", "可解释性强", "具有重要意义",
    ],
}

VERBATIM_ENVS = ("lstlisting", "verbatim", "minted")
ALLOW_START = "% language-audit: allow-start"
ALLOW_END = "% language-audit: allow-end"


def source_without_exemptions(text: str) -> str:
    for env in VERBATIM_ENVS:
        text = re.sub(
            rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}",
            "",
            text,
            flags=re.DOTALL,
        )
    text = re.sub(
        rf"{re.escape(ALLOW_START)}.*?{re.escape(ALLOW_END)}",
        "",
        text,
        flags=re.DOTALL,
    )
    # TeX comments are not visible submission text. Preserve escaped percent signs.
    text = re.sub(r"(?<!\\)%[^\n]*", "", text)
    # 文件名/命令名（\texttt、\url、\lstinline）不是作者正文，按"禁用表达不适用于文件名/文献题名"剔除。
    text = re.sub(r"\\texttt\{[^{}]*\}", "", text)
    text = re.sub(r"\\url\{[^{}]*\}", "", text)
    text = re.sub(r"\\lstinline\{[^{}]*\}", "", text)
    # 文献题名（thebibliography 中的 \bibitem 行）不适用禁用表达，剔除。
    text = re.sub(r"\\bibitem\{[^{}]*\}.*", "", text)
    return text


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def term_pattern(term: str) -> str:
    if re.fullmatch(r"[A-Za-z]+", term):
        return rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])"
    return re.escape(term)


def audit(path: Path) -> list[str]:
    findings: list[str] = []
    for tex_file in sorted(path.rglob("*.tex")):
        original = tex_file.read_text(encoding="utf-8")
        text = source_without_exemptions(original)
        for category, terms in RULES.items():
            for term in terms:
                for match in re.finditer(term_pattern(term), text, flags=re.IGNORECASE):
                    findings.append(
                        f"{tex_file}:{line_number(text, match.start())}: {category}: {term}"
                    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_dir", type=Path, help="directory containing paper TeX sources")
    args = parser.parse_args()

    if not args.paper_dir.is_dir():
        parser.error(f"directory does not exist: {args.paper_dir}")

    findings = audit(args.paper_dir)
    if findings:
        print("submission-language audit failed:")
        print("\n".join(findings))
        return 1

    print("submission-language audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
