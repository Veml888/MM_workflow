---
name: mm-problem-analysis
description: CUMCM 赛题分析与下游交接阶段。当用户需要解读国赛题、拆分子问题、追踪硬性要求、审计题面与表格数据、判断题型、筛选候选模型、评估可建模性，或为后续建模与编程建立输入契约时使用。产出 docs/01-analysis-report.md，并用稳定 ID 更新 project-manifest.json。
---

<!-- READ-GATE:complete -->

> **🛑 本阶段开工前的完整读取门禁（必做第一步）**
>
> **本 skill = 赛题分析阶段（第 1 阶段）**。从你打开这份 SKILL.md 的那一刻起，下面这些动作**全都算"开工"**——任一动作之前都**必须**先按共享 read-protocol 读完本 skill 注册表里的全部 11 个文件，并拿到 `verify` exit 0：
>
> - 读取题面 / `data/` 附件 / 用户提供的 PDF/DOCX/图片
> - 生成 `docs/00-problem-transcription.md` / `docs/00-problem-interpretation.md`
> - 调用 `references/problem-taxonomy.md` 做判型、调用 `references/model-selection-library.md` 选候选
> - 调用 `references/data-audit-manual.md` 做 Step 2.5 数据审计
> - 写 `docs/01-analysis-report.md` / 更新 manifest 的 `requirements`、`problems`、`datasets`、`model_candidates`
> - 跑 `scripts/check_analysis_report.py` 等任何脚本
>
> **`read_complete.py` 不是"检测脚本"——它是"强制读完 + 检测"组合机制**（chunk 子命令**强制按块打到 stdout**、write-receipt + verify **强制记账与三层 SHA256 锁定**）。跳过任何一块都会让 verify exit ≠ 0，**"声称读过"就站不住脚**。
>
> ```bash
> # Step 1: plan
> python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-problem-analysis
>
> # Step 2: chunk（按 plan 输出的 chunks[] 逐块读取；缺 READ-BEGIN/READ-END 视为截断）
> echo '{"schema_version":"1.0","reads":[]}' > .read-session.json
> python <mm-orchestrator目录>/scripts/read_complete.py chunk \
>     --skill mm-problem-analysis \
>     --path <rel> --start N --end M \
>     --session .read-session.json
>
> # Step 3: write-receipt
> python <mm-orchestrator目录>/scripts/read_complete.py write-receipt \
>     --skill mm-problem-analysis --pass 1 \
>     --receipt skill-read-receipt.json --session .read-session.json
>
> # Step 4: verify（exit 0 才算 PASS）
> python <mm-orchestrator目录>/scripts/read_complete.py verify \
>     --skill mm-problem-analysis \
>     --receipt skill-read-receipt.json --session .read-session.json
> ```
>
> 共享协议完整文档：`../mm-orchestrator/references/read-protocol.md`
> 本 skill 的注册表：`references/reading-order.json`（11 文件 / 19 块 / ~84 KB，含跨 skill 引用 mm-orchestrator 两份 policy/contract）。

<!-- /READ-GATE -->

# 数学建模赛题分析

本 skill 是数模流程第 1 阶段。目标：把"自然语言赛题"翻译成"可建模的技术问题"，给出建模方向。它只产出分析报告，不写模型公式、不写代码。

**工具与路径（相对本 SKILL.md 所在目录解析）**：`<本skill目录>` 即本文件所在目录；`<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`。脚本内部路径自解析，参数中相对路径相对当前工作目录解析，机检一律在 PROJECT_ROOT 下执行。

## 一、定位与产出

**输入**：赛题文件（PDF/DOCX/图片/文字）、`data/` 附件、`plan.md` 和 `project-manifest.json`（若有）。

**产出**：

- `docs/00-problem-transcription.md`（赛题复现稿，必须）
- `docs/00-problem-interpretation.md`（逐子问题语义解释与 G-SEM 门禁，必须）
- `docs/01-analysis-report.md`（分析报告，必须）
- 必要时在 `docs/source-evidence/` 保存公式、图件和复杂表格的来源证据
- 更新 manifest 的 `requirements`、`problems`、`datasets`、候选 `assumptions`、`model_candidates`、验证需求、`artifacts` 和 `stages.analysis`

