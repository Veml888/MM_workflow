# 论文终稿机检与门禁

> 本文件登记论文终稿阶段（写作轮 6a + 独立审查轮 6b）跑的全部机检脚本与门禁字段。编排器在 `stages.paper_final` 状态置 `complete` 前必须确认本文件列举的全部 exit 0；明细以 owner skill 的细则为准。

## owner 与权威

- `mm-paper-writing` 拥有论文终稿的全部细则与机检；本文件只是其 `references/workflow-and-gates.md` 的镜像清单，**以 mm-paper-writing 为权威**。
- 编排器只负责：① 在 paper_plan 阶段把 `paper/writing-gates.md` 的 G-1~G-5 初始化成 `pending`；② 在 paper_final 阶段 `complete` 前核对本表清单全部 PASS；③ 跑 `<mm-orchestrator目录>/scripts/validate_manifest.py` 校验 manifest。

## 论文阶段读取与覆盖机检

编排器在 paper_plan `complete` 与 paper_final `complete` 前还需确认：

- `<mm-paper-writing目录>/scripts/read_complete.py`：写作轮必读文件读取完整性（`verify` exit 0）。
- `<mm-paper-writing目录>/scripts/validate_requirement_coverage.py`：题面要求 ↔ 正文小节 ↔ 模型变量/约束 ↔ 结果证据 ↔ 最终回答五元组覆盖校验。

这两条由 `mm-paper-writing` 在写作轮与独立审查轮分别触发；脚本路径以 owner skill 为权威。

## 11 项论文机检脚本

全部位于 `<mm-paper-writing目录>/scripts/`，仅依赖 Python 标准库或论文项目内的 LaTeX 编译结果：

| # | 脚本 | 检查内容 | exit 0 含义 |
|---|---|---|---|
| 1 | `check_paper_length.py` | 正文页数 ∈ `[25, 30]` | 通过 |
| 2 | `check_line_spacing.py` | 行距、段距合规 | 通过 |
| 3 | `check_noindent.py` | 首行缩进 2 字符（中文约定） | 通过 |
| 4 | `check_quotes.py` | 中英文标点不混用、错位闭合 | 通过 |
| 5 | `check_abstract_symbols.py` | 摘要符号与正文一致、不出现超纲符号 | 通过 |
| 6 | `audit_paper_tables.py` | 表格三线表、跨页续表四件套、末底线唯一 | 通过 |
| 7 | `audit_submission_language.py` | 提交稿语言一致性（中文为主、英文段合规） | 通过 |
| 8 | `audit_abstract_page.py` | 摘要在第 1 页或第 2 页顶部 | 通过 |
| 9 | `check_paper_cites.py` | 正文引文与参考文献条目对得上 | 通过 |
| 10 | `check_paper_refs.py` | 参考文献条目格式、重复检测 | 通过 |
| 11 | `check_layout.py` | 版心、页边距、页眉页脚、图表题注一致性 | 通过 |

额外：写作轮结束后还须跑 `validate_requirement_coverage.py`，确认每个 `REQ-###` / `P-##` 都有正文小节、模型变量/约束、结果证据、最终回答可定位。

**PASS 一律以脚本 exit 0 为准，禁止手写 PASS。** 任一脚本 FAIL 不得继续下游，先返回该阶段修正。

## G-1~G-5 写作门禁

写在 `paper/writing-gates.md`，由 `init_paper_gates.py` 初始化成 `pending`；写作轮启动前由 `mm-paper-writing` 全部置 `pass`。

| ID | 含义 | 置 pass 条件 |
|---|---|---|
| G-1 | 必读已读 | `paper/skill-read-receipt.json` 生成 + `read_complete.py verify` exit 0 |
| G-2 | 图表齐全 | 数据图、非数据图全部 `complete` 或 `n_a`，且 figure-requirements.md 两区填齐 |
| G-3 | 上游数据 | `docs/01~03`、`results/`、`paper/page-budget.json` 全部已登记哈希 |
| G-4 | 结构拟定 | `paper/structure-plan.md` + `paper/draft-audit.md` 已 complete |
| G-5 | 工具就绪 | XeLaTeX / `tectonic` 可用、字体可用、模板就绪 |

## 写作轮（6a）产出物

- `paper/论文.tex`、`paper/论文.pdf`（XeLaTeX 编译）
- `paper/skill-read-receipt.json`（必读文件读取回执）
- `paper/.read-session.json`（写作轮账本，写作轮唯一）
- `paper/.read-notes-pass-<N>.md`（实质阅读证据，每文件 1~2 句要点摘录）
- `paper/writing-audit.md`（按每个必读文件及全部二/三级标题记录"已执行/不适用（含理由）/阻断"）
- `paper/page-audit.json`（正文页数审计）
- `paper/content-gap-report.md`（实质内容缺口）

写作轮结束时 `paper_final.status` 保持 `in_progress`。

## 独立审查轮（6b）产出物

- `paper/review-findings.md`（逐章发现：问题/严重度/证据/处置）
- `paper/review-audit.md`（覆盖注册表每个必读文件"已执行/不适用及理由"，并通过 `validate_requirement_coverage.py`）
- 修订后的 `paper/论文.tex|pdf`（如本轮有修订）
- 修订后复跑本表 11 项机检 + `validate_requirement_coverage.py`

审查轮无阻断项、`read_receipt`、`writing_audit`、`review_findings`、`review_audit` 均登记哈希时，`paper_final.status` 才能 `complete` 并进入 `mm-verification`。

## compile_passes

- 写作轮至少 2 遍连续编译（`check_paper_length` 每次都得 exit 0）。
- 独立审查轮有修订时修订后再加至少 2 遍。
- `manifest.stages.paper_final.compile_passes` 必须 ≥ 2（与 `project-manifest.schema.json` 校验一致）。

## 编排器在 paper_final complete 前的核对清单

1. `validate_manifest.py` exit 0。
2. 11 项论文机检 + `validate_requirement_coverage.py` 全部 exit 0。
3. G-1~G-5 全部 `pass`。
4. `compile_passes ≥ 2` 且 `final_body_pages ∈ [25, 30]`。
5. `read_receipt`、`writing_audit`、`review_findings`、`review_audit` 四份文件路径与哈希已写入 manifest。
6. `project-manifest.schema.json` 通过（如果环境装了 `jsonschema`）。