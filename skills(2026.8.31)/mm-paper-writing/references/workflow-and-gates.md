# 终稿工作流、输入输出与写作门禁

> 本模块由原 `mm-paper-writing/SKILL.md` 的 第15–20、25–28、288–360、397–404行 迁移而来。它是终稿写作的强制规范；不得只读摘要或以其它模块代替。

本 skill 在完整工作流中必须由 `mm-orchestrator` **连续、独立调用两次**。每次调用都必须从头完整读取本文件和本次适用的直接引用规范，读取已定稿的结构规划、页面预算、初稿审计、图件清单、全部报告和结果，并在本次调用内完成多轮终稿、双遍编译、正文页数与全部专项审计；不合格时生成内容缺口报告并继续有依据地补充或压缩，直到本轮全部门禁通过。它不是“打开初稿快速润色后结束”的工具。

### 双调用协议（进入验收前的硬门禁）

1. **两次调用相互独立**：第一次与第二次调用开始时，都必须运行 `scripts/read_complete.py plan`，按 `writing-order.json` 的必读清单逐块读至全部文件末尾并确认每块出现 `READ-END`。不得以第一次调用的上下文、摘要、缓存或“已读过”为由跳过第二次完整读取。直接引用且本轮适用的规范也须重新完整读取。
2. **第一次调用（成稿轮）**：从上游材料新建或重构 `paper/论文.tex`，落实全部注册模块的适用要求，完成至少双遍编译和全部专项门禁。生成第一轮读取回执与 `paper/pass-1-audit.md`，按每个必读文件及其全部二/三级标题记录“已执行/不适用（含理由）/阻断”，并在 manifest 写入 `paper_final.full_skill_passes=1`、登记回执和审计文件哈希；此时 `paper_final.status` 只能保持 `in_progress`，不得置为 `complete`。

## 输入与产出
- 输入：编排器正式定稿的 `paper/structure-plan.md`、`paper/page-budget.json`、`paper/draft-audit.md`、`paper/draft-metrics.json` 与 `paper/writing-gates.md`；`paper/figure-requirements.md`（由图件 skills 填入）；可选只读初稿 `paper/draft-baseline.tex|pdf`；全部 `docs/01~05`、`figures/`、`results/`、`plan.md`、`project-manifest.json`。
- 产出：`paper/论文.tex`、`paper/论文.pdf`、`paper/page-audit.json` 与 `paper/content-gap-report.md`。唯一终稿格式为 LaTeX；初稿基线不得被覆盖或作为终稿提交。
- 跨阶段不变量遵循 `../../mm-orchestrator/references/cumcm-shared-policy.md`；论文结构、写作、字体、排版、引用、附录和终稿交付细则以本 skill 注册的必读模块为准。交接字段遵循 `../../mm-orchestrator/references/project-manifest-contract.md`。

## 工作流

### Step 0：输出格式（默认 LaTeX）

- **本 skill 默认且唯一输出 LaTeX**：`paper/论文.tex` + xelatex 编译 `paper/论文.pdf`，不再提供 Word/DOCX 排版路径。若用户明确要求 Word/DOCX，明确告知：Word 排版流水线已移除，需另用旧版工具或自行转换，不在本 skill 范围内。
- 写作前先确认本机已装 TeX 发行版（MiKTeX/TeX Live），用其自带的 `xelatex` 引擎编译（当前环境 xelatex 不在 PATH，需定位本机已装发行版的 `xelatex.exe`）：**用 `where xelatex` / `shutil.which` 或 `render_tikz.py` 的定位逻辑找到本机已装的那个（含常见 MiKTeX 路径），找不到就把它加入 PATH 或传绝对路径——不要自动下载安装新的 TeX 发行版**；确认本机确实没有 TeX 才暂停并告知用户。

> 结构规划（`paper/structure-plan.md`）由编排器建；图件清单（`paper/figure-requirements.md`）由编排器建骨架、`mm-figures`/`mm-graphics` 填内容；写作门禁初始状态（`paper/writing-gates.md`）由编排器初始化。本 skill 只负责终稿写作，并在写作前核对写作门禁。

### Step 0.25：初稿接管确认

- 若存在 `paper/draft-baseline.tex|pdf`，只读核对其 SHA256、可编译状态和 `draft-audit.md`；初稿只作为最低权威的语言与排版素材，题面、`docs/02`、`docs/03`、`results/`、图件报告和 manifest 依次优先。
- 不得直接把 `draft-baseline.tex` 复制成终稿后只做局部润色。必须新建 `paper/论文.tex`，仅吸收 `draft-audit.md` 标记为“保留”的内容；“改写/删除/补充”逐项落实。
- 若初稿整体失效，保留基线并按 `invalidated` 处理，从上游报告重建；若无初稿，按 `none` 走全新写作，但仍执行页面预算和多轮审计。
- 第二次调用时，第一次调用生成的 `paper/论文.tex|pdf` 是待独立终审的当前终稿，不得改名为 `draft-baseline`，也不得重新执行初稿接管改名逻辑；原始 `draft-baseline.*` 仍保持只读。

