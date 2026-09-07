---
name: mm-graphics
description: 为 CUMCM 论文创建"非数据图"——逻辑/框架/机理图（中文技术路线图、数据处理图、指标体系图、模型结构图、决策树、检验反馈图、节点—箭头型机理图，默认 TikZ 源 + 矢量 PDF + 600DPI PNG）；题目场景、空间关系类示意同样用 TikZ/SVG 按题面事实与坐标精确绘制，不使用 AI 图像生成。常规求解步骤用正文表达；只有复杂自研算法才允许算法流程图。数据图归 mm-figures。
---

<!-- READ-GATE:complete -->

> **🛑 本阶段开工前的完整读取门禁（必做第一步）**
>
> **本 skill = 非数据图生成阶段（图件分支 5b）**。从你打开这份 SKILL.md 的那一刻起，下面这些动作**全都算"开工"**——任一动作之前都**必须**先按共享 read-protocol 读完本 skill 注册表里的全部 7 个文件，并拿到 `verify` exit 0：
>
> - 读上游题面 / `paper/structure-plan.md` / `paper/figure-requirements.md` 任何产物
> - 查 `references/line-art-syntax.md`（线型 / 节点 / 连线语法）与 `references/implementation-spec.md`（设计令牌 / TikZ 模板 / 硬性要求全集）
> - 写任何 `.tex` / `.svg` / 渲染 `figures/*.tex|pdf|png`
> - 跑 `scripts/render_tikz.py` / `audit_tikz.py` / `render_svg.py` / `audit_svg.py` 等任何脚本
>
> **`read_complete.py` 不是"检测脚本"——它是"强制读完 + 检测"组合机制**（chunk 子命令**强制按块打到 stdout**、write-receipt + verify **强制记账与三层 SHA256 锁定**）。跳过任何一块都会让 verify exit ≠ 0，**"声称读过"就站不住脚**。
>
> ```bash
> # Step 1: plan（7 文件 / 13 块 / ~60 KB）
> python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-graphics
>
> # Step 2: chunk
> echo '{"schema_version":"1.0","reads":[]}' > .read-session.json
> python <mm-orchestrator目录>/scripts/read_complete.py chunk \
>     --skill mm-graphics \
>     --path <rel> --start N --end M \
>     --session .read-session.json
>
> # Step 3: write-receipt
> python <mm-orchestrator目录>/scripts/read_complete.py write-receipt \
>     --skill mm-graphics --pass 1 \
>     --receipt skill-read-receipt.json --session .read-session.json
>
> # Step 4: verify（exit 0 才算 PASS）
> python <mm-orchestrator目录>/scripts/read_complete.py verify \
>     --skill mm-graphics \
>     --receipt skill-read-receipt.json --session .read-session.json
> ```
>
> 共享协议完整文档：`../mm-orchestrator/references/read-protocol.md`
> 本 skill 的注册表：`references/reading-order.json`（7 文件 / 13 块 / ~60 KB）。
> 重要：本 skill 强依赖 `references/line-art-syntax.md`（线型 / 节点 / 连线语法）与 `references/implementation-spec.md`（设计令牌 / TikZ 模板 / 硬性要求全集）。必须读完两份 references 才能开始画。

<!-- /READ-GATE -->

# 非数据图（mm-graphics）

创建能够承担论证功能的学术图，统一走**精确路线**：逻辑/框架/机理图（TikZ 矢量，克制严谨、灰度可打印）；题目场景、空间关系类示意图同样用 TikZ/SVG 按题面事实与坐标精确绘制——**不使用 AI 图像生成**（AI 生成位图不可复现、几何精度不可控，与"凡声称必有真实证据"的纪律冲突）。目标是国家级竞赛优秀论文的清晰度、严谨性和版面完成度，但不承诺任何奖项结果。

