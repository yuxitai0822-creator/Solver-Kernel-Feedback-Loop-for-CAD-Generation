# plan2kqp — DesignPlan → KQP (compile + runtime)

模态转换模块：**DesignPlan → KQP instance**（compile 子模块）+ **KQP instance + STEP → KQP result**（dispatch/runtime 子模块）。

## 目录结构

```
plan2kqp/
├── README.md
├── __init__.py                # 公开 API
├── CHANGELOG.md
│
├── schema/
│   ├── current.txt            # 当前 KQP schema（原 kqp_schema_v0.2.txt）
│   └── archive/
│       └── v0.1.txt           # 历史版本（原 kqp_schema_v0.1.txt）
│
├── core/
│   ├── compiler/              # DesignPlan → KQP instance
│   │   ├── __init__.py
│   │   ├── compiler.py            # Plan → KQP instance (CLI + lib)
│   │   ├── compiler_v0.1_FROZEN.py
│   │   ├── query_builder.py
│   │   ├── query_builder_v0.1_FROZEN.py
│   │   ├── plan_reader.py
│   │   ├── source_mapper.py
│   │   └── feedback_builder.py
│   └── dispatch/              # KQP instance + STEP → KQP result
│       ├── __init__.py
│       ├── dispatcher.py           # 单 query dispatch (原 query_dispatcher.py)
│       ├── dispatcher_v0.1_FROZEN.py
│       ├── dispatcher_v0.6_FROZEN.py
│       ├── geometry_backend.py
│       ├── step_loader.py
│       └── result_builder.py
│
├── runtime/
│   └── cli.py                 # CLI 入口（原 run_kqp.py）
│
├── tests/
│   ├── analysis/
│   │   ├── analyze_patterns.py
│   │   ├── fix_canonical.py
│   │   └── semantic_match.py
│   └── smoke/
│       ├── gen_batch5.py
│       ├── gen_batch6.py
│       ├── review_batch_1.py
│       └── run_review_v0.2.py
│
└── legacy/                    # 旧数据 + 停用代码
    ├── _FROZEN/               # frozen v0.1 snapshots
    ├── samples/               # 重复数据（已被 data/phase1_positive/kqp/instances/ 取代）
    ├── results/               # GT verification 报告
    ├── outputs/               # 已清空
    ├── match/, review/, verification/
    ├── exp01_sample1_feasibility/
    └── task4_report.md
```

## 公开 API

```python
from plan2kqp.core.compiler.compiler import compile_one, compile_batch
from plan2kqp.core.dispatch.dispatcher import dispatch_query
from plan2kqp.core.dispatch.step_loader import load_step
from plan2kqp.runtime.cli import main  # CLI
```

## 上下游

- **上游**：`history2plan.core.compiler` 输出 DesignPlan JSON → `plan2kqp.core.compiler`
- **下游**：
  - `cad_verification/kernel.py::KernelVerification` 使用 `core.dispatch.dispatcher`
  - `dataset/triplet.py::_verify_layer3_difference` 使用 `runtime.cli`
  - `experiments/phase2b_m0m3/` 实验使用 `core.dispatch`

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `kqp.compiler.compile_kqp` | `plan2kqp.core.compiler.compiler` |
| `kqp.runner.run_kqp` | `plan2kqp.runtime.cli` |
| `kqp.runner.query_dispatcher` | `plan2kqp.core.dispatch.dispatcher` |
| `kqp.runner.step_loader` | `plan2kqp.core.dispatch.step_loader` |
| `kqp.runner.geometry_backend` | `plan2kqp.core.dispatch.geometry_backend` |
| `kqp.compiler.plan_reader` | `plan2kqp.core.compiler.plan_reader` |
| `kqp.compiler.query_builder` | `plan2kqp.core.compiler.query_builder` |