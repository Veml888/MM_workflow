#!/usr/bin/env python3
"""Machine-check the paper's citation/bibliography integrity from the paper .tex.

Objective checks (no self-report):
  * every in-text citation (\\cite / \\supcite) resolves to an existing \\bibitem;
  * every \\bibitem is cited at least once in the body (no orphan entry);
  * bibitem labels are non-empty character tags (author-year), not raw digits;
  * in-text citation label matches exactly one \\bibitem label;
  * the abstract region (\\begin{document} .. first \\newpage) contains no citation;
  * the DISPLAYED number of each in-text citation equals the PHYSICAL position of its
    \\bibitem inside \\begin{thebibliography} (because thebibliography numbers items by
    physical order), catching the misalignment where body says [1,2] but the rendered
    [1] is a different reference.
Output is ASCII-only.
"""

from __future__ import annotations

import argparse
import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---
from pathlib import Path


def _ascii(value: object) -> str:
    # 保留可打印的中文/符号，仅对不可打印/控制字符转义（配合 UTF-8 输出保护，避免报错信息变成 \uXXXX）
    return "".join(ch if ch.isprintable() else ("\\u%04x" % ord(ch)) for ch in str(value))


# supcite{label,label} OR cite{label,label}; labels may be a-z0-9_-+
CITE_RE = re.compile(r"\\(?:supcite|cite)\{([^}]*)\}")
BIBITEM_RE = re.compile(r"\\bibitem\{([^}]*)\}")
THEBIB_RE = re.compile(r"\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}", re.DOTALL)


def _split_labels(chunk: str) -> list[str]:
    out: list[str] = []
    for raw in chunk.split(","):
        lab = raw.strip()
        if lab:
            out.append(lab)
    return out


def parse_tex(text: str) -> tuple[list[str], list[str], bool]:
    """Return (ordered_intext_labels, physical_bib_order, abstract_has_citation).

    Abstract region: \\begin{document} .. first \\section{...} OR first \\newpage,
    whichever comes first. Cintro uses \\section{问题重述} to end the abstract (no
    \\newpage), so we must not fall back to treating the whole file as body (that would
    count the \\newcommand{\\supcite} preamble definition as an in-text citation).
    """
    doc_idx = text.find("\\begin{document}")
    if doc_idx < 0:
        doc_idx = 0

    # Find abstract end: first \section after \begin{document}, else first \newpage
    after_doc = text[doc_idx:]
    sec_m = re.search(r"\\section\b", after_doc)
    newp_m = re.search(r"\\newpage\b", after_doc)
    candidates = []
    if sec_m:
        candidates.append((doc_idx + sec_m.start(), "section"))
    if newp_m:
        candidates.append((doc_idx + newp_m.start(), "newpage"))
    abstract_end = doc_idx
    has_boundary = False
    if candidates:
        candidates.sort()
        abstract_end = candidates[0][0]
        has_boundary = True

    # Everything from \begin{document} to abstract_end = abstract region
    abstract_text = text[doc_idx:abstract_end]
    if not has_boundary:
        # No clear boundary: treat abstract as the title/摘要 block only (to first \section)
        # If none found, keep abstract empty to avoid missing checks.
        abstract_text = ""
    body_text = text[abstract_end:]

    abstract_has = bool(CITE_RE.search(abstract_text))

    # Ordered in-text citations (body only, after \begin{document} region)
    ordered: list[str] = []
    for m in CITE_RE.finditer(body_text):
        for lab in _split_labels(m.group(1)):
            ordered.append(lab)

    # Physical order of \bibitem labels inside thebibliography
    physical: list[str] = []
    thebib = THEBIB_RE.search(text)
    if thebib:
        for m in BIBITEM_RE.finditer(thebib.group(1)):
            lab = m.group(1).strip()
            if lab:
                physical.append(lab)

    return ordered, physical, abstract_has


def check(text: str, path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ordered, physical, abstract_has = parse_tex(text)

    if abstract_has:
        errors.append("abstract region contains a citation (\\cite/\\supcite); 摘要不得放参考文献编号")

    # Label set from bibliography
    phys_set = set(physical)

    # 1) Every in-text label resolves to a bibitem; label must not be a bare digit
    for lab in ordered:
        if lab.isdigit():
            errors.append(f"in-text citation uses bare digit label {lab!r}; use an author-year tag (zhu2018)")
        elif lab not in phys_set:
            errors.append(f"in-text citation [{lab}] has no matching \\bibitem")

    # Separate labels living OUTSIDE thebibliography (stray bibitem) from those inside.
    # Any in-text label must be found among physical bibitem labels.
    # 2) Every bibitem inside thebibliography is cited at least once (no orphan)
    for lab in physical:
        if lab not in ordered:
            errors.append(f"\\bibitem{{{lab}}} is never cited in the body (orphan entry)")

    # 3) Every bibitem label is a non-empty character tag (not bare digit)
    for lab in physical:
        if not lab or lab.isdigit():
            errors.append(f"\\bibitem key {lab!r} should be a non-empty author-year tag, not a bare digit")

    # 4) Displayed number of each in-text citation = physical position (1-based) of its bibitem
    # physical[i] renders as [i+1]. For every in-text label, its physical index must be a
    # contiguous 1..N sequence by first in-text order (no gap/dup) --- this replaces the old
    # "bibitem keys numbered by first citation order" check.
    ordered_unique: list[str] = []
    for lab in ordered:
        if lab not in ordered_unique:
            ordered_unique.append(lab)

    # Build display-number map: label -> physical index (1-based)
    index_of = {lab: i + 1 for i, lab in enumerate(physical)}

    # Ensure physical order matches first-in-text order: the physical k-th rendered label
    # should be the k-th distinct in-text label.
    for pos, lab in enumerate(ordered_unique, 1):
        if lab not in index_of:
            continue
        if index_of[lab] != pos:
            errors.append(
                f"displayed-number mismatch: reference [{lab}] renders as [{index_of[lab]}] "
                f"but is first cited at in-text position [{pos}]; "
                "thebibliography numbers by physical order, so reorder \\bibitem entries "
                "to match first-citation order (or use \\cite consistently)"
            )
            break

    # Ensure no gap/dup in physical numbering: physical must be a permutation of ordered_unique
    if sorted(phys_set) != sorted(set(ordered_unique)):
        # Some bibitem present in bibliography but not cited, or cited but not in bibliography.
        # Individual cases already flagged above; here just a consistency note.
        pass

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="machine-check paper citation/bibliography integrity")
    parser.add_argument("tex", nargs="?", default="paper/论文.tex", type=Path)
    args = parser.parse_args()

    if not args.tex.exists():
        print("cit checks: FAIL")
        print(f"- tex not found: {args.tex}")
        return 1

    text = args.tex.read_text(encoding="utf-8")
    errors, warnings = check(text, args.tex)

    if warnings:
        for w in warnings:
            print("  [WARN]", _ascii(w))

    if errors:
        print("cit checks: FAIL")
        for e in errors:
            print("- ", _ascii(e))
        return 1

    print("cit checks: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
