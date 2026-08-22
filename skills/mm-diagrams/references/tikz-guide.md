# TikZ 论文流程图实现规范

## 1. 编译骨架

使用 XeLaTeX，避免把中文转路径或手工定位字形：

```latex
\documentclass[border=5pt]{standalone}
\usepackage{fontspec}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,calc,shapes.geometric}
\setsansfont{Microsoft YaHei}
```

若 Microsoft YaHei 不存在，依次尝试 `Noto Sans CJK SC`、`Source Han Sans SC`、`SimHei`。全图使用 `\sffamily`，正文节点以 `\small` 为起点；最终嵌入后不得小于 8 pt。

## 2. 节点尺寸

- 用 `align=center`、`inner xsep`、`inner ysep` 让节点随内容扩展。
- `minimum width/height` 只统一同类节点的最低尺寸，不得限制内容上限。
- 长标签主动拆成最多两行；副说明用 `\footnotesize`，不在节点中放完整句子。
- 不用 `text width` 强行压缩中文，除非版式确实要求固定列宽且已经验证换行。

## 3. 边界锚点定位

TikZ 的 `right=<距离> of <node>` 对节点有效，因为距离按边界计算；但 `<coordinate>` 是零尺寸对象。把节点放在 coordinate 右侧时，距离是“coordinate 到新节点边界/锚点”的关系，不能假定它等于两个既有方框之间的净距。

多输入汇流使用边界中点和显式锚点：

```latex
\coordinate (inputeastmid) at ($(inputA.east)!0.5!(inputB.east)$);
\node[module, anchor=west] (merge)
  at ([xshift=1.35cm]inputeastmid) {统一问题契约};
```

左侧辅助节点同理：

```latex
\node[inputbox, anchor=east] (baseline)
  at ([xshift=-1.25cm]solve.west) {基线方案};
```

定位后必须确认：`input.east.x < merge.west.x`，且中间净距足以容纳转折和箭头尖端。

## 4. 连线路由

- 单段主链直接连接相邻边界锚点：`(a.south) -- (b.north)`。
- 非对齐节点使用 `|-` 或 `-|`，每条边最多两个转折。
- 多输入先从各自 `east` 向右走一小段，再进入目标 `west`；转折点必须位于两框净距内。
- 反馈使用虚线，沿主链右侧或下侧外轨返回，不穿过节点。
- 箭头终点写目标锚点，禁止让路径靠近目标后反向折回；视觉上所有箭头都应顺着阅读方向进入。
- 边标签使用白底小内边距，放在出口附近；判断节点的每个出口都标明条件。

## 5. 设计令牌

默认只用正文深灰、结构灰和一种低饱和强调色。普通框直角或轻微圆角；状态/输出可明显圆角；菱形只表示判断。禁止阴影、渐变、装饰分隔线、无语义图标和画布内大标题。

## 6. 编译与视觉门禁

运行：

```powershell
python scripts/render_tikz.py figures/fig_xxx.tex `
  --png figures/fig_xxx_600dpi.png --dpi 600 --strict
```

然后回读 PNG，逐项确认：

1. 中文无乱码、缺字、裁切或出框；
2. 节点无重叠，净距稳定；
3. 箭头方向正确，不穿框、不压文字；
4. 交叉边为 0，反馈走外围；
5. 无无语义横线、竖线或装饰；
6. PDF 自然宽度接近论文嵌入宽度；
7. 600 DPI PNG 像素量与物理尺寸一致；
8. 缩到最终版心后正文标签仍不小于 8 pt。

编译成功但视觉门禁失败时，必须修改并重编。只有最终回读版本可以登记为 `complete`。
