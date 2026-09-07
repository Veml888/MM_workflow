# 7 阶段流水线

> 本文件是 `mm-orchestrator` 的"流水线定义"。速查见 `orchestrator-quickcard.md`；阶段门禁与机检见 `checkpoint-gates.md`。

## 适用范围

- 全国大学生数学建模竞赛（CUMCM）全流程，适配历年任意赛题；不绑定年份。
- 其他竞赛（美赛、研赛等）不适用；用户改换竞赛类型时必须另起项目。
- 编程语言固定 Python，不询问；详见 `references/orchestrator-quickcard.md` 第 2 节。

## 阶段顺序与关键产出

阶段依赖固定如下，不可乱序；可跳过（`n_a`）但必须登记原因。

| 序 | 阶段 | skill | 关键产出 | 验收脚本 |
|---|---|---|---|---|
| 1 | 赛题分析 | `mm-problem-analysis` | `docs/01-analysis-report.md`（含条件性 `docs/source-evidence/`） | `<mm-problem-analysis目录>/scripts/check_analysis_report.py` |
| 2 | 建模求解 | `mm-modeling` | `docs/02-modeling-report.md` | 每个子问题调 `<mm-model-dictionary目录>/scripts/query_model_dictionary.py`，结果须为 `合适/有条件合适/不合适/证据不足待复核`；`不合适` 必须回退重选 |
| 3 | 编程实现 | `mm-coding` | `code/`、`results/`、`docs/03-results-report.md` | `<mm-coding目录>/scripts/check_reproducibility.py` |
| 4 | 论文策划 | `mm-orchestrator`（本 skill） | `paper/draft-audit.md`、`paper/draft-metrics.json`、`paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md`、`paper/writing-gates.md` | `<mm-orchestrator目录>/scripts/validate_paper_plan.py` |
| 5a | 数据图 | `mm-figures` | `figures/*.png/pdf/svg`、`docs/04-figures-report.md` | `<mm-figures目录>/scripts/check_figure_overlap.py` |
| 5b | 非数据图 | `mm-graphics` | `figures/*.tex|pdf|png`（可选 svg）、`docs/05-diagrams-report.md` | `<mm-graphics目录>/scripts/render_tikz.py`、`<mm-graphics目录>/scripts/audit_tikz.py`、`<mm-graphics目录>/scripts/render_svg.py`、`<mm-graphics目录>/scripts/audit_svg.py` |
| 6a | 写作轮 | `mm-paper-writing` | `paper/论文.tex|pdf`、`paper/skill-read-receipt.json`、`paper/writing-audit.md` | 11 项论文机检（见 `paper-final-checks.md`） |
| 6b | 独立审查轮 | `mm-paper-writing` | `paper/review-findings.md`、`paper/review-audit.md`、修订后的 `paper/论文.tex|pdf` | 同上 + `validate_requirement_coverage.py` |
| 7 | 验收 | `mm-verification` | `docs/06-verification-report.md` | manifest schema 校验 + 各阶段机检复跑 |

## 阶段依赖与并行

- **严格串行**：1→2→3→4→6a→6b→7。
- **可并行**：5a（数据图）与 5b（非数据图），按适用性同时调用；任一标 `n_a` 不影响另一阶段。
- **写作轮 6a 与图件 5a/5b 的依赖**：6a 启动前 5a/5b 必须 `complete` 或 `n_a`，且 `paper/figure-requirements.md` 已由对应 skill 填写完整。

## `n_a` 与范围化验收

- 某一阶段不适用时，在 `plan.md` 注明原因并将 manifest 对应 `stages.<name>.status` 标 `n_a`。
- 范围化验收不要求 `n_a` 阶段产物，但最终总结必须说明本次未做的范围。
- 不得以 "n_a" 为由声称"全流程完成"。

## 阶段状态机

`pending → in_progress → {complete | failed | n_a}`。

- `complete` 前必须登记产物哈希、版本、`change_log`，并跑对应机检 exit 0。
- `failed` 时由编排器发起 `rework[]`，指定 owner skill 修复后回到 `in_progress`。
- 验收阶段额外允许 `conditional`，但仅限非关键缺陷；数据真实性、核心结果不可复现、关键数字不一致、编译失败、硬性格式违规必须为 `failed`。

## 调度职责

- 编排器在每个阶段开始前**回显**：当前阶段、负责 skill、将读取的上游报告、将产出的文件、对应机检脚本。
- 每个阶段开始前输出 **GATE 确认**：上游产物存在、必读规范已读、计划产出明确；缺上游先补齐再进下一阶段。
- 每个阶段结束更新 manifest 中自己负责的阶段状态、产物哈希和版本；发生回写时追加 `change_log`。
- 详细门禁协议见 `checkpoint-gates.md`。

## 阶段产物未通过验收前

不得声称"全流程完成"。`mm-verification` 只审计、定位并指定回写阶段；本 skill 负责调用对应 skill 修复后再次验收。