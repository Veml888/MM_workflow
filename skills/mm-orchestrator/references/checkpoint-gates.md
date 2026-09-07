# 阶段门禁与机检协议

> 本文件定义编排器在每个阶段开始前与结束时的硬性协议。所有 `stages.*.status` 状态变更必须按本协议留痕；以 owner skill 与 scripts 为权威。

## 阶段开始前：回显 + GATE

每个阶段启动时（无论编排器直接调用还是交给下游 skill）必须输出：

```
[STAGE: <name>]
  owner skill     : <mm-xxx>
  upstream reports: [列出上游 report 路径]
  this-stage output: [列出本阶段将产出的文件]
  scripts to run   : [列出本阶段机检脚本]
```

之后输出 **GATE 确认**：

1. 上游产物存在（manifest 已登记 + 文件在磁盘）。
2. 必读规范已读（引用 owner skill 的必读文件原文路径或 SHA）。
3. 计划产出明确（文件路径、阶段状态机检清单已写在 manifest）。
4. 任意上游缺失先补齐再进下一阶段。

## 阶段结束：更新 manifest + 跑机检

每阶段完成（含 n_a）必须：

1. 把本阶段拥有的字段写进 manifest：状态、产物路径、产物哈希、版本。
2. 追加 `change_log`：时间、发起阶段、目标阶段、原因、受影响 ID、新版本。
3. 跑对应机检脚本，exit 0 才能置 `complete`；详见 `stage-pipeline.md` 表格"验收脚本"列。
4. 跑 `<mm-orchestrator目录>/scripts/validate_manifest.py`（如果装了 `jsonschema`，会自动跑 Schema 校验）。
5. 若产生新文件或覆盖了旧文件，把它登记到 `artifacts[]`（`path`、`sha256`、`producer_stage`、`version`）。

## 阶段 `n_a`

- 在 `plan.md` 写明不适用原因。
- manifest 把对应 `stages.<name>.status` 置 `n_a`，**不要再写哈希或版本**。
- 范围化验收不要求 `n_a` 产物；但最终总结必须说明本次未做的范围。

## 返工（rework）协议

- 验收阶段发现问题时，由 `mm-verification` 创建 `rework[]` 条目（`id`、`source`、`target_stage`、`affected_stages`、`issue`、`severity`、`status`、`created_at`、`resolved_at`）。
- `severity`：critical / major / minor；critical 与 major 必须 `resolved` 后才能再次验收。
- 修复由对应 owner skill 完成；`stages.<name>.status` 从 `complete` 回到 `in_progress`，修完后重跑本阶段机检 + 下游阶段机检（按 `affected_stages` 决定重跑范围）。
- 修复完毕：把 `rework[].status` 置 `resolved`，`resolved_at` 填时间戳。

## 阶段产物未通过验收前

不得声称"全流程完成"。`mm-verification` 只审计、定位并指定回写阶段；编排器负责调用对应 skill 修复后再次验收。

## 编排器自身的脚本

| 脚本 | 用途 |
|---|---|
| `<mm-orchestrator目录>/scripts/init_project_skeleton.py` | 第 3 步一次性建齐 plan.md / todo.md / manifest + paper/ 4 份空骨架 |
| `<mm-orchestrator目录>/scripts/init_paper_gates.py` | 把 G-1~G-5 初始化成 `pending` 写入 manifest 与 writing-gates.md |
| `<mm-orchestrator目录>/scripts/validate_paper_plan.py` | 论文策划正式定稿结束前的字段级校验 |
| `<mm-orchestrator目录>/scripts/validate_manifest.py` | manifest Schema 校验 + stdlib 检查 |

每个阶段 owner skill 也提供对应机检脚本，详见 `stage-pipeline.md` 表格。