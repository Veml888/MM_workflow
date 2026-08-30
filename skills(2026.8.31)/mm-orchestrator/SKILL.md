---
name: mm-orchestrator
description: 全国大学生数学建模竞赛（CUMCM）全流程编排入口。当用户要开始国赛建模、说"开始建模"、"做这道国赛题"、"跑完整流程"、"写数模论文"，或需要按阶段调度赛题分析、建模求解、编程实现、图表生成、流程与示意图绘制、论文撰写时使用。本 skill 负责询问关键偏好、生成 plan.md、todo.md、project-manifest.json 与论文结构规划/图需求，并调度下游阶段 skill。
---

<!-- READ-PREAMBLE:v1 -->

> **本技能文件较长，务必先完整读取再执行。** ①先用 `read_complete.py` 量出本文件总行数、列出全部 `##/###` 标题并给出分块范围；②按 `[起始–结束]` 分块读取本文件，不要一次整读；③确认任一次读取无 `truncated`，且分块覆盖到文件末尾、所有标题都被读到；④在读全之前不执行本技能的任何动作；某段被截断就立即补读，读全后再开始。
>
> **工具与路径（全部相对本 SKILL.md 所在目录解析，skills 目录整体搬移或换机无需改动）**：`read_complete.py` 位于 `../mm-paper-writing/scripts/read_complete.py`；量取本文件行数/标题/分块用 `python ../mm-paper-writing/scripts/read_complete.py analyze --path <本文件路径>`；文中 `<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`。脚本内部路径自解析、可在任意工作目录运行；但脚本参数中的相对路径（如 `paper/page-budget.json --root .`）相对当前工作目录解析，机检一律在 PROJECT_ROOT 下执行。

<!-- /READ-PREAMBLE -->


# 数学建模全流程编排

本 skill 是 CUMCM 数模 skills 的总控入口，不替代任何阶段 skill。它只做三件事：**问清偏好 → 建立计划与交接清单 → 调度各阶段 skill**。

跨阶段不变量遵循 `references/cumcm-shared-policy.md`；阶段专属细则以负责产物的 owner skill 及其直接引用的 references 为准。机器可读交接遵循 `references/project-manifest-contract.md` 和 `project-manifest.schema.json`。开始前完整读取这三份文件和 `references/project-layout.md`。

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

### 第 3 步：生成 plan.md、todo.md、project-manifest.json 与论文策划文件

按 `references/project-layout.md` 的骨架，在当前项目根目录创建：

- `plan.md`：整体方案。包含：题目概述、用户偏好、阶段顺序、每阶段负责的 skill 与预期产出文件、风险控制。
- `todo.md`：阶段性待办清单，每阶段一条，勾选进度。
- `project-manifest.json`：按 `references/project-manifest-contract.md` 初始化，登记阶段状态、稳定 ID、文件哈希与回写版本。
- 初始化论文文件时只创建空骨架：`paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md` 和 `paper/writing-gates.md`。此时 `stages.paper_plan.status` 必须保持 `pending`，不得填写虚构的章节预算、结果证据或图件需求；正式策划在分析、建模和编程全部完成后执行。

`plan.md` 中的阶段依赖固定为：

| 序 | 阶段 | skill | 关键产出 |
|---|---|---|---|
| 1 | 赛题分析 | `mm-problem-analysis` | `docs/01-analysis-report.md` |
| 2 | 建模求解 | `mm-modeling` | `docs/02-modeling-report.md` |
| 3 | 编程实现 | `mm-coding` | `code/`、`results/`、`docs/03-results-report.md` |
| 4 | 论文策划定稿（初稿审计 + 结构规划 + 页面预算 + 图件骨架） | `mm-orchestrator` | `paper/draft-audit.md`、`paper/draft-metrics.json`、`paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md`、`paper/writing-gates.md` |
| 5a | 数据图（按需） | `mm-figures` | `figures/*.png/pdf/svg`、`docs/04-figures-report.md` |
| 5b | 非数据图（逻辑/框架/机理图 + 视觉示意图；完整论文必做示意图） | `mm-graphics` | `figures/*.tex|pdf|png`（逻辑图）、`figures/*.png`（视觉图，可选 `*.svg`）、`docs/05-diagrams-report.md`、`docs/05-visual-report.md` |
| 6a | 论文终稿第一轮（完整成稿） | `mm-paper-writing` | `paper/论文.tex`、`paper/论文.pdf`、`paper/skill-read-receipt-pass-1.json`、`paper/pass-1-audit.md` |
| 6b | 论文终稿第二轮（重新完整读全部模块后独立终审） | `mm-paper-writing` | 修订后的 `paper/论文.tex`、`paper/论文.pdf`、`paper/skill-read-receipt-pass-2.json`、`paper/pass-2-audit.md` |
| 7 | 验收 | `mm-verification` | `docs/06-verification-report.md` |

