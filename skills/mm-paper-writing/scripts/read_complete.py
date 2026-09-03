#!/usr/bin/env python3
"""Plan, emit, and verify complete reads for mm-paper-writing."""

from __future__ import annotations

import argparse
import os
import hashlib
import json
import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = SKILL_ROOT / "references" / "writing-order.json"
HEADING_RE = re.compile(r"^#{2,3}\s+(.+?)\s*$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def strict_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"invalid UTF-8: {path}: {exc}") from exc
    bad = [ch for ch in text if (ord(ch) < 32 and ch not in "\t\r\n") or ord(ch) == 127]
    if bad:
        codes = ", ".join(f"U+{ord(ch):04X}" for ch in sorted(set(bad)))
        raise ValueError(f"control characters found in {path}: {codes}")
    return data, text


def load_registry() -> dict:
    _, text = strict_text(REGISTRY_PATH)
    registry = json.loads(text)
    required = registry.get("required_before_writing")
    if not isinstance(required, list) or not required:
        raise ValueError("required_before_writing must be a non-empty list")
    paper_order = registry.get("paper_order")
    writing_order = registry.get("writing_order")
    expected_chapters = [
        "references/chapters/00-摘要.md",
        "references/chapters/01-问题重述.md",
        "references/chapters/02-问题分析.md",
        "references/chapters/03-模型假设.md",
        "references/chapters/04-符号说明.md",
        "references/chapters/05-模型的建立与求解.md",
        "references/chapters/06-模型评价与推广.md",
        "references/chapters/07-AI使用声明.md",
        "references/chapters/08-参考文献.md",
        "references/chapters/09-附录.md",
    ]
    if paper_order != expected_chapters:
        raise ValueError("paper_order must match the fixed ten-part paper order")
    if not isinstance(writing_order, list) or sorted(writing_order) != sorted(expected_chapters):
        raise ValueError("writing_order must contain each fixed chapter exactly once")
    if writing_order[-1] != "references/chapters/00-摘要.md":
        raise ValueError("abstract must be last in writing_order")
    if registry.get("abstract_must_be_written_last") is not True:
        raise ValueError("abstract_must_be_written_last must be true")
    reread = registry.get("reread_before_writing")
    if not isinstance(reread, dict) or sorted(reread.values()) != sorted(expected_chapters):
        raise ValueError("reread_before_writing must cover every chapter exactly once")
    return registry


def resolve_relative(relative: str) -> Path:
    path = (SKILL_ROOT / relative).resolve()
    if not path.is_file():
        raise ValueError(f"required file does not exist: {relative} -> {path}")
    return path


def _ledger_path(path: Path) -> Path:
    return path.resolve()


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": "1.0", "reads": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"ledger is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("ledger root must be an object")
    reads = data.get("reads")
    if not isinstance(reads, list):
        raise ValueError("ledger.reads must be a list")
    return data


def save_ledger(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_read(path: Path, relative: str, start: int, end: int, sha256: str) -> None:
    data = load_ledger(path)
    entry = {"path": relative, "start": start, "end": end, "sha256": sha256,
             "end_marker_seen": True}
    key = lambda r: (r.get("path"), r.get("start"), r.get("end"))
    reads = [r for r in data["reads"] if not (r.get("path") == relative and r.get("start") == start and r.get("end") == end)]
    reads.append(entry)
    reads.sort(key=lambda r: (str(r.get("path")), int(r.get("start", 0))))
    data["reads"] = reads
    save_ledger(path, data)


def ledger_reads(ledger: dict) -> set:
    out = set()
    for r in ledger.get("reads", []):
        out.add((str(r.get("path")), int(r.get("start")), int(r.get("end"))))
    return out


def expected_paths(registry: dict) -> list[str]:
    paths = list(registry["required_before_writing"])
    registry_rel = "references/writing-order.json"
    if registry_rel not in paths:
        paths.append(registry_rel)
    if "SKILL.md" not in paths:
        paths.insert(0, "SKILL.md")
    if len(paths) != len(set(paths)):
        raise ValueError("required reading list contains duplicate paths")
    return paths


def analyze_path(path: Path, chunk_limit: int) -> dict:
    data, text = strict_text(path)
    lines = text.splitlines()
    headings = [match.group(1) for line in lines if (match := HEADING_RE.match(line))]
    chunks: list[dict] = []
    start = 1
    used = 0
    for index, line in enumerate(lines, start=1):
        line_bytes = len((line + "\n").encode("utf-8"))
        if index > start and used + line_bytes > chunk_limit:
            chunks.append({"start": start, "end": index - 1})
            start = index
            used = 0
        used += line_bytes
    if lines:
        chunks.append({"start": start, "end": len(lines)})
    return {
        "path": str(path),
        "resolved_path": str(path),
        "bytes": len(data),
        "lines": len(lines),
        "sha256": digest(data),
        "headings": headings,
        "chunks": chunks,
    }


def analyze(relative: str, chunk_limit: int) -> dict:
    item = analyze_path(resolve_relative(relative), chunk_limit)
    item["path"] = relative
    return item


def build_plan() -> dict:
    registry = load_registry()
    limit = int(registry.get("limits", {}).get("chunk_max_bytes", 7000))
    files = [analyze(relative, limit) for relative in expected_paths(registry)]
    skill_limit = int(registry.get("limits", {}).get("skill_max_bytes", 12000))
    module_limit = int(registry.get("limits", {}).get("module_max_bytes", 20000))
    for item in files:
        allowed = skill_limit if item["path"] == "SKILL.md" else module_limit
        if item["bytes"] > allowed:
            raise ValueError(f"file exceeds registered size limit: {item['path']} {item['bytes']} > {allowed}")
    return {
        "schema_version": "1.0",
        "registry_sha256": digest(REGISTRY_PATH.read_bytes()),
        "chunk_max_bytes": limit,
        "files": files,
    }


def command_plan(_: argparse.Namespace) -> int:
    print(json.dumps(build_plan(), ensure_ascii=False, indent=2))
    return 0


def command_analyze(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"file does not exist: {path}")
    print(json.dumps(analyze_path(path, args.chunk_bytes), ensure_ascii=False, indent=2))
    return 0


def command_chunk(args: argparse.Namespace) -> int:
    plan = build_plan()
    allowed = {item["path"]: item for item in plan["files"]}
    if args.path not in allowed:
        raise ValueError(f"path is not registered as required reading: {args.path}")
    item = allowed[args.path]
    if args.start < 1 or args.end < args.start or args.end > item["lines"]:
        raise ValueError(f"invalid range {args.start}-{args.end} for {args.path} ({item['lines']} lines)")
    _, text = strict_text(resolve_relative(args.path))
    lines = text.splitlines()
    print(f"READ-BEGIN path={args.path} range={args.start}-{args.end} sha256={item['sha256']}")
    for number in range(args.start, args.end + 1):
        print(f"{number:04d}: {lines[number - 1]}")
    print(f"READ-END path={args.path} range={args.start}-{args.end} sha256={item['sha256']}")
    if getattr(args, "session", None):
        record_read(Path(args.session), args.path, args.start, args.end, item["sha256"])
    return 0


def command_write_receipt(args: argparse.Namespace) -> int:
    """从读取账本生成回执；账本必须覆盖全部必读文件的所有分块。"""
    plan = build_plan()
    session = Path(args.session)
    ledger = load_ledger(session)
    reads = ledger_reads(ledger)
    expected = set()
    for item in plan["files"]:
        for chunk in item["chunks"]:
            expected.add((item["path"], chunk["start"], chunk["end"]))
    missing = sorted(expected - reads)
    if missing:
        raise ValueError(f"ledger is incomplete; missing {len(missing)} chunk(s): "
                         + ", ".join(f"{p} [{s}-{e}]" for p, s, e in missing[:10]))
    receipt = {
        "schema_version": "1.0",
        "pass": args.pass_number,
        "registry_sha256": plan["registry_sha256"],
        "ledger_sha256": digest(session.read_bytes()),
        "files": [],
    }
    for item in plan["files"]:
        chunks = [dict(c, end_marker_seen=True) for c in item["chunks"]]
        receipt["files"].append({
            "path": item["path"],
            "sha256": item["sha256"],
            "headings_seen": item["headings"],
            "chunks": chunks,
        })
    out = Path(args.receipt)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "written", "receipt": str(out),
                      "ledger": str(session), "files": len(plan["files"])}, ensure_ascii=False))
    return 0


