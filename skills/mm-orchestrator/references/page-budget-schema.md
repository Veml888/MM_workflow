# page-budget.json 字段约束

> 本文件是 `paper/page-budget.json` 的字段级规范。脚本级校验以 `<mm-orchestrator目录>/scripts/validate_paper_plan.py` 为准；本文件解释每个字段的含义与合法取值。

## 顶层字段

```json
{
  "schema_version": "1.0",
  "target_body_pages": 28,
  "allowed_range": [25, 30],
  "draft": {"mode": "none"},
  "sections": []
}
```

- `schema_version`：固定 `"1.0"`；非该值则脚本 FAIL。
- `target_body_pages`：仅允许 `28` 或 `29`；其他值脚本 FAIL。
- `allowed_range`：固定 `[25, 30]`；其他值脚本 FAIL。
- `draft.mode`：四选一 `"retained" | "partial" | "invalidated" | "none"`。详见 `draft-takeover.md`。
- `sections`：非空数组；每项结构见下。

## sections[] 元素

每项至少包含以下 7 个字段：

| 字段 | 类型 | 约束 |
|---|---|---|
| `id` | string | 非空、整文件唯一；推荐命名 `SEC-FRONT`、`SEC-P01`、`SEC-P02`、`SEC-SENS`、`SEC-CLOSE` 等 |
| `title` | string | 非空 |
| `min_pages` | number | `0 <= min_pages <= target_pages <= max_pages` |
| `target_pages` | number | 与 `min_pages`、`max_pages` 满足上述不等式；所有 sections 之和必须等于 `target_body_pages`（误差 ≤ 1e-6） |
| `max_pages` | number | 同上 |
| `source_paths` | string[] | 非空；每一项相对 PROJECT_ROOT 可解析；脚本检查文件存在性 |
| `evidence_ids` | string[] | 非空；引用 `project-manifest.json` 中的稳定 ID（`REQ-###`、`P-##`、`R-P##-###`、`SYM-###` 等） |

## 占位符扫描

脚本会扫以下模式（大小写不敏感），命中即 FAIL：

- `<...>`（尖括号包住的占位符）
- `【...填写...】`、`【...待补充...】`、`【...占位...】`（中文书名号 + 动作词）
- 裸词 `待补充`、`以后完善`、`TODO`、`TBD`

定稿时这些都必须替换为真实内容；初始化阶段的空骨架（`sections: []`）不算占位符。

## draft.mode 字段

当 `mode != "none"` 时，draft 对象必须包含：

```json
{
  "mode": "retained",
  "path": "paper/draft-baseline.tex",
  "sha256": "<64位十六进制>",
  "body_pages": 24,
  "audit_path": "paper/draft-audit.md"
}
```

- `path` 与 `audit_path` 都必须是 PROJECT_ROOT 下存在的文件，脚本会检查。
- `sha256` 必须为合法 64 位 hex。
- `body_pages` 数值非负。

## 校验脚本

```bash
python <mm-orchestrator目录>/scripts/validate_paper_plan.py paper/page-budget.json --root .
```

退出码：0 = PASS，1 = FAIL（错误列表 JSON 输出到 stdout）。脚本只依赖 Python 标准库。

## 字段示例（5 章节版本，仅作参考）

```json
{
  "schema_version": "1.0",
  "target_body_pages": 28,
  "allowed_range": [25, 30],
  "draft": {"mode": "none"},
  "sections": [
    {
      "id": "SEC-FRONT", "title": "前部章节", "min_pages": 3, "target_pages": 4, "max_pages": 5,
      "source_paths": ["docs/01-analysis-report.md", "docs/02-modeling-report.md"],
      "evidence_ids": ["P-01", "SYM-001"]
    },
    {
      "id": "SEC-P01", "title": "问题一模型建立与求解", "min_pages": 8, "target_pages": 9, "max_pages": 10,
      "source_paths": ["docs/02-modeling-report.md", "docs/03-results-report.md"],
      "evidence_ids": ["P-01", "R-P01-001"]
    },
    {
      "id": "SEC-P02", "title": "问题二模型建立与求解", "min_pages": 8, "target_pages": 10, "max_pages": 11,
      "source_paths": ["docs/02-modeling-report.md", "docs/03-results-report.md"],
      "evidence_ids": ["P-02", "R-P02-001"]
    },
    {
      "id": "SEC-SENS", "title": "灵敏度分析与模型检验", "min_pages": 1, "target_pages": 2, "max_pages": 3,
      "source_paths": ["docs/02-modeling-report.md", "docs/03-results-report.md"],
      "evidence_ids": ["R-P01-001", "R-P02-001"]
    },
    {
      "id": "SEC-CLOSE", "title": "评价与收尾", "min_pages": 2, "target_pages": 3, "max_pages": 4,
      "source_paths": ["plan.md", "docs/03-results-report.md"],
      "evidence_ids": ["REQ-001", "R-P02-001"]
    }
  ]
}
```

- 上例 `target_pages` 之和 = 4 + 9 + 10 + 2 + 3 = 28，与 `target_body_pages` 一致。
- 章节数量、各章命名可按题目调整；只要通过校验脚本即可。
- **禁止照搬**——按问题难度与证据量分配，不平均分配。