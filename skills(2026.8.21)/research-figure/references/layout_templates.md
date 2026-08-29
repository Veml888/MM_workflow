# Layout Templates

Minimal compilable TikZ templates for common pipeline layouts. Each template is a standalone `.tex` file that compiles directly. Choose the template that best matches the pipeline structure, then customize.

## Table of Contents
1. [Linear Horizontal (Left to Right)](#1-linear-horizontal-left-to-right)
2. [Linear Vertical (Top to Bottom)](#2-linear-vertical-top-to-bottom)
3. [Loop / U-Shape (Two Rows)](#3-loop--u-shape-two-rows)
4. [Two Independent Modules](#4-two-independent-modules)
5. [Multi-Branch with Merge](#5-multi-branch-with-merge)
6. [Template Selection Guide](#template-selection-guide)

---

## 1. Linear Horizontal (Left to Right)

Best for: straightforward pipelines with 3-6 stages, the most common layout.

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds, decorations.pathreplacing}

% --- Color Scheme (Blue-Gray) ---
\definecolor{bgPrimary}{HTML}{DAE8FC}
\definecolor{bgSecondary}{HTML}{E8EEF7}
\definecolor{bgAccent}{HTML}{B3CDE3}
\definecolor{bgInput}{HTML}{F0F4F8}
\definecolor{borderPrimary}{HTML}{6C8EBF}
\definecolor{borderAccent}{HTML}{3A6EA5}
\definecolor{arrowColor}{HTML}{4A6A8A}
\definecolor{textMain}{HTML}{2C3E50}
\definecolor{textLight}{HTML}{7F8C8D}
\definecolor{bgHighlight}{HTML}{FFF3CD}

% --- Styles ---
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=2.8cm, minimum height=1.2cm,
    font=\sffamily\small, text=textMain, line width=0.6pt, align=center,
  },
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=2.8cm, minimum height=1.2cm,
    font=\sffamily\small\bfseries, text=textMain, line width=1.0pt, align=center,
  },
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2cm, minimum height=1cm,
    font=\sffamily\small, text=textMain, line width=0.5pt, align=center,
  },
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]}, line width=0.6pt, color=arrowColor,
  },
}

\begin{document}
\begin{tikzpicture}

  % --- Nodes ---
  \node[iobox]      (input)  {Input};
  \node[module,      right=1.0cm of input]  (mod1) {Module 1};
  \node[novelmodule, right=1.0cm of mod1]   (mod2) {\textbf{Module 2}\\[-1pt]{\footnotesize\color{textLight}(Ours)}};
  \node[module,      right=1.0cm of mod2]   (mod3) {Module 3};
  \node[iobox,       right=1.0cm of mod3]   (output) {Output};

  % --- Arrows ---
  \draw[stdarrow] (input) -- (mod1);
  \draw[stdarrow] (mod1)  -- (mod2);
  \draw[stdarrow] (mod2)  -- (mod3);
  \draw[stdarrow] (mod3)  -- (output);

  % --- Arrow labels (optional) ---
  \node[above, font=\sffamily\scriptsize, text=textLight] at ($(mod1)!0.5!(mod2)$) {features};

