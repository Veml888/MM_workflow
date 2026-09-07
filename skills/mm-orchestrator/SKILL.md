---
name: mm-orchestrator
description: 全国大学生数学建模竞赛（CUMCM）全流程编排入口。当用户要开始国赛建模、说"开始建模"、"做这道国赛题"、"跑完整流程"、"写数模论文"，或需要按阶段调度赛题分析、建模求解、编程实现、图表生成、流程与示意图绘制、论文撰写时使用。本 skill 负责确认少量关键偏好（编程语言固定 Python 不问、侧重点、子问题数）、生成 plan.md / todo.md / project-manifest.json 与论文策划文件，并调度下游阶段 skill。
---

<!-- READ-GATE:complete -->

> **🛑 本阶段开工前的完整读取门禁（必做第一步）**
>
> **本 skill = 总控入口（mm-orchestrator）**。从你打开这份 SKILL.md 的那一刻起，下面这些动作**全都算"开工"**——任一动作之前都**必须**先按共享 read-protocol 读完本 skill 注册表里的全部 13 个文件，并拿到 `verify` exit 0：
>
> - 询问用户偏好 / 解读用户意图
> - 读题面 / 读 `data/` / 读上一阶段产物
> - 写 `plan.md` / `todo.md` / 初始化 `project-manifest.json`
> - 调度任何下游 skill（`mm-problem-analysis` / `mm-modeling` / `mm-coding` / `mm-figures` / `mm-graphics` / `mm-paper-writing` / `mm-verification`）
> - 跑 `init_project_skeleton.py` / `init_paper_gates.py` / `validate_*` 任何脚本
> - 修改任何 `paper/structure-plan.md` / `page-budget.json` / `figure-requirements.md` / `writing-gates.md`
>
> **`read_complete.py` 不是"检测脚本"——它是"强制读完 + 检测"组合机制**（chunk 子命令**强制按块打到 stdout**、write-receipt + verify **强制记账与三层 SHA256 锁定**）。跳过任何一块都会让 verify exit ≠ 0，**"声称读过"就站不住脚**。
>
> ```bash
> # Step 1: plan（列出本 skill 所有必读文件与分块边界）
> python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-orchestrator
>
> # Step 2: chunk（按 plan 输出的 chunks[] 逐块读取；缺 READ-BEGIN/READ-END 视为截断）
> echo '{"schema_version":"1.0","reads":[]}' > .read-session.json
> python <mm-orchestrator目录>/scripts/read_complete.py chunk \
>     --skill mm-orchestrator \
>     --path <rel> --start N --end M \
>     --session .read-session.json
>
> # Step 3: write-receipt（账本未覆盖全部分块会 FAIL）
> python <mm-orchestrator目录>/scripts/read_complete.py write-receipt \
>     --skill mm-orchestrator --pass 1 \
>     --receipt skill-read-receipt.json --session .read-session.json
>
> # Step 4: verify（三层 SHA256 + EOF 覆盖校验，exit 0 才算 PASS）
> python <mm-orchestrator目录>/scripts/read_complete.py verify \
>     --skill mm-orchestrator \
>     --receipt skill-read-receipt.json --session .read-session.json
> ```
>
> 共享协议完整文档（含"读完整+检测"双重角色说明）：`../mm-orchestrator/references/read-protocol.md`
> 本 skill 的注册表：`references/reading-order.json`（13 文件 / 15 块 / ~60 KB）。

<!-- /READ-GATE -->

# 数学建模全流程编排

本 skill 是 CUMCM 数模 skills 的总控入口。本文件只保留**调度面**：速查、入口选择、阶段调度、门禁协议；流水线、字段约束、机检清单、图件边界、初稿接管全部下放到 `references/`。

**工具与路径（相对本 SKILL.md 所在目录解析）**：`<本skill目录>` 即本文件所在目录；`<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`。脚本内部路径自解析，参数中相对路径相对当前工作目录解析，机检一律在 PROJECT_ROOT 下执行。

## 入口选择

1. 读取 `references/orchestrator-quickcard.md`：拿到 1 页流水线速查与硬约束。
2. 读取 `references/cumcm-shared-policy.md`：确认跨阶段不变量。

## 工作流

### 第 1 步：确认题目与 PROJECT_ROOT

- 用户可能直接给赛题 PDF/DOCX/图片，也可能只说"开始建模"。
- 没题目时，先请用户提供 CUMCM 赛题文件；本流水线不适配其他竞赛。
- 若用户未指定 PROJECT_ROOT，在当前工作目录新建一个以题目命名的文件夹。

### 第 2 步：询问关键偏好

用 `AskUserQuestion` 只问会实质影响后续阶段的问题（不超过 2 个，能推断的不要问）：

1. **侧重点**：精度优先 / 可解释性优先 / 速度优先 / 均衡。
2. **子问题数量**：已知 N 个 / 待赛题分析确定。

**编程语言固定 Python（默认，不询问）**：本工作流所有校验脚本均为 Python，图件与结果用 Python 实现最一致；除非用户显式要 MATLAB，否则一律按 Python 执行，并把 `python` 写入 `plan.md` 与各阶段交割。

### 第 3 步：生成 plan.md / todo.md / project-manifest.json + paper/ 4 份空骨架

直接跑：

```bash
python <mm-orchestrator目录>/scripts/init_project_skeleton.py --root <PROJECT_ROOT>
python <mm-orchestrator目录>/scripts/init_paper_gates.py --root <PROJECT_ROOT>
```

产物清单与字段约束：

