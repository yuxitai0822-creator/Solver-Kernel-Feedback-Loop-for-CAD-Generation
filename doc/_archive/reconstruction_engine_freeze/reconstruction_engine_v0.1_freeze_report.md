# Reconstruction Engine v0.1 Freeze Report

> **Frozen date**: 2026-07-03
> **Status**: FROZEN — do not modify without version bump to v0.2

---

## 1. Phase 1 Execution Validation

| Metric | Required | Actual | Status |
|---|---|---|---|
| compile_success | 50/50 | 50/50 | ✅ |
| execute_success | 50/50 | 50/50 | ✅ |
| export_success | 50/50 | 50/50 | ✅ |
| occt_load_success | 50/50 | 50/50 | ✅ |
| unsupported_ops | 0 | 0 | ✅ |

**Phase 1: PASS**

---

## 2. Phase 2 KQP-Equivalence Validation

| Metric | Required | Actual | Status |
|---|---|---|---|
| Clean reconstruction samples | ≥ 45 | 46 | ✅ |
| Query pass rate | ≥ 98% | 98.5% (329/334) | ✅ |
| All failures have root-cause labels | Yes | Yes (4 samples, 5 queries) | ✅ |
| Isolated samples excluded from Task 5 | Yes | Yes (4 samples) | ✅ |

**Phase 2: CONDITIONAL PASS** (46/50 clean, 4 isolated with documented root causes)

---

## 3. Failure Analysis Summary

### 3.1 Fixed (arc discretization)

| Sample | Failed Query | Root Cause | Fix |
|---|---|---|---|
| 102295_86f842dd_0000 | q_bbox_u (48.0 vs 47.91) | 24-segment polyline approximation | N_ARC 24→128, error reduced to <0.01mm |
| 104453_aba0f2d1_0002 | q_bbox_u (600.0 vs 599.57) | 24-segment polyline on large stadium | N_ARC 24→128, error reduced to <0.01mm |
| 103552_c3a389ed_0003 | q_bbox_u (225.0 vs 224.89) | 24-segment polyline | N_ARC 24→128, bbox fixed (but void_count still fails → isolated) |

### 3.2 Isolated (backend limitation)

| Sample | Failed Query | Root Cause | Isolation Reason |
|---|---|---|---|
| 102369_65e5a7e6_0003 | q_void_count (2 vs 1) | polygon+2holes: 2nd hole cut-prism misaligned | cadquery cut limitation on multi-hole polygons |
| 102369_65e5a7e6_0003 | q_occt_valid (True vs False) | polygon fillet (corner arcs) not generated | cadquery cannot compose fillet + multi-hole |
| 103552_c3a389ed_0003 | q_void_count (2 vs 1) | stadium+2holes: 2nd hole not cut | cut-prism alignment issue |
| 107075_beb19139_0000 | q_occt_valid (True vs False) | arbitrary_closed (343°+94° arcs) degraded to polygons | large-angle arc handling limitation |
| 107466_72cd4ce9_0002 | q_void_count (2 vs 1) | stadium+2holes: 2nd hole not cut | cut-prism alignment issue |

---

## 4. Clean Set Definition

```
Clean Reconstruction Set = { sample | reconstructed STEP passes all KQP queries (100%) }
```

- **Clean set size**: 46 samples
- **Isolated set size**: 4 samples
- **Eligibility rule**: original reconstructed STEP must pass all KQP queries
- **Task 5 usage**: only clean_samples are used for main negative perturbation statistics

### Clean samples (46)

All 50 sanity samples EXCEPT the 4 isolated samples below.

### Isolated samples (4)

| sample_id | profile type | failure | reason |
|---|---|---|---|
| 102369_65e5a7e6_0003 | polygon_with_fillets | void_count + occt_valid | fillet + multi-hole backend limitation |
| 103552_c3a389ed_0003 | stadium+2holes | void_count | 2nd hole cut-prism misaligned |
| 107075_beb19139_0000 | arbitrary_closed | occt_valid | large-angle arc degradation |
| 107466_72cd4ce9_0002 | stadium+2holes (degenerate_two_side) | void_count | 2nd hole cut-prism misaligned |

