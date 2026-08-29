#!/usr/bin/env python3
"""Validate a CUMCM project-manifest.json without project dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ORDINARY_STATUSES = {"pending", "in_progress", "complete", "failed", "n_a"}
VERIFICATION_STATUSES = ORDINARY_STATUSES | {"conditional"}
STAGE_NAMES = {
    "analysis", "modeling", "coding", "figures", "diagrams", "visual",
    "paper_draft", "paper_final", "verification",
}
ID_ARRAYS = {
    "requirements", "problems", "datasets", "assumptions", "model_candidates",
    "selected_models", "implemented_models", "validation_plans", "symbols",
    "results", "figures",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "2.0":
        fail(errors, "schema_version must be '2.0'")
    if manifest.get("competition") != "CUMCM-2026":
        fail(errors, "competition must be 'CUMCM-2026'")
    if not isinstance(manifest.get("project"), dict):
        fail(errors, "project must be an object")

    stages = manifest.get("stages")
    if not isinstance(stages, dict):
        fail(errors, "stages must be an object")
    else:
        missing = STAGE_NAMES - stages.keys()
        for name in sorted(missing):
            fail(errors, f"stages.{name} is missing")
        for name, stage in stages.items():
            if name not in STAGE_NAMES:
                continue
            if not isinstance(stage, dict):
                fail(errors, f"stages.{name} must be an object")
                continue
            status = stage.get("status")
            allowed = VERIFICATION_STATUSES if name == "verification" else ORDINARY_STATUSES
            if status not in allowed:
                fail(errors, f"stages.{name}.status '{status}' is invalid")

    seen_ids: dict[str, str] = {}
    for field in ID_ARRAYS:
        value = manifest.get(field)
        if not isinstance(value, list):
            fail(errors, f"{field} must be an array")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                fail(errors, f"{field}[{index}].id is required")
                continue
            item_id = item["id"]
            previous = seen_ids.get(item_id)
            if previous:
                fail(errors, f"duplicate stable id {item_id!r} in {previous} and {field}[{index}]")
            else:
                seen_ids[item_id] = f"{field}[{index}]"

    for field in ("artifacts", "paper_gates", "rework", "change_log"):
        if not isinstance(manifest.get(field), list):
            fail(errors, f"{field} must be an array")

    gates = manifest.get("paper_gates", [])
    if isinstance(gates, list):
        valid_gates = {"G-1", "G-2", "G-3", "G-4", "G-5"}
        for index, gate in enumerate(gates):
            if not isinstance(gate, dict):
                fail(errors, f"paper_gates[{index}] must be an object")
                continue
            if gate.get("gate") not in valid_gates:
                fail(errors, f"paper_gates[{index}].gate is invalid")
            if gate.get("status") not in {"pending", "pass", "fail"}:
                fail(errors, f"paper_gates[{index}].status is invalid")

    rework = manifest.get("rework", [])
    if isinstance(rework, list):
        for index, item in enumerate(rework):
            if not isinstance(item, dict):
                fail(errors, f"rework[{index}] must be an object")
                continue
            if item.get("severity") not in {"critical", "major", "minor"}:
                fail(errors, f"rework[{index}].severity is invalid")
            if item.get("status") not in {"open", "resolved", "superseded"}:
                fail(errors, f"rework[{index}].status is invalid")

    verification = stages.get("verification") if isinstance(stages, dict) else None
    if isinstance(verification, dict) and verification.get("status") in {"complete", "conditional"}:
        open_blockers = [
            item for item in rework
            if isinstance(item, dict)
            and item.get("status") == "open"
            and item.get("severity") in {"critical", "major"}
        ]
        if open_blockers:
            fail(errors, "verification cannot pass while critical or major rework items are open")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default="project-manifest.json")
    parser.add_argument("--schema", default=None, help="Optional JSON Schema path")
    args = parser.parse_args()
    path = Path(args.manifest)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: manifest not found: {path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(manifest, dict):
        print("ERROR: manifest root must be an object", file=sys.stderr)
        return 2

    errors = validate(manifest)
    schema_path = Path(args.schema) if args.schema else Path(__file__).resolve().parents[1] / "project-manifest.schema.json"
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema is not None and schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors.extend(str(error.message) for error in jsonschema.Draft202012Validator(schema).iter_errors(manifest))

    if errors:
        print("manifest validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    mode = "JSON Schema + stdlib" if jsonschema is not None and schema_path.exists() else "stdlib checks"
    print(f"manifest validation: PASS ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