\end{tikzpicture}
\end{document}
```

---

## 2. Linear Vertical (Top to Bottom)

Best for: narrow column figures, papers with two-column layout where horizontal space is limited.

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usepackage{amssymb}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds}

% --- Color Scheme (Blue-Gray) ---
\definecolor{bgPrimary}{HTML}{DAE8FC}
\definecolor{bgSecondary}{HTML}{E8EEF7}
\definecolor{bgAccent}{HTML}{B3CDE3}
\definecolor{bgInput}{HTML}{F0F4F8}
\definecolor{borderPrimary}{HTML}{6C8EBF}
\definecolor{borderAccent}{HTML}{3A6EA5}
\definecolor{arrowColor}{HTML}{4A6A8A}
\definecolor{textMain}{HTML}{2C3E50}
\definecolor{textLight}{HTML}{7F8C8D}
\definecolor{bgHighlight}{HTML}{FFF3CD}

% --- Styles ---
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=3.5cm, minimum height=1.0cm,
    font=\sffamily\small, text=textMain, line width=0.6pt, align=center,
  },
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=3.5cm, minimum height=1.0cm,
    font=\sffamily\small\bfseries, text=textMain, line width=1.0pt, align=center,
  },
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2.5cm, minimum height=0.8cm,
    font=\sffamily\small, text=textMain, line width=0.5pt, align=center,
  },
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]}, line width=0.6pt, color=arrowColor,
  },
}

\begin{document}
\begin{tikzpicture}

  % --- Nodes (top to bottom) ---
  \node[iobox]      (input)  {Input};
  \node[module,      below=0.7cm of input]  (mod1) {Encoder};
  \node[novelmodule, below=0.7cm of mod1]   (mod2) {\textbf{Our Method}};
  \node[module,      below=0.7cm of mod2]   (mod3) {Decoder};
  \node[iobox,       below=0.7cm of mod3]   (output) {Output};

  % --- Arrows ---
  \draw[stdarrow] (input) -- (mod1);
  \draw[stdarrow] (mod1)  -- (mod2);
  \draw[stdarrow] (mod2)  -- (mod3);
  \draw[stdarrow] (mod3)  -- (output);

  % --- Side labels (optional) ---
  \node[right=0.3cm of mod1, font=\sffamily\scriptsize, text=textLight] {$\mathbf{z} \in \mathbb{R}^{d}$};

\end{tikzpicture}
\end{document}
```

---

## 3. Loop / U-Shape (Two Rows)

Best for: pipelines with feedback, iterative refinement, or cyclic processes. Top row goes left-to-right, bottom row goes right-to-left.

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds}

% --- Color Scheme (Blue-Gray) ---
\definecolor{bgPrimary}{HTML}{DAE8FC}
\definecolor{bgSecondary}{HTML}{E8EEF7}
\definecolor{bgAccent}{HTML}{B3CDE3}
\definecolor{bgInput}{HTML}{F0F4F8}
\definecolor{borderPrimary}{HTML}{6C8EBF}
\definecolor{borderAccent}{HTML}{3A6EA5}
\definecolor{arrowColor}{HTML}{4A6A8A}
\definecolor{textMain}{HTML}{2C3E50}
\definecolor{textLight}{HTML}{7F8C8D}
\definecolor{bgHighlight}{HTML}{FFF3CD}

% --- Styles ---
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=2.8cm, minimum height=1.1cm,
    font=\sffamily\small, text=textMain, line width=0.6pt, align=center,
  },
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=2.8cm, minimum height=1.1cm,
    font=\sffamily\small\bfseries, text=textMain, line width=1.0pt, align=center,
  },
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2cm, minimum height=0.9cm,
    font=\sffamily\small, text=textMain, line width=0.5pt, align=center,
  },
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]}, line width=0.6pt, color=arrowColor,
  },
}

\begin{document}
\begin{tikzpicture}

  % --- Top row (left to right): forward pass ---
  \node[iobox]      (input) {Input};
  \node[module,      right=0.8cm of input] (enc) {Encoder};
  \node[novelmodule, right=0.8cm of enc]   (core) {\textbf{Core Module}};
  \node[module,      right=0.8cm of core]  (dec) {Decoder};

  % --- Bottom row (right to left): refinement / feedback ---
  \node[module, below=1.5cm of dec]  (refine)  {Refinement};
  \node[module, below=1.5cm of core] (update)  {Update};
  \node[iobox,  below=1.5cm of enc]  (output)  {Output};

  % --- Top row arrows ---
  \draw[stdarrow] (input) -- (enc);
  \draw[stdarrow] (enc)   -- (core);
  \draw[stdarrow] (core)  -- (dec);

  % --- Turn: top-right to bottom-right ---
  \draw[stdarrow] (dec.south) -- (refine.north);

  % --- Bottom row arrows (right to left) ---
  \draw[stdarrow] (refine) -- (update);
  \draw[stdarrow] (update) -- (output);

  % --- Feedback arrow (bottom to top, optional) ---
  \draw[stdarrow, dashed] (update.north) -- node[right, font=\sffamily\scriptsize, text=textLight] {feedback} (core.south);

