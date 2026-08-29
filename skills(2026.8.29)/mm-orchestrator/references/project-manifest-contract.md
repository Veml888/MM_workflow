# project-manifest.json 交接契约

`project-manifest.json` 是九个数模 skills 的机器可读交接中心；Markdown 报告继续保留，负责完整论证。manifest 只登记可验证事实、路径、状态和溯源，不复制长篇正文。

## 最小结构（schema 2.0）

```json
{
  "schema_version": "2.0",
  "competition": "CUMCM-2026",
  "project": {"title": "", "language": "zh-CN"},
  "stages": {
    "analysis": {"status": "pending", "report": "docs/01-analysis-report.md"},
    "modeling": {"status": "pending", "report": "docs/02-modeling-report.md"},
    "coding": {"status": "pending", "report": "docs/03-results-report.md"},
    "figures": {"status": "pending", "report": "docs/04-figures-report.md"},
    "graphics": {"status": "pending", "report": "docs/05-diagrams-report.md"},
    "paper_plan": {"status": "pending", "report": "paper/structure-plan.md", "gates": "paper/writing-gates.md", "page_budget": "paper/page-budget.json", "draft_audit": "paper/draft-audit.md"},
    "paper_final": {"status": "pending", "draft_mode": "none", "full_skill_passes": 0},
    "verification": {"status": "pending", "report": "docs/06-verification-report.md"}
  },
  "requirements": [],
  "problems": [],
  "datasets": [],
  "assumptions": [],
  "model_candidates": [],
  "selected_models": [],
  "implemented_models": [],
  "validation_plans": [],
  "paper_gates": [],
  "symbols": [],
  "results": [],
  "figures": [],
  "artifacts": [],
  "rework": [],
  "change_log": []
}
```

## 字段规则

- `schema_version` 固定为 `2.0`，本工作流只创建新项目，不提供 1.0 迁移逻辑。
- 阶段 `status` 只能是 `pending`、`in_progress`、`complete`、`failed`、`n_a`；只有 `verification.status` 可以额外使用 `conditional`。
- 要求、子问题、数据集、假设、候选模型、符号、结果和图件必须有稳定唯一 `id`；下游引用该 ID，不靠报告章节号、显示名称或数组位置猜测。推荐前缀为 `REQ-###`、`P-##`、`DS-###`、`A-###`、`MC-P##-##`、`SYM-###`、`R-P##-###`、`FIG-###`。
- `requirements[]` 至少记录 `id`、`problem_id`、`text`、`source_location`、`expected_output`、`verification`；题面硬性要求必须逐条登记。
- `problems[]` 至少记录 `id`、`label`、`statement`、`requirement_ids`、`dataset_ids`、`depends_on`、`output_contract`；依赖只引用稳定 ID。
- `datasets[]` 至少记录 `id`、`path`、`sha256`、`role`、`format`、`schema_or_fields`、`audit_status`；输入文件保持只读，派生数据另登记 artifact。
- `assumptions[]` 至少记录 `id`、`problem_ids`、`text`、`basis`、`status`；分析阶段使用 `candidate`，建模阶段只能通过回写记录将其改为 `accepted` 或 `rejected`。
- `model_candidates[]` 至少记录 `id`、`problem_id`、`name`、`rank`、`dataset_ids`、`assumption_ids`、`selection_evidence`、`baseline`、`rejection_criteria`。
- `selected_models[]` 至少记录 `id`、`problem_id`、`candidate_id`、`name`、`assumption_ids`、`objective_or_role`、`selection_basis`、`validation_plan_ids`、`status`；它记录建模阶段最终确认的模型，不删除候选模型。
- `implemented_models[]` 至少记录 `id`、`selected_model_id`、`problem_id`、`code_paths`、`entrypoint`、`result_ids`、`status`；它记录编程阶段实际实现的模型。
- `validation_plans[]` 至少记录 `id`、`problem_id`、`type`、`requested_by`、`plan`、`execution`、`verification`。同一 ID 从分析需求贯穿到建模细化、编程执行和验收核对。
- `paper_gates[]` 至少记录 `id`、`gate`、`status`、`evidence_path`、`evidence_summary`、`checked_at`；论文策划阶段（`mm-orchestrator`）创建 G-1~G-5 的 `pending` 记录，终稿前全部置为 `pass`。
- `results[]` 至少记录 `id`、`problem_id`、`metric`、`value_or_file`、`source_script`、`source_input`。
- `figures[]` 至少记录 `id`、`kind`、`files`、`source_result_ids`、`caption`、`paper_anchor`、`version`。
- `artifacts[]` 至少记录 `path`、`sha256`、`producer_stage`、`version`。
- `rework[]` 至少记录 `id`、`source`、`target_stage`、`affected_stages`、`issue`、`severity`、`status`、`created_at`、`resolved_at`；阻断性返工必须关闭后才能通过验收。
- 任一回写必须追加 `change_log`：时间、发起阶段、目标阶段、原因、受影响 ID 和新版本。
- 每个阶段开始时读取 manifest，结束时只更新自己负责的字段；不得删除未知字段或改写其他阶段的已完成记录。

