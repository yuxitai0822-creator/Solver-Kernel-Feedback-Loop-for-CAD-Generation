# cgvm — 3 个 CAD Generation Verification Module

`cgvm/` 是模型与系统层（model & system layer）的 verification primitives 子层。3 个 CGVM 模块独立校验 CAD 的不同维度，输出统一的 `VerificationResult` dataclass，并通过 `system.policy.policy.METHOD_FEEDBACK_CHANNELS` 决定哪些 diagnostic 被注入 prompt。

## 目录结构（5 子目录统一）

```
cgvm/
├── __init__.py                # re-export 4 个公开类
├── _shared/                   # 3 个 CGVM 共享基类
│   ├── README.md
│   └── base.py                # VerificationResult dataclass
├── pipeline/                  # Pipeline CGVM
│   ├── README.md / CHANGELOG.md
│   ├── schema/                # 4 子状态 contract
│   ├── core/verification.py
│   ├── runtime/executor.py
│   ├── tests/
│   └── legacy/
├── solver/                    # Solver CGVM
│   ├── README.md / CHANGELOG.md
│   ├── schema/                # Solver Acceptable 定义
│   ├── core/verification.py   # 接口层 + ACCEPTABLE/BLOCKING 判定
│   ├── runtime/
│   │   ├── freecad/           # FreeCAD 后端（默认）
│   │   └── kiwisolver/        # Kiwisolver 后端（archived）
│   ├── tests/
│   └── legacy/api_probe/       # 历史 FreeCAD API 探针
├── kernel/                    # Kernel CGVM
│   ├── README.md / CHANGELOG.md
│   ├── schema/                # KQP schema v0.2 symlink
│   ├── core/verification.py
│   ├── runtime/{dispatcher,geometry_backend,step_loader,result_builder}.py
│   ├── tests/
│   └── legacy/
└── README.md                  # 本文件
```

## 公开 API（从 `cgvm` 顶层）

```python
from cgvm import (
    VerificationResult,         # cgvm._shared.base
    PipelineVerification,      # cgvm.pipeline.core.verification
    SolverVerification,        # cgvm.solver.core.verification
    KernelVerification,        # cgvm.kernel.core.verification
)
```

各子模块也有自己的 re-export（`from cgvm.pipeline import ...`、`from cgvm.solver import ...`、`from cgvm.kernel import ...`）。

## 3 个 CGVM 的关系

3 个 CGVM 都通过 `cgvm._shared.base.VerificationResult` 输出，不继承同一基类（仅 duck-typed `run() → VerificationResult` 接口对齐）。

`system.policy.policy.METHOD_FEEDBACK_CHANNELS` 按 `name`（`pipeline` / `solver` / `kernel`）决定哪些 diagnostic 字段在 iter 循环里被喂回 LLM：

| CGVM | 验证内容 | 验证粒度 | 公开类位置 |
|---|---|---|---|
| Pipeline | compile + execute + export + load | code-level | `cgvm.pipeline.core.verification` |
| Solver | sketch constraint 可解性 + 无冲突 + 工程约束 | constraint-level | `cgvm.solver.core.verification` |
| Kernel | design intent 几何符合性（7 种 intent）| intent-level | `cgvm.kernel.core.verification` |

## 上下游

- **上游（被消费）**：`cgvm/system/core/iter_loop.py::run()` 三段 verification 全部调用
- **下游（被谁驱动）**：`system/batch/runner.py` 的 batch runner 与 `experiment/phase2b_m0m3/` 等