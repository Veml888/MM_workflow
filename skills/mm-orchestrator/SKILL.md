---
name: mm-orchestrator
description: 全国大学生数学建模竞赛（CUMCM 2026）全流程编排入口。当用户要开始国赛建模、说"开始建模"、"做这道国赛题"、"跑完整流程"、"写数模论文"，或需要按阶段调度赛题分析、建模求解、编程实现、图表生成、流程与示意图绘制、论文撰写时使用。本 skill 负责询问关键偏好、生成 plan.md、todo.md 与 project-manifest.json，并调度下游阶段 skill。
---

# 数学建模全流程编排

本 skill 是 CUMCM 2026 数模 skills 的总控入口，不替代任何阶段 skill。它只做三件事：**问清偏好 → 建立计划与交接清单 → 调度各阶段 skill**。

跨阶段规则以 `references/cumcm-2026-shared-policy.md` 为唯一权威来源；机器可读交接遵循 `references/project-manifest-contract.md` 和 `project-manifest.schema.json`。开始前完整读取这两份文件和 `references/project-layout.md`。

## 工作流

### 第 1 步：确认题目与项目根目录

- 用户可能直接给出赛题 PDF/DOCX/图片，也可能只说"开始建模"。
- 没有题目时，先请用户提供 CUMCM 赛题文件；本流水线不适配其他竞赛。
- 确定 `PROJECT_ROOT`（本次项目的根目录）。若用户未指定，在当前工作目录新建一个以题目命名的文件夹。

### 第 2 步：询问关键偏好

用提问工具（`AskUserQuestion`，名称以当前环境可用工具为准）只问会实质影响后续阶段的问题（不要超过 4 个，能推断的不要问）：

1. **编程语言**：Python（默认）/ MATLAB / 混合。
2. **侧重点**：精度优先（默认）/ 可解释性优先 / 速度优先 / 均衡。
3. **子问题数量**：已知 N 个 / 待赛题分析确定。

把答案连同题目信息一起写入 `plan.md`。

### 第 3 步：生成 plan.md、todo.md 与 project-manifest.json

按 `references/project-layout.md` 的骨架，在当前项目根目录创建：

- `plan.md`：整体方案。包含：题目概述、用户偏好、阶段顺序、每阶段负责的 skill 与预期产出文件、风险控制。
- `todo.md`：阶段性待办清单，每阶段一条，勾选进度。
- `project-manifest.json`：按 `references/project-manifest-contract.md` 初始化，登记阶段状态、稳定 ID、文件哈希与回写版本。

`plan.md` 中的阶段依赖固定为：

| 序 | 阶段 | skill | 关键产出 |
|---|---|---|---|
| 1 | 赛题分析 | `mm-problem-analysis` | `docs/01-analysis-report.md` |
| 2 | 建模求解 | `mm-modeling` | `docs/02-modeling-report.md` |
| 3 | 编程实现 | `mm-coding` | `code/`、`results/`、`docs/03-results-report.md` |
| 4 | 论文结构草稿 | `mm-paper-writing` | `paper/structure-draft.md`、`paper/figure-requirements.md`、`paper/writing-gates.md` |
| 5a | 数据图（按需） | `mm-figures` | `figures/*.png/pdf/svg`、`docs/04-figures-report.md` |
| 5b | 流程架构图（按需） | `mm-diagrams` | `figures/*.tex|pdf|png`（可选 `*.svg`）、`docs/05-diagrams-report.md` |
| 5c | 纯视觉示意图（完整论文必做） | `mm-visual-concept` | `figures/*.png`、可选 `*.svg`、`docs/05-visual-report.md` |
| 6 | 论文终稿 | `mm-paper-writing` | `paper/论文.tex`、`paper/论文.pdf` |
| 7 | 验收 | `mm-verification` | `docs/06-verification-report.md` |

### 第 4 步：按序调用阶段 skill

- 先完成分析、建模、编程和论文结构草稿；随后 `mm-figures`、`mm-diagrams`、`mm-visual-concept` 三个分支按适用性并行调用，全部完成或标记 `n_a` 后再进入论文终稿。
- `mm-diagrams` 负责技术路线、总体框架、模型结构、指标体系、变量关系和验证闭环；只有复杂自研算法才允许算法流程图。完整论文必须调用 `mm-visual-concept` 生成至少 1 张纯视觉示意图。
- 每个阶段开始前，回显：当前阶段、负责 skill、将读取的上游报告、将产出的文件。
- 每个阶段开始前输出 GATE 确认：上游产物存在、必读规范已读（引用原文）、计划产出明确；缺上游先补齐再进下一阶段。
- 每阶段结束后更新 `project-manifest.json` 中自己负责的阶段状态、产物哈希和版本。发生回写时追加 `change_log`，记录原因和受影响 ID。
- 若某一阶段被跳过或不适用，在 `plan.md` 中注明原因，并将 manifest 对应阶段标记为 `n_a`；范围化验收不要求 `n_a` 阶段产物，但最终总结必须说明范围。
- 阶段产物未通过 `mm-verification` 前，不得声称"全流程完成"。
- `mm-verification` 只审计、定位并指定回写阶段；本 skill 负责调用对应 skill 修复后再次验收。
- 每个阶段完成前运行 `scripts/validate_manifest.py`；校验失败不得继续下游。验收发现的问题写入 `rework[]`，按影响范围重新调用目标阶段及下游阶段。

## 边界

- 本 skill 不亲自解题、不写模型、不画图、不写论文正文——只编排与调度。
- 不覆盖 `PROJECT_ROOT` 之外的任何既有文件；输入附件只读。
