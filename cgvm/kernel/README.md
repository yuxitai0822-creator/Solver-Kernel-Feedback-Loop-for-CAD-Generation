# cgvm/kernel — Kernel validation CGVM

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD geometry 是否满足 Design Intent（dimension / topology / spatial relation / derived geometry） |
| **验证方式** | `Design Plan → Kernel Query → OCCT Geometry Query → Expected vs Actual comparison` |
| **通过方式（sample-level）** | All required queries pass |
| **通过方式（query-level）** | Actual within tolerance |
| **诊断 schema** | `{failed_query, target, expected, actual, error, tolerance}`（per-failed-query）+ `failed_queries[]` 数组 |
| **粒度** | intent-level |

## 目录结构

```
cgvm/kernel/
├── schema/
│   └── current.txt           # symlink 到 data/phase1_positive/kqp/schema/current.txt（KQP v0.2）
├── core/
│   └── verification.py        # KernelVerification class（接口层）
├── runtime/
│   ├── dispatcher.py          # 单 query dispatch（按 intent 分发到 geometry_backend）
│   ├── geometry_backend.py    # OCCT 原子查询（get_solid_count / bbox_size / cylinder_radius / ...）
│   ├── step_loader.py         # STEP → TopoDS_Shape（OCP STEPControl_Reader）
│   └── result_builder.py      # 组装 KQPResult JSON
├── tests/
└── legacy/
```

## SUPPORTED_INTENTS

`cgvm.kernel.core.verification` 中定义的 7 种 intent：
```
body_count, bbox_size, cylinder_radius, through_void_count,
is_solid, occt_valid, symmetric_about_plane
```

## DEFAULT_TOLERANCE

按 intent 的默认 tolerance：
```
body_count=0, bbox_size=0.05, cylinder_radius=0.01,
through_count=0, is_solid=None (精确), occt_valid=None (精确),
symmetric_about_plane=None (精确)
```

## 公开 API

```python
from cgvm.kernel import (
    KernelVerification,
    SUPPORTED_INTENTS,
    DEFAULT_TOLERANCE,
    dispatch_query,        # runtime dispatcher
    load_step,             # runtime step_loader
    build_kqp_result,      # runtime result_builder
)
```

## 上下游

- **上游**：`cgvm/system/core/iter_loop.py` 调 `KernelVerification.run(step_path, kqp_path, plan)`
- **下游**：feedback 注入 prompt 作为 kernel feedback

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `cad_verification.kernel.KernelVerification` | `cgvm.kernel.core.verification.KernelVerification` |
| `plan2kqp.core.dispatch.dispatcher.dispatch_query` | `cgvm.kernel.runtime.dispatcher.dispatch_query` |
| `plan2kqp.core.dispatch.step_loader.load_step` | `cgvm.kernel.runtime.step_loader.load_step` |
| `plan2kqp.core.dispatch.geometry_backend.*` | `cgvm.kernel.runtime.geometry_backend.*` |
| `plan2kqp.core.dispatch.result_builder.build_kqp_result` | `cgvm.kernel.runtime.result_builder.build_kqp_result` |