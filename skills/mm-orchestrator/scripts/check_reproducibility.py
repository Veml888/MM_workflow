#!/usr/bin/env python3
"""Machine-check results/reproducibility-manifest.json.

PASS is derived from actual files, not self-report: recompute each input/script
SHA-256 and compare to what the manifest claims. A mismatched or missing hash is a
hard FAIL (the manifest was not derived from the real files). Output is ASCII-only
to avoid Windows console encoding issues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path


REQUIRED_TOP = {"project", "working_directory", "environment", "random_seeds", "inputs", "scripts"}
REQUIRED_INPUT = {"file", "sha256"}
REQUIRED_SCRIPT = {"name", "sha256", "command", "inputs", "outputs", "exit_code"}


def _ascii(value: object) -> str:
    # 保留可打印的中文/符号，仅对不可打印/控制字符转义（配合 UTF-8 输出保护，避免报错信息变成 \uXXXX）
    return "".join(ch if ch.isprintable() else ("\\u%04x" % ord(ch)) for ch in str(value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(root: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"manifest not found: {manifest_path}")
        return errors
    except json.JSONDecodeError as exc:
        errors.append(f"manifest is not valid JSON: {exc}")
        return errors
    if not isinstance(data, dict):
        errors.append("manifest root must be an object")
        return errors

    if data.get("schema_version") != "2.0":
        errors.append("schema_version must be '2.0'")
    for field in REQUIRED_TOP:
        if field not in data or data.get(field) in (None, ""):
            errors.append(f"missing field: {field}")

    env = data.get("environment")
    if isinstance(env, dict):
        for field in ("os", "python_version", "dependency_lock"):
            if not env.get(field):
                errors.append(f"environment missing field: {field}")

    inputs = data.get("inputs")
    if not isinstance(inputs, list):
        errors.append("inputs must be an array")
        inputs = []
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            errors.append(f"inputs[{index}] must be an object")
            continue
        for field in REQUIRED_INPUT:
            if not item.get(field):
                errors.append(f"inputs[{index}] missing {field}")
        rel = item.get("file")
        if rel and not (root / rel).exists():
            errors.append(f"inputs[{index}].file missing: {rel}")
        rec = item.get("sha256")
        if rec and rel and (root / rel).exists():
            actual = sha256(root / rel)
            if actual != rec:
                errors.append(f"inputs[{index}] SHA-256 mismatch: {rel} (claimed {rec[:12]}, actual {actual[:12]})")

    scripts = data.get("scripts")
    if not isinstance(scripts, list):
        errors.append("scripts must be an array")
        scripts = []
    for index, item in enumerate(scripts):
        if not isinstance(item, dict):
            errors.append(f"scripts[{index}] must be an object")
            continue
        for field in REQUIRED_SCRIPT:
            if item.get(field) in (None, ""):
                errors.append(f"scripts[{index}] missing {field}")
        rel = item.get("name")
        if rel and not (root / rel).exists():
            errors.append(f"scripts[{index}].name missing: {rel}")
        rec = item.get("sha256")
        if rec and rel and (root / rel).exists():
            actual = sha256(root / rel)
            if actual != rec:
                errors.append(f"scripts[{index}] SHA-256 mismatch: {rel} (claimed {rec[:12]}, actual {actual[:12]})")
        for out in item.get("outputs", []):
            if out and not (root / out).exists():
                errors.append(f"scripts[{index}] output missing: {out}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="machine-check reproducibility manifest")
    parser.add_argument("manifest", nargs="?", default="results/复现清单.json")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    manifest_path = root / args.manifest
    errors = check(root, manifest_path)
    if errors:
        print("reproducibility check: FAIL")
        for error in errors:
            print("- " + _ascii(error))
        return 1
    print("reproducibility check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
