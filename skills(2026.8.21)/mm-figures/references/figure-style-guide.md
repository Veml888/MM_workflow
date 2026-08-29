# 论文级数据图样式规范

## 全局配置

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "SimSun",
    "font.sans-serif": ["SimSun", "Times New Roman"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "text.color": "black",
    "axes.labelcolor": "black",
    "axes.titlecolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})
```

字体分工：中文正文/图内文字宋体（SimSun），中文标题黑体（SimHei，可在 `ax.set_title` 用 `fontproperties` 或标题处单独设置），英文、数字、拉丁字母 Times New Roman，数学字体 STIX。

## 配色（高对比、白底、黑字）

| 用途 | 色值 |
|---|---|
| 蓝色 | `#0066CC` |
| 青绿色 | `#008F78` |
| 橙色 | `#E68A00` |
| 红色 | `#D83A58` |
| 深灰色 | `#657487` |
| 网格线 | `#D7E1EA` |

重要类别同时用颜色、线型和点形区分；网格只保留有助于读数的方向；禁止深色底、渐变、阴影卡片、灰暗低对比配色和装饰纹理。

## 画布与字号

- 核心统计图优先 2×2 多面板，四个子图围绕同一问题；推荐 `figsize=(7.80, 4.39)`（接近 16:9）；子图标记统一 `(a)(b)(c)(d)`；
- 轴名和刻度 7.5~9 pt，图例 6.5~8 pt，子图标记 10~11 pt；
- 最终判断以插入 A4 页面后的可读性为准。

## 图形选择

| 数据关系 | 图种 |
|---|---|
| 模型排序 | ROC、AUC 区间或置换结果 |
| 审核效果 | 容量捕获曲线、Lift 曲线 |
| 参数不确定性 | 点区间图 |
| 分组比例 | 带 Wilson 区间的柱形图/点图 |
| 小样本分布 | ECDF |
| 字段闭合 | 点图、哑铃图或误差对比图 |
| 建模流程 | 对齐方框 + 正交箭头（流程图归 `mm-diagrams`） |

## 导出

每张终稿图同时导出 PDF、SVG 和 PNG：PDF 用于 LaTeX，SVG 用于编辑，PNG 用于检查与支撑材料。PNG 不低于 300 DPI，多面板图推荐 420 DPI。

## 3D 图（可选）

仅当数据适合三维展示时采用：`view_init(elev, azim)` 选不遮挡视角，`cmap` 用色弱友好色带，加 colorbar，黑白打印可辨识。

## 文字重叠防复发

数据图交付前必须通过 `scripts/check_figure_overlap.py` 的文字-文字重叠扫描（重叠数 = 0），并逐项检查以下高发场景：

1. **2×2 多面板行距**：底部面板标题不得与上排面板的刻度、x 轴标签重叠。实现：`fig.subplots_adjust(hspace=0.55, wspace=0.25)`（或更大）；上排 xlabel 与下排标题之间必须肉眼可见空隙。刻度标签很多（如 15 个 y 刻度）或旋转 45°/90° 时，会向下/向外溢出，需缩小刻度字号或加大 hspace，不能用默认行距赌运气。
2. **面板标记**：2×2 面板必须标 `(a)(b)(c)(d)`（`ax.text(-0.10, 1.06, tag, transform=ax.transAxes, ...)`），标记不得与标题/刻度重叠。
3. **图例**：优先放数据稀疏区；放在图顶部时不得压面板标题，否则移到图下方（`fig.legend(..., bbox_to_anchor=(0.5, -0.05))` 并给底部留白 `fig.subplots_adjust(bottom=...)`）。
4. **热力图**：矩阵 ≥10×10 时，数值标注只放内圈单元格（跳过最外圈行/列）或缩小字号并加大画布；colorbar 避免与右缘/底缘标注及旋转刻度相交（必要时改底部横向 `orientation="horizontal"` 并加大 `pad`）；`ax.tick_params(pad=6)` 分隔刻度与图形。
5. **3D 图**：限制刻度数量（如 `set_xticks([0,1,2,3,4])`），轴标签 `labelpad≥10`，扫描确认刻度标签与轴标签不重叠。
6. **堆叠柱小标签**：小计数段（v<2）不标注或加大偏移（`y+v+1.0` 以上），避免相邻数值标签重叠；计数标签字号 6pt 左右。
7. **旋转刻度**：`rotation=45/90` 会显著扩展标签占位，必须为 xlabel、相邻面板、colorbar 预留空间。

上述任一场景存在重叠，必须返工后重扫，禁止带病进入 docs/04 与论文。

## 检查清单

- [ ] 中文正常显示、无方框；负号正常（`axes.unicode_minus=False`）
- [ ] 全部文字为黑色；标题黑体、正文宋体、拉丁 Times New Roman、数学 STIX
- [ ] 有标题、轴标签、单位；嵌入 A4 后字号可读（轴 7.5~9pt、图例 6.5~8pt、子图标记 10~11pt）
- [ ] 重要类别同时有颜色、线型、点形区分
- [ ] 图例放在数据稀疏区域，不遮挡曲线和标签（`framealpha=0.9`）
- [ ] 数据标签只标关键值；条形图数值标签上方留白 ≥10%，不贴柱顶
- [ ] 节点编号/均值标注不压线不压点：节点编号加白色圆角底框并置顶，均值标注偏移或用引线
- [ ] 出图后运行 `scripts/check_figure_overlap.py` 扫描全部数据图 PDF，文字-文字重叠数 = 0
- [ ] 2×2 面板行距：底部标题不压上排刻度/xlabel；`(a)(b)(c)(d)` 标记不与标题刻度重叠
- [ ] 图例不压标题/曲线/标签；热力图标注不压刻度与 colorbar；3D 刻度与轴标签不重叠；堆叠柱小计数标签不互相重叠
- [ ] 2×2 多面板子图标记 `(a)(b)(c)(d)`
- [ ] 无多余留白（tight bbox）
- [ ] PDF + SVG + PNG 三格式齐全；PNG ≥300 DPI（多面板 ≥420）