跨阶段不变量遵循 `../mm-orchestrator/references/cumcm-shared-policy.md`；逻辑图、框架图、机理图、复杂算法流程图和场景/空间精确示意的边界、格式与质量细则以本 SKILL 与 `references/line-art-syntax.md`、`references/implementation-spec.md` 三者共同为准。读取 `paper/figure-requirements.md`，并按 `../mm-orchestrator/references/project-manifest-contract.md` 登记图件 ID、正文锚点、哈希和版本。

## 一、定位与边界（做什么、不做什么）

### 职责

- **负责**：把题面、模型、结果中的**论证性逻辑**和**抽象机理**画成非数据图——技术路线、数据管线、模型结构、机理、决策树、指标树、反馈闭环，以及需要按真实几何、拓扑或坐标精确呈现的场景与空间关系示意（TikZ/SVG 精确路线，按题面事实绘制）。
- **不负责**：
  - 数据图（折线/柱状/散点/热力/曲面/灵敏度等展示数值结果或结果分析）→ `mm-figures`；
  - 具体算法求解步骤、迭代伪代码、软件操作步骤 → 用正文编号或伪代码环境，**不画成本 skill 的流程图**（只有复杂自研算法，确有实质分支/循环/状态更新/终止机制，才可画算法流程图）；
  - 重跑模型、修改数值结论 → 发现数据异常回写 `mm-coding`，不在图阶段擅自改动；
  - 正文最终插入与图注、版心复核 → 由 `mm-paper-writing` 完成，本 skill 不修改 `paper/论文.tex`。**但接受 `mm-paper-writing` 的"返回补画"调用**：写作中发现缺图或图需调整时，`mm-paper-writing` 可回写本 skill 先补画/改图、再回正文写作（见 `../mm-paper-writing/references/workflow-and-gates.md` §Step 2.5）。

### 交付物

- `figures/<descriptive-name>.tex`：可编辑 TikZ 源（默认论文源，用 XeLaTeX 编译）。
- `figures/<descriptive-name>.pdf`：XeLaTeX 编译的矢量终稿。
- `figures/<descriptive-name>_600dpi.png`：按论文物理宽度渲染的位图备份。
- `docs/05-diagrams-report.md`：记录论证用途、正文位置、逻辑骨架、候选布局、选择依据、审查指标和验收结果。
- `.svg`：**仅当用户或下游明确要求**矢量编辑/网页嵌入/SVG 语义审计时才附，并运行 SVG 分支；不是默认交付。
- `.drawio`：仅用户明确要求可编辑源时附，不作为论文成图。
- Mermaid：只可验证拓扑，不作为论文成图。

写入 `paper/figure-requirements.md` 的"非数据图"区：逐图登记类型、核心论证用途、来源依据、候选正文锚点、推荐宽度与负责路线。

开始前必须确认 `project-manifest.json` 中 `stages.paper_plan.status=complete`，且运行 `python <mm-orchestrator目录>/scripts/validate_paper_plan.py paper/page-budget.json --root .` exit 0。初始化空骨架、未审计初稿或未闭合到 28～29 页的计划不得用于终稿非数据图制作。

## 二、决定要画哪些非数据图（决策入口）

读取 `docs/01~03`、`paper/structure-plan.md`（章节骨架、逐问论证链、插图锚点）和 `figures/` 清单，综合决定非数据图集合：

1. **逻辑/框架/机理图**：哪些位置需要技术路线 / 总体框架 / 模型结构 / 机理 / 反馈 / 指标树（见 §二路由表）；
2. **场景/空间精确示意图**：题目是否存在需按真实几何、坐标或对象关系呈现的场景（几何构型、区域划分、布局、遮蔽/覆盖关系等）——有则入精确路线按题面事实绘制，纯数值/抽象题不硬塞。

**决策规则**：