- `plan.md`、`todo.md`、`project-manifest.json`（机器可读，schema 2.0）—— 详见 `references/project-manifest-contract.md` 与本目录的 `project-manifest.schema.json`。
- `paper/structure-plan.md`、`paper/page-budget.json`、`paper/figure-requirements.md`、`paper/writing-gates.md`（G-1~G-5 全 pending）—— 字段级约束见 `references/paper-plan-spec.md` 与 `references/page-budget-schema.md`。

此时 `stages.paper_plan.status` 必须保持 `pending`，不得填写虚构的章节预算、结果证据或图件需求；正式策划在分析、建模和编程全部完成后执行。

### 第 4 步：按序调度下游 skill

流水线定义与依赖关系见 `references/stage-pipeline.md`；每个阶段的回显、开始前 GATE 确认、结束更新 manifest 见 `references/checkpoint-gates.md`。

- 先完成分析、建模和编程，再正式完成 paper_plan（init 时已经初始化，**正式定稿**时填充 4 份文件并跑 `validate_paper_plan.py` exit 0）。
- paper_plan `complete` 后才能调度 `mm-figures` / `mm-graphics`（边界见 `references/figure-boundary.md`），全部完成或 `n_a` 后才能进入论文终稿。
- 论文终稿分两轮（写作轮 + 独立审查轮），owner skill 为 `mm-paper-writing`；机检清单见 `references/paper-final-checks.md`，初稿接管见 `references/draft-takeover.md`。
- 每个阶段开始前**回显**：当前阶段、负责 skill、将读取的上游报告、将产出的文件、对应机检脚本。
- 每个阶段开始前输出 **GATE 确认**：上游产物存在、必读规范已读、计划产出明确；缺上游先补齐再进下一阶段。
- 每阶段结束后：跑对应机检脚本 exit 0，更新 manifest 中本阶段的状态、产物哈希、版本、`change_log`，并在 `validate_manifest.py` 校验通过后再进入下一阶段。
- 任一阶段 `n_a` 时在 `plan.md` 写明原因，manifest 对应状态置 `n_a`；范围化验收不要求 `n_a` 产物，但最终总结必须说明范围。
- 阶段产物未通过 `mm-verification` 前，不得声称"全流程完成"。`mm-verification` 只审计、定位并指定回写阶段；本 skill 负责调用对应 skill 修复后再次验收。

## 边界

- 本 skill 不亲自解题、不写模型、不画图、不写论文正文——只编排与调度。
- 不覆盖 `PROJECT_ROOT` 之外的任何既有文件；输入附件只读。
- 不写阶段 owner 细则——以各 owner skill 的 `references/` 与脚本为权威。

## 索引（references/）

| 文件 | 内容 |
|---|---|
| `orchestrator-quickcard.md` | 1 页速查卡 |
| `stage-pipeline.md` | 7 阶段流水线定义、依赖、并行、`n_a` 规则、状态机 |
| `paper-plan-spec.md` | paper_plan 阶段全部产出物的写法、完成门禁 |
| `page-budget-schema.md` | `paper/page-budget.json` 字段约束与示例 |
| `paper-final-checks.md` | 论文终稿 11 项机检 + G-1~G-5 + 写作轮/审查轮产出物 |
| `draft-takeover.md` | 初稿接管（rename、SHA256、metrics、audit） |
| `figure-boundary.md` | 数据图 / 非数据图 / 场景图三类边界 |
| `checkpoint-gates.md` | 阶段开始前回显 + GATE、结束更新 manifest、返工协议 |
| `project-layout.md` | PROJECT_ROOT 标准骨架与阶段交接契约（共享） |
| `project-manifest-contract.md` | manifest 字段契约（共享） |
| `cumcm-shared-policy.md` | 跨阶段不变量（共享） |

## 索引（scripts/）

| 脚本 | 用途 |
|---|---|
| `init_project_skeleton.py` | 第 3 步一次性建齐 plan.md / todo.md / manifest + paper/ 4 份空骨架 |
| `init_paper_gates.py` | 把 G-1~G-5 初始化成 `pending` 写入 manifest 与 writing-gates.md |
| `validate_paper_plan.py` | paper_plan 正式定稿结束前的字段级校验 |
| `validate_manifest.py` | manifest schema + stdlib 校验 |
| `read_complete.py` | **共享读取协议**（被本目录内所有 mm-* skill 调用）。本目录里这份是唯一副本，不要在 mm-paper-writing / mm-problem-analysis 等下复制；需要完整读取时请用 `python <mm-orchestrator目录>/scripts/read_complete.py --skill <mm-xxx>`。本 skill 自己的注册表是 `references/reading-order.json`。 |

## 共享读取协议（read_complete.py）

> 完整机制文档在 `references/read-protocol.md`，含失败模式与恢复。**以下只是概览**——本 skill 与下游 7 个 skill 共享同一份协议与脚本。

所有 mm-* skill 的"完整读取、不可截断"由挂在 `mm-orchestrator/scripts/read_complete.py` 的**单一脚本**保证。每个 owner skill 只维护一份轻量注册表（`references/reading-order.json`，或 mm-paper-writing 的 `references/writing-order.json`），脚本按 `--skill` 加载。

```bash
# 8 个 skill 各自 plan
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-orchestrator      # 13 文件 / 15 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-problem-analysis  # 11 文件 / 19 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-paper-writing     # 35 文件 / 57 块（含跨 skill）
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-modeling         # 13 文件 / 27 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-coding           # 7 文件 / 11 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-figures          # 7 文件 / 11 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-graphics         # 7 文件 / 13 块
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-verification     # 9 文件 / 13 块
```

四步流程（plan → chunk → write-receipt → verify）的完整模板与失败恢复见 `references/read-protocol.md`。