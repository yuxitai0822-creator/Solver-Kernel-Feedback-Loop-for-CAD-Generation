# cgvm/pipeline — Pipeline Execution CGVM

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD code 能被 CAD runtime 正确执行并生成有效 artifact（syntax correctness / API availability / execution success / STEP export / OCCT loading） |
| **验证方式** | Pipeline executor: `CAD Script → CAD Runtime → Execution log → STEP file → OCCT loader` |
| **通过方式** | `compile ∧ execute ∧ export ∧ load`（4 个 boolean AND） |
| **诊断 schema** | `{stage, error_type, message, trace}`（stage ∈ compile / execute / export / load） |
| **粒度** | code-level |

## 目录结构

```
cgvm/pipeline/
├── schema/
│   └── current.txt           # 4 子状态 contract + 诊断 schema
├── core/
│   └── verification.py        # PipelineVerification class
├── runtime/
│   └── executor.py           # execute_cad_script()
├── tests/
└── legacy/
```

## 公开 API

```python
from cgvm.pipeline import PipelineVerification, execute_cad_script, DEFAULT_CADQUERY_PYTHON
```

## 上下游

- **上游**：experiment/ runner（`p2b_full.py` / `p2b_pilot.py` / `p2b_m0m3_on_frozen.py` 等）调用 `execute_cad_script` 执行 LLM 生成的脚本
- **下游**：`cgvm/system/core/iter_loop.py` 调 `PipelineVerification.run()` 做 verification，并记录 4 子状态；这些状态会被选择性注入 prompt 作为 pipeline feedback

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `cad_verification.pipeline.PipelineVerification` | `cgvm.pipeline.core.verification.PipelineVerification` |
| `cad_runtime.execute_cad_script` | `cgvm.pipeline.runtime.executor.execute_cad_script` |
| `cad_runtime.executor.DEFAULT_CADQUERY_PYTHON` | `cgvm.pipeline.runtime.executor.DEFAULT_CADQUERY_PYTHON` |