所有交接对象使用稳定 ID。

**跨阶段不变量**遵循 `../mm-orchestrator/references/cumcm-shared-policy.md`；交接字段遵循 `../mm-orchestrator/references/project-manifest-contract.md`。

**与 mm-modeling 的边界**：本阶段只做"判型 + 给候选池"——用 `references/problem-taxonomy.md` + `references/model-selection-library.md`，为每个子问题挑 2~3 个候选、标推荐首选。**最终模型定稿是 mm-modeling Step 3.6 的职责**（它用 `model-selection-matrix.md` + `algorithm-catalog.md` 按"数据→目标→约束"从候选里定稿）。本阶段的候选只登记 `MC-P##-##` 并可被证据推翻，不是最终选择。

**整题主线意识**：判型不能只"逐问孤立归类"，还要留意整题——研究对象、核心矛盾、最终目标、问题间的推进关系，以及哪些量会被多问共享、哪些输出要传给后问；在 01 报告里为后文"统一口径表 + 跨问联动链"（mm-modeling Step 2/5 产出）留下接口。

## 二、工作流（按这七步做）

主流程就是这七步。某一步要打开的 references 列在该步的"参考"小节；执行时按 Step 顺序走，到对应步骤才读对应 references。

### Step 0：阶段 GATE 与只读盘点

按 `references/problem-reading-protocol.md` 执行：冻结原始输入，生成按页的 `docs/00-problem-transcription.md` 和逐问的 `docs/00-problem-interpretation.md`；对公式、关键数字、单位、表头、硬约束和附件关系做视觉或来源核验，完成正向与反向核对，并完成 `G-SEM` 语义核对。

开工前回显并核验 `G-PA1` ~ `G-PA4`（详见 `references/quality-gates.md` §1）：

1. **G-PA1 题面可读**：题目正文与所有附件可访问；缺页、模糊扫描或附件缺失时停止实质分析并列出缺口。
2. **G-PA2 规范已读**：引用共享规则中"模型复杂度必须与题目难点匹配"和"凡声称稳定、优越、可靠，必须给出对应证据"。
3. **G-PA3 输入已盘点**：列出题面文件、`data/` 文件、文件 SHA256、格式、用途和解析状态；输入只读。
4. **G-PA4 交付已声明**：明确将产出 `docs/01-analysis-report.md`，并更新 manifest 的本阶段字段。

`G-READ` 或 `G-SEM` 未通过时只记录缺口和阻断范围，不得依据未经核验的 OCR、转录或模型推测进入正式分析。普通装饰图无需强制裁剪，复杂图表或高风险内容才保存到 `docs/source-evidence/`。

### Step 1：基于已核验题面复现稿做问题重述

- 以已通过 `G-READ` 和 `G-SEM` 的复现稿为主输入，用自己的话复述题目背景、任务目标、要回答的问题，逐条列出（Q1/Q2/Q3…）。
- 不重复从头通读原始 PDF；只有复现稿标记"待确认"，或公式、数字、单位、硬约束和附件关系需要核实时，才按页码和位置定点回看原始 PDF，并把核验结果回写复现记录。
- 区分"题目问什么"（硬性要求）与"题目暗示什么"（可发挥空间）。
- 标注每个子问题需要"输出什么格式的结果"（数值、方案、图表、建议等）。
- 建立**要求追踪矩阵**：为题面每条硬性要求分配 `REQ-###`，记录原文位置、所属子问题、预期输出和验收方式；为子问题分配 `P-##`。题面没有要求的内容不得伪装成硬约束。

### Step 2：拆解数据与约束

- 盘点 `data/` 里有哪些数据：字段、量纲、缺失（区分结构性缺失与真缺失）、时间跨度、样本量、测量次数（是否单次测量）。
- **实验设计审计（本阶段核心，决定可建模性）**：识别数据背后的设计结构——
  - 设计类型：完全/部分正交、析因、单因素轮换、稀疏设计；
  - 天然对照组合：哪些样本仅相差一个变量（如 A12/B1 仅装料方式不同），可用于分离因素效应；
  - 共线性风险：哪些特征几乎同步变化（如用量与配比），哪些组合从未同时出现；
  - 覆盖与稀疏区：自变量空间的覆盖范围、稀疏/缺失区域（这些区域就是外推禁区与补充实验点候选）；
  - 时间/批次混淆：数据是否来自同一批次、时间序列与实验条件是否混淆。
