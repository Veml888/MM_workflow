#!/usr/bin/env python3
"""Require a pass audit to cover every mandatory file and every ##/### heading."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
READ_SCRIPT = Path(__file__).with_name("read_complete.py")
STATUS_RE = re.compile(r"\[(已执行|不适用(?::[^\]]+)?|阻断)\]")


def load_plan() -> dict:
    result = subprocess.run(
        [sys.executable, str(READ_SCRIPT), "plan"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "read_complete plan failed")
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit")
    args = parser.parse_args()
    audit_path = Path(args.audit).resolve()
    text = audit_path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if STATUS_RE.search(line)]
    missing: list[str] = []
    for item in load_plan()["files"]:
        path = item["path"]
        headings = item["headings"] or ["<文件整体>"]
        for heading in headings:
            if not any(path in line and heading in line for line in lines):
                missing.append(f"{path} :: {heading}")
    if missing:
        print("REQUIREMENT-COVERAGE FAIL", file=sys.stderr)
        for value in missing:
            print(f"- {value}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "covered_items": sum(len(item["headings"] or [1]) for item in load_plan()["files"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