\end{tikzpicture}
\end{document}
```

---

## 4. Two Independent Modules

Best for: methods with two separate sub-networks or stages shown side by side, each with its own sub-pipeline.

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds, decorations.pathreplacing}

% --- Color Scheme (Blue-Gray) ---
\definecolor{bgPrimary}{HTML}{DAE8FC}
\definecolor{bgSecondary}{HTML}{E8EEF7}
\definecolor{bgAccent}{HTML}{B3CDE3}
\definecolor{bgInput}{HTML}{F0F4F8}
\definecolor{borderPrimary}{HTML}{6C8EBF}
\definecolor{borderAccent}{HTML}{3A6EA5}
\definecolor{arrowColor}{HTML}{4A6A8A}
\definecolor{textMain}{HTML}{2C3E50}
\definecolor{textLight}{HTML}{7F8C8D}
\definecolor{bgHighlight}{HTML}{FFF3CD}

% --- Styles ---
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=2.5cm, minimum height=1.0cm,
    font=\sffamily\small, text=textMain, line width=0.6pt, align=center,
  },
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=2.5cm, minimum height=1.0cm,
    font=\sffamily\small\bfseries, text=textMain, line width=1.0pt, align=center,
  },
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2cm, minimum height=0.8cm,
    font=\sffamily\small, text=textMain, line width=0.5pt, align=center,
  },
  groupbox/.style={
    draw=borderPrimary, fill=bgSecondary, fill opacity=0.3,
    rounded corners=6pt, inner sep=10pt, line width=0.5pt, dashed,
  },
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]}, line width=0.6pt, color=arrowColor,
  },
}

\begin{document}
\begin{tikzpicture}

  % === Stage A (top) ===
  \node[iobox]      (inA) {Input A};
  \node[module, right=0.8cm of inA]      (a1) {Process A1};
  \node[novelmodule, right=0.8cm of a1]  (a2) {\textbf{Method A2}};
  \node[iobox, right=0.8cm of a2]        (outA) {Output A};

  \draw[stdarrow] (inA) -- (a1);
  \draw[stdarrow] (a1) -- (a2);
  \draw[stdarrow] (a2) -- (outA);

  % Group box for Stage A
  \begin{scope}[on background layer]
    \node[groupbox, fit=(inA)(a1)(a2)(outA),
      label={[font=\sffamily\footnotesize\bfseries, text=textMain]above:Stage A}] {};
  \end{scope}

  % === Stage B (bottom) ===
  \node[iobox, below=2.0cm of inA]        (inB) {Input B};
  \node[module, right=0.8cm of inB]       (b1) {Process B1};
  \node[novelmodule, right=0.8cm of b1]   (b2) {\textbf{Method B2}};
  \node[iobox, right=0.8cm of b2]         (outB) {Output B};

  \draw[stdarrow] (inB) -- (b1);
  \draw[stdarrow] (b1) -- (b2);
  \draw[stdarrow] (b2) -- (outB);

  % Group box for Stage B
  \begin{scope}[on background layer]
    \node[groupbox, fit=(inB)(b1)(b2)(outB),
      label={[font=\sffamily\footnotesize\bfseries, text=textMain]above:Stage B}] {};
  \end{scope}

  % === Optional connection between stages ===
  \draw[stdarrow, dashed, rounded corners=4pt]
    (outA.south) -- ++(0, -1.0cm)
    -| node[near start, right, font=\sffamily\scriptsize, text=textLight] {shared} (inB.north);

\end{tikzpicture}
\end{document}
```

---

## 5. Multi-Branch with Merge

Best for: pipelines with parallel branches (e.g., multi-modal input, multi-scale features) that merge later.

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds}

