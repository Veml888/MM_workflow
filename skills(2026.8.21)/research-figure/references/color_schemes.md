# Color Schemes for Academic Figures

Low-saturation color palettes designed for publication-quality figures. Each scheme includes TikZ `\definecolor` definitions ready to copy into your preamble.

## Table of Contents
1. [Blue-Gray (Classic Academic)](#1-blue-gray-classic-academic)
2. [Warm Tones (Innovation Highlight)](#2-warm-tones-innovation-highlight)
3. [Green-Cyan (Fresh & Natural)](#3-green-cyan-fresh--natural)
4. [Purple-Blue (Elegant & Calm)](#4-purple-blue-elegant--calm)
5. [Monochrome Gradient](#5-monochrome-gradient)
6. [Usage Guidelines](#usage-guidelines)

---

## 1. Blue-Gray (Classic Academic)

Best for: general-purpose pipeline figures, systems diagrams, neutral tone.

```latex
% Blue-Gray Scheme
\definecolor{bgPrimary}{HTML}{DAE8FC}     % light blue - module backgrounds
\definecolor{bgSecondary}{HTML}{E8EEF7}   % very light blue - secondary modules
\definecolor{bgAccent}{HTML}{B3CDE3}      % medium blue - highlighted modules
\definecolor{bgInput}{HTML}{F0F4F8}       % near white - input/output backgrounds
\definecolor{borderPrimary}{HTML}{6C8EBF}  % medium blue - borders
\definecolor{borderAccent}{HTML}{3A6EA5}   % darker blue - accent borders
\definecolor{arrowColor}{HTML}{4A6A8A}     % steel blue - arrows
\definecolor{textMain}{HTML}{2C3E50}       % dark blue-gray - main text
\definecolor{textLight}{HTML}{7F8C8D}      % gray - secondary text
\definecolor{bgHighlight}{HTML}{FFF3CD}    % light yellow - novel contribution highlight
```

## 2. Warm Tones (Innovation Highlight)

Best for: figures emphasizing novelty, creative methods, attention-grabbing modules.

```latex
% Warm Tones Scheme
\definecolor{bgPrimary}{HTML}{FDEBD0}     % light peach - module backgrounds
\definecolor{bgSecondary}{HTML}{FAE5D3}   % light salmon - secondary modules
\definecolor{bgAccent}{HTML}{F5CBA7}      % warm orange - highlighted modules
\definecolor{bgInput}{HTML}{FDF2E9}       % cream - input/output backgrounds
\definecolor{borderPrimary}{HTML}{E59866}  % warm orange - borders
\definecolor{borderAccent}{HTML}{CA6F1E}   % burnt orange - accent borders
\definecolor{arrowColor}{HTML}{A04000}     % dark brown - arrows
\definecolor{textMain}{HTML}{3E2723}       % dark brown - main text
\definecolor{textLight}{HTML}{8D6E63}      % medium brown - secondary text
\definecolor{bgHighlight}{HTML}{FADBD8}    % light pink - novel contribution highlight
```

## 3. Green-Cyan (Fresh & Natural)

Best for: eco/bio-related papers, generation pipelines, refreshing visual tone.

```latex
% Green-Cyan Scheme
\definecolor{bgPrimary}{HTML}{D5F5E3}     % light mint - module backgrounds
\definecolor{bgSecondary}{HTML}{D1F2EB}   % light cyan - secondary modules
\definecolor{bgAccent}{HTML}{A9DFBF}      % medium green - highlighted modules
\definecolor{bgInput}{HTML}{EAFAF1}       % near-white green - input/output backgrounds
\definecolor{borderPrimary}{HTML}{76D7C4}  % teal - borders
\definecolor{borderAccent}{HTML}{1ABC9C}   % vivid teal - accent borders
\definecolor{arrowColor}{HTML}{148F77}     % dark teal - arrows
\definecolor{textMain}{HTML}{1B4332}       % dark green - main text
\definecolor{textLight}{HTML}{52796F}      % gray-green - secondary text
\definecolor{bgHighlight}{HTML}{FEF9E7}    % light yellow - novel contribution highlight
```

## 4. Purple-Blue (Elegant & Calm)

Best for: theoretical/math-heavy papers, elegant system designs, stylish figures.

```latex
% Purple-Blue Scheme
\definecolor{bgPrimary}{HTML}{E8DAEF}     % light lavender - module backgrounds
\definecolor{bgSecondary}{HTML}{D4E6F1}   % light blue - secondary modules
\definecolor{bgAccent}{HTML}{D2B4DE}      % medium purple - highlighted modules
\definecolor{bgInput}{HTML}{F4ECF7}       % very light purple - input/output backgrounds
\definecolor{borderPrimary}{HTML}{AF7AC5}  % purple - borders
\definecolor{borderAccent}{HTML}{7D3C98}   % dark purple - accent borders
\definecolor{arrowColor}{HTML}{6C3483}     % deep purple - arrows
\definecolor{textMain}{HTML}{2C2C54}       % dark purple-gray - main text
\definecolor{textLight}{HTML}{7F8FA6}      % blue-gray - secondary text
\definecolor{bgHighlight}{HTML}{FDEBD0}    % light peach - novel contribution highlight
```

## 5. Monochrome Gradient

Best for: minimalist figures, grayscale-friendly (prints well in B&W), clean look.

```latex
% Monochrome Scheme
\definecolor{bgPrimary}{HTML}{E5E7EB}     % light gray - module backgrounds
\definecolor{bgSecondary}{HTML}{F3F4F6}   % very light gray - secondary modules
\definecolor{bgAccent}{HTML}{D1D5DB}      % medium gray - highlighted modules
\definecolor{bgInput}{HTML}{F9FAFB}       % near white - input/output backgrounds
\definecolor{borderPrimary}{HTML}{9CA3AF}  % medium gray - borders
\definecolor{borderAccent}{HTML}{4B5563}   % dark gray - accent borders
\definecolor{arrowColor}{HTML}{374151}     % charcoal - arrows
\definecolor{textMain}{HTML}{1F2937}       % near black - main text
\definecolor{textLight}{HTML}{6B7280}      % gray - secondary text
\definecolor{bgHighlight}{HTML}{DBEAFE}    % light blue - novel contribution highlight
```

---

## Usage Guidelines

### Color Roles
| Role | Usage | Notes |
|------|-------|-------|
| `bgPrimary` | Standard module background | Most modules use this |
| `bgSecondary` | Secondary/supporting modules | Inputs, outputs, less important modules |
| `bgAccent` | Key module background | Use for novel contribution modules |
| `bgInput` | Input/output boxes | Lighter than modules for visual hierarchy |
| `bgHighlight` | Special emphasis | Use sparingly for the most important element |
| `borderPrimary` | Standard module border | All normal module borders |
| `borderAccent` | Accent border | Novel contribution module borders |
| `arrowColor` | Arrow/connection color | All arrows and connection lines |
| `textMain` | Primary text | Module titles, main labels |
| `textLight` | Secondary text | Descriptions, annotations, dimension labels |

### Principles
- **Low saturation**: All colors are muted/pastel. Avoid vivid, fully saturated colors.
- **Consistent hierarchy**: Backgrounds are lightest, borders medium, text/arrows darkest.
- **Highlight sparingly**: Only use `bgAccent`/`bgHighlight` for 1-2 key modules (novel contributions).
- **Text contrast**: Ensure `textMain` has sufficient contrast against all background colors.
- **Print-friendly**: Monochrome scheme works well for papers that may be printed in grayscale.

### Mixing Colors Across Schemes
Avoid mixing colors from different schemes. Each scheme is designed as a cohesive palette. If you need more variety, add intermediate shades by blending existing colors within the same scheme.
