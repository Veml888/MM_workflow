#!/usr/bin/env python3
"""Initialize the CUMCM project skeleton in PROJECT_ROOT.

Usage:
    python init_project_skeleton.py --root <PROJECT_ROOT> [--force] [--dry-run]

Creates (if missing):
  - plan.md
  - todo.md
  - project-manifest.json (schema 2.0)
  - paper/structure-plan.md
  - paper/page-budget.json
  - paper/figure-requirements.md
  - paper/writing-gates.md

Files that already exist are left alone unless --force is passed (then they
are only rewritten for the *empty* initial templates, not for user-edited
content). Use init_paper_gates.py afterwards to populate writing-gates.md
and the manifest's paper_gates[].

Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PLAN_TEMPLATE = """# 整体方案（plan.md）

> 由 `mm-orchestrator` 在第 3 步生成；每阶段完成后回填实际进度。

## 题目

- 标题：
- 来源：CUMCM

## 用户偏好

- 侧重点：（精度 / 可解释性 / 速度 / 均衡）
- 子问题数量：（N / 待分析确定）
- 编程语言：Python（默认，不询问）

## 阶段顺序与负责 skill

| 序 | 阶段 | skill | 关键产出 | 状态 |
|---|---|---|---|---|
| 1 | 赛题分析 | mm-problem-analysis | docs/01-analysis-report.md | pending |
| 2 | 建模求解 | mm-modeling | docs/02-modeling-report.md | pending |
| 3 | 编程实现 | mm-coding | code/、results/、docs/03-results-report.md | pending |
| 4 | 论文策划 | mm-orchestrator | paper/structure-plan.md 等 6 份 | pending |
| 5a | 数据图 | mm-figures | figures/*、docs/04-figures-report.md | pending |
| 5b | 非数据图 | mm-graphics | figures/*、docs/05-diagrams-report.md | pending |
| 6a | 写作轮 | mm-paper-writing | paper/论文.tex|pdf 等 | pending |
| 6b | 独立审查轮 | mm-paper-writing | paper/review-*.md 等 | pending |
| 7 | 验收 | mm-verification | docs/06-verification-report.md | pending |

## 风险控制

- 每阶段 `complete` 前必须跑对应机检并 exit 0；禁手写 PASS。
- 跨阶段回写走 `manifest.change_log`；稳定 ID 永不复用。
- 论文终稿页数目标 28/29，允许 25–30；compile_passes ≥ 2。

## n_a 范围（如有）

（如有阶段不适用，在此写明原因）
"""


TODO_TEMPLATE = """# 阶段待办清单（todo.md）

> 每阶段一条，勾选进度。本文件由 `mm-orchestrator` 第 3 步生成。

- [ ] 阶段 1：赛题分析（mm-problem-analysis）
- [ ] 阶段 2：建模求解（mm-modeling）
- [ ] 阶段 3：编程实现（mm-coding）
- [ ] 阶段 4：论文策划（mm-orchestrator）
- [ ] 阶段 5a：数据图（mm-figures）
- [ ] 阶段 5b：非数据图（mm-graphics）
- [ ] 阶段 6a：论文写作轮（mm-paper-writing）
- [ ] 阶段 6b：论文独立审查轮（mm-paper-writing）
- [ ] 阶段 7：验收（mm-verification）
"""


PAGE_BUDGET_INITIAL = {
    "schema_version": "1.0",
    "target_body_pages": 28,
    "allowed_range": [25, 30],
    "draft": {"mode": "none"},
    "sections": [],
}


STRUCTURE_PLAN_TEMPLATE = """# 论文结构计划（structure-plan.md）

> 初始化时仅占位；正式定稿在分析、建模、编程完成后由 paper_plan 阶段填充。
> 章节骨架以 `mm-paper-writing/references/common-paper-rules.md` 的"整体论文骨架"与 `mm-paper-writing/references/writing-order.json` 的章节清单为唯一权威。

（待 paper_plan 阶段填写：每问独立一章 + 模型评价与推广单独一章；每问写清核心论证链：承接 → 建模 → 求解 → 结果表 → 结果分析；建立"题面要求/子问题 → 正文小节 → 模型变量与约束 → 结果证据 → 最终回答"的追踪关系）
"""


FIGURE_REQS_TEMPLATE = """# 论文插图需求清单（figure-requirements.md）

> 编排器只建骨架；具体图种、锚点、依据题面位置由 `mm-figures` / `mm-graphics` 在自己的执行阶段填写。

## 数据图（mm-figures 负责）

- 边界规则：必须有真实数值结果（results/ 或 docs/03-results-report.md）。
- 本题需要画的数据图（由 mm-figures 阶段填写）：
  - （待 mm-figures 阶段填写）

## 非数据图（mm-graphics 负责）

- 边界规则：逻辑/框架/机理图 + 场景/空间精确示意图。
- 本题需要画的非数据图（由 mm-graphics 阶段填写）：
  - （待 mm-graphics 阶段填写）
"""


def build_manifest(title: str) -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "schema_version": "2.0",
        "competition": "CUMCM",
        "project": {"title": title, "language": "zh-CN", "created_at": now},
        "stages": {
            "analysis": {"status": "pending", "report": "docs/01-analysis-report.md"},
            "modeling": {"status": "pending", "report": "docs/02-modeling-report.md"},
            "coding": {"status": "pending", "report": "docs/03-results-report.md"},
            "figures": {"status": "pending", "report": "docs/04-figures-report.md"},
            "graphics": {"status": "pending", "report": "docs/05-diagrams-report.md"},
            "paper_plan": {"status": "pending", "report": "paper/structure-plan.md"},
            "paper_final": {"status": "pending", "draft_mode": "none"},
            "verification": {"status": "pending", "report": "docs/06-verification-report.md"},
        },
        "requirements": [],
        "problems": [],
        "datasets": [],
        "assumptions": [],
        "model_candidates": [],
        "selected_models": [],
        "implemented_models": [],
        "validation_plans": [],
        "symbols": [],
        "results": [],
        "figures": [],
        "artifacts": [],
        "paper_gates": [],
        "rework": [],
        "change_log": [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize CUMCM project skeleton")
    parser.add_argument("--root", type=Path, default=Path("."), help="PROJECT_ROOT")
    parser.add_argument("--title", default="", help="Project title used in manifest")
    parser.add_argument("--force", action="store_true", help="Overwrite existing empty templates")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    return parser.parse_args()


def write_or_skip(path: Path, content: str, force: bool, dry_run: bool) -> str:
    """Return 'created' / 'kept' / 'overwritten'."""
    if path.exists():
        if force:
            if dry_run:
                print(f"[dry-run] overwrite: {path}")
            else:
                path.write_text(content, encoding="utf-8")
            return "overwritten"
        if dry_run:
            print(f"[dry-run] keep existing: {path}")
        return "kept"
    if dry_run:
        print(f"[dry-run] create: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return "created"


def main() -> int:
    args = parse_args()
    root: Path = args.root.resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2

    paper_dir = root / "paper"
    actions: list[tuple[str, str]] = []

    actions.append((
        "plan.md",
        write_or_skip(
            root / "plan.md", PLAN_TEMPLATE, force=args.force, dry_run=args.dry_run,
        ),
    ))
    actions.append((
        "todo.md",
        write_or_skip(
            root / "todo.md", TODO_TEMPLATE, force=args.force, dry_run=args.dry_run,
        ),
    ))
    manifest_path = root / "project-manifest.json"
    if args.dry_run:
        if manifest_path.exists() and not args.force:
            print(f"[dry-run] keep existing: {manifest_path}")
            actions.append(("project-manifest.json", "kept"))
        else:
            print(f"[dry-run] create/overwrite: {manifest_path}")
            actions.append(("project-manifest.json", "overwritten" if manifest_path.exists() else "created"))
    else:
        if manifest_path.exists() and not args.force:
            actions.append(("project-manifest.json", "kept"))
        else:
            manifest_path.write_text(
                json.dumps(build_manifest(args.title), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            actions.append((
                "project-manifest.json",
                "overwritten" if manifest_path.exists() else "created",
            ))

    paper_dir.mkdir(parents=True, exist_ok=True)
    actions.append((
        "paper/structure-plan.md",
        write_or_skip(
            paper_dir / "structure-plan.md",
            STRUCTURE_PLAN_TEMPLATE,
            force=args.force,
            dry_run=args.dry_run,
        ),
    ))
    page_budget = paper_dir / "page-budget.json"
    if page_budget.exists() and not args.force:
        actions.append(("paper/page-budget.json", "kept"))
        if args.dry_run:
            print(f"[dry-run] keep existing: {page_budget}")
    elif args.dry_run:
        print(f"[dry-run] {'overwrite' if page_budget.exists() else 'create'}: {page_budget}")
        actions.append((
            "paper/page-budget.json",
            "overwritten" if page_budget.exists() else "created",
        ))
    else:
        page_budget.write_text(
            json.dumps(PAGE_BUDGET_INITIAL, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        actions.append((
            "paper/page-budget.json",
            "overwritten" if page_budget.exists() else "created",
        ))
    actions.append((
        "paper/figure-requirements.md",
        write_or_skip(
            paper_dir / "figure-requirements.md",
            FIGURE_REQS_TEMPLATE,
            force=args.force,
            dry_run=args.dry_run,
        ),
    ))

    writing_gates = paper_dir / "writing-gates.md"
    if writing_gates.exists() and not args.force:
        actions.append(("paper/writing-gates.md", "kept"))
        if args.dry_run:
            print(f"[dry-run] keep existing: {writing_gates}")
    else:
        from init_paper_gates import render_writing_gates_md  # type: ignore

        content = render_writing_gates_md()
        if args.dry_run:
            print(f"[dry-run] {'overwrite' if writing_gates.exists() else 'create'}: {writing_gates}")
        else:
            writing_gates.write_text(content, encoding="utf-8")
        actions.append((
            "paper/writing-gates.md",
            "overwritten" if writing_gates.exists() else "created",
        ))

    print()
    print("init_project_skeleton summary:")
    for name, action in actions:
        print(f"  - {action:11s} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())