---
name: mm-paper-writing
description: CUMCM 论文撰写阶段。当用户需要撰写国赛数模论文初稿、或接管已有初稿并完成摘要、问题重述、问题分析、模型假设、符号说明、模型的建立与求解、模型评价与推广、AI 使用声明、参考文献与附录的终稿时使用。产出 LaTeX 论文（paper/论文.tex|pdf），要求完整读取注册规范、按章节重读并独立编译审计。
---

<!-- READ-GATE:complete -->

> **🛑 本阶段开工前的完整读取门禁（必做第一步）**
>
> **本 skill = 论文撰写阶段（写作轮 + 独立审查轮）**。从你打开这份 SKILL.md 的那一刻起，下面这些动作**全都算"开工"**——任一动作之前都**必须**先按共享 read-protocol 读完本 skill 注册表里的全部 35 个文件，并拿到 `verify` exit 0：
>
> - 读 `docs/01~05` / `results/` / `figures/` / `paper/structure-plan.md` / `paper/page-budget.json` / `paper/figure-requirements.md` 任何上游产物
> - 读或写 `paper/论文.tex` / `paper/论文.pdf`
> - 跑任何论文机检脚本（`check_paper_length.py` / `check_line_spacing.py` / `check_noindent.py` 等 11 项 + `validate_requirement_coverage.py`）
> - 写 `paper/skill-read-receipt.json` / `paper/writing-audit.md` / `paper/review-findings.md` / `paper/review-audit.md`
> - 调度独立审查轮（哪怕写作轮已完成）
> - 跑 `check_paper_order.py`（paper 特异性校验）
>
> **`read_complete.py` 不是"检测脚本"——它是"强制读完 + 检测"组合机制**（chunk 子命令**强制按块打到 stdout**、write-receipt + verify **强制记账与三层 SHA256 锁定**）。跳过任何一块都会让 verify exit ≠ 0，**"声称读过"就站不住脚**。
>
> ```bash
> # Step 1: plan（35 文件 / 57 块 / ~278 KB；含跨 skill 引用 mm-orchestrator/mm-problem-analysis）
> python <mm-orchestrator目录>/scripts/read_complete.py plan --skill mm-paper-writing
>
> # Step 2: chunk（按 plan 输出的 chunks[] 逐块读取；缺 READ-BEGIN/READ-END 视为截断）
> echo '{"schema_version":"1.0","reads":[]}' > paper/.read-session.json
> python <mm-orchestrator目录>/scripts/read_complete.py chunk \
>     --skill mm-paper-writing \
>     --path <rel> --start N --end M \
>     --session paper/.read-session.json
>
> # Step 3: write-receipt
> python <mm-orchestrator目录>/scripts/read_complete.py write-receipt \
>     --skill mm-paper-writing --pass 1 \
>     --receipt paper/skill-read-receipt.json --session paper/.read-session.json
>
> # Step 4: verify（三层 SHA256 + EOF 覆盖校验，exit 0 才算 PASS）
> python <mm-orchestrator目录>/scripts/read_complete.py verify \
>     --skill mm-paper-writing \
>     --receipt paper/skill-read-receipt.json --session paper/.read-session.json
>
> # Step 5: paper 特异性校验（11 章顺序 / 摘要最后写 / reread 全覆盖）
> python <mm-paper-writing目录>/scripts/check_paper_order.py
> ```
>
> **实质阅读证据（防"刷账本"）**：除 verify 之外，每个必读文件还需在 `paper/.read-notes-pass-<N>.md` 记录 1~2 句要点摘录（详见下文"实质阅读证据"段）。
>
> 共享协议完整文档：`../mm-orchestrator/references/read-protocol.md`
> 本 skill 的注册表：`references/writing-order.json`（35 文件 / 57 块 / ~278 KB）。
> paper 特异性脚本：`scripts/check_paper_order.py`。

<!-- /READ-GATE -->

# 数学建模：竞赛论文撰写

本文件只负责总控。章节细则、公共规则、排版规则和写作/审查协议分别保存在 `references/`；不得凭本入口的概述直接开始写作。

**工具与路径（全部相对本 SKILL.md 所在目录解析，skills 目录整体搬移或换机无需改动）**：`<本skill目录>` 即本文件所在目录；`read_complete.py` 不在本目录，统一挂在 `../mm-orchestrator/scripts/read_complete.py`；其他文件中的 `<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`。脚本内部路径自解析、可在任意工作目录运行；但脚本参数中的相对路径相对当前工作目录解析，机检一律在 PROJECT_ROOT 下执行。**调用时必须显式带 `--skill mm-paper-writing`**。

## 完整读取硬门禁（详见顶部 READ-GATE）

完整协议与四步模板在顶部 `<!-- READ-GATE -->` 块与共享文档 `../mm-orchestrator/references/read-protocol.md`。本段只补充 mm-paper-writing 特有的纪律：

