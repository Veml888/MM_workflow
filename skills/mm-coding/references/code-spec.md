# 代码规范（可复现性优先）

数模代码的核心评价不是"写得多高级"，而是"评委/队友能否复现你的数"。

## 必须遵守

1. **固定随机种子**：任何涉及随机（智能优化、随机森林、采样、train/test 划分）的模块，在文件顶部显式设置 `np.random.seed(...)`、`random.seed(...)`，并在 `复现清单.json` 中记录种子值。
2. **输入/输出路径参数化**：不硬编码绝对路径；用相对 `PROJECT_ROOT` 的路径，通过常量或参数传入。
3. **量纲与单位注释**：每个关键数值变量的单位在注释里写清，避免张冠李戴。
4. **可运行**：每个 `problemN.py` 单独可运行；`utils.py` 不含顶层副作用代码（用 `if __name__ == "__main__":` 保护）。
5. **依赖可查**：用到的第三方库在文件头注释列出；尽量限定在 numpy/scipy/pandas/matplotlib/sklearn 等主流库。

## 命名与结构

- 函数名动宾结构，变量名有意义（`cost_matrix` 优于 `c`）。
- 子问题脚本按"读数据 → 建模计算 → 写结果"三段式组织。
- 结果写入 `results/`，文件名含子问题号与含义（如 `results/q1_最优方案.xlsx`）。

## 结果落盘约定

- 数值结果优先存 CSV（utf-8-sig，方便 Excel 打开中文），题面要求 `.xlsx` 时用 pandas 写 xlsx。
- 表头用中文列名（与论文一致），关键中间量也保留，便于论文引用。

## 数据真实性（硬性要求）

- 输入参数只允许来自题面/附件，或建模报告"待确认项"里明确约定的来源/假设。
- **禁止编造数据、拼凑数字、为了让结果好看而改参数**；对答案真实性负责。
- 凡使用假设值的参数，在代码注释与结果报告中标注"假设值 + 来源/理由"。

## 模型对比实验规范

- 对比必须"同数据、同指标"，否则结论不可信。
- 备选模型与所选模型在同一份输入上分别运行，输出同一指标的对比表（如 RMSE、成本、耗时、准确率）。
- 对比结果落盘到 `results/`，命名含"对比"字样（如 `results/q1_模型对比.csv`）。

## 仿真与多帧输出规范

- 仿真/迭代/时间演化类问题，把演化过程按代表性时间步/迭代次数采样成多帧。
- 每帧分别落盘 2D 与 3D 视角所需数据（如 `results/q4_frames_t00.csv`、`q4_frames3d_t10.csv`）。
- 帧采样 3~6 个（初始、中间转折、收敛/终态），供 `mm-figures` 做多帧可视化。

## 反模式（避免）

- 在循环里重复读盘/重复加载模型。
- 全程 `print` 关键结果却不落盘。
- 把随机种子设成与时间相关（`time.time()`），导致不可复现。
- 一个文件混着三四个子问题、上千行逻辑。

## 示例骨架

```python
# problem1.py — 问题一：xxx 优化
import numpy as np
import pandas as pd
from utils import load_data

SEED = 42
np.random.seed(SEED)

def solve(data):
    """返回最优方案与目标值。"""
    ...

if __name__ == "__main__":
    data = load_data("data/xxx.csv")
    plan, obj = solve(data)
    pd.DataFrame(plan).to_csv("results/q1_方案.csv", index=False, encoding="utf-8-sig")
    print(f"最优目标值 = {obj:.6f}")
```
