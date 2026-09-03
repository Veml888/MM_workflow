# 图表、公式、LaTeX 排版、编译与专项审计

> **本文件定位：实现层（怎么做）。** 它管排版与编译的**具体 LaTeX 写法、命令、机检脚本和排查手段**；内容分为"排版规范（实现）"与"编译与机检（操作）"两大块。
>
> **与 `common-paper-rules.md` 的关系（去重原则）**：`common-paper-rules.md` 是**规则层（做什么）**，凡"所有章节通用、何时都成立"的版式规则（缩进两字符、正文 27–30 页、无 `Overfull`、中文弯引号、图表锚定原则、跨页长表应"续表 N 原表题/续下页/仅末页 bottomrule"）以 `common-paper-rules.md` 为**唯一权威**；本文件**只保留其实现手段**（`\FloatBarrier` 写法、`longtable` 四件套模板、无溢出的具体 LaTeX 等），不再复述规则条文。两者是"规则 → 实现"的参考关系，不是重复。
>
> 本模块由原 `mm-paper-writing/SKILL.md` 的 第61–82、361–396行 迁移而来。它是终稿写作的强制规范；不得只读摘要或以其它模块代替。

## 图表与格式

- **数量基线**：正文图 ≥ 12；**表按需使用，仅在内容适合用三线表时才做**（无"每问至少 1 表"、无最低表数）；每张图必须服务明确论点、禁止为凑图堆图；表（结果/对比/参数）应被正文引用并解读，"符号说明"表除外（只需一个三线表，不要求正文引用）。
- **图题**「图 N 描述」（图下方）、**表题**「表 N 描述」（表上方），统一使用小四号宋体；全文连续编号、无重号跳号；正文必须引用每张图/表。
- **题注短命名（硬性，所有章节通用）**：图题/表题只写对象名（短名词短语，如「各月光学效率分量」「鲁棒性扰动检验」「分区异质布局」），不得在题注里写说明性长句、冒号解释、结论或机理；图/表的关键现象、机理与结论一律在正文首次引用处用 2～4 句说明。题注通常不超过16字；同节多图/多表以内容词区分，禁止用“问题一/二/三”或Q1/Q2作题注区分词。
  - **表与首次引用相邻（规则见 `common-paper-rules.md` 第 13 条《图表锚定规则》）**：每张结果表、参数表和汇总表必须紧跟第一次正文引用段，不得被无关文字、公式、图或其它表隔开；发生漂移时对该关键表局部使用 `[H]` 或改用 `longtable`，不得机械全局锁位。
  - **交叉引用颜色**：正文 `\ref`、`\eqref`、`\cite` 显示为普通黑色正文，不得使用彩色、下划线或彩色边框；使用 `\usepackage[hidelinks]{hyperref}` 或明确将全部链接颜色设为黑色。
- **三线表**：凡使用表格，一律采用 `booktabs` 的 `\toprule/\midrule/\bottomrule`，无竖线；符号说明只放一个三线表且无需正文引用。
- 图内文字必须在最终物理尺寸下可读；位图不低于300 DPI，子图使用(a)(b)标注。
- **浮动与边界**：单页图表默认 `[htbp]`；一级和二级标题边界使用 `\FloatBarrier`，图表不得跨入下一小节；只有必须紧跟解释的关键图表使用 `[H]`。
- **表格字体与对齐**：表内文字统一五号宋体，表头、文字和数字水平居中，长文本使用居中的定宽列换行；表格结束后恢复小四号宋体正文，避免字体和字号泄漏。
- **关键表顺序**：数据审计表、符号表和核心结果汇总表紧跟首次引出，并优先于同节大型图片。
- **数字一致性**：摘要、表内和正文数字完全一致，精度统一为2～3位小数或按题面口径执行。
- **求解步骤呈现**：是否单设求解小节取决于信息量；成熟求解器通常并入模型末尾但仍须完整交代工具、版本、参数、终止、状态和输出，常规算法可用连续段落或普通编号，复杂自研算法按需使用内容化小节与流程图。

