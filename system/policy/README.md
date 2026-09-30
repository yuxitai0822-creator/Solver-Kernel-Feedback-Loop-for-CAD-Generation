# system/policy/ — M0-M3 feedback channel policy

| 文件 | 作用 |
|---|---|
| `policy.py` | 原 `method_policy.py` |

## 核心声明

```python
METHOD_FEEDBACK_CHANNELS: dict[str, set[str]] = {
    "M0_NoFeedback":  {"pipeline"},
    "M1_SolverOnly":  {"pipeline", "solver"},
    "M2_KQPOnly":     {"pipeline", "kernel"},
    "M3_SolverKQP":   {"pipeline", "solver", "kernel"},
}
MAX_ITERATIONS: int = 3
METHODS_IN_ORDER: tuple[str, ...] = ("M0_NoFeedback", "M1_SolverOnly", "M2_KQPOnly", "M3_SolverKQP")
VERIFICATION_NAMES: tuple[str, ...] = ("pipeline", "solver", "kernel")
```

## 公开 API

```python
from system.policy.policy import (
    METHOD_FEEDBACK_CHANNELS,    # dict[method → set of channels]
    MAX_ITERATIONS,               # 3
    METHODS_IN_ORDER,             # tuple of 4
    VERIFICATION_NAMES,           # tuple of 3
    feedback_channels_for(method),  # 返回该 method 启用的 channel set（拷贝）
)
```

## 不变式（docstring 明示）

- 3 个 verification **永远全部执行**（iter loop 内 pipeline → solver → kernel 顺序）
- `feedback_channels_for(method)` 只决定哪些 `diagnostic` 被注入 prompt
- 4 个 system 共享 100% 代码路径——method 是唯一差异源

## 上下游

- **被消费**：`system/core/iter_loop.py::run()`（feedback 过滤）、`system/batch/runner.py::main()`（batch 遍历顺序）