## 阶段所有权

- `analysis` 创建和维护 `requirements`、`problems`、`datasets`、`model_candidates`、候选 `assumptions` 和验证需求，并登记 `docs/01-analysis-report.md`。分析可以写变量/目标/约束和公式骨架，但必须标记为候选。
- `modeling` 创建和维护 `selected_models`、正式 `assumptions` 状态、`symbols` 和 `validation_plans.plan`，并登记 `docs/02-modeling-report.md`。正式公式、参数、假设和求解算法由本阶段定型。
- `coding` 创建和维护 `implemented_models`、`results` 和 `validation_plans.execution`，并登记 `docs/03-results-report.md`。
- `paper_plan`（论文策划，由 `mm-orchestrator` 产出）初始化空骨架时保持 `pending`；分析、建模和编程完成后冻结/登记可选初稿，创建 `paper/draft-audit.md`、`paper/draft-metrics.json`、正式 `structure-plan.md`、`page-budget.json`、`figure-requirements.md` 与 `writing-gates.md`。只有 `validate_paper_plan.py` exit 0、预算目标28～29页且产物哈希已登记时才能 `complete`。
- `figures` 只创建数据图、`graphics` 创建非数据图（逻辑/框架/机理图 + 视觉示意图，含 `docs/05-visual-report.md`），二者只创建自己负责的图件、报告和 `figures[]` 记录，不修改论文源文件；缺少适用性时标记对应阶段为 `n_a`。
- `paper_final` 独占 `paper/论文.tex`、`paper/论文.pdf` 的写入权；初稿基线只读且不得覆盖。完整流程必须独立调用 `mm-paper-writing` 两次，每次都重新完整读取该 skill、将 G-1~G-5 全部复核为 `pass`，生成对应轮次审计，并在该次调用内多轮编译直至正文27～30页和全部专项机检通过。第一轮结束保持 `in_progress`；第二轮通过后才可 `complete`。
- `verification` 只审计、创建 `rework[]` 和验收报告，不直接修改上游产物；`conditional` 只允许非关键问题。
- 下游阶段可以引用这些 ID、补充自己负责的字段；发现上游事实错误时必须通过 `change_log` 发起回写，不得静默改写。
- 阶段置为 `complete` 前，必须登记本阶段必需产物的 SHA256 和版本；缺失、占位或门禁未通过时不得标记完成。

## 状态与回写规则

- 稳定 ID 永不复用。返工产生新版本或新 ID，旧记录保留并标记 `rejected`、`superseded` 或 `invalidated`。
- `verification=conditional` 只表示非关键缺陷；数据真实性、核心结果不可复现、关键数字不一致、编译失败和硬性格式违规必须为 `failed`。
- 返工后按 `affected_stages` 重验目标阶段及其下游阶段；目标阶段只有在 manifest Schema 校验通过、产物哈希更新且返工项关闭后才能完成。
- 所有阶段结束、验收开始和返工关闭前运行 `project-manifest.schema.json` 校验。建议使用 `<mm-orchestrator目录>/scripts/validate_manifest.py`，仅依赖 Python 标准库；若环境安装了 `jsonschema`，可额外执行完整 Schema 校验。

## 论文阶段完成字段

- `paper_plan.status=complete` 时必须登记：`report`、`gates`、`page_budget`、`draft_audit`、`draft_metrics`、`planned_body_pages`（28或29）、本阶段产物哈希和版本。
- `paper_final.draft_mode` 只能是 `retained`、`partial`、`invalidated`、`none`。有初稿时登记 `draft_path`、`draft_sha256`、`draft_body_pages`；无初稿时三项使用 `null`。
- `paper_final.status=complete` 时必须登记：`planned_body_pages`、`final_body_pages`（27～30）、`length_audit`、`content_gap_report`、`compile_passes`（两轮合计至少4）、`full_skill_passes=2`、`first_pass_audit`、`second_pass_audit`、论文TeX/PDF及两轮审计文件的哈希与版本。缺任一字段、任一轮未完整读取 skill、页数越界或任一轮专项脚本非零，不得标记完成，也不得进入 `mm-verification`。
