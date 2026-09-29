# Phase 0 — Initial Dataset

## 描述
50 个 Fusion360 source samples，作为整个数据 lineage 的 root。  
每个 sample 5 模态：Fusion360 history JSON（建模过程）、STEP（可读本体）、OBJ（视效）、SMT（备用 B-rep）、PNG（缩略图）。

## 来源
Fusion360 Gallery Reconstruction dataset（参见 `data/sanity_set_50/` 历史位置，迁移后将位于 `history/`、`step/`、`obj/`、`smt/`、`png/` 各子目录）。

## Selection rule
见 `data/build_sanity_set.py`：
- 仅 sketch + extrude 实体（无 Revolve / Fillet / Hole / Loft）
- 1-2 个 sketch，恰好 1 个 extrude
- 每个 sketch ≤ 8 曲线，无 spline/ellipse/conic
- 按 sorted id 取前 50

## Downstream consumers
- `reconstruction_engine/orchestrator.py::reconstruct_sample` — 读 history → CadQuery
- `DesignPlan/compiler/design_plan_compiler.py::compile_design_plan` — 读 history → DesignPlan
- `experiments/history2ir/batch/run_history2ir.py` — 读 history → CAD IR