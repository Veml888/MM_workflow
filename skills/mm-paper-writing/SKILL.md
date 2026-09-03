---
name: mm-paper-writing
description: CUMCM 论文撰写阶段。当用户需要撰写或接管国赛数模论文初稿，并完成摘要、问题重述、问题分析、模型假设、符号说明、模型的建立与求解、模型评价与推广、AI 使用声明、参考文献和附录终稿时使用。全流程须连续调用两次；每次必须完整读取注册表中的全部规范、按章节重读并独立完成编译审计。
---

# 数学建模：竞赛论文撰写

本文件只负责总控。章节细则、公共规则、排版规则和第二轮终审规则分别保存在 `references/`；不得凭本入口的概述直接开始写作。

**工具与路径（全部相对本 SKILL.md 所在目录解析，skills 目录整体搬移或换机无需改动）**：`<本skill目录>` 即本文件所在目录，`read_complete.py` 位于 `scripts/read_complete.py`；其他文件中的 `<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`。脚本内部路径自解析、可在任意工作目录运行；但脚本参数中的相对路径相对当前工作目录解析，机检一律在 PROJECT_ROOT 下执行。

## 完整读取硬门禁

每次调用开始时必须：

1. 运行 `python <本skill目录>/scripts/read_complete.py plan`，取得 `references/writing-order.json` 登记的全部必读文件、SHA256、行数、标题和安全分块。
2. 为本轮建立独立读取账本：`paper/.read-session-pass-1.json`（第一轮）或 `paper/.read-session-pass-2.json`（第二轮）。
3. 按计划逐块、**按序**运行 `read_complete.py chunk --path <相对路径> --start <起始行> --end <结束行> --session <本轮账本路径>`；每块输出必须**先看到 `READ-BEGIN`、读完该块全部行、再看到 `READ-END` 结束标记**，缺任一标记即视为输出被截断，缩小分块后重读。**必须真正阅读该块打印出的正文内容**，并在继续前能复述其要点；仅执行命令而不读内容不算完成读取。
4. 全部必读文件的所有分块都逐块 chunk 后，运行 `read_complete.py write-receipt --pass <1|2> --receipt paper/skill-read-receipt-pass-<N>.json --session <本轮账本路径>`。该脚本只从账本生成回执；账本未覆盖任何一块都会失败。
5. 运行 `read_complete.py verify --receipt <回执路径> --session <本轮账本路径>`。`verify` 会校验：回执的注册表哈希、账本 SHA256、以及账本是否覆盖了注册表中每个必读文件的每个分块。**脚本非零时不得写入或修改 `paper/论文.tex`。**
6. G-1 必须引用回执路径、注册表 SHA256、本轮账本路径及其 SHA256、以及所有必读文件哈希。

**硬性纪律**：禁止用 `template` 直接生成回执；禁止手工编写回执 JSON；禁止复用上一轮账本、回执、上下文或"已读"结论。第一轮用 `paper/.read-session-pass-1.json`，第二轮必须重新建立 `paper/.read-session-pass-2.json` 并重新逐块读取，两轮账本互不相同、均须覆盖全部必读文件。

## 必读模块

- 流程、输入输出、初稿接管与 GATE：`references/workflow-and-gates.md`
- 全文公共规则和固定论文骨架：`references/common-paper-rules.md`
- 正文页数控制（27–30 页，篇幅不足怎么补/超出怎么减）：`references/篇幅控制-playbook.md`
- 十个实际论文章节：`references/chapters/00-摘要.md` 至 `references/chapters/09-附录.md`
- 图表、公式、LaTeX、分页、编译和专项审计：`references/layout-and-compilation.md`
- 去 AI 味、技术保真、故事线和冷读：`references/language-and-storyline.md`
- 第二次调用独立终审：`references/second-pass-review.md`
- 排版顺序、写作顺序、必读清单和章节重读映射：`references/writing-order.json`
- 跨阶段共享策略与 manifest 契约：注册表列出的 `../mm-orchestrator/references/*` 文件。

## 论文排版顺序

摘要 → 问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型的建立与求解 → 模型评价与推广 → AI 使用声明 → 参考文献 → 附录。

## 实际写作顺序

问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型的建立与求解 → 模型评价与推广 → AI 使用声明 → 参考文献 → 附录 → 摘要。

**摘要在 PDF 中排第一，但必须最后写。** 其他九部分、真实结果和检验尚未完成时，不得起草或定稿摘要。

## 就地重读

全量预读通过后，每写一个章节前必须再次完整读取 `writing-order.json.reread_before_writing` 指向的章节文件。写模型章前还要重读 `layout-and-compilation.md`；写摘要前必须确认其他九部分已完成并重读 `00-摘要.md`。

## 两次独立调用

- 第一轮完成全文、至少双遍编译和全部专项审计，生成 `paper/pass-1-audit.md` 与第一轮读取回执；`paper_final.status` 保持 `in_progress`。
- 第二轮重新执行全量读取和就地重读，以第一轮终稿为审查对象，逐章修订并重跑全部审计，生成 `paper/pass-2-audit.md` 与第二轮读取回执。
- 两轮审计必须列出每个必读文件及其全部二/三级标题，记录“已执行”或“不适用及理由”，并通过 `validate_requirement_coverage.py`。
- 只有第二轮无阻断项、两轮各至少双遍编译、读取回执和要求覆盖均通过，才能设置 `full_skill_passes=2`、`paper_final.status=complete` 并进入 `mm-verification`。

## 产出与边界

- 唯一终稿：`paper/论文.tex` 与 XeLaTeX 编译的 `paper/论文.pdf`；同时生成页数审计、内容缺口报告、两轮读取回执和两轮审计。
- 不改动数值结果和图件内容；冲突回写对应 owner skill。
- 不画图；所有正文插图来自 `mm-figures` 或 `mm-graphics`。
- 不编造数据、参数、实验、文献或人工核验记录。
- 最终稿仍以当届官方规则和用户明确提供的模板为最高优先级，并记录覆盖原因。