### 跨页续表排版

- 单页能够容纳的表格继续用 `table` + `tabular/tabularx`；只有保持五号宋体、可读列宽和合理行距后仍无法单页容纳时，才使用 `longtable`。
- `longtable` 不得包在 `table` 环境中，也不使用 `[H]`；跨页只发生在数据行之间，不拆同一逻辑行，整张表必须在同一小节内结束。
- 首页使用正常表号和完整表题，只设置一个 `\label`；续页顶部标“续表 N　原表题”，重复完整表头和单位，沿用原表号且不重复进入表目录。
- 非末页底部右侧标“续下页”；中间页不使用最终底线，只在末页使用 `\bottomrule`。
- 至少双遍编译，逐页检查续表号、表题、重复表头、单位、续下页、末页底线、数据连续性，以及是否出现漏行、重行、空白续页或下一小节标题插入表内。

**续表是完整跨页配置，不是“加一个 endfirsthead 表头”**。一个 `longtable` 必须先配齐 `\endhead`（表体表头）、`\endfoot`（非末页页脚）、`\endlastfoot`（末页页脚）三件套，缺一即视为未实现跨页续表。续页标题必须带原表号（`\thetable` 自动跟随），分隔用全角空格。

标准骨架（N 列，`\thetable` 自动取表号，非末页“续下页”、末页用 `\bottomrule`）：

```latex
\begin{longtable}{...列定义...}
\caption{表题}
\label{tab:xxx}\\
\toprule
\tabfont 列1 & \tabfont 列2 & \tabfont 列3 \\   % 首页表头
\midrule
\endfirsthead
\multicolumn{N}{c}{续表\quad \thetable\quad 表题}\\   % 续页标题，必带表号
\toprule
\tabfont 列1 & \tabfont 列2 & \tabfont 列3 \\   % 续页表头（与首页一致，必须重复）
\midrule
\endhead
\midrule
\multicolumn{N}{r}{\footnotesize 续下页}\\   % 非末页页脚
\endfoot
\bottomrule                           % 末页收尾底线
\endlastfoot
% ……数据行，行间无需重复表头……
\end{longtable}
```

要点：
- `\endfirsthead` 之前的 `\toprule/\midrule` 只用于首页；续页表头写在 `\endfirsthead` 之后、`\endhead` 之前。
- `\bottomrule` **只能**出现在 `\endlastfoot` 里，不得再在表末数据行之后单独写第二个 `\bottomrule`（否则末页会出两条底线）。
- 续页标题用 `\multicolumn{N}{c}{续表\quad \thetable\quad 原表题}`，`\quad` 分隔而非普通空格；表号必须由 `\thetable` 引用，不要手写数字。
- 若表格恰好单页放下、未触发跨页，`\endfoot`/`\endlastfoot` 配置依旧保留（“备而不用”），无需删除。
- 封底项（`\endlastfoot`）与页脚项（`\endfoot`）可同时存在：前者只在最后的物理页出现，后者在中间每页的底部出现。

## 生成论文（LaTeX）