- 每张图必须有一个**核心论证目标**、来源依据、拟放正文位置，以及与已有图的区别；**没有信息增益的孤图不画**。
- **保守规划（决定"该画什么图"时的克制原则，硬性）**：只规划**确定、且大概率会被正文实际引用**的示意图/流程图；**可画可不画、不确定会不会用到的图，先不画**（可在 `figure-requirements.md` 标为 `planned`/待定，不真正去画）。**宁缺毋滥、按需触发**——避免"前面画了、后面又不用"的浪费与返工。真正需要时走"图件时序·路径 B"（写作中返回补画）再产图。
- **主要落点 = "模型的建立与求解"章节（硬性）**：这类辅助理解公式/符号/推导的示意图、流程图，规划时**针对"模型的建立与求解"章节**里的公式、符号、约束、算法、推导去配（如几何夹角定义图、接受域/拒绝域图、递归/循环流程图、模型结构图、指标树）。**不**为问题分析、摘要、问题重述等章节规划这类图；唯一例外是跨问**总技术路线图**（涵盖全部问题的递进链），它锚在问题分析章节的"总体技术路线"独立小节。
- **拟放正文位置的锚点归属（硬性）**：问题**专属**的模型结构图、指标体系图、机理图、场景图，其锚点必须是**该问题的模型建立章节**（如配时结构图→问题二模型建立、指标树→问题三模型建立）；**不得**锚在"问题分析"章节。只有**跨问总技术路线图**（涵盖全部问题的递进链）锚在问题分析章节的"总体技术路线"独立小节。分析阶段在 `figure-requirements.md` 填"候选正文锚点"时即须遵守，避免图被错挂到问题分析。
- **图件时序（先画后写 / 写作中返回补画，双路径，硬性）**：本 skill 画的是"帮读者理解"的非数据图，因此图必须**在正文动笔写引用它的那段文字之前**完成。两条路径都允许：① **先画后写**——`mm-paper-writing` 在 Step 2.5 先登记该问需哪些图，本 skill 先画好，正文再写；② **写作中返回补画**——`mm-paper-writing` 写到某处发现缺图，**返回本 skill（或 `mm-figures`）补画**，本 skill 接受该返回调用、先产图更新 `figure-requirements.md` 状态为 `drawn`，再交回正文写作。**禁止**"整段写完再补图当装饰"，也禁止"用文字替代本该配图的位置"。每个 `figure-requirements.md` 条目带状态（`planned`→`drawn`→`in-text`）供验收反查"图是否先于文字"。
- 与数据图、与其它非数据图均不重复；避免无信息孤图。
- **一切为"帮助理解"，不为"美观"**：用色、线形、布局的唯一目的是让读者最短时间看懂论证关系；禁止为装饰性视觉效果（渐变、阴影、卡片投影、彩色底板、插画图标）牺牲可读性。凡能用更简单的线条+文字说清关系，就不用更花哨的形式。
- **背景一律纯白，节点无填充色**（见 `implementation-spec.md §1.5` 与 §7.13）。黑白灰下必须完全可读；彩色仅作语义区分且不超 3 个。

**视觉风格决策与路由表（先路由，再画）**——按图的**语义**定位类别；**硬性：动手前必须读取 `references/line-art-syntax.md` 对应小节并按其执行，跳过路由直接画视为未按本 skill 执行**：

| 图的语义 | 类别 | 画法详见 |
|---|---|---|
| 严格顺序、包含、因果传导（技术路线、数据管线、机理框架、泳道、指标树、决策树、反馈闭环） | 1 逻辑/流程类 | `references/line-art-syntax.md` §1 |
| 几何、坐标、空间关系（天球、三维实体、几何构型、投影） | 2 空间类 | 同上 §2 |
| 零件→组件→成品的归属、层级、爆炸装配 | 3 结构/装配类 | 同上 §3 |
| 概率密度、接受域/拒绝域、置信区间 | 4 分布/统计类 | 同上 §4 |
| 约束边界、可行域、目标等值线、最优解 | 5 规划/可行域类 | 同上 §5 |
| 状态机、马尔可夫链、吸收态 | 6 状态/转移类 | 同上 §6 |
| 加权图、网络流、路径 | 7 网络/图论类 | 同上 §7 |
| 工序调度、甘特图、时间轴 | 8 时序/调度类 | 同上 §8 |
| 符号定义（向量、法向量、夹角）、物理场景 | 9 符号定义/物理场景类 | 同上 §9 |
| 遮挡、阴影、覆盖等对象间空间因果 | 10 物理机理场景类 | 同上 §10 |

