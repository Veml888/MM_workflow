#!/usr/bin/env python3
"""Initialize G-1~G-5 pending entries in manifest and writing-gates.md.

Usage:
    python init_paper_gates.py --root <PROJECT_ROOT> [--force] [--dry-run]

Writes (or refreshes):
  - paper/writing-gates.md
  - manifest.paper_gates[] (5 entries, all pending)

Pairs with init_project_skeleton.py but can be invoked separately to refresh
the gates after a manifest rewrite.

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


GATES = [
    ("G-1", "必读已读", "paper/skill-read-receipt.json"),
    ("G-2", "图表齐全", "paper/figure-requirements.md"),
    ("G-3", "上游数据", "project-manifest.json"),
    ("G-4", "结构拟定", "paper/structure-plan.md"),
    ("G-5", "工具就绪", "paper/论文.tex"),
]


def render_writing_gates_md() -> str:
    lines = ["# 写作门禁（writing-gates.md）", ""]
    lines.append("> 由 `mm-orchestrator` 初始化为 `pending`；写作轮启动前由 `mm-paper-writing` 全部置 `pass`。")
    lines.append("")
    lines.append("| ID | 含义 | 证据路径 | 状态 | 复核时间 |")
    lines.append("|---|---|---|---|---|")
    for gid, desc, evidence in GATES:
        lines.append(f"| {gid} | {desc} | `{evidence}` | pending |  |")
    lines.append("")
    lines.append("## 置 pass 规则")
    lines.append("")
    lines.append("- G-1：必读文件读取回执生成 + `read_complete.py verify` exit 0。")
    lines.append("- G-2：数据图、非数据图阶段全部 `complete` 或 `n_a`，figure-requirements.md 两区填齐。")
    lines.append("- G-3：`docs/01~03`、`results/`、`paper/page-budget.json` 全部已登记哈希。")
    lines.append("- G-4：`paper/structure-plan.md` + `paper/draft-audit.md` 已 complete。")
    lines.append("- G-5：XeLaTeX / tectonic 可用、字体可用、模板就绪。")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize paper writing gates")
    parser.add_argument("--root", type=Path, default=Path("."), help="PROJECT_ROOT")
    parser.add_argument("--force", action="store_true", help="Reset all gates to pending even if already pass")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    return parser.parse_args()


def merge_gates(existing: list[dict], force: bool) -> list[dict]:
    """Merge G-1..G-5 into existing paper_gates[] without demoting pass → pending unless --force."""
    by_id = {item.get("id"): item for item in existing if isinstance(item, dict)}
    merged: list[dict] = []
    for gid, desc, evidence in GATES:
        cur = by_id.get(gid)
        if cur and not force:
            if cur.get("status") in {"pending", "pass", "fail"}:
                cur.setdefault("gate", gid)
                cur.setdefault("evidence_path", evidence)
                merged.append(cur)
                continue
        merged.append({
            "id": gid,
            "gate": gid,
            "status": "pending",
            "evidence_path": evidence,
            "evidence_summary": desc,
            "checked_at": None,
        })
    return merged


def main() -> int:
    args = parse_args()
    root: Path = args.root.resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2

    paper_dir = root / "paper"
    paper_dir.mkdir(parents=True, exist_ok=True)
    gates_md = paper_dir / "writing-gates.md"
    if args.dry_run:
        print(f"[dry-run] {'overwrite' if gates_md.exists() else 'create'}: {gates_md}")
    else:
        gates_md.write_text(render_writing_gates_md(), encoding="utf-8")

    manifest_path = root / "project-manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid manifest JSON: {exc}", file=sys.stderr)
        return 2

    paper_gates = manifest.get("paper_gates", [])
    if not isinstance(paper_gates, list):
        print("ERROR: manifest.paper_gates must be an array", file=sys.stderr)
        return 2

    merged = merge_gates(paper_gates, force=args.force)
    if args.dry_run:
        for item in merged:
            print(f"[dry-run] merge gate: id={item.get('id')} status={item.get('status')}")
    else:
        manifest["paper_gates"] = merged
        manifest.setdefault("change_log", []).append({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "by": "mm-orchestrator/init_paper_gates",
            "action": "init/refresh paper_gates[]",
            "affected_ids": [g[0] for g in GATES],
            "version": "v1",
        })
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"manifest.paper_gates[] updated ({len(merged)} entries)")

    print()
    print("init_paper_gates summary:")
    for item in merged:
        print(f"  - {item.get('id')} status={item.get('status')} evidence={item.get('evidence_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())