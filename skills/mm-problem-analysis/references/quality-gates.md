# 质量门禁（quality-gates）

mm-problem-analysis 阶段使用的全部门禁与机检，按三类层级登记：
- **G-PA**：阶段开工前 GATE（Step 0 自查，不入机检脚本）
- **G-READ / G-SEM**：题面复现与语义核对（problem-reading-protocol.md §6-7）
- **Q-PA**：阶段完成后质量门禁（`scripts/check_analysis_report.py` 硬机检）

凡是写 "PASS" 都必须以脚本 exit 0 或可核验证据为据；手写 PASS 视为未通过。

## 1. G-PA：阶段开工前 GATE

| ID | 含义 | 核验证据 | 通过条件 |
|---|---|---|---|
| G-PA1 | 题面可读 | 题目正文与所有附件可访问；文件路径、格式、SHA256 | 缺页、模糊扫描或附件缺失时停止实质分析并列出缺口 |
| G-PA2 | 规范已读 | 引用 `../mm-orchestrator/references/cumcm-shared-policy.md` 中"模型复杂度必须与题目难点匹配"和"凡声称稳定、优越、可靠，必须给出对应证据" | 在 `docs/01-analysis-report.md` §0 引用条款 |
| G-PA3 | 输入已盘点 | `data/` 文件清单、SHA256、格式、用途、解析状态 | 输入只读；盘点完整 |
| G-PA4 | 交付已声明 | 明确将产出 `docs/01-analysis-report.md`，并更新 manifest 的本阶段字段 | manifest 中本阶段字段已规划 |

**GATE 未通过时，只生成缺口清单，不臆测题面、字段或数据值。**

## 2. G-READ / G-SEM：题面复现门禁

由 `references/problem-reading-protocol.md` 全权定义；这里只登记通过条件：

- **G-READ**：原始题面和附件可访问、复现稿按页生成、关键内容视觉/来源核验完成、正反双向核对完成、没有未解决的关键"待确认"项。
- **G-SEM**：每个 `P-##` 均有 G-SEM 字段表；动作、对象、输入、输出和限制能回到原题位置；不存在未解决的语义分歧；关键量的图证口径已登记。

详见 `problem-reading-protocol.md` §3、§6、§7。

## 3. Q-PA：阶段完成后质量门禁

| ID | 含义 | 通过条件 | 机检 |
|---|---|---|---|
| Q-PA1 | 完整性 | 每个 `REQ-###` 都映射到 `P-##`、输出和验收方式；无遗漏附件 | `check_analysis_report.py` 通过八部分标题检查（间接保证） |
| Q-PA2 | 可追溯性 | 报告中的问题、数据、假设、候选模型均有稳定 ID，路径与 manifest 一致 | `check_analysis_report.py` 强制 ID 至少出现一次 |
| Q-PA3 | 可证伪性 | 每个首选模型都有选择证据、基线、验证指标和淘汰条件 | `check_analysis_report.py` 强制 §5 "首选"必须伴随"淘汰/弃用/局限"字样 |
| Q-PA4 | 防泄漏 | 测试集或最终评价数据未参与字段选择、规则设定或候选排序 | 允许 `N/A`（仅当题面无显式训练/测试划分） |
| Q-PA5 | 下游可执行 | 建模阶段无需重新猜测变量、数据域、目标、约束、参数上限和待确认项 | 人工自查；机检覆盖八部分标题存在 |

## 4. 机检脚本

### 4.1 `scripts/check_analysis_report.py`

- 入参：`docs/01-analysis-report.md`
- 检查项：① 八部分标题齐全；② 出现稳定 ID（`REQ-###` / `P-##` / `DS-###` / `MC-P##-##`）；③ §5 中每个"首选"候选均有"淘汰条件/局限/何时弃用"表述；④ Q-PA1~Q-PA5 门禁已填写（Q-PA4 允许 `N/A`）。
- 退出码：0 = PASS，1 = FAIL。

### 4.2 与 owner skill 的关系

- 本文件不替 `mm-orchestrator/references/paper-final-checks.md` 或 `mm-verification` 写规则。
- `mm-orchestrator/references/checkpoint-gates.md` 第 4 节登记"分析阶段机检脚本"；本文件是该脚本的语义详细版。

## 5. 命名约定（避免漂移）

| 层级 | 前缀 | 含义 |
|---|---|---|
| 阶段 GATE | `G-PA` | 开工前自查，不入机检脚本 |
| 题面复现 | `G-READ`、`G-SEM` | 复现与语义核对，独立于 G-PA |
| 阶段质量 | `Q-PA` | 完成后机检；`check_analysis_report.py` 硬门禁 |
| 论文写作 | `G-1~G-5` | 由编排器初始 pending，写作前全部置 pass |

`G-*` 表示开工前，`Q-*` 表示完成后；`PA` 前缀专属于 mm-problem-analysis，下游 skill 不得复用。