> **流程图、思维导图属类别 1**：本质是"节点+边"拓扑，用白底细框或空心圆点、细实线主链、细虚线反馈、引线标注，**不**用空间类的椭圆透视/角度弧。逻辑要点梳理（罗列、对比、归纳，非严格流程）用线稿要点组（圆点项+细线标签），亦归类别 1。

决定后写入 `paper/figure-requirements.md` 的"非数据图"区，输出图清单（每图：类型、核心用途、来源依据、候选正文锚点、推荐宽度、负责路线）。

## 三、工作流（骨架）

> 本节是入口骨架。**几何排布方法、连线和节点硬规则、TikZ 模板、SVG/Draw.io/Mermaid 分支、几何机检详见 `references/implementation-spec.md` §3-§7**；本节不重复。

1. **Step 1 建立 DIAGRAM PLAN**：写明每张图的一个核心论证目标、来源依据、图类型、拟放正文位置和与已有图的区别。没有信息增益的孤图不要制作。（"要画哪些图"由 §二决定，本步落实为每图的论证目标与定位。）
2. **Step 2 抽取语义图**：先列出节点、节点类型、边、边标签、主链、反馈、分组和外部约束。消除逻辑歧义后再绘图；不得自行补造模型步骤。
3. **Step 3 两个候选布局择优**：见 §五.2；输出 `LAYOUT DECISION: <选定布局> — <比较依据>`。
4. **Step 4 几何排布**：详见 `implementation-spec.md §6.2`（6 步法：定版心→定网格→节点定位→连线沿格走→标签放格隙→画完先算后看）。**先看后画**——按当前语义图布局使用相对定位（`below/right=... of`、`at ($(锚点)+(偏移)$)`），不得按估算节点宽度手摆绝对坐标。
5. **Step 5 渲染与几何机检（硬性）**：
   - 编译：`python <mm-graphics目录>/scripts/render_tikz.py figures/fig_xxx.tex --png figures/fig_xxx_600dpi.png --dpi 600 --strict`（详见 `implementation-spec.md §6.3`）；
   - **几何机检（硬性，exit 0 才算 PASS）**：`python <mm-graphics目录>/scripts/audit_tikz.py figures/fig_xxx.tex --wmin 6.5 --wmax 15.6 --hmax 22 --line-text-gap 0.5`（详见 `implementation-spec.md §6.5`）；
   - 视觉回读：见 `implementation-spec.md §6.6`。
   - **PASS 一律以 `audit_tikz.py` exit 0 为准；不得只写"已核对"或手写 PASS。**
6. **Step 6 论文级验收**：使用 §五"100 分论文级验收"量表。
7. **Step 7 交付与嵌入**：报告稳定 ID、TEX/PDF/PNG 路径、像素尺寸、DPI、PDF 自然尺寸、最终嵌入宽度、正文锚点、建议 `\caption`、候选布局比较和审查结果，并同步更新 `project-manifest.json`。本 skill 不修改 `paper/论文.tex`；论文终稿由 `mm-paper-writing` 插入 PDF，并在真实版心中再次编译检查。

## 四、硬性要求（最关键的 6 条）

完整硬性要求 13 条见 `references/implementation-spec.md §7`。这里只列最关键的 6 条，进门必看：

