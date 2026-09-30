# cgvm/solver — Solver CGVM

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD 中 sketch constraint 是否可求解、无冲突、满足工程约束 |
| **Solver Acceptable 判定** | `solver_executed ∧ no_conflict ∧ no_redundant ∧ engineering_constraint_satisfied`（接口层 `cgvm/solver/core/verification.py::_is_acceptable()`） |
| **通过方式** | Solver Acceptable（不要简单 `fully_constrained`，因为工业 CAD 不一定要求完全约束；allow `under_constrained` 与 `redundant`） |
| **诊断 schema** | `{solver_status, dof, conflict_constraints, redundant_constraints, severity}` |
| **粒度** | constraint-level |

## 目录结构

```
cgvm/solver/
├── schema/
│   └── current.txt           # Solver Acceptable 定义
├── core/
│   └── verification.py        # SolverVerification class（接口层）
├── runtime/
│   ├── freecad/               # FreeCAD 后端实现（默认 + 9 文件）
│   │   ├── pipeline.py
│   │   ├── solver_runner.py
│   │   ├── recompute_runner.py
│   │   ├── registry_builder.py
│   │   ├── diagnostic_normalizer.py
│   │   ├── fallback_analyzer.py
│   │   ├── diagnostics_builder.py
│   │   ├── feedback_builder.py
│   │   └── history_parser.py
│   └── kiwisolver/            # Kiwisolver 后端实现（archived，不参与 benchmark）
│       └── ... (9 文件)
├── tests/
└── legacy/
    └── api_probe/             # 历史 FreeCAD API 探针
        └── ...
```

## Solver Acceptable 判定逻辑

接口层 `_is_acceptable()`（`cgvm/solver/core/verification.py` L77-L97）：
- 若 `solve.status ∈ BLOCKING_STATUSES = {conflicting, over_constrained, unsolvable, invalid_constraint_reference}` → False
- 若 `flags.has_conflict` 或 `has_over_constrained` → False
- 若 `severity ∈ {"blocking","error"}` → False
- 其余（含 `fully_constrained / under_constrained / redundant`）→ True

`solve.status` 字符串生成位置：每个后端 `runtime/<backend>/diagnostic_normalizer.py::normalize_solve()`（FreeCAD: 6 个状态字符串 if/elif；Kiwisolver: 同构）。

## 公开 API

```python
from cgvm.solver import (
    SolverVerification,
    ACCEPTABLE_STATUSES,
    BLOCKING_STATUSES,
    build_solver_feedback,    # FreeCAD 后端（默认）
)
```

## 上下游

- **上游**：`cgvm/system/core/iter_loop.py` 调 `SolverVerification.run(history_path)` 做 verification
- **下游**：feedback 注入 prompt（按 `method_policy.METHOD_FEEDBACK_CHANNELS` 过滤）

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `cad_verification.solver.SolverVerification` | `cgvm.solver.core.verification.SolverVerification` |
| `Freecadsolver_feedback.core.pipeline.build_solver_feedback` | `cgvm.solver.runtime.freecad.pipeline.build_solver_feedback` |
| `Kiwisolver_feedback.core.pipeline.build_solver_feedback` | `cgvm.solver.runtime.kiwisolver.pipeline.build_solver_feedback` |