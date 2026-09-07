# mm-orchestrator 速查卡

> 一页纸：拿到任务时按这个跑。细节按需打开 `references/`：流水线 `stage-pipeline.md`、论文策划 `paper-plan-spec.md` / `page-budget-schema.md`、论文终稿机检 `paper-final-checks.md`、初稿接管 `draft-takeover.md`、图件边界 `figure-boundary.md`、阶段门禁 `checkpoint-gates.md`。

## 触发条件

- 用户说"开始建模 / 跑完整流程 / 做这道国赛题 / 写数模论文"。
- 适用范围：**全国大学生数学建模竞赛（CUMCM）**；不绑定年份；其他竞赛不适用。

## 两条硬约束

- **编程语言 = Python（不问）**。除非用户显式要 MATLAB，否则一律 Python，并把 `python` 写入 `plan.md` 与各阶段交割。
- **只问 2 项偏好**：① 侧重点（精度/可解释/速度/均衡）② 子问题数量（已知 N 个 / 待分析确定）。其余能推断的不问。

## 7 阶段流水线（一图流）

| # | 阶段 | skill | 关键产出 |
|---|---|---|---|
| 1 | 赛题分析 | `mm-problem-analysis` | `docs/01-analysis-report.md` |
| 2 | 建模求解 | `mm-modeling` | `docs/02-modeling-report.md` |
| 3 | 编程实现 | `mm-coding` | `code/`、`results/`、`docs/03-results-report.md` |
| 4 | 论文策划 | `mm-orchestrator`（本 skill） | `paper/draft-audit.md`、`paper/draft-metrics.json`、`paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md`、`paper/writing-gates.md` |
| 5a | 数据图 | `mm-figures` | `figures/*.png/pdf/svg`、`docs/04-figures-report.md` |
| 5b | 非数据图 | `mm-graphics` | `figures/*.tex|pdf|png`、`docs/05-diagrams-report.md` |
| 6a | 写作轮 | `mm-paper-writing` | `paper/论文.tex|pdf`、`paper/skill-read-receipt.json`、`paper/writing-audit.md` |
| 6b | 独立审查轮 | `mm-paper-writing` | `paper/review-findings.md`、`paper/review-audit.md`、修订后的 `paper/论文.tex|pdf` |
| 7 | 验收 | `mm-verification` | `docs/06-verification-report.md` |

阶段 5a/5b 按适用性并行；阶段 6a/6b 严格串行。详见 `stage-pipeline.md`。

## 第 3 步的产物清单

- `plan.md`、`todo.md`、`project-manifest.json`（机器可读）
- `paper/` 4 个空骨架：`structure-plan.md`、`page-budget.json`、`figure-requirements.md`、`writing-gates.md`（G-1~G-5 全 pending）
- 建议直接跑 `python <mm-orchestrator目录>/scripts/init_project_skeleton.py --root <PROJECT_ROOT>` 一次建齐；详见脚本说明。

## 阶段 PASS 的硬证据

- 每个阶段 `complete` 前必须以**真实产物 + 哈希 + 版本 + 该阶段机检 exit 0** 为据；禁手写 PASS。
- 论文终稿阶段（写作轮 + 独立审查轮）跑全套论文机检，详见 `paper-final-checks.md`。
- 验收前运行 `validate_manifest.py` + 各阶段机检脚本；详见 `checkpoint-gates.md`。

## 编排器只做调度、不亲自解题

不写模型、不画图、不写论文正文、不改 `PROJECT_ROOT` 之外的文件。冲突一律以 owner skill 的细则与上游产物为准。