1. **拒绝 PPT 风**：禁止阴影、渐变、玻璃效果、浮动卡片、胶囊标签、装饰图标、大面积彩色底板、营销式大标题和口号式副标题。一切为帮助理解，不为美观。
2. **几何机检 `audit_tikz.py` 必须 PASS**：交付前必跑，exit 0 才算 PASS（详见 `implementation-spec.md §6.5`）。
3. **节点无填充 / 背景纯白（硬性）**：所有非数据图背景一律纯白，节点/对象一律白底、无填充色。强调某节点只允许用加粗边框或加粗文字，或用低饱和单一强调色（不超 3 个语义色、不超 20% 画面面积）。
4. **线稿/无填充为整个非数据图体系的默认语法**：凡非数据图默认采用"白底细框/空心圆点节点 + 细实线主链 + 细虚线反馈 + 引线标注 + 黑白灰"。空间/几何类额外用椭圆透视、角度弧；拓扑类只用节点/边/点/引线。
5. **字体分工（与论文正文一致，硬性）**：中文宋体 `SimSun`（核心节点粗体用 `AutoFakeBold=2.5` 仿粗）+ 西文/数字 `Times New Roman`；全图不用 `\sffamily`。
6. **命名规范、图题外置**：文件名和 `\caption` 不使用"问题一/二/三、Q1/Q2"等题号，用内容与场景命名；图题默认外置（不在画布内重复大标题）。

## 五、100 分论文级验收 + 两个候选布局择优

### 5.1 100 分论文级验收

| 维度 | 分值 | 验收要点 |
|---|---:|---|
| 逻辑准确 | 30 | 节点、方向、条件、反馈与报告一致，无虚构 |
| 布局与路由 | 20 | 主链清晰、交叉为 0、反馈短、无穿框与断连 |
| 中文排版 | 15 | 最终字号合格、无溢出、短语平行、字体一致 |
| 视觉层级 | 10 | 主次明确、密度均衡、分组克制、无大块空洞 |
| 论文风格 | 15 | 无 PPT 卡片、标题外置、颜色克制、灰度可读 |
| 技术交付 | 10 | TEX 可编辑、PDF 可编译且为矢量、PNG 尺寸/DPI 正确；SVG 分支另查语义标记 |

总分至少 90，逻辑准确与论文风格两项不得失分至否决线，且无任何一票否决项。

**一票否决项**：与模型或正文逻辑矛盾；箭头穿过节点、断连、方向错误或判断分支无条件；最终物理字号小于 8 pt；中文乱码、溢出或被裁切；使用阴影、渐变、玻璃效果、照片背景、装饰图标或 PPT 卡片阵列；在画布内重复大标题与宣传式副标题；只修改 DPI 标签而没有足够像素；未回读最终 PNG 就声称通过。不允许无依据写 `visual_review: passed`。

### 5.2 两个候选布局择优（逻辑图用）

同一语义图先做两个低成本骨架，按下表评分，选择总分高者。不要为两个候选都做完整美化；先比较骨架，再精修胜者。输出 `LAYOUT DECISION: <选定布局> — <比较依据>`。不能只因为示例文件存在就选该布局。

| 指标 | 权重 | 优秀标准 |
|---|---:|---|
| 逻辑追踪 | 30 | 主链无需回看，条件与反馈入口明确 |
| 交叉与转折 | 25 | 交叉为 0，平均每边转折不超过 1 |
| 论文适配 | 20 | 匹配单栏/通栏，缩放后字号合格 |
| 密度与留白 | 15 | 无局部拥挤，也无超过约 25% 的无效单侧留白 |
| 视觉层级 | 10 | 读者先看到主链，再看到分组和辅助关系 |

## 六、边界

- 不绘制成熟求解器、常规算法或一般求解步骤。复杂自研算法若确有实质分支、循环、状态更新或终止机制，可绘制算法流程图。
- 不绘制数据图，不重跑模型，不修改数值结论。
- 不使用 AI 图像生成（imagegen 等）制作论文任何插图；场景/空间示意一律走 TikZ/SVG 精确路线。
- 用户明确要求答辩版时，可另做高对比版本，但必须同时保留克制的论文版。