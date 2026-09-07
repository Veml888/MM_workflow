# 图件边界（数据图 vs 非数据图 vs 场景图）

> 本文件规定论文内全部图件按"数据驱动 / 逻辑机理 / 场景空间"三类归到哪个 skill，避免重复或漏画。**以 owner skill 细则为准**：`mm-figures` 负责数据图、`mm-graphics` 负责非数据图与场景图。

## 三类图件

| 类型 | 定义 | 归口 skill | 主要产物 |
|---|---|---|---|
| 数据图 | 基于真实数值结果（折线、柱状、散点、热力、曲面、灵敏度、多帧等） | `mm-figures` | `figures/*.pdf|svg|png`（三格式）、`docs/04-figures-report.md` |
| 非数据图（逻辑/框架/机理） | 技术路线、总体框架、模型结构、指标体系、变量关系、验证闭环、复杂自研算法流程图 | `mm-graphics` | `figures/*.tex|pdf|png`（可选 svg）、`docs/05-diagrams-report.md` |
| 场景/空间图 | 题目场景示意、空间几何关系、坐标系、设备布置等需按题面事实精确呈现的示意图 | `mm-graphics`（TikZ/SVG 精确路线） | 同上 |

## 边界规则

- **数据图**：必须有真实数据来源（`results/` 或 `docs/03-results-report.md`）；无数据仅描述性示意图不归此。
- **非数据图（逻辑/框架/机理）**：必须有清晰节点与箭头，能表达一个论证步骤或算法阶段；常规求解步骤用正文表达，不画流程图。
- **场景/空间图**：必须按题面事实绘制，坐标系、几何尺寸、相对位置与题面一致；不适用时不强画。
- **不重叠**：同一图件不允许多 skill 重复产出；下游脚本 `check_figure_overlap.py` 会扫 `figures/` 检测重复。

## 在 paper/figure-requirements.md 中的写法

编排器在 paper_plan 阶段只建两份空区：

```markdown
## 数据图（mm-figures 负责）

- 边界规则：必须有真实数值结果。
- 本题需要画的数据图（由 mm-figures 阶段填写）：
  - （待 mm-figures 阶段填写图种、锚点、来源结果 ID）

## 非数据图（mm-graphics 负责）

- 边界规则：逻辑/框架/机理图 + 场景/空间图。
- 本题需要画的非数据图（由 mm-graphics 阶段填写）：
  - （待 mm-graphics 阶段填写图种、锚点、依据题面位置）
```

每个图件 skill 在自己的执行阶段填入具体清单；编排器不预决定。

## 与 manifest 的对应

- `figures[]` 数组每个图件必须有稳定 ID（推荐前缀 `FIG-###`）、`kind`（`data | diagram | scene`）、`files`、`source_result_ids`、`caption`、`paper_anchor`、`version`。
- 数据图 `source_result_ids` 必须引用 `results[]` 中已有条目；非数据图可不引用 `source_result_ids` 但必须登记依据题面位置（写入 `caption` 或 `paper_anchor`）。