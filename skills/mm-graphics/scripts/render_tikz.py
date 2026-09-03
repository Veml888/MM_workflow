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

    found = shutil.which(name)
    if found:
        return found

    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            candidate = (
                Path(local)
                / "Programs"
                / "MiKTeX"
                / "miktex"
                / "bin"
                / "x64"
                / f"{name}.exe"
            )
            if candidate.is_file():
                return str(candidate)

    raise FileNotFoundError(
        f"Cannot locate {name}. Install MiKTeX/TeX Live or pass an explicit path."
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