**LaTeX 路径（默认）**：
- **前置检查**：本机必须已安装 TeX 发行版（MiKTeX/TeX Live），并使用其自带的 `xelatex` 引擎（当前环境 xelatex 不在 PATH，需定位本机已装发行版的 `xelatex.exe`）。**用 `where xelatex` / `shutil.which` / `render_tikz.py` 的定位逻辑找到本机已装的 MiKTeX/TeX Live**（常见路径如 `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64` 等），找不到就把该发行版的 bin 目录加入 PATH 或传绝对路径——**不要自动下载或安装新的 TeX 发行版，默认复用本机已装的那个**；确认本机确实没有 TeX 才暂停并告知用户，不得以未编译的 `.tex` 充当最终交付。
- 生成 `paper/论文.tex`（ctexart / xelatex），结构同 Step 2 规划，公式用 `equation` 环境自动编号、正文 `\eqref` 交叉引用；凡同一个公式表达中原本会用逗号、分号等并列书写多个等式，均用 `equation` 内嵌 `aligned` 与左花括号逐行排版，每行一个等式，整体只保留一个式号；需要逐条引用或分别推导的公式才拆分编号；三线表用 `booktabs`；插图用 `graphicx` 并 `\graphicspath{{figures/}}`。
- **内部多轮要求**：完成全部正文并最后写摘要后，至少双遍编译；随后依次运行页面长度、字体/表格/结构、引用、布局、摘要和语言审计。任一脚本失败都不得结束本次调用。正文页数不足或章节明显偏离预算时，生成/更新 `paper/content-gap-report.md`，按缺失的推导、参数来源、约束解释、算法细节、结果机理、检验、误差传播、最终回答和有数据依据的图表逐项补充，再次双遍编译和复检。
- 一级标题按中文序号手工或通过可靠的 LaTeX 编号配置显示（"一、""二、""三、"…），非顺序标题使用无编号命令（如 `\section*{附录}`、`\section*{AI 工具使用声明}`）；编译后逐页核对标题显示，禁止出现"1、问题重述"或"九、参考文献"这类混用。
  - **参考文献标题（容易重复的坑）**：参考文献**只允许一个标题**，且**不要再用 `\section*{参考文献}` 手动加标题**。`thebibliography` 环境自带的 `\refname` 已提供"参考文献"标题（`ctexart` 中 `\refname=参考文献`），若再手动写一个 `\section*{参考文献}` 会产生**两个标题**。正确做法：删除手动标题，仅保留 `\begin{thebibliography}`，并用 `\renewcommand*{\refname}{参考文献}`（必要时）与 `\ctexset` 配好其无编号黑体居中样式；编译后核对 PDF 中"参考文献"只出现一次、位于 AI 工具使用声明之后、文献条目之前。
  - 同理：**附录与 AI 工具使用声明**用 `\section*{...}` 是它们正确的方式（它们不依赖环境自带标题），不要与 `thebibliography` 的情况混淆。
