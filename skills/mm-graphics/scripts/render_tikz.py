#!/usr/bin/env python3
"""Compile a standalone TikZ figure and render a metadata-correct PNG."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def find_tool(name: str, explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return str(path)
        raise FileNotFoundError(f"Tool not found: {path}")

    # ① PATH（Git Bash / 系统 PATH）
    found = shutil.which(name)
    if found:
        return found

    # ② 穷举本机常见 TeX 发行版安装位置（按优先级）
    candidates = []
    if os.name == "nt":
        # 用户机器已知安装位置（最高优先，优先命中；即使 PATH/LOCALAPPDATA 异常也能找到）
        known = [
            r"C:\Users\32530\AppData\Local\Programs\MiKTeX",
            r"C:\Program Files\MiKTeX",
            r"C:\Program Files (x86)\MiKTeX",
        ]
        local = os.environ.get("LOCALAPPDATA")
        prog = os.environ.get("ProgramFiles")
        prog_x86 = os.environ.get("ProgramFiles(x86)")
        if local:
            known.insert(1, str(Path(local) / "Programs" / "MiKTeX"))
        if prog:
            known.append(str(Path(prog) / "MiKTeX"))
        if prog_x86:
            known.append(str(Path(prog_x86) / "MiKTeX"))
        # 每个根目录下穷举 MiKTeX bin 相对路径（find_tool 会自动拼 name.exe）
        miktex_rel = [
            "miktex/bin/x64",
            "miktex/bin",
            "bin/x64",
            "bin",
        ]
        for base in known:
            for rel in miktex_rel:
                candidates.append(Path(base) / rel / f"{name}.exe")

        # TeX Live 常见位置（texlive/<年>/bin/windows）
        texlive_root = Path(prog) / "texlive" if prog else None
        if texlive_root and texlive_root.is_dir():
            for year_dir in texlive_root.iterdir():
                if year_dir.is_dir() and (year_dir / "bin" / "windows").is_dir():
                    candidates.append((year_dir / "bin" / "windows") / f"{name}.exe")

    for cand in candidates:
        if cand.is_file():
            return str(cand)

    # ③ 找不到：提示如何定位已装的发行版，而不是诱导去下载/安装。
    raise FileNotFoundError(
        f"找不到 {name}。请先确认本机已安装 MiKTeX/TeX Live，并把该发行版的 bin 目录加入 PATH，"
        f"或把 {name}.exe 的完整路径通过 --xelatex/--pdftocairo 传入。"
        f"不要擅自下载或安装新的 TeX 发行版；工作流默认复用本机已有的 MiKTeX/TeX Live。"
    )


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(command) + "\n" + result.stdout)
    return result.stdout


def read_png(path: Path) -> tuple[int, int, float | None, float | None]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a PNG file: {path}")
        width = height = None
        dpi_x = dpi_y = None
        while True:
            raw_length = handle.read(4)
            if not raw_length:
                break
            length = struct.unpack(">I", raw_length)[0]
            chunk_type = handle.read(4)
            data = handle.read(length)
            handle.read(4)
            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", data[:8])
            elif chunk_type == b"pHYs" and len(data) == 9:
                x_ppm, y_ppm, unit = struct.unpack(">IIB", data)
                if unit == 1:
                    dpi_x = x_ppm * 0.0254
                    dpi_y = y_ppm * 0.0254
            elif chunk_type == b"IEND":
                break
    if width is None or height is None:
        raise ValueError(f"PNG has no IHDR chunk: {path}")
    return width, height, dpi_x, dpi_y


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tex", type=Path)
    parser.add_argument("--png", type=Path)
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--xelatex")
    parser.add_argument("--pdftocairo")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    tex = args.tex.expanduser().resolve()
    if not tex.is_file():
        raise FileNotFoundError(tex)
    if tex.suffix.lower() != ".tex":
        raise ValueError("Input must be a .tex file")

    xelatex = find_tool("xelatex", args.xelatex)
    pdftocairo = find_tool("pdftocairo", args.pdftocairo)
    compile_output = run(
        [xelatex, "-interaction=nonstopmode", "-halt-on-error", tex.name], tex.parent
    )

    pdf = tex.with_suffix(".pdf")
    log = tex.with_suffix(".log")
    if not pdf.is_file():
        raise RuntimeError(f"XeLaTeX did not create {pdf}")

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else compile_output
    forbidden = ["LaTeX Error", "Undefined control sequence", "Missing character"]
    if args.strict:
        forbidden.append("Overfull \\hbox")
    hits = [token for token in forbidden if token in log_text]
    if hits:
        raise RuntimeError("LaTeX log failed checks: " + ", ".join(hits))

    png = (args.png or tex.with_name(tex.stem + "_600dpi.png")).expanduser().resolve()
    png.parent.mkdir(parents=True, exist_ok=True)
    output_stem = png.with_suffix("")
    run(
        [
            pdftocairo,
            "-png",
            "-singlefile",
            "-r",
            str(args.dpi),
            str(pdf),
            str(output_stem),
        ],
        tex.parent,
    )
    if not png.is_file():
        raise RuntimeError(f"pdftocairo did not create {png}")

    width, height, dpi_x, dpi_y = read_png(png)
    if args.strict:
        if dpi_x is None or dpi_y is None:
            raise RuntimeError("PNG has no physical-resolution metadata")
        tolerance = max(1.0, args.dpi * 0.01)
        if abs(dpi_x - args.dpi) > tolerance or abs(dpi_y - args.dpi) > tolerance:
            raise RuntimeError(f"Unexpected PNG DPI: {dpi_x:.3f} x {dpi_y:.3f}")

    width_cm = width / (dpi_x or args.dpi) * 2.54
    height_cm = height / (dpi_y or args.dpi) * 2.54
    print(f"PDF: {pdf}")
    print(f"PNG: {png}")
    print(f"Pixels: {width} x {height}")
    print(f"DPI: {(dpi_x or args.dpi):.3f} x {(dpi_y or args.dpi):.3f}")
    print(f"Physical size: {width_cm:.2f} x {height_cm:.2f} cm")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