- 列出题面明确给的约束与假设（如容量上限、成本系数、物理规律）。
- 数据初探：描述性统计（均值/极值/缺失率/分布）+ 变量相关性 + 分组对比，不建模、不调参。

> 实验设计审计的产出要直接写入报告：它决定了"哪些效应可识别、哪些区域可外推、哪些组合可优化"，是建模阶段选模型与约束域的依据。

### Step 2.5：数据审计（有样本型/时序型/实验记录型表格时必做）

按 `references/data-audit-manual.md` 执行并出五张审计表，按"字段保留/剔除决策"给出每个字段的动作；字段保留与剔除必须给出字段定义、逐条复算或训练折证据；测试集只在规则冻结后用于外部评价。纯参数表、规则表跳过统计审计，但仍做单位、范围、来源和一致性检查，不虚构样本级结论。

### Step 3：判定问题类型

**参考：`references/problem-taxonomy.md`**

对每个子问题，先到 `problem-taxonomy.md` 找主类型 + 辅类型（识别信号 + 一句判型要点），再立即到 `references/model-selection-library.md` 同章节检索对应场景行（含组合配方），核对适用条件与翻车点，为 Step 4 提供候选池。

**跳出条款**：若十二类与场景表均无法覆盖该子问题，允许自定义判型与建模结构，但必须在报告中写明"为什么现有库不够"（题面特殊性、数据形态、目标函数结构等），不得为套模板强行归入某一类。

### Step 4：给出建模方向

**参考：`references/model-selection-library.md` + `references/case-cards.md`**

- 针对每类子问题，从 `model-selection-library.md` 的场景表挑候选方法（名称 + 一句话理由 + 主要局限）：默认 2~3 个，复杂问题可给 4~5 个但必须说明取舍；按"机理优先、精确解优先、可解释优先、简单优先"排序，并标注**推荐首选**及理由；组合型子问题用该库 §13 的组合配方衔接。
- **数学形态预演**：对每个候选，用一两句话预演它的"雏形"——决策变量/输入是什么、目标/响应是什么、约束或适用条件、估计参数个数、数据是否支撑（样本量 vs 自由度）。目的不是写公式，而是让建模阶段"按图施工"，避免选型跑偏。
- 为候选模型分配 `MC-P##-##`，逐个记录所依赖的 `DS-###`、关键假设、可验证基线、选择证据和淘汰条件。推荐首选必须能被证据推翻，不得只写"效果好"或"常用"。
- 标注需要进一步采集/构造的数据或参数。
- 明确子问题间的依赖关系（Q2 是否依赖 Q1 结果）。
- **案例参考**：可翻 `references/case-cards.md` 找"真题怎么拆"的主线启发，但**不复制结论**，公式与结果必须由本赛题数据重新建立。

> 本阶段只给候选池、不定稿；最终模型由 mm-modeling Step 3.6 定稿。

### Step 5：可建模性审计与输出契约

- **样本-自由度审计**：逐问核对"样本量 / 候选模型参数个数"，给出参数上限（如每组 5~7 个点 → 模型参数 ≤4 个）；样本不足的候选直接降级或标注"需正则化/需补充实验"。
- **外推边界审计**：明确每个模型的可用自变量范围（温度/特征域），标出超出即不可信的区域。
- **失败模式预判**：每问写出 1~2 个最可能翻车的点（小样本过拟合、外推越界、共线性导致系数不稳、噪声被低估、时间与条件混淆、测试集泄漏），并给出前置对策（小样本校正指标、域约束、正则化、重复实验点）。
- **输出契约**：每问明确最终交付格式（数值表/方案/图/建议）、评委最关注的指标（如收率、误差、覆盖率、AUC/容量指标）、以及可核验的基准（如题面/数据中的最优观测值、官方要求格式）。
- **目标契约**：若子问题需要优化或决策，明确题面真实目标、可控变量、硬约束、软偏好和不可替代的评价指标；区分"题目要求优化的对象"与"用于计算的代理指标"。任何候选目标都要说明方向、量纲/归一化、权重或惩罚来源以及可能遗漏的代价，不能等到建模阶段才猜测目标。
- **验证契约**：每问至少指定一个基线或极端/退化情形，并说明后续应如何验证。灵敏度、鲁棒性、模型对比和统计检验按题目需要触发；若计划声称稳定、优越或可靠，必须预先绑定相应证据。