- **LaTeX 固定排版要求**：
  - `\documentclass[12pt,a4paper]{ctexart}` + `\usepackage[margin=2.54cm]{geometry}`；导言区必须显式写入 `\setCJKmainfont{SimSun}`、`\setCJKsansfont{SimHei}`，并在正文开始时使用 `\songti\zihao{-4}`，确保小四号宋体正文而不是依赖默认字体。
  - 摘要独占一页（`\newpage`）、页码从摘要页起（`\pagenumbering`/`\thispagestyle` 控制，页脚中部从 1 起）；摘要后的正文各章节连续自然排版，不因章节标题另起一页；附录可在前文结束后另起页；
  - 摘要页主标题必须使用 `{\centering\heiti\zihao{3}\bfseries ...\par}`，摘要标题使用 `{\centering\heiti\zihao{3}\bfseries 摘\quad 要\par}`，摘要正文使用 `\songti\zihao{-4}`；关键词行使用 `\noindent{\heiti\zihao{-4}关键词：}{\songti\zihao{-4}关键词内容}`，两标题间距默认 `0.4em`。
  - 通过 `\ctexset` 固定标题字体：`section` 使用居中的 `\heiti\zihao{-3}`，`subsection` 使用左对齐的 `\heiti\zihao{4}`，`subsubsection` 使用左对齐的 `\heiti\zihao{-4}`；有编号和无编号标题均适用。AI 工具使用声明、参考文献和附录总标题均使用无编号一级标题，保持小三号黑体居中。**标题编号格式（硬性）**：`section` 设 `number=\chinese{section}` 且 `name={,、}`（一级显式 `一、`、`二、`…中文序数+顿号）；`subsection` 设 `number={\arabic{section}.\arabic{subsection}}`，`subsubsection` 设 `number={\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}`——使二级为 `章号.节号`（`1.1`）、三级为 `章号.节号.小节号`（`1.1.1`），且**章号 = 该章中文序号对应的阿拉伯数**（“一、”→`1.1`，“五、”→`5.1`），一级中文序数与二级阿拉伯章号保持一致。附录内 `\appendix` 后 `\renewcommand{\thesection}{\Alph{section}}`、`\ctexset{section/number={\Alph{section}、}}`，改按 A/B 编号。
  - 附录前正文使用小四号宋体；图题、表题使用小四号宋体，可用 `\DeclareCaptionFont{cjkcaption}{\songti\zihao{-4}}` 与 `\captionsetup{font=cjkcaption}` 强制；所有 `tabular`、`tabularx`、`longtable` 表内文字使用 `\songti\zihao{5}`。附录总标题小三号黑体居中，A/B 二级标题四号黑体左对齐，三级标题小四号黑体，说明正文小四号宋体，源码 `listings` 基本字体为 `\ttfamily\zihao{5}`。
  - 正文段落缩进实现：**两字符首行缩进**、相邻正文段落间隔约 `0.25\baselineskip`（规则条文见 `common-paper-rules.md` 第 17 条，此处只给实现值）；`\noindent` 仅限摘要关键词行，`\paragraph{}` 小标题后的正文仍须缩进。
  - **正文行距（硬性）**：导言区必须显式 `\linespread{1.2}`（12pt 字号下基线距约 17pt，对齐获奖论文实测的约 1.4 倍字号）。**禁止单倍行距**（文字密度过大、观感拥挤）。**表内文字必须是单倍行距**：表格分组内 `\linespread{1.0}\selectfont`，与五号宋体一起限定在局部分组（表格换行单元格按单倍排版，防止 1.2 行距渗入表内撑高行距）。**附录保持单倍行距**：在附录起始处（`\clearpage` 后）局部 `\linespread{1.0}` 恢复，代码与清单类内容用单倍更紧凑。**全局排版参数（行距/字号/页边距）在 Step 4 生成 `.tex` 时一次定死，终稿阶段不得用调整全局参数的方式消化页数**——行距后调会使正文页数上涨 15%～20%，被迫大删正文。
  - 不设页眉：必须显式 `\pagestyle{plain}`（页码在页脚中部）或 `\pagestyle{empty}`（仅用于演示草稿）；
  - 无目录（正文边界与 27–30 页规则见 `common-paper-rules.md` 第 5 条，此处只给实现）：正文用 `\clearpage` 前连续排版、附录另起页；附录用 `\clearpage` 单独另起一页，总篇幅控制在 9～11 页，固定包含 A、支撑材料文件列表和 B、主要的源程序；附录只展示主要源码，其余完整可运行源码在支撑材料中提供；全文匿名；
  - 单页图表默认使用 `[htbp]`；一级标题边界使用 `placeins`，并在每个 `\subsection` 前执行 `\FloatBarrier`，禁止图表跨入下一小节。顺序保持"文字引出 → 图表 → 解读"。确需跨物理页面的长表改用 `longtable`，按本文件“跨页续表排版”设置续表，不得嵌套在 `table` 中。
