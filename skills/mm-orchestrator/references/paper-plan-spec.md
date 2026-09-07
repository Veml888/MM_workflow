# 论文策划（paper_plan）阶段规范

> 本阶段由 `mm-orchestrator` 直接产出（在分析、建模、编程完成后调用一次），不调用其它 skill 做策划。字段级约束见 `page-budget-schema.md`；初稿接管细节见 `draft-takeover.md`；图件边界见 `figure-boundary.md`。

## 阶段定位

- 阶段名：`paper_plan`（manifest `stages.paper_plan`）。
- 触发时机：阶段 1/2/3（分析、建模、编程）全部 `complete` 后；阶段 4 之前。
- 不在阶段 0（项目初始化）就定稿——初始化时只建空骨架，状态保持 `pending`，详见下方"初始化骨架"。

## 初始化骨架（第 3 步统一建，状态保持 pending）

阶段 3（生成 plan.md / todo.md / manifest）时，同步在 `paper/` 下建 4 份空骨架 + `paper/writing-gates.md`（G-1~G-5 全 pending）。可用脚本：

```bash
python <mm-orchestrator目录>/scripts/init_project_skeleton.py --root <PROJECT_ROOT>
python <mm-orchestrator目录>/scripts/init_paper_gates.py --root <PROJECT_ROOT>
```

初始化骨架的内容约束：

- `paper/structure-plan.md`：可留空，仅含标题占位。
- `paper/page-budget.json`：必须包含顶层 `target_body_pages`、`allowed_range`、`sections`、`draft` 四项；`sections` 可先为空数组，`draft.mode` 写 `none`。
- `paper/figure-requirements.md`：分"数据图 / 非数据图"两区，各区写明边界规则（图件归哪个 skill）；具体画哪些图暂不写。
- `paper/writing-gates.md`：G-1~G-5 各一条 `pending` 记录。

初始化阶段**不得**填虚构的章节预算、结果证据或图件需求；正式定稿在本阶段正式调用时完成。

## 正式定稿（本阶段唯一一次完整调用）

正式定稿前必须先具备：① `docs/01-analysis-report.md` 已 complete；② `docs/02-modeling-report.md` 已 complete；③ `docs/03-results-report.md` 已 complete；④ `results/` 已有真实数值结果。任意上游缺失则回到上游阶段补齐后再来。

定稿产出 6 份文件：

1. `paper/draft-audit.md`：若用户提供了初稿，先按 `draft-takeover.md` 完成接管；无论有无初稿，都要逐章标记"保留 / 改写 / 删除 / 补充"，核对题意、最终模型、公式符号、真实结果、图件锚点、题面覆盖、占位符与模板化段落；冲突一律以上游报告、结果和 manifest 为准。
2. `paper/draft-metrics.json`：记录初稿模式、路径、SHA256、总页数/正文页数、各章起始页和可编译状态；没有初稿时仍生成并写明 `mode=none`。
3. `paper/structure-plan.md`：章节骨架 + 逐问论证链 + 预计篇幅。**章节骨架以 `mm-paper-writing/references/common-paper-rules.md` 的"整体论文骨架"与 `mm-paper-writing/references/writing-order.json` 的章节清单为唯一权威**；每问独立成章、模型评价与推广单独一章这类结构编排不在此重复。每问写清核心论证链（承接 → 建模 → 求解 → 结果表 → 结果分析）与预计篇幅，并建立"题面要求/子问题 → 正文小节 → 模型变量与约束 → 结果证据 → 最终回答"的追踪关系（供 `mm-verification` 逐项验收）。
4. `paper/page-budget.json`：`target_body_pages` 只能为 28 或 29，`allowed_range` 固定 `[25, 30]`；每章记录 `min_pages/target_pages/max_pages`、真实 `source_paths` 与 `evidence_ids`，各章目标页数之和必须等于总目标。预算按问题难度和证据量分配，不平均分配、不以空泛内容补页。**目标页数 28/29 是为分页波动留余量；实际正文允许到 30 页，`check_paper_length` 以 `allowed_range` 兜底，不因低于 30 而判过预算缺陷**。字段细节见 `page-budget-schema.md`。
5. `paper/figure-requirements.md`：分"数据图 / 非数据图"两区，**具体画哪些图、图种、锚点由 `mm-figures` / `mm-graphics` 自行决定并填入对应区**；本阶段只保证骨架存在、两区清晰、边界一致，不预决定。场景/空间类精确示意图（如题目需要）由 `mm-graphics` 按题面事实用 TikZ/SVG 绘制。边界规则见 `figure-boundary.md`。
6. `paper/writing-gates.md`：写入 G-1~G-5 的初始 `pending` 状态（G-1 必读已读 / G-2 图表齐全 / G-3 上游数据 / G-4 结构拟定 / G-5 工具就绪），供论文终稿阶段的写作前门禁使用。

## 完成门禁

正式定稿结束前运行：

```bash
python <mm-orchestrator目录>/scripts/validate_paper_plan.py paper/page-budget.json --root .
```

**只有脚本 exit 0、结构计划无占位、初稿审计完成且相关产物已登记哈希时，才能把 `stages.paper_plan.status` 置为 `complete`；否则不得进入图件阶段。**

字段级校验（占位符、`draft.mode`、source_paths 存在性、target 之和等）以脚本输出为准；脚本比正文更权威。

## 与下游阶段的接力

- 本阶段 `complete` 后才能调度 `mm-figures` / `mm-paper-writing`。
- `mm-figures` 与 `mm-graphics` 各自只填 `figure-requirements.md` 属于自己的区，不改对方的区。
- 写作轮 6a 启动前需重读 `paper/writing-gates.md`，把 G-1~G-5 全部置 `pass`。