# Global storage policy (Windows)

Apply the following storage priority to every Codex task.

## 1. Work that belongs to a project

- Keep all project-related downloads, dependency caches, temporary files, extracted archives, build intermediates, generated data, model files, and other task working files inside the current project/workspace.
- Prefer the project's existing conventions first, such as `data/`, `models/`, `outputs/`, `build/`, `.venv/`, or an existing cache directory.
- When the project has no suitable location, create `.codex-work/<task-name>/` inside the project, with subdirectories such as `downloads/`, `temp/`, and `cache/`. Use a short, descriptive task name and reuse it for the same task.
- Keep disposable `.codex-work/` content out of version control. Use an existing ignore rule when possible; otherwise add `.codex-work/` to `.gitignore` without disturbing other entries. Do not hide files that are intended project deliverables.
- For commands that may create substantial temporary or cached data, set supported process-scoped variables such as `TEMP`, `TMP`, `PIP_CACHE_DIR`, `UV_CACHE_DIR`, `npm_config_cache`, `PLAYWRIGHT_BROWSERS_PATH`, `HF_HOME`, and `TORCH_HOME` to the appropriate directory inside the project. Do not change Windows user-wide or system-wide variables without explicit permission.
- If the project is located on C: and the task is expected to create or download more than 100 MB of non-deliverable data, warn the user before starting and ask whether that data should instead be offloaded to D:.

## 2. Large standalone software

- For software that is not a dependency contained in the current project, download its installer, archive, and installation support files under `D:\CodexSoftware/<software-name>/`.
- Prefer an installation destination on D: when the installer supports choosing one. Some software may still require small system components on C:; disclose this before installation.
- Before installing or upgrading standalone software, report the software name, expected download/install size, download path, proposed installation path, and whether administrator access is required. Obtain explicit user approval before running the installer.
- Never silently install large software or accept a default C-drive installation path.

## 3. Work without a project

- Use `D:\CodexDownloads/<task-name>/` for downloads and working files that do not belong to a project or standalone software installation.
- Do not place files directly in `D:\CodexDownloads` or `D:\CodexSoftware`; always create or reuse a named subdirectory.

## General safeguards

- Do not use `C:\Users\32530\Downloads`, `C:\Users\32530\AppData\Local\Temp`, or another C-drive location for durable Codex downloads or avoidable caches.
- If a tool cannot redirect a large download or temporary file away from C:, stop before downloading and tell the user its expected size and destination.
- After substantial downloads or generation, report the final paths and approximate sizes.
- Remove disposable files only when cleanup was requested or clearly authorized; otherwise leave them in the relevant project or task directory.

--- project-doc ---

# AGENTS.md — CUMCM 2026 工作流入口

本工作区只用于全国大学生数学建模竞赛 CUMCM 2026。用户要求其他竞赛时，说明当前流水线不适配，不套用本工作流。

## 权威来源

执行数模任务前，先读取以下文件：

1. `C:\Users\32530\.codex\skills\mm-orchestrator\references\cumcm-2026-shared-policy.md`：跨阶段唯一权威规则；
2. `C:\Users\32530\.codex\skills\mm-orchestrator\references\project-manifest-contract.md`：机器可读交接契约；
3. `C:\Users\32530\.codex\skills\mm-orchestrator\references\project-layout.md`：目录与产物约定；
4. 当前阶段 skill 的完整 `SKILL.md` 及其明确要求的参考文件。

本文件只负责范围、路由、顺序和回写机制，不重复论文页数、图表数量、视觉风格、格式参数等详细规定。详细规则发生冲突时，以用户当前明确指令和上述共享规则为准。

## 调用路由

| 请求 | 使用 skill |
|---|---|
| 开始建模、做完整赛题、跑全流程、写完整论文 | `mm-orchestrator` |
| 赛题重述、题型判断、数据初探、建模方向 | `mm-problem-analysis` |
| 假设、符号、公式、推导、算法与验证设计 | `mm-modeling` |
| 编码求解、计算结果、证据实验、仿真与复现 | `mm-coding` |
| 基于真实结果的数据图 | `mm-figures` |
| 技术路线、总体框架、模型结构、指标体系、变量关系、验证闭环 | `mm-diagrams` |
| 场景、空间关系、对象交互、算法原理隐喻等纯视觉示意图 | `mm-visual-concept` |
| 论文结构草稿或论文终稿 | `mm-paper-writing` |
| 完整性、一致性、可复现性、格式与支撑材料验收 | `mm-verification` |

用户只要求一个阶段时，只调用对应 skill。需要上游数据但当前缺失时，先报告缺口；不得凭空补造上游结果。

## 完整流程

1. `mm-orchestrator` 创建 `plan.md`、`todo.md` 和 `project-manifest.json`。
2. `mm-problem-analysis` 生成 `docs/01-analysis-report.md`。
3. `mm-modeling` 生成 `docs/02-modeling-report.md`。
4. `mm-coding` 生成 `code/`、`results/`、`docs/03-results-report.md` 和扩展复现清单。
5. `mm-paper-writing` 第一遍生成 `paper/structure-draft.md` 与 `paper/figure-requirements.md`，不生成终稿。
6. 按插图需求分别调用：
   - `mm-figures` 制作数据图；
   - `mm-diagrams` 制作框架与逻辑图；
   - `mm-visual-concept` 制作每篇论文必需的纯视觉示意图。
7. `mm-paper-writing` 第二遍生成并编译 `paper/论文.tex` 与 `paper/论文.pdf`。
8. `mm-verification` 验收全部产物。
9. 验收发现问题时，由 `mm-orchestrator` 调用对应上游 skill 修复，更新 manifest 的 `change_log` 后重新验收。

## 阶段门禁与交接

- 每阶段开始前确认：上游产物存在、当前 skill 已完整读取、必读参考已读取、本阶段产出明确。
- 每阶段结束时更新 `project-manifest.json` 中本阶段负责的状态、稳定 ID、产物路径、SHA256 与版本。
- 任一阶段不得静默改写其他阶段产物；发现错误时登记回写原因，由编排器路由修复。
- `mm-verification` 只审计、定位和指定回写阶段，不直接修改论文、代码、图表或阶段报告。
- 未通过最终验收前，不得声称全流程完成。

## 图件边界

- 数据图归 `mm-figures`。
- 框架、逻辑和关系图归 `mm-diagrams`；成熟求解器与常规算法不画流程图，复杂自研算法按共享规则判断是否例外。
- 非数据、非流程的场景与原理示意图归 `mm-visual-concept`。
- 论文写作阶段只规划、引用和排版图件，不使用临时脚本替代画图 skill。

## 文件与安全边界

- `data/` 与用户提供的原始附件默认只读。
- 不覆盖项目根目录之外的既有文件，除非用户明确要求修改相应 skill。
- 不编造数据、参数、结果、参考文献或官方要求。
- 缺少必要授权、依赖或输入时，报告具体阻塞项，不以占位产物冒充完成。
