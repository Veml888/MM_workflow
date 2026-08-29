# 复现清单结构（results/复现清单.json）

编码阶段结束后生成，验收阶段据此完整重跑或抽查。字段缺失时写 `null` 并说明原因，不得伪造。

```json
{
  "schema_version": "2.0",
  "project": "<题目名>",
  "working_directory": ".",
  "environment": {
    "os": "<系统与版本>",
    "python_version": "3.x.x",
    "dependency_lock": "requirements-lock.txt",
    "key_packages": {},
    "solvers": [{"name": "", "version": ""}]
  },
  "random_seeds": { "global": 42, "per_problem": { "problem2": 2024 } },
  "numeric_policy": {
    "absolute_tolerance": null,
    "relative_tolerance": null,
    "solver_tolerance": null
  },
  "inputs": [
    { "file": "data/xxx.csv", "sha256": "<64位哈希>" }
  ],
  "scripts": [
    {
      "name": "code/problem1.py",
      "sha256": "<64位哈希>",
      "command": "python code/problem1.py --input data/xxx.csv --output results/q1_result.csv",
      "inputs": ["data/xxx.csv"],
      "outputs": ["results/q1_方案.csv"],
      "runtime_seconds": 12.3,
      "exit_code": 0,
      "convergence": {
        "status": "converged",
        "iterations": null,
        "optimality_gap": null
      }
    }
  ],
  "notes": "<特殊说明，如某参数手工标定来源>"
}
```

依赖必须有可安装的锁定清单；Python 项目可使用带精确版本的 `requirements-lock.txt`，MATLAB 项目记录版本与所需 toolbox。执行命令应从项目根目录直接运行，不依赖未记录的交互操作。

输入与代码文件哈希可用：

```python
import hashlib
def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
```

> 若某些文件哈希或耗时缺失，宁可写 `null` 也不要伪造；验收阶段会据此标记"可复现性不完整"。
