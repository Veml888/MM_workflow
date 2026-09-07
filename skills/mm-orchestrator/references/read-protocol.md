# 完整读取协议（read-protocol）

> **本文件是 8 个 mm-* skill 共享的"完整读取、不可截断"机制文档**。每个 SKILL.md 的顶部 `<!-- READ-GATE -->` 块指向这里。
>
> **本协议的核心纪律**：未走完 `plan → chunk → write-receipt → verify` 四步且 `verify` exit 0，**不得进入本阶段任何正式工作流**——这不只是"写产出物之前"的检查，而是**整个阶段开工前**的 GATE：第一次调用本 skill、第一次读题面、第一次看上游报告，都属于"开工"。

## 1. 为什么需要这个机制

数模 skill 的入口 SKILL.md 通常较长（部分超过 25 KB），加上跨 skill 的 references（mm-orchestrator 13 文件 / mm-problem-analysis 11 / mm-paper-writing 35 / mm-modeling 13 / mm-coding 7 / mm-figures 7 / mm-graphics 7 / mm-verification 9），单次读入会触发模型截断——下游会"以为读了其实只读到一半"，按残缺的认知做决策。完整读取协议就是用机器可验证的方式强制"每块都被实际读过、覆盖到 EOF"。

## 1.5 `read_complete.py` 的双重角色

经常被混淆的一点：**`read_complete.py` 不是"检测脚本"——它是"强制读完 + 检测"组合机制**。

| 阶段 | 角色 | 它做什么 | 它阻止什么 |
|---|---|---|---|
| `plan` | **只读** | 量文件行数、算 SHA256、算分块边界，输出 JSON | 不阻止任何事——只输出注册表的物理视图 |
| `chunk` | **强制读完整** | 把文件第 [start, end] 行实际打到 stdout，**并把"这块被读过"写进 ledger.json**。你必须**真的看到 stdout 内容**才算读完 | 你可以跳过 chunk——但跳过意味着 ledger 没那块，verify 必然 FAIL |
| `write-receipt` | **强制记账** | 从 ledger.json 生成 receipt.json；**账本里没有的块** → exit ≠ 0 | "没真读过就生成回执"被堵死 |
| `verify` | **强制校验** | 拿 ledger + receipt + 当前文件 SHA256 三层对照；**任一不一致 exit ≠ 0** | "账本和文件不一致就声称读过"被堵死 |

**一句话总结**：

> `read_complete.py` 的 `chunk` 子命令**强制你按块读到 EOF**，`write-receipt` + `verify` 子命令**强制记账与三层 SHA256 锁定**。如果任何环节你跳过或漏块，verify exit ≠ 0，**你"声称读过"这件事就站不住脚**。

它**不能**替你"读"——它只能**强制你"读"**（chunk 必须被调一次、每次调必须实际看 stdout 内容、写进 ledger）。
它**能**阻止"读一半"——任何漏块都让 verify 失败。
它**不能**阻止"读了但没懂"——这是 `.read-notes-pass-<N>.md` 的职责（仅 mm-paper-writing 强制要求）。

## 2. 物理拓扑

```
mm-orchestrator/scripts/read_complete.py     ← 唯一共享脚本（~370 行，--skill 加载）
mm-paper-writing/scripts/check_paper_order.py ← paper 特异性校验（仅 mm-paper-writing 必跑）

每个 skill 的 references/ 下放自己的注册表：
  - mm-orchestrator/references/reading-order.json
  - mm-problem-analysis/references/reading-order.json
  - mm-modeling/references/reading-order.json
  - mm-coding/references/reading-order.json
  - mm-figures/references/reading-order.json
  - mm-graphics/references/reading-order.json
  - mm-verification/references/reading-order.json
  - mm-paper-writing/references/writing-order.json  （含 paper_order / writing_order 字段）
```

**严禁在 owner skill 内复制 read_complete.py**——所有 skill 统一调用 mm-orchestrator 下的共享副本。

## 3. 完整读取四步（统一模板）

**Step 1：plan —— 看本 skill 必读的所有文件与分块**

```bash
python <mm-orchestrator目录>/scripts/read_complete.py plan --skill <mm-xxx>
```

输出 JSON：每个文件的 `path` / `lines` / `bytes` / `sha256` / `chunks[]`。这一步不写文件，**只看不读**。

**Step 2：chunk —— 逐块、逐文件读取，每块输出必须看到 `READ-BEGIN` 与 `READ-END`**

```bash
# 先建本轮账本
echo '{"schema_version":"1.0","reads":[]}' > .read-session.json

# 按 plan 给出的 chunks 逐块读取
python <mm-orchestrator目录>/scripts/read_complete.py chunk \
    --skill <mm-xxx> \
    --path <rel> \
    --start <起始行> \
    --end <结束行> \
    --session .read-session.json
```

每块输出格式：

```
READ-BEGIN skill=mm-xxx path=<rel> range=<start>-<end> sha256=<64hex>
0001: <line content>
0002: <line content>
...
READ-END skill=mm-xxx path=<rel> range=<start>-<end> sha256=<64hex>
```

**关键纪律**：

