#!/usr/bin/env python3
"""Validate mm-paper-writing's writing-order.json invariants.

This is the mm-paper-writing-specific validator. It enforces the paper-
specific fields (paper_order, writing_order, abstract_must_be_written_last,
reread_before_writing) that the *generic* read-protocol script
(`<mm-orchestrator目录>/scripts/read_complete.py`) deliberately does not
know about.

The generic read script guarantees plan/chunk/receipt/verify across every
skill; this script guarantees mm-paper-writing's 11-chapter paper order
and abstract-last invariant.

Usage:
    python <mm-paper-writing目录>/scripts/check_paper_order.py
    python <mm-paper-writing目录>/scripts/check_paper_order.py --registry references/writing-order.json

Stdlib-only. Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import argparse
import json
import sys

if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

EXPECTED_CHAPTERS = [
    "references/chapters/00-摘要.md",
    "references/chapters/01-问题重述.md",
    "references/chapters/02-问题分析.md",
    "references/chapters/03-模型假设.md",
    "references/chapters/04-符号说明.md",
    "references/chapters/05-模型的建立与求解.md",
    "references/chapters/05b-灵敏度分析与模型检验.md",
    "references/chapters/06-模型评价与推广.md",
    "references/chapters/07-AI使用声明.md",
    "references/chapters/08-参考文献.md",
    "references/chapters/09-附录.md",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate mm-paper-writing writing-order.json")
    parser.add_argument("--registry", default="references/writing-order.json",
                        help="Path to writing-order.json (relative to mm-paper-writing/)")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    registry_path = (here.parent / args.registry).resolve()
    if not registry_path.is_file():
        print(f"FAIL: registry not found: {registry_path}", file=sys.stderr)
        return 1

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON in {registry_path}: {exc}", file=sys.stderr)
        return 1

    errs: list[str] = []
    if registry.get("abstract_must_be_written_last") is not True:
        errs.append("abstract_must_be_written_last must be true")

    paper_order = registry.get("paper_order")
    if paper_order != EXPECTED_CHAPTERS:
        if not isinstance(paper_order, list):
            errs.append("paper_order must be an array")
        else:
            missing = [c for c in EXPECTED_CHAPTERS if c not in paper_order]
            extra = [c for c in paper_order if c not in EXPECTED_CHAPTERS]
            if missing:
                errs.append(f"paper_order missing chapters: {missing}")
            if extra:
                errs.append(f"paper_order has extra chapters: {extra}")

    writing_order = registry.get("writing_order")
    if not isinstance(writing_order, list) or sorted(writing_order) != sorted(EXPECTED_CHAPTERS):
        if not isinstance(writing_order, list):
            errs.append("writing_order must be an array")
        else:
            missing = [c for c in EXPECTED_CHAPTERS if c not in writing_order]
            extra = [c for c in writing_order if c not in EXPECTED_CHAPTERS]
            if missing:
                errs.append(f"writing_order missing chapters: {missing}")
            if extra:
                errs.append(f"writing_order has extra chapters: {extra}")
    elif writing_order[-1] != "references/chapters/00-摘要.md":
        errs.append("abstract (chapters/00-摘要.md) must be last in writing_order")

    reread = registry.get("reread_before_writing")
    if not isinstance(reread, dict) or sorted(reread.values()) != sorted(EXPECTED_CHAPTERS):
        if not isinstance(reread, dict):
            errs.append("reread_before_writing must be an object")
        else:
            values = list(reread.values())
            missing = [c for c in EXPECTED_CHAPTERS if c not in values]
            extra = [c for c in values if c not in EXPECTED_CHAPTERS]
            if missing:
                errs.append(f"reread_before_writing missing chapters: {missing}")
            if extra:
                errs.append(f"reread_before_writing has extra chapters: {extra}")

    if errs:
        print("check_paper_order: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 1

    print("check_paper_order: PASS")
    print(f"  paper_order    : {len(EXPECTED_CHAPTERS)} chapters")
    print(f"  writing_order  : abstract last, all 11 chapters present")
    print(f"  reread coverage: all 11 chapters covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())