### Step 0.5：写作前门禁（GATE，防止跳步）

**未通过下列任一 GATE，不得开始撰写正文。** 每项必须在 commentary 输出 `PASS + 证据`，并写入 `paper/writing-gates.md`（表格：检查项 | 证据 | 结果）。GATE 是流程硬门禁：发现 G-1~G-5 任一未满足，立即停下补齐，不允许带着缺口继续。

| GATE | 检查内容 | 通过标准 |
|---|---|---|
| G-1 必读已读 | 完整读取 `writing-order.json.required_before_writing` 的全部文件 | 本轮独立读取回执通过 `read_complete.py verify`，`writing-gates.md`记录注册表SHA256、全部文件哈希和回执路径；任一文件、分块、标题或 `READ-END` 缺失不得 PASS |
| G-2 图表齐全 | 按 manifest 检查适用的 `figures/`、`docs/04`、`docs/05-diagrams-report.md`、`docs/05-visual-report.md` | 列出实际文件清单；按 `paper/figure-requirements.md` 核对适用的非数据图（视觉示意图仅在非 `n_a` 时要求）；缺图或写作中临时新增图，先回写对应 skill |
| G-3 上游数据 | `docs/02` 公式/符号、`docs/03` 结果已核对 | 说明每问公式与结果来自哪个报告小节，禁止凭空写数 |
| G-4 结构拟定 | 正式策划和初稿审计已完成 | `draft-audit.md`/`draft-metrics.json`存在，`page-budget.json`目标为28～29且各章预算闭合，`validate_paper_plan.py` exit 0；每问论证链、真实来源、证据ID、最终回答与图件锚点齐全，无占位符 |
| G-5 工具就绪 | xelatex/MiKTeX 可用，`paper/` 存在 | 定位 `xelatex.exe` 路径或确认已安装 |

论文终稿开始前，`paper/writing-gates.md` 和 manifest 的 `paper_gates` 必须全部 PASS 并随论文保留；验收阶段据此反查跳步。

### Step 1：确认结构与排版要求

- 写作前完整读取注册表中的公共要求、十个章节规范、图表排版、语言故事线、双轮终审和跨阶段不变量，确认页边距、页数、页码、附录和匿名要求。
- 运行 `python <mm-orchestrator目录>/scripts/validate_paper_plan.py paper/page-budget.json --root .`，确认 `paper_plan.status=complete`；失败时停止写作并返回论文策划阶段，不得在终稿阶段临时猜测页面分配。
- 固定按 CUMCM 规范与中文论文规范执行，见 `common-paper-rules.md` 与 `writing-order.json`，并以编排器产出的 `paper/structure-plan.md` 为章节骨架与逐问论证链。若用户提供官方模板/格式要求，以官方为准并记录覆盖原因。
- 确认摘要排版目标：主标题与摘要标题均为三号，整页但不过页、加粗关键方法/结论、无目录、页码从摘要页起；官方模板或用户另有明确字号时记录覆盖原因。

### Step 2：规划各节内容来源

按 `paper/structure-plan.md` 的章节骨架，把每个章节映射到上游报告与图表，避免凭空编造：

| 章节 | 内容来源 |
|---|---|
| 摘要 | 综合全部报告，见 `chapters/00-摘要.md`；必须最后写 |
| 问题重述 | `docs/01` 问题重述 |
| 问题分析 | `docs/01` 问题分类/建模方向（逐问分析 + 技术路线图） |
| 模型假设 | `docs/02` 模型假设 |
| 符号说明 | `docs/02` 符号表 |
| 模型建立与求解 | `docs/02` 公式 + 求解步骤 + `docs/03` 结果（每问内嵌结果表与结果分析） |
| 模型对比 | 仅当适用：`docs/02` 对比方案 + `docs/03` 对比结果 |
| 模型检验/灵敏度/鲁棒性 | 仅当适用：`docs/02` 方案 + `docs/03` 结果 |
| 模型评价 | 综合，客观（优点+缺点示弱+推广） |
| 参考文献 | 见「参考文献写作」节 |
| 附录 | A 支撑材料文件列表 + B 主要的源程序；其余完整源码在支撑材料中提供 |

### Step 3：撰写正文

