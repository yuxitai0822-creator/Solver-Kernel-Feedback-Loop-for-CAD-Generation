# system — 4-system iterative CAD generation (M0/M1/M2/M3)

`system/` 包实现 4 个 system（M0_NoFeedback / M1_SolverOnly / M2_KQPOnly / M3_SolverKQP）的**共享 codebase**。3 个 verification（pipeline / solver / kernel）**全部跑**；唯一差异是 `system.policy.policy.METHOD_FEEDBACK_CHANNELS` 决定哪些 diagnostic 被注入 prompt。

## 目录结构（5 子目录统一）

```
system/
├── __init__.py                # re-export 公共 API
├── README.md                  # 本文件
├── CHANGELOG.md
├── core/
│   └── iter_loop.py           # 原 trial_iteration.py::run()
├── policy/
│   ├── README.md
│   └── policy.py              # 原 method_policy.py
├── batch/
│   ├── README.md
│   └── runner.py              # 原 p2b_m0m3_on_frozen.py::main()
├── agent/
│   ├── README.md
│   ├── __init__.py
│   ├── schema.py
│   ├── core/caller.py         # 原 cad_agent/agent_v2.py（DeepSeek backend）
│   ├── prompt/
│   │   ├── __init__.py
│   │   ├── builder.py         # 原 cad_agent/prompt_builder_v2.py
│   │   └── legacy_shim.py     # 原 cad_agent/prompt_builder.py（v0 shim）
│   └── legacy/
│       ├── agent_zhipu.py     # 原 cad_agent/agent.py（ZHIPU backend）
│       ├── agent_v0.1_FROZEN.py
│       ├── prompt_builder_v0.1_FROZEN.py
│       └── schema_v0.1_FROZEN.py
├── tests/
└── legacy/
    └── cad_repair_loop/       # 前世 IR-based 系统（不进 M0-M3）
```

## 公开 API

```python
from system import (
    METHOD_FEEDBACK_CHANNELS,
    MAX_ITERATIONS,
    METHODS_IN_ORDER,
    feedback_channels_for,
    run_iter,            # system.core.iter_loop.run
    run_batch,           # system.batch.runner.main
    call_cad_agent_v2,   # system.agent.core.caller (DeepSeek)
)
```

## 4 个 system 的唯一差异

| system | feedback channels |
|---|---|
| **M0_NoFeedback** | `{pipeline}` |
| **M1_SolverOnly** | `{pipeline, solver}` |
| **M2_KQPOnly** | `{pipeline, kernel}` |
| **M3_SolverKQP** | `{pipeline, solver, kernel}` |

`MAX_ITERATIONS = 3`、`METHODS_IN_ORDER = (M0_NoFeedback, M1_SolverOnly, M2_KQPOnly, M3_SolverKQP)`。

## 上下游

- **上游（数据）**：`data/phase3_triplets/` 提供 120 frozen triplets
- **下游（实验）**：`experiments/phase2b_m0m3/` 跑 batch experiment；`p2b_iter_runner.py` 跑单 trial iter loop
- **依赖 cgvm 层**：iter loop 调用 `cgvm.pipeline/solver/kernel.core.verification` 三类 Verification Object

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `trial_iteration.run(...)` | `system.core.iter_loop.run(...)` |
| `method_policy.METHOD_FEEDBACK_CHANNELS` | `system.policy.policy.METHOD_FEEDBACK_CHANNELS` |
| `p2b_m0m3_on_frozen.main()` | `system.batch.runner.main()` |
| `cad_agent.agent_v2.call_cad_agent(...)` | `system.agent.core.caller.call_cad_agent_v2(...)` |
| `cad_agent.prompt_builder_v2.build_prompt_v2(...)` | `system.agent.prompt.builder.build_prompt(...)` |
| `cad_agent.prompt_builder.build_prompt(...)`（v0 shim）| `system.agent.prompt.legacy_shim.build_prompt(...)` |
| `cad_agent.schema.{is_valid_output, make_no_change, make_repair}` | `system.agent.schema.{is_valid_output, make_no_change, make_repair}` |