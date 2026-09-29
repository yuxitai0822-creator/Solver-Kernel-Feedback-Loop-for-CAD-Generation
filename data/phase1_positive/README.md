# Phase 1 — Positive Augmentation

## 描述
正样本增强。50 source → 51 instances（50 + 1 额外 sanity test），分 4 个子模态：

| 子目录 | 内容 | Schema |
|---|---|---|
| `reconstruction/` | ReconstructionEngine 产物（CadQuery code + STEP + report + stdout/stderr） | — |
| `cad_ir/` | CAD IR v0.1（手工 examples + History2IR 批量编译） | `cad_ir_schema_v0.1.json` |
| `design_plan/` | DesignPlan v0.6 | `DesignPlan_schema06.txt` |
| `kqp/` | KQP v0.2 + legacy v0.1 | `kqp_schema_v0.2.txt` |

## Lineage
- `reconstruction/` ← `reconstruction_engine/orchestrator.py::reconstruct_sample(phase0_initial.history)`
- `design_plan/` ← `DesignPlan/compiler/design_plan_compiler.py::compile_design_plan(phase0_initial.history)`
- `kqp/` ← `kqp/compiler/compile_kqp.py::compile_kqp(design_plan)`
- `cad_ir/clean/` ← `experiments/history2ir/batch/run_history2ir.py(phase0_initial.history)`
- `cad_ir/negative/` ← 同上，但 source 是 phase2_perturbation.artifacts.perturbed_history

## Frozen
- `design_plan/instances/` — DesignPlan v0.6 frozen
- `cad_ir/instances/` — cad_ir v0.1 frozen（Phase 2A 之后该模式转向 legacy）
- `kqp/instances/v0.2/` — KQP v0.2 frozen