### 流程策划：初稿接管、结构规划与图件骨架

分析、建模和编程完成后，基于 `docs/01~03`、`results/` 与 `plan.md` 正式定稿论文策划；初始化阶段的空骨架不能直接通过本阶段。

**初稿接管（如存在）**：若此时 `paper/论文.tex` 已存在且尚未由 `paper_final` 产出，将其精确改名为 `paper/draft-baseline.tex`，保留原文件并记录 SHA256，不得直接覆盖；能够编译时生成 `paper/draft-baseline.pdf`，用 `<mm-paper-writing目录>/scripts/check_paper_length.py --draft` 记录基线页数。编排器只做只读比较和缺口规划，不改写初稿正文。若已有 `draft-baseline.*`，不得覆盖；若无初稿，记录 `draft.mode=none`。

- `paper/draft-audit.md`：逐章将初稿内容标记为“保留 / 改写 / 删除 / 补充”，核对题意、最终模型、公式符号、真实结果、图件锚点、题面覆盖、占位符与模板化段落；冲突一律以上游报告、结果和 manifest 为准。
- `paper/draft-metrics.json`：记录初稿模式、路径、SHA256、总页数/正文页数、各章起始页和可编译状态；没有初稿时仍生成并写明 `mode=none`。

- `paper/structure-plan.md`（内容，由编排器建）：章节骨架 + 逐问论证链 + 预计篇幅。章节按固定论文结构；每问写清核心论证链（承接 → 建模 → 求解 → 结果表 → 结果分析）与预计篇幅，并建立"题面要求/子问题 → 正文小节 → 模型变量与约束 → 结果证据 → 最终回答"的追踪关系（供 `mm-verification` 逐项验收）。
- `paper/page-budget.json`（机器可读预算）：`target_body_pages` 只能为 28 或 29，`allowed_range` 固定 `[27,30]`；每章记录 `min_pages/target_pages/max_pages`、真实 `source_paths` 与 `evidence_ids`，各章目标页数之和必须等于总目标。预算按问题难度和证据量分配，不平均分配、不以空泛内容补页。

正式预算使用以下内联结构（初始化时可为空，定稿时不得保留占位符）：

```json
{
  "schema_version": "1.0",
  "target_body_pages": 28,
  "allowed_range": [27, 30],
  "draft": {"mode": "none"},
  "sections": [
    {
      "id": "SEC-FRONT", "title": "前部章节", "min_pages": 3, "target_pages": 4, "max_pages": 5,
      "source_paths": ["docs/01-analysis-report.md", "docs/02-modeling-report.md"], "evidence_ids": ["P-01", "SYM-001"]
    },
    {
      "id": "SEC-P01", "title": "问题一模型建立与求解", "min_pages": 8, "target_pages": 10, "max_pages": 11,
      "source_paths": ["docs/02-modeling-report.md", "docs/03-results-report.md"], "evidence_ids": ["P-01", "R-P01-001"]
    },
    {
      "id": "SEC-P02", "title": "问题二模型建立与求解", "min_pages": 9, "target_pages": 11, "max_pages": 12,
      "source_paths": ["docs/02-modeling-report.md", "docs/03-results-report.md"], "evidence_ids": ["P-02", "R-P02-001"]
    },
    {
      "id": "SEC-CLOSE", "title": "评价与收尾", "min_pages": 2, "target_pages": 3, "max_pages": 4,
      "source_paths": ["plan.md", "docs/03-results-report.md"], "evidence_ids": ["REQ-001", "R-P02-001"]
    }
  ]
}
```
- `paper/figure-requirements.md`（**空骨架**，只建框不填内容）：分"数据图 / 非数据图"两区，并写明图件边界规则（见下）。**具体画哪些图、图种、锚点由 `mm-figures` / `mm-graphics` 自行决定并填入对应区**；编排器只保证骨架存在、两区清晰、边界一致，不预决定。视觉示意图（如题目需要）由 `mm-graphics` 视觉示意图路线落实。
- `paper/writing-gates.md`：写入 G-1~G-5 的初始 `pending` 状态（G-1 必读已读 / G-2 图表齐全 / G-3 上游数据 / G-4 结构拟定 / G-5 工具就绪），供论文终稿阶段的写作前门禁使用。

正式策划结束前运行 `python <mm-orchestrator目录>/scripts/validate_paper_plan.py paper/page-budget.json --root .`。只有脚本 exit 0、结构计划无占位、初稿审计完成且相关产物已登记哈希时，才能把 `stages.paper_plan.status` 置为 `complete`；否则不得进入图件阶段。

图件边界（决定某图归哪个 skill，具体写在 `figure-requirements.md` 骨架中，供图件 skill 遵守）；下列规则分别以 `mm-figures` 与 `mm-graphics` 的 owner 细则为准：