- **G-1 必须引用**：回执路径、注册表 SHA256、本轮账本路径及其 SHA256、以及所有必读文件哈希。
- **paper 特异性校验**（11 章顺序 / 摘要最后写 / reread 全覆盖）：单独运行 `python <本skill目录>/scripts/check_paper_order.py`，exit 0 才能继续。
- **实质阅读证据**（防"刷账本过关"）：除 verify 之外，每个必读文件还需在 `paper/.read-notes-pass-<N>.md` 记录 1~2 句要点摘录（该文件对本题最关键的 2~3 条要求、与本轮论文直接相关的规则）。审计与 `verify` 互相对照——凡某文件只有"已读"而无要点摘录，视为未实质阅读，须回读补记。
- **硬性纪律**：禁止用 `template` 直接生成回执；禁止手工编写回执 JSON；禁止复用其他项目或历史轮次的账本、回执、上下文或"已读"结论；账本与回执只对应本次写作轮的完整读取，独立审查轮不得以回执替代其实际核对。

## 必读模块

- 流程、输入输出、初稿接管与 GATE：`references/workflow-and-gates.md`
- 全文公共规则和固定论文骨架：`references/common-paper-rules.md`
- 正文页数控制（25–30 页，篇幅不足怎么补/超出怎么减）：`references/篇幅控制-playbook.md`
- 十一个实际论文章节：`references/chapters/00-摘要.md` 至 `references/chapters/09-附录.md`（含 `05b-灵敏度分析与模型检验.md`）
- 图表、公式、LaTeX、分页、编译和专项审计：`references/layout-and-compilation.md`
  - **硬性纪律**：凡使用 `longtable`，必须配齐 `\endfirsthead` / `\endhead` / `\endfoot` / `\endlastfoot` 四件套；续页标题必带原表号（`\thetable`，形如“续表 N　原表题”）；末页底线 `\bottomrule` 只允许一条并放在 `\endfoot` 与 `\endlastfoot` 之间的末页页脚段内，表末数据行后不得再写第二个 `\bottomrule`。缺任一即视为未实现跨页续表，`audit_paper_tables.py` 的 T-5b 将 FAIL。
- 去 AI 味、技术保真、故事线和冷读：`references/language-and-storyline.md`
- 排版顺序、写作顺序、必读清单和章节重读映射：`references/writing-order.json`
- 跨阶段共享策略与 manifest 契约：注册表列出的 `../mm-orchestrator/references/*` 文件。

## 论文排版顺序

摘要 → 问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型的建立与求解 → 灵敏度分析与模型检验 → 模型评价与推广 → AI 使用声明 → 参考文献 → 附录。

## 实际写作顺序

问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型的建立与求解 → 灵敏度分析与模型检验 → 模型评价与推广 → AI 使用声明 → 参考文献 → 附录 → 摘要。

**摘要在 PDF 中排第一，但必须最后写。** 其他十部分、真实结果和检验尚未完成时，不得起草或定稿摘要。

## 就地重读

全量预读通过后，每写一个章节前必须再次完整读取 `writing-order.json.reread_before_writing` 指向的章节文件。写模型章前还要重读 `layout-and-compilation.md`；写摘要前必须确认其他十部分已完成并重读 `00-摘要.md`。

## 写作轮与独立审查轮

- **写作轮（唯一一次完整调用）**：完整执行“完整读取硬门禁”（账本 `paper/.read-session.json`、回执 `paper/skill-read-receipt.json`、`verify` exit 0），从上游材料成稿 `paper/论文.tex|pdf`，至少双遍编译并跑全部专项机检；生成 `paper/writing-audit.md`，按每个必读文件及其全部二/三级标题记录“已执行/不适用（含理由）/阻断”，并通过 `validate_requirement_coverage.py`。此时 `paper_final.status` 保持 `in_progress`。
- **独立审查轮**：以写作轮终稿为审查对象做独立终审与修订。**不要求重新完整读取全部注册文件**——读取完整性已由写作轮回执硬门禁保证；只就地重读本轮实际修订章节对应的 `reread_before_writing` 模块，涉排版改动加读 `references/layout-and-compilation.md`。审查优先由**未参与写作的独立会话或子代理**执行（真实的 fresh eyes）；无条件时由主会话按冷读清单执行并在审计中注明。审查必须：① 对照 `docs/01~03`、`results/` 与 `paper/structure-plan.md` 追踪表逐问核对终稿（数字一致、题面逐条覆盖、最终回答可定位、无模板化段落）；② 对未改动项也逐项记录核对证据，不得以“写作轮已通过”为由跳过；③ 跑全套专项机检，发现问题直接修正、重编译双遍并重跑全部机检。
- 产出：`paper/review-findings.md`（逐章发现：问题/严重度/证据/处置）与 `paper/review-audit.md`（覆盖注册表每个必读文件“已执行/不适用及理由”，并通过 `validate_requirement_coverage.py`）。
- 只有审查轮无阻断项、终稿正文 25～30 页、全套机检 exit 0，且 `read_receipt`、`writing_audit`、`review_findings`、`review_audit` 均登记哈希，才能置 `paper_final.status=complete` 并进入 `mm-verification`。

## 产出与边界

- 唯一终稿：`paper/论文.tex` 与 XeLaTeX 编译的 `paper/论文.pdf`；同时生成页数审计、内容缺口报告、写作轮读取回执与写作/审查两份审计。
- 不改动数值结果和图件内容；冲突回写对应 owner skill。
- 不画图；所有正文插图来自 `mm-figures` 或 `mm-graphics`。
- 不编造数据、参数、实验、文献或人工核验记录。
- 最终稿仍以当届官方规则和用户明确提供的模板为最高优先级，并记录覆盖原因。