- 从新建的 `paper/论文.tex` 开始，按 `draft-audit.md` 吸收有效初稿内容；不得直接覆盖或改名初稿基线充当终稿。
- 章节结构遵循 `common-paper-rules.md` 与 `writing-order.json`；语言遵循"去 AI 味与讲好故事"硬性要求，详见 `language-and-storyline.md`。
- 写"某问建模与求解"前，必须再次完整读取 `chapters/05-模型的建立与求解.md`，不得跳过或只读简介。
- 公式、符号与 `docs/02` 一致；求解表达根据内容采用连续段落或普通编号，复杂自研算法可使用流程图。
- 插图按 `docs/04`、`docs/05-diagrams-report.md`、`docs/05-visual-report.md` 说明插入，图注/表注全文连续编号；结果表用三线表。写结果与插图前必须再次读取 `layout-and-compilation.md`。**写正文前先核对 `figures/` 与 `docs/04`/`docs/05` 是否齐全**，缺图或写作中临时发现新图需求时，先停止该处撰写、回写对应画图 skill，待图产出并更新报告后再继续；不在本阶段自行生成。
- 流程/框架图优先用 `\includegraphics` 插入 `mm-graphics` 生成的矢量 PDF；600 DPI PNG 只作兼容与核查备份。插入后按实际版心复核最终字号与线宽。
- 模型对比、灵敏度、鲁棒性和检验只在适用时写入，可内嵌于对应论证位置，不强制独立小节；动态、空间演化或迭代题写入关键状态结果。
- **表格数字核对**：每张结果表写完后，与 `results/` 对应文件逐项核对（易错列：LOOCV-RMSE、标准化系数、$p$ 值、百分位区间、logdet/方差等），发现不符立即修正。
- **章节归属检查**：图表插入后确认其位于对应问题章节内（不得跨章节错位），提交前通读目录结构核对一遍。
- **关键汇总表位置**：数据审计表、符号表和核心结果汇总表紧跟首次引出文字，并排在同节大型图片之前。默认 `[htbp]`；编译后若因浮动竞争脱离引出段、落到无关图片之后或形成孤立浮动页，只将该关键表改为 `[H]`，不得把全部表格机械锁位。
- **问题分析与数据预处理分离**：问题分析章可以概括数据来源、可用性、质量风险、必要处理方向及其理由，但不写具体缺失率、异常值数量、处理参数、特征构造结果或描述统计结果。多问共享同一数据时，在模型章最前设置条件性的公共数据处理二级标题；各问数据独立时分别写入对应问题；部分共享时采用“公共处理 + 问题专属处理”。
- **推导链自检**：每问模型建立必须形成闭环推导链——变量定义 → 基础公式（给出机理/统计/数据形态来源）→ 本题化改造 → 目标与约束；纯经验公式必须说明来源，后一条公式须解决前一条公式尚未解决的困难；写完模型节后逐条自检"这条公式从哪来、为什么需要它"。
- **求解展示方式**：成熟求解器简洁但完整地写明模型性质、算法/求解器、软件版本、关键参数、容差或终止条件、求解状态和输出；常规算法用连续段落或普通编号说明输入、核心步骤和输出；智能优化或复杂自研算法进一步说明编码、初始化、目标/适应度、更新规则、参数来源、随机种子、独立运行和收敛证据。只有具有实质分支、循环、状态更新或终止机制的复杂自研算法才使用流程图；不得给每问机械设置相同的"求解流程"小节。
- **反模式**：四问小节标题完全一致（如每问都出现"建模思路"）即模板化；承接段不设标题，小节标题随问拟定。
- **问题重述与分析的自然篇幅**：问题背景和逐问重述按题目数量、对象复杂度及输入输出边界自然展开，不设置最低占页率；`1.1 问题背景`不得只写可替换到任意题目的短套话。问题分析只有在缺少任务边界、数学类型、主要困难、数据条件、方法依据、跨问依赖、验证方式或交付形式时才补写，不得为填页重复题意。具体执行 `chapters/01-问题重述.md` 与 `chapters/02-问题分析.md`。**若正文整体不足 27 页，按 `篇幅控制-playbook.md` 处理，不要把"补篇幅"误解为"只能加长问题重述/问题分析"——那两章恰恰是最不该注水的**。

**输出要求**：摘要页、图表数量、正文27～30页、字体、数字一致和匿名要求均按注册模块执行；跨阶段真实性与追踪遵循共享不变量。第一次调用即使全部脚本通过也只能保持 `paper_final.status=in_progress` 并登记 `full_skill_passes=1`。只有第二次独立调用再次完整读取全部注册模块、完成全部适用要求，且 `check_paper_length.py` 与全部专项脚本 exit 0、读取回执、要求覆盖、`page-audit.json`、`content-gap-report.md`、两轮回执和两轮审计均已生成并登记哈希、两轮各自至少完成两遍稳定编译时，才能把 `paper_final.status` 置为 `complete`，并登记 `full_skill_passes=2` 与 `second_pass_audit`。同时登记初稿模式/SHA256/基线页数、计划页数、最终正文页数、页数审计路径、缺口报告路径和两轮编译遍数。

## 边界

- 不改动数值结果与图表内容；发现矛盾回写对应阶段。
- 不画图、不生成图片文件；所有插图必须来自 `mm-figures`/`mm-graphics` 的产出，缺失时回写对应 skill 补齐，而不是在本阶段替代。
- 不编造参考文献、不编造数据。
- 生成的论文是"参考稿"，最终以当届官方规则与模板为准。