### 回退条款（判型修正）

Step 2 数据初探、Step 2.5 数据审计或 Step 5 可建模性审计发现判型错误、候选不支撑、数据与题面理解冲突、存在泄漏字段时，**显式允许回到 Step 1/Step 3 重判与重选候选**，禁止硬着头皮往下写。回退后必须在报告"判型修正记录"中写明：原判型 → 触发回退的证据 → 修正后的判型。

### Step 6：写出分析报告

**参考：`references/analysis-report-template.md` + `references/quality-gates.md`**

按 `references/analysis-report-template.md` 写 `docs/01-analysis-report.md`。报告必须包含"阶段 GATE、问题重述与要求追踪、数据概览与实验设计审计、数据审计、问题分类、建模方向、可建模性与验证契约、依赖关系、输出契约与下游交接"九个部分；适用表格数据时另含五张审计表与字段决策。数据流、机理链、候选对比树和判型修正记录可追加，不被模板压扁。

完成前执行**阶段机检（硬门禁）**：运行

```bash
python <本skill目录>/scripts/check_analysis_report.py docs/01-analysis-report.md
```

脚本校验：① 九部分标题齐全；② 出现稳定 ID（`REQ-###` / `P-##` / `DS-###` / `MC-P##-##`）；③ 每个"首选"候选均有"淘汰条件/局限/何时弃用"表述（首选必须可被证据推翻）；④ Q-PA1~Q-PA5 门禁已填写（Q-PA4 可 N/A）。**任一 FAIL 必须修正报告后重跑，禁止只写"已核对"或手写 PASS**。

Q-PA1~Q-PA5 详细规则见 `references/quality-gates.md` §3。

门禁通过后，将 `stages.analysis.status` 置为 `complete`，登记报告 SHA256、版本及其关联 ID；否则置为 `failed` 或保留 `in_progress` 并写清缺口。不得改写其他阶段记录。

## 三、边界

- 不展开完整模型公式与推导（那是 `mm-modeling` 的活），但**允许一行式可行性校验雏形**：为验证可辨识性、自由度、量纲一致性，可写出候选模型的"公式骨架"（如 S 型响应、指数衰减、二次响应面），并在报告中标注"候选，待建模阶段定型"。分析阶段不得把候选模型、变量、目标、约束或公式骨架登记为最终模型。
- 不写、不运行求解代码。
- 不替用户拍板最终模型，但每问给出**推荐首选 + 理由**；最终选择由建模阶段结合题面定。
- 允许预演变量/目标/约束的"雏形"、参数个数估算与公式骨架（属分析深度，不算越界写公式）。

## 四、索引

### references/

| 文件 | 用途 | 何时打开 |
|---|---|---|
| `problem-reading-protocol.md` | 赛题阅读协定（复现稿 + G-READ + G-SEM） | Step 0 |
| `problem-taxonomy.md` | 十二类判型决策树 | Step 3 |
| `model-selection-library.md` | 场景→候选库（首选/备选/适用条件/翻车点） | Step 3-4 |
| `case-cards.md` | 历年真题主线示范 | Step 4（启发用，不复制结论） |
| `data-audit-manual.md` | 数据审计手册（五张审计表 + 字段冻结） | Step 2.5 |
| `analysis-report-template.md` | 报告模板（八部分 + 字段决策） | Step 6 |
| `quality-gates.md` | G-PA / G-READ / G-SEM / Q-PA 集中登记 | 开工前 + 完成后 |

### scripts/

| 脚本 | 用途 |
|---|---|
| `check_analysis_report.py` | 报告机检（八部分标题、稳定 ID、可证伪、Q-PA） |