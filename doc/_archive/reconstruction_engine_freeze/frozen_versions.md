# Frozen Component Versions

> This file tracks all frozen versions in the project pipeline. Each entry records the version, frozen date, key parameters, and validation status.

---

## DesignPlanSchema v0.6

| Field | Value |
|---|---|
| Schema file | `DesignPlan/DesignPlan_schema06.txt` |
| Compiler | `DesignPlan/compiler/design_plan_compiler.py` |
| 50 instances | `DesignPlan/compiler/instances_v6/` |
| Frozen date | 2026-07-03 |
| Input dataset | 50 sanity samples (Fusion360 Gallery subset) |
| Validation | 50/50 compile success, 41/44 field match (3 hand-written errors corrected by compiler), 0 sample-specific hardcoding |

---

## KQPInstanceSchema v0.2

| Field | Value |
|---|---|
| Schema file | `kqp/kqp_schema_v0.2.txt` |
| 50 manual instances | `kqp/samples/v0.2/` |
| Compiler | `kqp/compiler/` (plan_reader, source_mapper, feedback_builder, query_builder, compile_kqp) |
| Frozen date | 2026-07-03 |
| Validation | 50/50 4-criteria review pass, 50/50 semantic match (334/334 queries), 0 sample-specific hardcoding |

---

## KQP Runner v0.1

| Field | Value |
|---|---|
| Modules | `kqp/runner/` (step_loader, geometry_backend, query_dispatcher, result_builder, run_kqp) |
| Frozen date | 2026-07-03 |
| GT verification | 50/50 samples pass, 334/334 queries pass, 0 crash, 0 unsupported intent |
| Supported intents | body_count, bbox_size, cylinder_radius, through_void_count, is_solid, occt_valid, symmetric_about_plane |
| Key design decisions | bbox_size uses best-match world-axis span for axis-aligned frames; through_void_count uses (total_wires - num_faces) / 2 |

---

## ReconstructionEngine v0.1

| Field | Value |
|---|---|
| Modules | `reconstruction_engine/` (compiler, executor, orchestrator, run_kqp_validation, export_clean_set) |
| Runtime config | `reconstruction_engine/runtime_config_v0.1.json` |
| Frozen date | 2026-07-03 |
| Input dataset | 50 sanity samples |
| Phase 1 (execution) | 50/50 compile/execute/export/occt_load pass |
| Phase 2 (KQP equivalence) | 46/50 clean (92%), 329/334 queries pass (98.5%) |
| Clean set | 46 samples (for Task 5 negative perturbation) |
| Isolated set | 4 samples (backend limitation, excluded from Task 5 main statistics) |
| Compiler setting | N_ARC=128 (arc discretization segments) |
| Unit conversion | cm→mm ×10 |
| Execution mode | subprocess isolated, 60s timeout |
| Cut-prism overshoot | 1.5× |
| Backend | cadquery (OCP 7.8.x) |
| Known limitations | polygon_with_fillets + multi-hole; stadium+2holes void_count; arbitrary_closed occt_valid |
