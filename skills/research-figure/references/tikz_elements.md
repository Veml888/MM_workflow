# TikZ Elements Library

Reusable TikZ code snippets for constructing method pipeline figures. All snippets assume the color scheme variables from `color_schemes.md` are defined.

## Table of Contents
1. [Required Packages](#required-packages)
2. [Module Box Styles](#module-box-styles)
3. [Connection Styles](#connection-styles)
4. [2D Visualization Elements](#2d-visualization-elements)
5. [Annotation Elements](#annotation-elements)
6. [Common Node Positioning Patterns](#common-node-positioning-patterns)

---

## Required Packages

Include these in your preamble:

```latex
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{
  positioning,       % relative node positioning (right=of, below=of)
  arrows.meta,       % modern arrow tips
  calc,              % coordinate calculations
  fit,               % fitting nodes around others
  backgrounds,       % drawing behind existing nodes
  decorations.pathreplacing,  % braces
  decorations.markings,       % arrow marks on paths
  shapes.geometric,  % diamond, ellipse, etc.
  shapes.misc,       % rounded rectangle
  patterns,          % fill patterns
  fadings,           % transparency effects
}
```

---

## Module Box Styles

### Standard Module Box
A rounded rectangle with title and optional content area. This is the primary building block.

```latex
% Style definition
\tikzset{
  module/.style={
    draw=borderPrimary, fill=bgPrimary, rounded corners=4pt,
    minimum width=3cm, minimum height=1.2cm,
    font=\sffamily\small, text=textMain,
    line width=0.6pt,
    align=center,
  },
}

% Usage: simple module
\node[module] (mod1) {Module Name};

% Usage: module with subtitle (use \\ for line break)
\node[module, minimum height=1.6cm] (mod2) {
  \textbf{Module Name}\\[2pt]
  {\footnotesize\color{textLight} description}
};
```

### Input/Output Box
Slightly different styling to distinguish data from processing modules.

```latex
\tikzset{
  iobox/.style={
    draw=borderPrimary, fill=bgInput, rounded corners=3pt,
    minimum width=2.2cm, minimum height=1cm,
    font=\sffamily\small, text=textMain,
    line width=0.5pt,
    align=center,
  },
}

% Usage
\node[iobox] (input) {Input Image};
\node[iobox] (output) {Output Mesh};
```

### Highlighted Module (Novel Contribution)
Use for modules that represent the paper's key contribution.

```latex
\tikzset{
  novelmodule/.style={
    draw=borderAccent, fill=bgAccent, rounded corners=4pt,
    minimum width=3cm, minimum height=1.2cm,
    font=\sffamily\small\bfseries, text=textMain,
    line width=1.0pt,
    align=center,
  },
}

% Usage
\node[novelmodule] (novel) {Our Method};
```

### Dashed Module (Optional/Alternative)
For optional or alternative pipeline branches.

```latex
\tikzset{
  optmodule/.style={
    draw=borderPrimary, fill=bgSecondary, rounded corners=4pt,
    minimum width=3cm, minimum height=1.2cm,
    font=\sffamily\small, text=textLight,
    line width=0.6pt, dashed,
    align=center,
  },
}

% Usage
\node[optmodule] (optional) {Optional Refinement};
```

### Group Box (Enclosing Multiple Modules)
Wraps a group of nodes to show they belong to the same stage.

```latex
\tikzset{
  groupbox/.style={
    draw=borderPrimary, fill=bgSecondary, fill opacity=0.3,
    rounded corners=6pt, inner sep=8pt,
    line width=0.5pt, dashed,
  },
}

% Usage: after placing inner nodes, use "fit" to enclose them
\begin{scope}[on background layer]
  \node[groupbox, fit=(mod1)(mod2), label={[font=\sffamily\footnotesize,text=textLight]above:Stage 1}] {};
\end{scope}
```

### Loss / Objective Box
Small box for loss functions or training objectives.

```latex
\tikzset{
  lossbox/.style={
    draw=borderAccent, fill=bgHighlight, rounded corners=3pt,
    minimum width=1.8cm, minimum height=0.8cm,
    font=\sffamily\footnotesize, text=textMain,
    line width=0.5pt,
    align=center,
  },
}

% Usage
\node[lossbox] (loss) {$\mathcal{L}_{\text{recon}}$};
```

---

## Connection Styles

### Standard Arrow
```latex
\tikzset{
  stdarrow/.style={
    -{Stealth[length=5pt, width=4pt]},
    line width=0.6pt, color=arrowColor,
  },
}

% Usage
\draw[stdarrow] (mod1) -- (mod2);
```

### Arrow with Label
```latex
% Usage: label above the arrow
\draw[stdarrow] (mod1) -- node[above, font=\sffamily\scriptsize, text=textLight] {feature} (mod2);

% Usage: label below the arrow
\draw[stdarrow] (mod1) -- node[below, font=\sffamily\scriptsize, text=textLight] {$\mathbf{z}$} (mod2);
```

### Right-Angle (Orthogonal) Arrow
```latex
\tikzset{
  orthoarrow/.style={
    -{Stealth[length=5pt, width=4pt]},
    line width=0.6pt, color=arrowColor, rounded corners=3pt,
  },
}

% Usage: go right then down
\draw[orthoarrow] (mod1.east) -| (mod2.north);

% Usage: go down then right
\draw[orthoarrow] (mod1.south) |- (mod2.west);
```

### Dashed Arrow (Optional Connection)
```latex
\tikzset{
  dasharrow/.style={
    -{Stealth[length=5pt, width=4pt]},
    line width=0.6pt, color=arrowColor, dashed,
  },
}

% Usage
\draw[dasharrow] (mod1) -- (mod2);
```

### Bidirectional Arrow
```latex
\tikzset{
  biarrow/.style={
    {Stealth[length=5pt, width=4pt]}-{Stealth[length=5pt, width=4pt]},
    line width=0.6pt, color=arrowColor,
  },
}

% Usage
\draw[biarrow] (mod1) -- (mod2);
```

### Loss Arrow (from module to loss)
```latex
\tikzset{
  lossarrow/.style={
    -{Stealth[length=4pt, width=3pt]},
    line width=0.5pt, color=borderAccent, dashed,
  },
}

% Usage
\draw[lossarrow] (mod1) -- (loss);
```

### Feedback / Loop Arrow
```latex
% Curved feedback arrow going below
\draw[stdarrow] (mod2.south) to[out=-30, in=-150] (mod1.south);

% Curved feedback arrow going above
\draw[stdarrow] (mod2.north) to[out=150, in=30] (mod1.north);
```

---

## 2D Visualization Elements

### Feature Map / Tensor (Stacked Rectangles)
Represents a feature map or tensor volume as stacked rectangles. Place inside a module or between modules.

```latex
% Draw a feature map: width w, height h, depth d (number of stacked layers)
% anchor at (x, y)
\newcommand{\featuremap}[5]{
  % #1=x, #2=y, #3=width, #4=height, #5=depth(layers)
  \foreach \i in {1,...,#5} {
    \pgfmathsetmacro{\offset}{(\i-1)*0.08}
    \draw[fill=bgAccent, draw=borderPrimary, line width=0.3pt]
      (#1+\offset, #2+\offset) rectangle (#1+#3+\offset, #2+#4+\offset);
  }
}

% Usage
\featuremap{0}{0}{0.6}{0.8}{4}

% With dimension label
\featuremap{0}{0}{0.6}{0.8}{4}
\node[font=\sffamily\tiny, text=textLight] at (0.3, -0.15) {$H{\times}W{\times}C$};
```

### Network Block Symbol (Conv, FC, Attention, etc.)
Small labeled block representing a network operation.

```latex
\tikzset{
  netblock/.style={
    draw=borderPrimary, fill=bgSecondary,
    minimum width=1.2cm, minimum height=0.6cm,
    font=\sffamily\tiny, text=textMain,
    rounded corners=2pt, line width=0.4pt,
    align=center,
  },
}

% Usage
\node[netblock] (conv) {Conv};
\node[netblock] (fc) {FC};
\node[netblock] (attn) {Attention};
\node[netblock] (mlp) {MLP};
\node[netblock] (norm) {LayerNorm};
```

### Matrix / Grid
A small grid representing a matrix or table.

```latex
% Draw a grid: rows x cols, cell size s, at position (x,y)
\newcommand{\matrixgrid}[5]{
  % #1=x, #2=y, #3=cols, #4=rows, #5=cell size
  \draw[draw=borderPrimary, line width=0.3pt, fill=bgInput, rounded corners=1pt]
    (#1, #2) rectangle (#1+#3*#5, #2+#4*#5);
  \foreach \i in {1,...,\numexpr#3-1} {
    \draw[draw=borderPrimary, line width=0.15pt] (#1+\i*#5, #2) -- (#1+\i*#5, #2+#4*#5);
  }
  \foreach \j in {1,...,\numexpr#4-1} {
    \draw[draw=borderPrimary, line width=0.15pt] (#1, #2+\j*#5) -- (#1+#3*#5, #2+\j*#5);
  }
}

% Usage: 4x3 grid with 0.2cm cells
\matrixgrid{0}{0}{4}{3}{0.2}
```

### Image Placeholder
A placeholder rectangle with a cross, representing an input/output image.

```latex
\newcommand{\imgplaceholder}[4]{
  % #1=x, #2=y, #3=width, #4=height
  \draw[draw=borderPrimary, fill=bgInput, line width=0.3pt, rounded corners=1pt]
    (#1, #2) rectangle (#1+#3, #2+#4);
  \draw[draw=textLight, line width=0.2pt]
    (#1, #2) -- (#1+#3, #2+#4)
    (#1+#3, #2) -- (#1, #2+#4);
}

% Usage
\imgplaceholder{0}{0}{1.0}{0.75}
```

### Document / Text Symbol
```latex
\tikzset{
  docsymbol/.style={
    draw=borderPrimary, fill=bgInput,
    minimum width=0.8cm, minimum height=1.0cm,
    font=\sffamily\tiny, text=textLight,
    line width=0.3pt, align=center,
  },
}

% Usage: document with text lines
\node[docsymbol] (doc) {};
% Draw text lines inside
\foreach \y in {0.15, 0.05, -0.05} {
  \draw[textLight, line width=0.2pt]
    ([xshift=-0.2cm, yshift=\y cm]doc.center) -- ([xshift=0.2cm, yshift=\y cm]doc.center);
}
```

### Database / Storage Symbol
```latex
\newcommand{\dbsymbol}[3]{
  % #1=x, #2=y, #3=scale (e.g. 0.4)
  \draw[draw=borderPrimary, fill=bgSecondary, line width=0.3pt]
    (#1-#3, #2-#3*1.5) -- (#1-#3, #2+#3*1.2) arc(180:360:#3 and #3*0.3) -- (#1+#3, #2-#3*1.5) arc(0:-180:#3 and #3*0.3);
  \draw[draw=borderPrimary, fill=bgSecondary, line width=0.3pt]
    (#1, #2+#3*1.2) ellipse (#3 and #3*0.3);
}

% Usage
\dbsymbol{0}{0}{0.4}
```

### Graph / Tree Structure
```latex
% Simple graph with 4 nodes
\newcommand{\simplegraph}[3]{
  % #1=x, #2=y, #3=scale
  \foreach \pos/\name in {
    (0,0)/a, (1,0)/b, (0.5,0.8)/c, (1.5,0.4)/d
  } {
    \node[circle, fill=bgAccent, draw=borderPrimary, inner sep=1.5pt, line width=0.3pt]
      (\name) at ([shift={\pos}, xshift=#1 cm, yshift=#2 cm, scale=#3]) {};
  }
  \draw[borderPrimary, line width=0.3pt] (a)--(b) (a)--(c) (b)--(c) (b)--(d);
}
```

### Plus / Concatenation Symbol
```latex
\tikzset{
  plusnode/.style={
    circle, draw=borderPrimary, fill=bgSecondary,
    inner sep=0pt, minimum size=14pt,
    font=\sffamily\scriptsize\bfseries, text=textMain,
    line width=0.5pt,
  },
}

% Usage
\node[plusnode] (plus) {$+$};    % addition
\node[plusnode] (cat) {$\oplus$}; % concatenation
```

---

## Annotation Elements

### Brace with Label
```latex
% Horizontal brace below a span
\draw[decorate, decoration={brace, amplitude=5pt, mirror}, line width=0.5pt, arrowColor]
  (mod1.south west) -- (mod3.south east)
  node[midway, below=6pt, font=\sffamily\footnotesize, text=textLight] {Our Contribution};

% Vertical brace to the right
\draw[decorate, decoration={brace, amplitude=5pt}, line width=0.5pt, arrowColor]
  (mod1.north east) -- (mod3.south east)
  node[midway, right=6pt, font=\sffamily\footnotesize, text=textLight] {Encoder};
```

### Callout / Bubble Annotation
```latex
\tikzset{
  callout/.style={
    draw=borderPrimary, fill=bgHighlight, rounded corners=3pt,
    font=\sffamily\scriptsize, text=textMain,
    inner sep=4pt, line width=0.4pt,
    align=center,
  },
}

% Usage
\node[callout, above right=0.3cm of mod1] (note) {Key insight:\\shared features};
\draw[-{Stealth[length=3pt]}, arrowColor, line width=0.4pt]
  (note.south west) -- (mod1.north east);
```

### Dimension Label
```latex
% Place near a feature map or tensor
\node[font=\sffamily\tiny, text=textLight] at (x, y) {$H{\times}W{\times}C$};

% Or with explicit values
\node[font=\sffamily\tiny, text=textLight] at (x, y) {$256{\times}256{\times}3$};
```

### Equality / Mapping Symbol
```latex
% Between two nodes to show equivalence
\node[font=\sffamily\small, text=arrowColor] at ($(mod1)!0.5!(mod2)$) {$\equiv$};

% Or mapping
\node[font=\sffamily\small, text=arrowColor] at ($(mod1)!0.5!(mod2)$) {$\mapsto$};
```

---

## Common Node Positioning Patterns

### Horizontal Chain (Left to Right)
```latex
\node[module] (m1) {Module 1};
\node[module, right=1.2cm of m1] (m2) {Module 2};
\node[module, right=1.2cm of m2] (m3) {Module 3};
\draw[stdarrow] (m1) -- (m2);
\draw[stdarrow] (m2) -- (m3);
```

### Vertical Chain (Top to Bottom)
```latex
\node[module] (m1) {Module 1};
\node[module, below=0.8cm of m1] (m2) {Module 2};
\node[module, below=0.8cm of m2] (m3) {Module 3};
\draw[stdarrow] (m1) -- (m2);
\draw[stdarrow] (m2) -- (m3);
```

### Fork (One to Many)
```latex
\node[module] (src) {Source};
\node[module, above right=0.5cm and 1.5cm of src] (a) {Branch A};
\node[module, below right=0.5cm and 1.5cm of src] (b) {Branch B};
\draw[stdarrow] (src.east) -- (a.west);
\draw[stdarrow] (src.east) -- (b.west);
```

### Merge (Many to One)
```latex
\node[module] (a) {Branch A};
\node[module, below=1cm of a] (b) {Branch B};
\node[module, right=1.5cm of $(a)!0.5!(b)$] (merge) {Merge};
\draw[stdarrow] (a.east) -- (merge.west);
\draw[stdarrow] (b.east) -- (merge.west);
```
