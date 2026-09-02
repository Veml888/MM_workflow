#!/usr/bin/env python3
"""Validate the finalized paper page budget before figure generation."""

from __future__ import annotations

import argparse

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
import json
import re
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"<[^>]+>|【[^】]*(填写|待补充|占位)[^】]*】|待补充|以后完善|TODO|TBD", re.I)
REQUIRED_SECTION_FIELDS = {
    "id",
    "title",
    "min_pages",
    "target_pages",
    "max_pages",
    "source_paths",
    "evidence_ids",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="validate finalized CUMCM paper page budget")
    parser.add_argument("budget", nargs="?", default="paper/page-budget.json", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    budget_path = args.budget if args.budget.is_absolute() else root / args.budget
    errors: list[str] = []
    if not budget_path.exists():
        errors.append(f"budget not found: {budget_path}")
        data: dict[str, object] = {}
    else:
        try:
            data = json.loads(budget_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot parse budget JSON: {exc}")
            data = {}

    if data:
        target = data.get("target_body_pages")
        allowed = data.get("allowed_range")
        sections = data.get("sections")
        if target not in (28, 29):
            errors.append("target_body_pages must be 28 or 29")
        if allowed != [27, 30]:
            errors.append("allowed_range must be [27, 30]")
        if not isinstance(sections, list) or not sections:
            errors.append("sections must be a non-empty array")
            sections = []

        total_target = 0.0
        seen_ids: set[str] = set()
        for index, section in enumerate(sections, start=1):
            label = f"section[{index}]"
            if not isinstance(section, dict):
                errors.append(f"{label} must be an object")
                continue
            missing = REQUIRED_SECTION_FIELDS - set(section)
            if missing:
                errors.append(f"{label} missing fields: {sorted(missing)}")
                continue
            section_id = str(section["id"])
            if not section_id or section_id in seen_ids:
                errors.append(f"{label} id is empty or duplicated: {section_id!r}")
            seen_ids.add(section_id)
            combined = json.dumps(section, ensure_ascii=False)
            if PLACEHOLDER_RE.search(combined):
                errors.append(f"{label} contains placeholder text")
            try:
                minimum = float(section["min_pages"])
                section_target = float(section["target_pages"])
                maximum = float(section["max_pages"])
                if not (0 <= minimum <= section_target <= maximum):
                    errors.append(f"{label} page values must satisfy 0 <= min <= target <= max")
                total_target += section_target
            except Exception:
                errors.append(f"{label} page values must be numeric")
            source_paths = section["source_paths"]
            if not isinstance(source_paths, list) or not source_paths:
                errors.append(f"{label} source_paths must be non-empty")
            else:
                for raw_path in source_paths:
                    source = root / str(raw_path)
                    if not source.exists():
                        errors.append(f"{label} source path not found: {raw_path}")
            evidence_ids = section["evidence_ids"]
            if not isinstance(evidence_ids, list) or not evidence_ids:
                errors.append(f"{label} evidence_ids must be non-empty")

        if isinstance(target, (int, float)) and abs(total_target - float(target)) > 1e-6:
            errors.append(f"section target sum {total_target:g} != target_body_pages {target}")

        draft = data.get("draft")
        if not isinstance(draft, dict) or draft.get("mode") not in {
            "retained",
            "partial",
            "invalidated",
            "none",
        }:
            errors.append("draft.mode must be retained/partial/invalidated/none")
        elif draft.get("mode") != "none":
            for field in ("path", "sha256", "body_pages", "audit_path"):
                if field not in draft or draft[field] in (None, ""):
                    errors.append(f"draft.{field} is required when a draft exists")
            for field in ("path", "audit_path"):
                if draft.get(field) and not (root / str(draft[field])).exists():
                    errors.append(f"draft {field} not found: {draft[field]}")

    result = {
        "status": "pass" if not errors else "fail",
        "budget": str(budget_path),
        "errors": errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
