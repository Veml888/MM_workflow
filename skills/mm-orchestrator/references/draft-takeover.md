# 初稿接管（draft-takeover）

> 仅当用户在调度编排器之前已经提供了一份 `paper/论文.tex`（例如旧项目复用或人手先起一版）时才执行。无初稿一律 `mode=none`。

## 触发条件

- 调用编排器第 3 步时检测到 `paper/论文.tex` 已存在，且 `paper_final.status` 尚未 `complete`。
- 没有初稿时：记录 `draft.mode=none`，跳过本文件全部步骤。

## 步骤

1. **改名为基线**：把 `paper/论文.tex` 改名为 `paper/draft-baseline.tex`（精确改名、不覆盖；同名则保留已有的 draft-baseline，不动）。记录 SHA256。
2. **尝试编译**：在 `paper/` 下跑 XeLaTeX 编译 `draft-baseline.tex`，产出 `paper/draft-baseline.pdf`（若编译失败，PDF 可缺，记录 `compile_ok=false`）。
3. **量基线页数**：跑 `<mm-paper-writing目录>/scripts/check_paper_length.py --draft paper/draft-baseline.tex`，记录 `body_pages`。
4. **写审计文件**：在 `paper/draft-audit.md` 逐章将初稿内容标注"保留 / 改写 / 删除 / 补充"，核对题意、最终模型、公式符号、真实结果、图件锚点、题面覆盖、占位符与模板化段落；冲突一律以上游报告、结果和 manifest 为准。
5. **写指标文件**：在 `paper/draft-metrics.json` 写入模式（`retained/partial/invalidated`）、路径、SHA256、页数与可编译状态。

编排器只做只读比较和缺口规划，不改写初稿正文。若已有 `draft-baseline.*`，不得覆盖。

## 三种模式

| mode | 含义 | 用法 |
|---|---|---|
| `retained` | 全文整体可用 | 写作轮基于 baseline 增量补章节与图件 |
| `partial` | 部分可用 | 写作轮保留可用章节、改写其余 |
| `invalidated` | 不可用 | 写作轮不引用 baseline 内容，但 metrics 仍登记便于审计 |

## draft 字段写入 page-budget.json

`draft.mode` 必须与 `draft-metrics.json.mode` 一致；脚本 `validate_paper_plan.py` 会检查：

```json
{
  "mode": "retained",
  "path": "paper/draft-baseline.tex",
  "sha256": "<64位hex>",
  "body_pages": 24,
  "audit_path": "paper/draft-audit.md"
}
```

`path` 与 `audit_path` 都必须是 PROJECT_ROOT 下存在的文件。

## 与 manifest 的对应

- `stages.paper_final.draft_mode`：四选一 `retained/partial/invalidated/none`，与 `paper/page-budget.json.draft.mode` 与 `paper/draft-metrics.json.mode` 三者一致。
- `stages.paper_final.draft_path`、`draft_sha256`、`draft_body_pages`：当 `draft_mode != "none"` 时必须登记，校验脚本 `validate_manifest.py` 会强制检查。