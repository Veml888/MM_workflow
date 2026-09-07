# CUMCM 数学建模 8 阶段流水线 — Skill 集

> 本仓库承载 **全国大学生数学建模竞赛（CUMCM）全流程的 8 个 mm-* skill** + **共享完整读取协议**。每个 skill 独立可用，遵循统一的目录结构与机器可验证的"完整读取"门禁。

---

## 流水线一览

| # | 阶段 | skill | 关键产出 |
|---|---|---|---|
| 1 | 赛题分析 | `mm-problem-analysis` | `docs/01-analysis-report.md` |
| 2 | 建模求解 | `mm-modeling` | `docs/02-modeling-report.md` |
| 3 | 编程实现 | `mm-coding` | `code/`、`results/`、`docs/03-results-report.md` |
| 4 | 论文策划 | `mm-orchestrator` | `paper/structure-plan.md` 等 6 份 |
| 5a | 数据图 | `mm-figures` | `figures/*`、`docs/04-figures-report.md` |
| 5b | 非数据图 | `mm-graphics` | `figures/*`、`docs/05-diagrams-report.md` |
| 6a | 写作轮 | `mm-paper-writing` | `paper/论文.tex|pdf` 等 |
| 6b | 独立审查轮 | `mm-paper-writing` | `paper/review-*.md` 等 |
| 7 | 验收 | `mm-verification` | `docs/06-verification-report.md` |

`mm-orchestrator` 是总入口与跨阶段调度器；`mm-model-dictionary` 是建模阶段的模型字典查询工具。

---

## 完整读取协议（共享机制）

8 个 skill 共用一份**强制读完 + 检测**组合机制：

- 共享脚本：`mm-orchestrator/scripts/read_complete.py`（**唯一副本**，所有 skill 共享）
- 每个 skill 的必读清单：`<mm-xxx>/references/reading-order.json` 或 `<mm-paper-writing>/references/writing-order.json`
- mm-paper-writing 特异性：`mm-paper-writing/scripts/check_paper_order.py`（守 11 章顺序 / 摘要最后写）

四步流程（每个 skill 开工前必走）：

```bash
# Step 1: plan —— 列出本 skill 必读的全部文件与分块边界
python skills/mm-orchestrator/scripts/read_complete.py plan --skill <mm-xxx>

# Step 2: chunk —— 逐块、逐文件读取；缺 READ-BEGIN/READ-END 视为截断
echo '{"schema_version":"1.0","reads":[]}' > .read-session.json
python skills/mm-orchestrator/scripts/read_complete.py chunk \
    --skill <mm-xxx> --path <rel> --start N --end M \
    --session .read-session.json

# Step 3: write-receipt —— 从账本生成回执
python skills/mm-orchestrator/scripts/read_complete.py write-receipt \
    --skill <mm-xxx> --pass 1 \
    --receipt skill-read-receipt.json --session .read-session.json

# Step 4: verify —— 三层 SHA256 + EOF 覆盖校验；exit 0 才算 PASS
python skills/mm-orchestrator/scripts/read_complete.py verify \
    --skill <mm-xxx> \
    --receipt skill-read-receipt.json --session .read-session.json
```

详细机制：`skills/mm-orchestrator/references/read-protocol.md`。

每个 skill 的 `SKILL.md` 顶部 `<!-- READ-GATE:complete -->` 块是开工前的强制门禁——`verify` exit 0 之前**任何动作都不得开始**（包括读题面、写报告、跑脚本）。

---

## 目录结构

```
MM_workflow/
├── skills/                       # 8 个 mm-* skill 平铺
│   ├── mm-orchestrator/         # 阶段 1~7 的入口与调度器
│   ├── mm-problem-analysis/      # 阶段 1：赛题分析
│   ├── mm-modeling/              # 阶段 2：建模求解
│   ├── mm-coding/                # 阶段 3：编程实现
│   ├── mm-figures/               # 阶段 5a：数据图
│   ├── mm-graphics/              # 阶段 5b：非数据图
│   ├── mm-paper-writing/         # 阶段 6：论文写作
│   ├── mm-verification/         # 阶段 7：验收
│   └── mm-model-dictionary/      # 阶段 2 辅助：模型字典查询
├── README.md
├── LICENSE
└── .gitignore
```

每个 mm-* skill 内部统一结构：

```
skills/<mm-xxx>/
├── SKILL.md                     # 总控（顶部必有 READ-GATE 块）
├── references/
│   ├── reading-order.json       # 完整读取必读清单
│   └── *.md                    # 阶段专属细则
└── scripts/
    └── *.py                    # 阶段专属脚本（机检 / 校验 / 渲染）
```

完整读取协议调用示例（任何 skill）：

```bash
python skills/mm-orchestrator/scripts/read_complete.py plan --skill <mm-xxx>
```

---

## 依赖

- **Python 3.8+**（脚本全部 stdlib-only，不需要额外依赖）
- **Git Bash / Bash shell**（`read_complete.py` 路径自解析，在任意工作目录运行）
- **XeLaTeX / Tectonic**（仅 mm-paper-writing 阶段需要）
- **Pandoc / MiKTeX**（可选，便于本地编译 LaTeX 论文）

---

## 快速开始

1. **选一个 skill**（通常是 `mm-orchestrator`，因为它是总入口）
2. **打开对应 SKILL.md**，先看顶部 `<!-- READ-GATE:complete -->` 块
3. **运行 READ-GATE 四步**，拿到 `verify exit 0`
4. **按 SKILL.md 的"工作流"段开始干活**

---

## 跨 skill 引用约定

- `<mm-xxx目录>` 一律指同级兄弟目录 `../mm-xxx/`
- `references/reading-order.json` 里可以写 `../mm-yyy/references/zzz.md` 跨 skill 引用
- 共享脚本路径永远在 `skills/mm-orchestrator/scripts/` 下

---

## 添加新的 mm-* skill

1. 在 `skills/` 下新建 `mm-<your-name>/` 目录，按统一结构组织
2. 写 `SKILL.md`（顶部加 `<!-- READ-GATE:complete -->` 块）
3. 写 `references/reading-order.json`（`schema_version: "1.0"` + `required_before_reading[]` + `limits`）
4. 调用 `python skills/mm-orchestrator/scripts/read_complete.py plan --skill mm-<your-name>` 校验
5. （可选）写 `scripts/*.py` 机检脚本

无需复制任何脚本——所有 skill 共享 `skills/mm-orchestrator/scripts/read_complete.py`。

---

## 许可

MIT License。详见 [LICENSE](./LICENSE)。