- 数据图（基于真实结果：折线/柱状/散点/热力/曲面/灵敏度/多帧）→ `mm-figures`；
- 技术路线、总体框架、模型结构、指标体系、变量关系、验证闭环、复杂自研算法流程图 → `mm-graphics`（常规求解步骤用正文，不画流程图）；
- 题目场景、空间关系、对象交互、算法原理隐喻等非数据、非流程纯视觉示意图 → `mm-graphics` 的视觉示意图路线（按题需要，无适用场景标记 `n_a`）。

论文固定结构（策划与终稿共用，详见 `mm-paper-writing/references/common-paper-rules.md` 与 `references/writing-order.json`）：

```text
一、问题重述（1.1 背景 / 1.2 提出）
二、问题分析（逐问一小节，不另设“各问之间的联系”汇总小节）
三、模型假设（2–8 条，编号列表）
四、符号说明（表格：符号 | 含义）
五、模型的建立与求解（外层按问题顺序，允许条件性的公共数据处理；内层标题按内容生成）
六、模型评价与推广（优点 + 真实缺点 + 改进/推广；模型对比、检验、灵敏度与鲁棒性按需嵌入对应位置）
AI 工具使用声明 / 参考文献 / 附录（不加顺序序号）
```

### 第 4 步：按序调用阶段 skill

- 先完成分析、建模和编程，再正式完成初稿审计、结构计划、页面预算与图件骨架；`validate_paper_plan.py` 必须 exit 0 且 `paper_plan.status=complete`。随后 `mm-figures` 与 `mm-graphics` 两个分支按适用性并行调用，全部完成或标记 `n_a` 后再进入论文终稿。
- 论文终稿阶段固定连续调用 `mm-paper-writing` 两次。每次调用都先运行该 skill 的 `scripts/read_complete.py plan`，再按计划逐块读取 `references/writing-order.json` 登记的全部必读文件；每块必须出现 `READ-END`，并以本轮独立读取回执通过 `read_complete.py verify` 为准。第二次不得复用第一次回执、上下文或“已读”结论。
- 第一次调用结束后生成 `paper/skill-read-receipt-pass-1.json` 与 `paper/pass-1-audit.md`，把 `paper_final.full_skill_passes` 记为 `1`，但 `paper_final.status` 保持 `in_progress`。随后立即进行第二次独立调用，以第一次终稿为审查和修订对象，重新运行双遍编译及全部专项机检，生成第二轮回执与审计。
- 两轮审计都必须覆盖注册表中的每个必读文件及其全部二/三级标题，并通过 `validate_requirement_coverage.py`。只有第二次无阻断项、`paper_final.full_skill_passes=2`、两轮回执和审计路径均已登记哈希时，才能把 `paper_final.status` 置为 `complete` 并进入 `mm-verification`；否则继续留在论文终稿阶段。
- `mm-graphics` 负责技术路线、总体框架、模型结构、指标体系、变量关系、验证闭环（逻辑图，TikZ）与题目场景/空间/交互/算法隐喻（视觉示意图，imagegen）；只有复杂自研算法才允许算法流程图。题目需要场景/机理视觉示意时，可由 `mm-graphics` 的视觉示意图路线生成纯视觉示意图；无适用场景标记 `n_a`。
- 每个阶段开始前，回显：当前阶段、负责 skill、将读取的上游报告、将产出的文件。
- 每个阶段开始前输出 GATE 确认：上游产物存在、必读规范已读（引用原文）、计划产出明确；缺上游先补齐再进下一阶段。
- 每阶段结束后更新 `project-manifest.json` 中自己负责的阶段状态、产物哈希和版本。发生回写时追加 `change_log`，记录原因和受影响 ID。
- 若某一阶段被跳过或不适用，在 `plan.md` 中注明原因，并将 manifest 对应阶段标记为 `n_a`；范围化验收不要求 `n_a` 阶段产物，但最终总结必须说明范围。
- 阶段产物未通过 `mm-verification` 前，不得声称"全流程完成"。
- `mm-verification` 只审计、定位并指定回写阶段；本 skill 负责调用对应 skill 修复后再次验收。
- 每个阶段完成前运行 `<mm-orchestrator目录>/scripts/validate_manifest.py` 及该阶段的**机检脚本**：paper_plan 用 `validate_paper_plan.py`，coding 用 `check_reproducibility.py`，paper_final 的两次独立调用都用 `check_paper_length.py`、`check_paper_refs.py`、`check_layout.py` 及论文专项脚本，figures 用 `check_figure_overlap.py`。**PASS 一律以脚本 exit 0 为准，禁止手写 PASS**。任一脚本 FAIL 不得继续下游，先返回该阶段修正；验收发现的问题写入 `rework[]`，按影响范围重新调用目标阶段及下游阶段。

## 边界

- 本 skill 不亲自解题、不写模型、不画图、不写论文正文——只编排与调度。
- 不覆盖 `PROJECT_ROOT` 之外的任何既有文件；输入附件只读。