- 缺 `READ-BEGIN` 或 `READ-END` → 输出被截断，**缩小分块后重读**
- 每一行编号 + 内容必须实际读懂（仅执行命令不算完成；`read_complete.py` 只能证明"每块被 chunk 过"，不能证明"真读了"——见 §6）
- 账本未覆盖任何一块都会让后续步骤 FAIL

**Step 3：write-receipt —— 从账本生成回执**

```bash
python <mm-orchestrator目录>/scripts/read_complete.py write-receipt \
    --skill <mm-xxx> \
    --pass 1 \
    --receipt skill-read-receipt.json \
    --session .read-session.json
```

- 账本未覆盖任何分块 → exit ≠ 0，FAIL
- 全部覆盖 → exit 0，生成 `skill-read-receipt.json` 含每个文件的 `sha256` / `headings_seen` / `chunks[]`

**Step 4：verify —— 三层 SHA256 校验 + EOF 覆盖校验**

```bash
python <mm-orchestrator目录>/scripts/read_complete.py verify \
    --skill <mm-xxx> \
    --receipt skill-read-receipt.json \
    --session .read-session.json
```

校验项（任一 FAIL 即整体 FAIL）：

| 校验项 | 失败后果 |
|---|---|
| 注册表 SHA256 与 receipt 一致 | FAIL（注册表被篡改） |
| 账本 SHA256 与 receipt 一致 | FAIL（账本被篡改） |
| 账本覆盖注册表每个文件的每个分块 | FAIL（漏读） |
| 每个分块 `end_marker_seen=true` | FAIL（READ-END 缺失） |
| 所有分块拼起来覆盖到 EOF | FAIL（不读到末尾） |
| 哈希与注册表文件当前哈希一致 | FAIL（文件被改动） |

**`verify` exit 0 = PASS**。后续工作流才能启动。

## 4. mm-paper-writing 的额外第 5 步

mm-paper-writing 有 11 章固定顺序、摘要最后写、reread_before_writing 全覆盖等 paper 特异性要求——这些不属于通用协议，由 mm-paper-writing 自己的 `check_paper_order.py` 守。

```bash
python <mm-paper-writing目录>/scripts/check_paper_order.py
```

exit ≠ 0 → mm-paper-writing 的写作轮**禁止开始**。

## 5. 防截断的4 重闸门（汇总）

| 闸 | 由谁保证 | 失效后果 |
|---|---|---|
| `READ-BEGIN` / `READ-END` 标记 | `chunk` 子命令 | 缺一视为输出被截断，必须缩小分块重读 |
| 分块 EOF 覆盖 | `verify` 第 `cursor == lines + 1` 检查 | 任何一块不读到末尾 → FAIL |
| 三层 SHA256 锁定 | `verify` 整体 | 任一不一致 → FAIL |
| paper 特异性（仅 mm-paper-writing） | `check_paper_order.py` | exit ≠ 0 → 写作轮禁止开始 |

## 6. 防"刷账本过关"

`write-receipt` / `verify` 只能证明"每块都被 chunk 过、覆盖全部分块"，**不能证明真正阅读**。因此：

- mm-paper-writing 写作轮**必须**额外维护 `paper/.read-notes-pass-<N>.md`，为每个必读文件记录 1~2 句要点摘录。审计与 `verify` 互相对照——凡某文件只有"已读"无要点摘录，视为未实质阅读，须回读补记。
- 其他 skill 若需要这一层证据，按 SKILL.md 的明示要求做（目前 mm-paper-writing 是唯一强制要求者）。

## 7. 跨 skill 引用与扩展

注册表 `required_before_reading[]` 允许：

- 同 skill 内：`SKILL.md`、`references/xxx.md` —— 相对路径相对该 skill 目录
- 跨 skill：`../mm-xxx/references/yyy.md` —— 通用脚本会自动 resolve

将来加新的 mm-* skill 时，只需两步：

1. 在该 skill 的 `references/` 下写一份 `reading-order.json`（`schema_version: "1.0"` + `required_before_reading[]` + `limits`）
2. 在 SKILL.md 顶部加 `<!-- READ-GATE -->` 块指向本文件

无需复制任何脚本。

## 8. 失败模式与恢复

| 失败 | 修复 |
|---|---|
| `plan` 报 "file exceeds registered size limit" | 调大 `reading-order.json` 的 `skill_max_bytes` / `module_max_bytes`；再重新 plan |
| `chunk` 缺 `READ-END` | 缩分块范围 + 重读那块 |
| `write-receipt` 报 "ledger is incomplete" | 补漏块的 chunk 调用 |
| `verify` 报 "registry hash does not match" | 注册表被改；重新 plan |
| `verify` 报 "hash mismatch in receipt: <rel>" | 必读文件被改；重跑 plan + chunk + write-receipt + verify |
| `check_paper_order` 报 FAIL（仅 mm-paper-writing） | 修 writing-order.json 的 paper_order / writing_order / reread 字段 |

## 9. 索引

- 共享脚本：`mm-orchestrator/scripts/read_complete.py`
- mm-paper-writing 特异性脚本：`mm-paper-writing/scripts/check_paper_order.py`
- 共享 references（本文件）：`mm-orchestrator/references/read-protocol.md`
- 每个 skill 的注册表：`<mm-xxx>/references/reading-order.json` 或 `<mm-paper-writing>/references/writing-order.json`
- 每个 SKILL.md 顶部的 READ-GATE 块都指向本文件