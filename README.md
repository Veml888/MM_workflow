# MM_workflow — 数学建模全流程工作流（CUMCM）

一套面向 **全国大学生数学建模竞赛（CUMCM）** 的 **Skills 工作流集合**。它把"读题 → 建模 → 编程 → 制图 → 截图 → 验收"整条链路拆成 9 个可复用的 skill，每个 skill 负责一个阶段，并通过 `project-manifest.json` 和 `plan.md` 交接，确保全流程产物一致、可复现、可验收。

> 本仓库是 **Skills 定义本身**（即"工作流怎么跑"），不是某一次的赛题成果。用它来跑一道真实赛题，会得到一个完整的项目目录（报告、图、代码、结果）。

## 为什么做成工作流

数模论文质量参差，根源往往在"阶段之间脱节"：建模的假设没传达到编程、生成的图和论文对不上、验收才发现缺文件。本工作流的核心思路是：

- **阶段解耦 + 明确产出契约**：每个阶段产出带有稳定 ID 的交接件（如 `docs/01-analysis-report.md`、`project-manifest.json`），下游只依赖契约，不依赖上游"怎么做的"。
- **机检驱动**：多阶段内置 Python 校验/审计脚本，用可复现的脚本替代人工判断。
- **先读全再执行**：每个 SKILL.md 开头要求先完整读取（`read_complete.py` 保证不截断），避免模型漏掉长文档细节。

## 快速开始

不用自己搭框架，让 `mm-orchestrator` 生成项目骨架：

```
1. 把本仓库的 skills 目录放到你的 agent 插件/技能目录
2. 命一个阶段入口（推荐用 mm-orchestrator），例如：
   让 agent 运行 "开始建模"
3. 它会问你两个关键偏好（侧重点、子问题数），然后生成：
   plan.md / todo.md / project-manifest.json / 论文结构规划
4. 之后每个阶段（分析、建模、代码、图、论文、验收）由对应 skill 接管
```

各阶段职责一览（点进对应目录看 `SKILL.md` 是完整说明）：

| skill | 阶段 | 产出 |
|---|---|---|
| `mm-problem-analysis` | 赛题分析与交接 | `docs/01-analysis-report.md`、更新 manifest |
| `mm-modeling` | 建模与求解设计 | `docs/02-modeling-report.md`、manifest 交接 |
| `mm-coding` | 编程实现 | `code/`、`results/`、`docs/03-results-report.md` |
| `mm-figures` | 数据图表 | 折线/柱状/散点/热力/箱线/曲面/灵敏度/误差图（PDF/SVG/PNG） |
| `mm-graphics` | 非数据图（示意图/流程图/机理图） | TikZ 源 + 矢量 PDF + 600DPI PNG，不用 AI 图像生成 |
| `mm-model-dictionary` | 模型知识库与适配评估 | 共享 BZD 模型字典、适配自查表（不代替选型） |
| `mm-orchestrator` | 全流程编排入口 | `plan.md`、`todo.md`、manifest、计划与图需求 |
| `mm-paper-writing` | 论文撰写 | LaTeX 论文（`paper/论文.tex|pdf`） |
| `mm-verification` | 交付验收 | 全流程完整性 / 可复现性 / 格式审计 |

> **固定约定**：编程语言为 **Python**（除非显式要求 MATLAB）；跨阶段不变量见 `mm-orchestrator/references/cumcm-shared-policy.md`；机器可读交接见 `project-manifest.schema.json`。

## 目录结构

```
MM_workflow/
├── .gitignore                # 排除 LaTeX 编译产物 / Python 缓存
├── README.md
├── LICENSE
└── skills/
    ├── mm-problem-analysis/  # 赛题分析
    ├── mm-modeling/          # 建模与求解设计
    ├── mm-coding/            # 编程实现
    ├── mm-figures/           # 数据图表
    ├── mm-graphics/          # 非数据图（示意/流程/机理）
    ├── mm-model-dictionary/  # 模型知识库
    ├── mm-orchestrator/      # 全流程编排（推荐入口）
    ├── mm-paper-writing/     # 论文撰写
    └── mm-verification/      # 交付验收
```

每个 skill 通常包含 `SKILL.md`（技能说明与步骤）、`references/`（模板、规范、知识库）、`scripts/`（Python 校验/审计脚本）、`agents/`（子代理配置）、`assets/`（辅助资源）。

## 版本历史

本仓库用 git 的 **tag** 记录每次快照，替代早期"按日期复制文件夹"的做法。可在 tag 间查看每一次演化：

| tag | 对应快照 | 内容 |
|---|---|---|
| `v0.8.21` | 2026-08-21 | 初始完整版（含实验性 skill，19 个） |
| `v0.8.29` | 2026-08-29 | 收敛为核心 8 skills |
| `v0.9.3` | 2026-09-03 | 当前版：9 个核心 skills |

```
git checkout v0.9.3   # 查看任意历史版本
```

## 许可

[MIT](LICENSE) — 欢迎 fork 与二次开发，请保留版权声明。