% --- Color Scheme (Blue-Gray) ---
\definecolor{bgPrimary}{HTML}{DAE8FC}
\definecolor{bgSecondary}{HTML}{E8EEF7}
\definecolor{bgAccent}{HTML}{B3CDE3}
\definecolor{bgInput}{HTML}{F0F4F8}
\definecolor{borderPrimary}{HTML}{6C8EBF}
\definecolor{borderAccent}{HTML}{3A6EA5}
\definecolor{arrowColor}{HTML}{4A6A8A}
\definecolor{textMain}{HTML}{2C3E50}
\definecolor{textLight}{HTML}{7F8C8D}
\definecolor{bgHighlight}{HTML}{FFF3CD}

% --- Styles ---
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=2.5cm, minimum height=1.0cm,
    font=\sffamily\small, text=textMain, line width=0.6pt, align=center,
  },
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=2.5cm, minimum height=1.0cm,
    font=\sffamily\small\bfseries, text=textMain, line width=1.0pt, align=center,
  },
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2cm, minimum height=0.8cm,
    font=\sffamily\small, text=textMain, line width=0.5pt, align=center,
  },
  plusnode/.style={
    circle, draw=borderPrimary, fill=bgSecondary,
    inner sep=0pt, minimum size=16pt,
    font=\sffamily\scriptsize\bfseries, text=textMain, line width=0.5pt,
  },
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]}, line width=0.6pt, color=arrowColor,
  },
}

\begin{document}
\begin{tikzpicture}

  % --- Input ---
  \node[iobox] (input) {Input};

  % --- Branch A (top) ---
  \node[module, above right=0.6cm and 1.2cm of input] (brA) {Branch A};
  \node[module, right=0.8cm of brA] (procA) {Process A};

  % --- Branch B (bottom) ---
  \node[module, below right=0.6cm and 1.2cm of input] (brB) {Branch B};
  \node[module, right=0.8cm of brB] (procB) {Process B};

  % --- Merge ---
  % Place merge node at x = procA.east + 0.8cm, y = midpoint of procA and procB
  \coordinate (midY) at ($(procA.center)!0.5!(procB.center)$);
  \coordinate (mergeX) at ($(procA.east)+(0.8cm, 0)$);
  \node[plusnode] (merge) at (mergeX |- midY) {$+$};

  % --- Post-merge ---
  \node[novelmodule, right=0.8cm of merge] (fuse) {\textbf{Fusion}};
  \node[iobox, right=0.8cm of fuse] (output) {Output};

  % --- Arrows ---
  \draw[stdarrow, rounded corners=4pt] (input.east) -- ++(0.25cm, 0) |- (brA.west);
  \draw[stdarrow, rounded corners=4pt] (input.east) -- ++(0.25cm, 0) |- (brB.west);
  \draw[stdarrow] (brA)  -- (procA);
  \draw[stdarrow] (brB)  -- (procB);
  \draw[stdarrow, rounded corners=4pt] (procA.east) -- ++(0.25cm, 0) |- (merge.155);
  \draw[stdarrow, rounded corners=4pt] (procB.east) -- ++(0.25cm, 0) |- (merge.205);
  \draw[stdarrow] (merge) -- (fuse);
  \draw[stdarrow] (fuse) -- (output);

\end{tikzpicture}
\end{document}
```

---

## Template Selection Guide

| Pipeline Structure | Template | When to Use |
|---|---|---|
| A → B → C → D | Linear Horizontal | Most common. Simple sequential pipeline |
| Top-down sequence | Linear Vertical | Narrow figures, single-column constraints |
| Forward + feedback | Loop / U-Shape | Iterative methods, GAN training loops, RL |
| Two separate stages | Two Independent | Multi-stage methods (e.g., train then infer) |
| Parallel branches | Multi-Branch | Multi-modal, multi-scale, ensemble methods |

### Combining Templates
For complex methods, combine templates:
- Use **Linear Horizontal** as the top-level structure, with each "module" being a group box containing a **Linear Vertical** sub-pipeline.
- Use **Multi-Branch** for the first half and **Linear Horizontal** for the second half after merging.
- Embed a **Loop** within one stage of a **Two Independent** layout.