---

## 5. Known Limitations

1. **polygon_with_fillets + multiple holes**: cadquery cannot reliably generate corner fillets combined with multi-hole cut. void_count and occt_valid may fail.
2. **stadium + 2 holes**: cut-prism for the 2nd inner hole may not align with body extent, causing through_void_count to undercount.
3. **arbitrary_closed profiles**: large-angle arcs (>180°) may degrade to polygon faces, causing occt_valid to fail.
4. **Validated only on 50-sample sanity set**: not validated on full Fusion360 Gallery (8625 sequences).
5. **Intended for controlled perturbation generation**: not a general-purpose CAD reconstruction tool.

---

## 6. Acceptance Criteria (Frozen)

### Phase 1
- compile_success = 50/50 ✅
- execute_success = 50/50 ✅
- export_success = 50/50 ✅
- occt_load_success = 50/50 ✅
- unsupported_ops = 0 ✅

### Phase 2
- clean reconstruction samples ≥ 45 ✅ (46)
- query pass rate ≥ 98% ✅ (98.5%)
- all failures have root-cause labels ✅
- isolated samples excluded from Task 5 main statistics ✅

---

## 7. Task 5 Calling Protocol

### Interface

```
Input:
  history_json (path to modeling_history.json)
  [optional] perturbation_meta (for Task 5 perturbed history)

Output:
  generated.step (OCCT-written STEP file)
  execution_report.json (compile/exec/export/occt_load status)
  reconstruction_status: "success" | "compile_fail" | "exec_fail" | "export_fail"
```

### Rules

1. Task 5 must only call the frozen ReconstructionEngine v0.1.
2. If a perturbation cannot be reconstructed, mark it as `perturbation_reconstruction_failed` — do NOT modify the engine.
3. If a universal bug is found (affects multiple samples), escalate to `ReconstructionEngine v0.2` upgrade — but v0.1 stays frozen for reproducibility.
4. Task 5 main statistics use ONLY clean_samples (46). Isolated samples (4) are excluded.
5. Minimum negatives required: 100. At 3 perturbations/sample × 46 clean = 138 ≥ 100. ✅

---

## 8. Frozen Artifacts

| Artifact | Path |
|---|---|
| Compiler (N_ARC=128) | `reconstruction_engine/compiler.py` |
| Executor (subprocess) | `reconstruction_engine/executor.py` |
| Orchestrator | `reconstruction_engine/orchestrator.py` |
| KQP validation script | `reconstruction_engine/run_kqp_validation.py` |
| Clean set exporter | `reconstruction_engine/export_clean_set.py` |
| Runtime config | `reconstruction_engine/runtime_config_v0.1.json` |
| Phase 1 summary | `Reconstruction_results/_summary.json` |
| Phase 2 KQP report | `Reconstruction_results/gt_vs_generated_kqp_validation/kqp_validation_report.json` |
| Clean set (with task5 rules) | `Reconstruction_results/clean_reconstruction_set.json` |
| Sanity set index | `Reconstruction_results/sanity_set_50_index.json` |
| Failure analysis | `doc/reconstruction_engine_failure_analysis.md` |
| Frozen versions | `doc/frozen_versions.md` |
| This freeze report | `doc/reconstruction_engine_v0.1_freeze_report.md` |

---

## 9. Runtime Environment

| Component | Version |
|---|---|
| Python | 3.11.15 |
| cadquery | 2.8.0 |
| OCP | 7.8.x (pybind11) |
| OS | win32 |
| Arc discretization | 128 segments |
| Unit conversion | cm→mm ×10 |
| Execution mode | subprocess isolated, 60s timeout |
| Cut-prism overshoot | 1.5× |
