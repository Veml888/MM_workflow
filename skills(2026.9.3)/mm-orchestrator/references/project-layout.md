# 项目目录结构与阶段交接契约

本文件是整套数模 skills 共享的目录约定。每个阶段 skill 都按此骨架读写，保证阶段之间能无缝交接。

## 标准骨架

```text
PROJECT_ROOT/
├── plan.md                        # 编排入口产出：整体方案与用户偏好
├── todo.md                        # 编排入口产出：阶段待办清单
├── project-manifest.json          # 跨阶段机器可读状态、溯源、哈希与版本
├── project-manifest.schema.json   # manifest 2.0 JSON Schema
├── scripts/                       # 编排级校验脚本
│   ├── validate_manifest.py
│   └── validate_paper_plan.py      # 正式论文页面预算与来源证据校验
├── data/                          # 输入数据（赛题附件、原始数据集），只读
├── docs/                          # 各阶段报告（阶段间交接的主要载体）
│   ├── 00-problem-transcription.md # 按原题页序复现的题面内容（分析阶段）
│   ├── 00-problem-interpretation.md # 逐子问题语义解释与 G-SEM 门禁
│   ├── source-evidence/            # 条件性来源证据：公式、复杂表格和信息图
│   ├── 01-analysis-report.md      # 赛题分析报告
│   ├── 02-modeling-report.md      # 建模报告（假设/符号/公式/求解流程）
│   ├── 03-results-report.md       # 结果报告（代码、数值结果）
│   ├── 04-figures-report.md       # 数据图说明
│   ├── 05-diagrams-report.md      # 流程图/机理图说明（mm-graphics）
│   └── 06-verification-report.md  # 验收报告
├── code/                          # 求解代码（按子问题组织）
│   ├── problem1.py
│   ├── problem2.py
│   └── utils.py
├── results/                       # 数值结果（csv / xlsx / json）
├── figures/                       # 全部图表
│   ├── *.pdf / *.svg / *.png      # 数据图三格式
│   ├── *.tex + *.pdf + *_600dpi.png # 流程/框架图（可选 *.svg）
└── paper/                         # 论文（LaTeX 为主）
    ├── structure-plan.md          # 策划：章节骨架与逐问论证链（编排器产出）
    ├── page-budget.json           # 策划：目标28~29页、允许27~30页的机器可读预算
    ├── figure-requirements.md     # 策划：插图需求清单（编排器建骨架、图件 skill 填入）
    ├── writing-gates.md           # 论文终稿前 G-1~G-5 门禁记录
    ├── draft-baseline.tex         # 可选：调用前已有初稿的只读基线
    ├── draft-baseline.pdf         # 可选：初稿基线编译结果
    ├── draft-audit.md             # 初稿保留/改写/删除/补充审计
    ├── draft-metrics.json         # 初稿模式、SHA256、页数与可编译状态
    ├── content-gap-report.md      # 终稿内部多轮修订的实质内容缺口
    ├── page-audit.json            # paper阶段正文页数审计
    ├── page-audit-verification.json # verification独立复核页数
    ├── 论文.tex
    ├── 论文.pdf
    └── assets/                    # 论文内嵌图片的本地副本
```

## 交接契约

每个阶段只消费上游报告、只产出自己负责的文件，不越界改写他人产物；同时按 `project-manifest-contract.md` 更新本阶段 manifest 字段：

| 阶段 | 读取（上游） | 写入（本阶段产物） |
|---|---|---|
| 赛题分析 | 题目文件、`data/` | `docs/00-problem-transcription.md`、`docs/00-problem-interpretation.md`、条件性 `docs/source-evidence/`、`docs/01-analysis-report.md` |
| 建模求解 | `docs/01-analysis-report.md` | `docs/02-modeling-report.md` |
| 编程实现 | `docs/02-modeling-report.md` | `code/`、`results/`、`docs/03-results-report.md` |
| 论文策划 | `docs/01~03`、`results/`、`plan.md`、可选调用前初稿 | 初稿冻结与审计、`paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md`、`paper/writing-gates.md`（pending） |
| 图表生成 | `docs/03-results-report.md`、`results/`、`paper/figure-requirements.md` | `figures/*.pdf|svg|png`、`docs/04-figures-report.md` |
| 非数据图（流程图/机理图 + 场景/空间精确示意图） | 题面、`docs/01~03`、`paper/figure-requirements.md` | `figures/*.tex|pdf|png`（可选 `*.svg`）、`docs/05-diagrams-report.md` |
| 论文终稿 | 正式结构规划 + 页面预算 + 初稿审计 + 全部报告 + `figures/` + `results/` + G-1~G-5 全部 PASS | 新建 `paper/论文.tex`、`paper/论文.pdf`、`paper/content-gap-report.md`、`paper/page-audit.json` |
| 验收 | 本次计划范围内的全部产物 + `project-manifest.json` | `docs/06-verification-report.md` |

## 命名约定

- 报告一律 `NN-名称.md`，NN 为两位数序号，与阶段一一对应（05 有两个并列文件：diagrams 与 visual）。
- 数据图与非数据图统一使用描述性英文或中文名称，禁止 `q1`、`q2`、`q3`、`q4` 或“问题一”等问题编号前缀。代码和结果文件仍可使用 `problem1.py`、`q1_result.csv` 等追踪编号。
- 代码文件 `problemN.py`（N 为子问题序号），公共工具 `utils.py`。
- 数值结果与题面要求的输出格式一致（国赛常要求 `.xlsx`）。