- **排版间距与留白控制**：图表与正文之间不得留下大段空白。先判断空白来自文字篇幅失衡、浮动约束、图表锚点还是图件尺寸，不预设"优先缩图"；默认 `[htbp]`，一级和二级标题边界均使用 `\FloatBarrier` 防止跨节漂移。图片缩放必须保持标签清晰、比例协调，不得把图缩到难以阅读。
- **相邻证据组留白审计**：表格与其直接对应的图（或图与对应表）若在源码中连续出现、共同支撑同一结论，编译后必须作为一个局部证据组检查。若独立浮动导致表后或图前出现明显空白，且当前页剩余空间足以容纳两者，应优先把该组关键表/图局部改为 `[H]` 或合并为同一排版块；不得只凭"仍在同一小节"判定通过。逐页核查相邻表图之间的空白比例。
- **前部改写回归检查**：改动问题背景、问题重述、问题分析或其他位于浮动体之前的文字后，必须双遍编译，并从改动页连续检查到首张后续关键表。至少核对图文顺序、孤立图页、大块无效留白、关键表页码与首次引出位置；不得只检查改动段本身。
- **局部修复顺序**：先审计相邻文字——缺少问题要害、证据、选择理由或交付边界时补充实质内容；存在重复题意、可合并句子或应移至其他章节的细节时删减压缩。若改变图片大小不适用、会损害可读性或不能解决空白，允许通过有依据的增写或减写平衡分页。文字已完整紧凑时，再调整图表锚点/叙事顺序、浮动参数、关联图组合和可读范围内的局部尺寸。禁止为排版编造内容、重复注水、删除必要论证，或改变全局字号、行距和页边距。**篇幅不足（<27 页）时按 `references/篇幅控制-playbook.md` 执行**（先定位缺在哪，再按"最终答案→推导链→验证证据→结果解释→图表"优先级补实质内容，禁止注水）；本节只处理"视觉留白/浮动"类缺口，不负责"内容不足"的扩充。
- **表格字号与对齐（含字体泄漏）**：表内文字统一五号宋体（`\songti\zihao{5}`，10.5pt）加**单倍行距**（分组内 `\linespread{1.0}\selectfont`）；表头、文字和数字全部水平居中，长文本使用 `>{\centering\arraybackslash}p{}` 或等价定宽列自动换行；使用紧凑列距与行距，禁止为消除溢出擅自缩小字号。**硬性**：`longtable` 或章节级表格结束后必须立即恢复 `\songti\zihao{-4}` 与正文行距，不能只写 `\normalsize` 而遗留错误字体族；浮动表也应把宋体五号与单倍行距限定在局部分组内。终稿须实测正文为小四号宋体、表内为五号宋体单倍行距，不得发生字号、字体族或行距泄漏。
- **表格浮动与跨页**：单页表格默认 `[htbp]` 并受一级、二级标题边界的 `\FloatBarrier` 约束；只有必须锁定在解释段后的关键表才使用 `[H]`。确实无法单页容纳的表格允许用 `longtable` 跨页，按本文件“跨页续表排版”设置：首页正常表题；续页"续表 N　原表题"；续页重复完整表头与单位；非末页标"续下页"；仅末页使用 `\bottomrule`。续页沿用原编号且不重复进入表目录，整张长表必须在同一小节内结束。
- **表格位置复核**：逐表比对"首次正文引用页 → 表题页 → 下一小节标题页"；关键汇总表不得晚于同节的大型图片，不得单独漂到下一页下半部或浮动专页。发现异常先调整源文件叙事顺序，再按需对单张关键表使用 `[H]`。
- **图片位置复核**：逐图比对"首次正文引用页 → 图题页 → 下一小节标题页"，确认图片位于对应问题和小节，且顺序为"文字引出 → 图片 → 实质解读"。关键图片不得脱离引出段、形成孤立图页或漂到下一小节；异常先调整叙事顺序和锚点，再在可读范围内调整浮动参数与局部尺寸。
- 编译验证：`xelatex -interaction=nonstopmode -halt-on-error paper/论文.tex` 产出 `paper/论文.pdf`；编译必须通过（无未定义引用、无缺图），若中文缺字检查 ctex/字体配置。
  - **语言门禁**：编译前运行 `python <mm-paper-writing目录>/scripts/audit_submission_language.py paper`，扫描 `paper/` 下的 TeX 正文源文件。出现禁用表达时，按 `language-and-storyline.md` 改写并重跑；只有官方规定的 AI 工具使用声明可用 `language-audit: allow-start` 与 `language-audit: allow-end` TeX 注释包围后豁免。不得用豁免标记包围其他正文。
  - **字体/表格/表题/模型章结构门禁（硬性）**：编译后运行 `python <mm-paper-writing目录>/scripts/audit_paper_tables.py paper/论文.tex`，**PASS 以脚本 exit 0 为准**。该脚本强制：① SimSun/SimHei 字体系统、正文/标题/图表题/表格/源码的固定字号与字体族；② 表题/图题标签为 "表1 标题 / 图1 标题"；③ 表格列全部居中；④ 符号说明只允许一个规范 `longtable`；⑤ 表内文字五号宋体（`\songti\zihao{5}`）；⑥ 三线表；⑦ `\end{document}` 恰一次；⑧符号表只收录跨章节核心量；⑨模型章允许条件性公共数据处理且问题小节按题面顺序；⑩公式多等式左花括号。任何 FAIL 必须修正后重跑，禁止只写"已核对"或手写 PASS。
  - **首行缩进门禁（硬性）**：每次调用编译后运行 `python <mm-paper-writing目录>/scripts/check_noindent.py paper/论文.tex`，**PASS 以脚本 exit 0 为准**。该脚本扫描 `\noindent`，除"摘要之关键词行"（含「关键词：」）外，任何正文段落出现 `\noindent` 均判 FAIL（正文新段落必须首行缩进两字符，禁止用 `\noindent` 消除缩进）。出现 FAIL 时须删除该处 `\noindent` 让段落自然缩进，重跑至 exit 0。
  - **中文引号门禁（硬性）**：每次调用编译后运行 `python <mm-paper-writing目录>/scripts/check_quotes.py paper/论文.tex`，**PASS 以脚本 exit 0 为准**。该脚本强制：① 中文正文禁止出现 ASCII 直引号 `"`（U+0022），应为中文弯引号 “（U+201C）/”（U+201D）；② 中文弯引号必须成对、数量相等（左=右）。合法豁免：`\texttt`/`\verb`/`\begin{lstlisting}` 代码块及行内 LaTeX 命令参数（文件名/源码/语法不含中文内容者）。出现 FAIL 时把对应 `"…"` 改为方向正确的中文弯引号后重跑，禁止只写"已核对"。
  - **摘要零数学符号门禁（硬性）**：摘要成稿后运行 `python <mm-paper-writing目录>/scripts/check_abstract_symbols.py paper/论文.tex`，**PASS 以脚本 exit 0 为准**。该脚本校验：① 摘要区无 `$...$` 行内数学模式与公式环境（equation/align）；② 无希腊字母、带上下标的变量、单字母数学关系式（如 `p_0=0.10`、`n=78`、`k≤13`、`P_g`、`Φ`）；③ 关键词数量为 4-5 个。白名单（不算符号）：纯数字、百分数、年份、常规单位（元/件）、化学式、已写全称的模型缩写。FAIL 时须把符号改写为自然语言、调整关键词数量后重跑。
