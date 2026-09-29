# history2cq — History → CadQuery

模态转换模块：**Fusion360 history JSON → CadQuery Python source**。

## 目录结构

```
history2cq/
├── README.md
├── __init__.py                # 公开 API
├── CHANGELOG.md
│
├── schema/                    # 本模块无独立 schema
│   └── README.md              # 说明：本模块输入是 Fusion360 history.json
│
├── core/                      # 纯转换逻辑
│   ├── compiler.py            # history → CadQuery source code (pure)
│   └── compiler_v0.1_FROZEN.py
│
├── runtime/                   # I/O + subprocess + orchestration
│   ├── executor.py            # subprocess wrapper
│   ├── executor_v0.1_FROZEN.py
│   ├── orchestrator.py        # compile → execute → occt_load
│   ├── generate_index.py      # batch: 50 source samples → index JSON
│   ├── export_clean_set.py    # batch: export clean reconstruction set
│   ├── run_kqp_validation.py  # batch: KQP validation on all 50 STEPS
│   └── runtime_config_v0.1.json
│
├── tests/                     # unit + smoke tests
│
└── legacy/                    # 停用代码（仍可加载）
    └── _FROZEN/               # frozen v0.1 snapshots
```

## 公开 API

```python
from history2cq.core.compiler import compile_history
from history2cq.runtime.executor import execute_generated_code
from history2cq.runtime.orchestrator import reconstruct_sample, ReconstructSampleResult
```

## 上下游

- **上游**：Fusion360 Gallery Reconstruction r1.0.1 dataset (`data/phase0_initial/`)
- **下游**：
  - `plan2kqp.core.dispatch.step_loader` — load generated STEP
  - `task5_negative_perturbation/perturbation/perturb_history.py` — 复用 compile_history

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `reconstruction_engine.compiler` | `history2cq.core.compiler` |
| `reconstruction_engine.executor` | `history2cq.runtime.executor` |
| `reconstruction_engine.orchestrator` | `history2cq.runtime.orchestrator` |