def command_template(args: argparse.Namespace) -> int:
    plan = build_plan()
    receipt = {
        "schema_version": "1.0",
        "pass": args.pass_number,
        "registry_sha256": plan["registry_sha256"],
        "files": [],
    }
    for item in plan["files"]:
        receipt["files"].append(
            {
                "path": item["path"],
                "sha256": item["sha256"],
                "headings_seen": item["headings"],
                "chunks": [dict(chunk, end_marker_seen=False) for chunk in item["chunks"]],
            }
        )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    plan = build_plan()
    receipt_path = Path(args.receipt).resolve()
    _, receipt_text = strict_text(receipt_path)
    receipt = json.loads(receipt_text)
    if receipt.get("pass") not in (1, 2):
        raise ValueError("receipt pass must be 1 or 2")
    if receipt.get("registry_sha256") != plan["registry_sha256"]:
        raise ValueError("receipt registry hash does not match current registry")
    session = Path(args.session).resolve()
    if not session.exists():
        raise ValueError(f"read session ledger missing: {session}. "
                         "Every chunk must be read via `read_complete.py chunk --session` before verifying.")
    ledger = load_ledger(session)
    ledger_sha = digest(session.read_bytes())
    if receipt.get("ledger_sha256") != ledger_sha:
        raise ValueError("receipt ledger hash does not match the session ledger; "
                         "receipt must be produced by `read_complete.py write-receipt` from that ledger")
    expected_chunks: set = set()
    for item in plan["files"]:
        for chunk in item["chunks"]:
            expected_chunks.add((item["path"], chunk["start"], chunk["end"]))
    reads = ledger_reads(ledger)
    unread = sorted(expected_chunks - reads)
    if unread:
        raise ValueError(f"session ledger is missing {len(unread)} required chunk(s): "
                         + ", ".join(f"{p} [{s}-{e}]" for p, s, e in unread[:10]))
    expected = {item["path"]: item for item in plan["files"]}
    actual_list = receipt.get("files")
    if not isinstance(actual_list, list):
        raise ValueError("receipt files must be a list")
    actual = {item.get("path"): item for item in actual_list}
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise ValueError(f"receipt file set mismatch; missing={missing}, extra={extra}")
    for relative, expected_item in expected.items():
        item = actual[relative]
        if item.get("sha256") != expected_item["sha256"]:
            raise ValueError(f"hash mismatch in receipt: {relative}")
        if item.get("headings_seen") != expected_item["headings"]:
            raise ValueError(f"heading coverage mismatch: {relative}")
        chunks = item.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise ValueError(f"missing chunks: {relative}")
        cursor = 1
        for chunk in chunks:
            if chunk.get("start") != cursor:
                raise ValueError(f"gap or overlap in {relative} before line {cursor}")
            if chunk.get("end_marker_seen") is not True:
                raise ValueError(f"READ-END not confirmed for {relative} {chunk.get('start')}-{chunk.get('end')}")
            end = chunk.get("end")
            if not isinstance(end, int) or end < cursor:
                raise ValueError(f"invalid chunk end in {relative}")
            cursor = end + 1
        if cursor != expected_item["lines"] + 1:
            raise ValueError(f"receipt does not reach EOF for {relative}")
    print(json.dumps({"status": "pass", "pass": receipt["pass"], "files": len(expected)}, ensure_ascii=False))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.set_defaults(func=command_plan)
    analyze_cmd = sub.add_parser("analyze", help="plan chunks for any file, not just registered ones")
    analyze_cmd.add_argument("--path", required=True)
    analyze_cmd.add_argument("--chunk-bytes", type=int, default=7000)
    analyze_cmd.set_defaults(func=command_analyze)
    chunk = sub.add_parser("chunk")
    chunk.add_argument("--path", required=True)
    chunk.add_argument("--start", required=True, type=int)
    chunk.add_argument("--end", required=True, type=int)
    chunk.add_argument("--session", default=None, help="append proof to this read-session ledger")
    chunk.set_defaults(func=command_chunk)
    template = sub.add_parser("template")
    template.add_argument("--pass", dest="pass_number", required=True, type=int, choices=(1, 2))
    template.set_defaults(func=command_template)
    wr = sub.add_parser("write-receipt")
    wr.add_argument("--pass", dest="pass_number", required=True, type=int, choices=(1, 2))
    wr.add_argument("--receipt", required=True)
    wr.add_argument("--session", required=True)
    wr.set_defaults(func=command_write_receipt)
    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--session", required=True, help="read-session ledger used to prove chunks were read")
    verify.set_defaults(func=command_verify)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"READ-COMPLETE FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