- **人工冷读门禁**：语言脚本通过后，逐节按"本节要解决的具体问题是什么 → 证据来自哪里 → 为什么得到这个判断 → 该判断如何服务题目"冷读。若删去一段后论证、边界或证据没有损失，删除该段；若读者需跳回上游报告才能理解变量、公式或结论，补足正文中的必要连接。此门禁不能由关键词脚本替代。
  - **通用原则（"要求 vs 实现 vs 机检盲区"）**：凡规范条文的**排版/视觉要求**（缩进、对齐、图表锚定、列表项缩进、Overfull、图表不跨节等），写规范时必须**同时给出实现手段**（怎么用 LaTeX/enumitem/placeins 做到），不能只写"须满足"；并**显式说明该点是否有机检覆盖**——机检覆盖不到的（如列表项缩进、图不跨节、图表是否同主题相邻），一律**标注为人工冷读必查项**，验收时逐条人工核对，不得因机检 PASS 而略过。这是防"规范写了但做不出来 / 机检兜不住"的通病。
- **题面追踪门禁**：提交前逐条核对题面要求追踪表。每个 `P-##` 子问题必须至少对应一个明确的模型、结果和结论落点；每个正文核心段落必须能指出其服务的 `P-##` 或 `REQ-###`。发现"写得正确但没有回答题目"的内容时删除或改写；发现题面要求没有模型、证据或结论承接时，回补对应内容后再交付。
- **正文页数硬门禁**：每轮编译后运行 `python <mm-paper-writing目录>/scripts/check_paper_length.py paper/论文.pdf --output paper/page-audit.json`。正文按摘要之后、附录之前计算并包含 AI 声明和参考文献，必须为 27～30 页；**附录按附录起始页到末页计算，必须为 9～11 页**（默认 `--appendix-min-pages 9 --appendix-max-pages 11`）。任一超界时脚本非零，本次调用必须继续修订。策划目标为正文28～29页、附录10页，用于给分页波动留余量。
- **正文行距硬门禁**：每轮编译后运行 `python <mm-paper-writing目录>/scripts/check_line_spacing.py paper/论文.pdf --output paper/line-spacing-audit.json`。实测正文（摘要后、附录前）相邻行基线距中位数必须为 15.5～18.5pt（12pt 字号 + `\linespread{1.2}` 的排版效果）；超界即 FAIL，禁止单倍行距正文。附录不参与本检查（附录保持单倍行距）。
- `content-gap-report.md`即使无缺口也必须存在并写明“无阻断性缺口”；禁止通过重复题意、重复结果、无信息图表、放大标题、增加空白、缩放页边距、重复代码、空泛创新或虚构参数补页。
- **图件引用机检（硬性）**：运行 `python <mm-paper-writing目录>/scripts/check_paper_refs.py paper/论文.tex --root .`，**PASS 以脚本 exit 0 为准**（核 `\includegraphics` 文件都存在、图/表编号连续、图题与文件名无题号前缀、报告声明的图都已被正文引用）；FAIL 必须修正后重跑，禁止只写"已核对"或手写 PASS。
- **文献引用机检（硬性）**：运行 `python <mm-paper-writing目录>/scripts/check_paper_cites.py paper/论文.tex`，**PASS 以脚本 exit 0 为准**（核：每个正文 `\supcite`/`\cite` 都有对应 `\bibitem`、每个 `\bibitem` 都被正文引用（无孤儿条目）、`\bibitem` 标签为**字符标签不准用裸数字**、正文标签与 `\bibitem` 标签一致、**显示编号 = thebibliography 物理序号（连续 1..N）**、摘要区无任何文献引用）；FAIL 必须修正后重跑，不得只写"已核对"或手写 PASS。若命中失败，优先回写 `mm-paper-writing` 在正文就地上标引用、并保证 `\bibitem` 随首次引用建立。
- **版面机检（硬性）**：编译产出 PDF 后运行 `python <mm-paper-writing目录>/scripts/check_layout.py paper/论文.pdf`，**PASS 以脚本 exit 0 为准**（检测页内大段空白/凑篇幅留白、孤立图/表页即图表与正文不相邻）；FAIL 需调整排版、浮动锚点或文字篇幅，直到 PASS。
- 定位 Poppler 的 `pdftotext` 后运行：`python <mm-paper-writing目录>/scripts/audit_abstract_page.py --pdf paper/论文.pdf --abstract-tex paper/sections/00-abstract.tex --pdftotext <pdftotext路径>`。只有 `status=pass` 才可交付；重点记录 `title_size_three`、`han_count` 与 `fill_ratio`。官方模板或用户明确覆盖标题字号时才可追加 `--allow-title-override`，并在验收报告写明依据。没有 `pdftotext` 时必须逐页渲染并用等价坐标工具测量，不能跳过占用率。
  - **pdftotext 版本区分（易踩坑）**：`audit_abstract_page` 依赖 `-bbox-layout`（Poppler 特有）。Git/Windows Git Bash 自带的 `pdftotext`（GNU/Glyph&Cog 版，提示 `pdftotext version 4.00`）**不支持** `-bbox-layout`，调用会 `exit 99`，误报失败。优先使用 TeX 发行版自带的 Poppler 版：MiKTeX 在 `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdftotext.exe`，TeX Live 在 `<发行版>\bin\windows\pdftotext.exe`；二者支持 `-bbox-layout`。定位顺序建议：先 `where pdftotext` 与 `shutil.which('pdftotext')`，再探测候选路径是否支持 `-bbox-layout`（`pdftotext -bbox-layout` 是否报 usage 而非 missing option）；明确选定 Poppler 版后把路径传给 `--pdftotext`。
