# Experiment Contract v0.1 — Solver-KQP Repair Loop Benchmark

> **Date**: 2026-07-09
> **Status**: FROZEN
> **Purpose**: freeze inputs, components, metrics, success criteria, and artifact
>  protocols so the four-method ablation (M0 / M1 / M2 / M3) is reproducible and
>  comparable.

---

## 1. Frozen Inputs

| Input | Path | Size |
|---|---|---|
| 46 clean positive samples | `Reconstruction_results/clean_reconstruction_set.json` | 46 |
| 132 valid negative samples | `task5_negative_perturbation/.../perturbations/` (after reconstruction_success==true) | 132 |
| 138 total perturbation records | `task5_negative_perturbation/reports/adaptor_run_summary.json` | 138 |
| DesignPlan v0.6 instances | `DesignPlan/compiler/instances_v6/<sid>.design_plan.json` | 46 |
| KQP v0.2 instances | `kqp/outputs/compiler_v0.1/<sid>.kqp_instance.json` | 46 |
| Original Fusion360 history JSON | `Reconstruction_results/<sid>/input_history.json` | 46 |
| CAD IR v0.1 examples | `cad_ir/samples/manual_ir_examples/` | 48 |

Negative sample initial-failure status is determined by the KQP runner:
a negative sample is "initially failed" if at least one of its KQP queries
returns `status: fail` on iter 0 (the unperturbed-GT STEP).  We use the
138 perturbation records; some have been pre-built (CED_S1/2, ED_S1/2) — for
the benchmark we re-run KQP feedback on the perturbed STEP to confirm initial failure.

---

## 2. Frozen Components (versions)

| Component | Version | Path |
|---|---|---|
| DesignPlan Schema | v0.6 | `DesignPlan/DesignPlan_schema06.txt` |
| DesignPlan Compiler | v6 | `DesignPlan/compiler/design_plan_compiler.py` |
| KQP Instance Schema | v0.2 | `kqp/kqp_schema_v0.2.txt` |
| KQP Compiler | v0.1 | `kqp/compiler/` |
| KQP Runner | v0.1 | `kqp/runner/` |
| Reconstruction Engine | v0.1 | `reconstruction_engine/` |
| Reconstructed STEP files | — | `Reconstruction_results/<sid>/generated.step` |
| Frozen Solver Feedback (FreeCAD) | v0.1 | `Freecadsolver_feedback/` |
| CAD IR Schema | v0.1 | `cad_ir/schema/cad_ir_schema_v0.1.json` |
| CAD IR Validator | v0.1 | `cad_ir/validator/validator.py` |
| CAD IR Adaptor | v0.1 | `cad_ir/adaptor/` |
| CED module | v0.1 | `cad_edit_distance/` |
| Repair Loop | v0.1 | `cad_repair_loop/` |
| LLM backend | ZHIPU glm-5.1 (temperature 0.0) | `https://open.bigmodel.cn/api/paas/v4/` |

See `doc/frozen_components_for_repair_benchmark.md` for full details.

---

## 3. Four Methods (M0 / M1 / M2 / M3)

All methods share the same Code Agent prompt, same LLM (ZHIPU glm-5.1),
same temperature (0.0), same max_iter (=3), same LLM timeout (120 s),
same repair-loop skeleton.  They differ ONLY in which feedback channels
the LLM agent is exposed to.

| ID | Method | Solver feedback | KQP feedback | LLM receives |
|---|---|---|---|---|
| **M0** | No Feedback | not run | not run | nothing — agent must fix from IR alone (open-loop) |
| **M1** | Solver Only | run | not run | solver_feedback (skip_status) |
| **M2** | KQP Only | not run | run | kqp_feedback (query_results) |
| **M3** | Solver + KQP | run | run | both feedbacks |

`not run` means the loop skips the corresponding call to avoid
  contaminating the LLM's response.  The STEP is still produced by the
  Adaptor in every iteration (so all 4 methods have a valid STEP to
  evaluate).  When a feedback is skipped, the LLM is told so explicitly in
  the agent prompt ("Solver feedback: skipped").

---

## 4. Repair Loop Skeleton (shared)

```
Initial IR_t (perturbed IR, v0.1)
  ↓
[Adaptor] → STEP  (Phase 2, in any env that has cadquery)
  ↓
[Solver Feedback]   ← skipped / run depending on method
  ↓
[KQP Feedback]       ← skipped / run depending on method
  ↓
[Code Agent]          ← LLM, sees IR_t + (Solver | KQP | both | neither) feedback
  ↓
IR_{t+1}            ← LLM output, schema-validated
  ↓
[CED_declared(IR_t, IR_{t+1})]   ← logged
  ↓
if KQP_sample_pass: break
  else loop until max_iter (3) reached
```

A iteration is "successful" iff `kqp_overall_status == "pass"` at that
iteration.  An iteration is "validated" iff the IR is schema-valid
(Phase 1 validator) AND the adaptor script syntax-checked AND the
adaptor execution produced a STEP file.

`success_kqp` is the PRIMARY success criterion.  `strict_success`
additionally requires `solver.status == "ran"` and `solve.solve_status
not in ("conflicting", "over_constrained")`.  Both are reported per
sample.

---

## 5. Repair Metrics (per task spec)

| ID | Metric | Definition |
|---|---|---|
| M1.1 | **Success@1** | Fraction of initial-failed samples whose KQP_sample_pass turns 1 within 1 repair iteration. |
| M1.2 | **Success@2** | Same, within 2 repair iterations. |
| M1.3 | **Success@3** | Same, within 3 repair iterations (= final). |
| M1.4 | **F2S Conversion Rate** | # initial-failed that end success ÷ # initial-failed (= Success@3 for K-only). |
| M1.5 | **Mean Iterations to Success** | Average (over successful samples) of the first iteration k* where Success(C_k) = 1. |
| M3.1 | **KQP Query Improvement** | ΔQPR = QPR_final − QPR_initial. |
| M3.2 | **Remaining Failed Query Count** | Mean / Median / P90 / Total of `∑ 1[query fail]` per sample, post-repair. |
| M3.3 | **Targeted Repair Success Rate (TRSR)** | For each negative, # targeted queries initially failed and finally passing ÷ # targeted. |
| M4.1 | **CED_declared** | Weighted operation-level edit distance between IR_t and IR_{t+1} (already implemented in `cad_edit_distance`). |
| M4.2 | **CED_executed** | Same on runtime traces. |
| M5.0 | **RepairCost** | Σ CED_executed across the repair trajectory. |
| M6.0 | **Runtime Cost** | Wall-clock seconds per sample. |
| M7.0 | **Token Cost** | Σ input + output tokens consumed by the LLM. |

---

## 6. Generation Metrics (per task spec)

| ID | Metric | Definition |
|---|---|---|
| M8.1 | **Compile Success** | IR schema-valid AND adaptor successfully renders executable script. |
| M8.2 | **Execute Success** | Adaptor script runs end-to-end (no uncaught exception) and produces a body. |
| M8.3 | **STEP Export Success** | STEP file exists, size > 0, export API call returned successfully. |
| M8.4 | **OCCT Load Success** | `OCP.STEPControl_Reader` reads the STEP and returns a non-null shape. |
| M9.0 | **Solver / Sketch Validity** | Re-run Solver Feedback on the generated STEP (or its closest freeform equivalent); count samples where status ∉ {`conflicting`, `unsolvable`, `invalid_constraint_reference`}. |
| M10.0 | **KQP Sample Pass** | KQP `overall_status == "pass"`. |
| M11.0 | **KQP Query Pass** | Total # passed queries ÷ Total # queries (micro average). |
| M12.0 | **Per-intent Pass** | For each KQP intent (body_count, bbox_size, …), the query pass rate. |

---

## 7. Auxiliary Metrics (lower priority)

| ID | Metric | Definition |
|---|---|---|
| M13.1 | **CED_text** | Normalized Levenshtein over raw IR JSON.  Auxiliary only. |
| M13.2 | **Edit Efficiency** | `(KQP Query Improvement) / (RepairCost + ε)`.  Higher = more efficient. |
| M13.3 | **BBox Error** | Mean per-axis normalized BBox error vs. GT. |
| M13.4 | **Volume Error** | `|V_pred − V_GT| / (V_GT + ε)`. |
| M13.5 | **Chamfer Distance** | Mean bidirectional nearest-neighbor distance between sampled point clouds. |
| M13.6 | **IoU** | Volumetric intersection-over-union of the predicted solid vs. GT solid. |

---

## 8. Main-Indicator Hierarchy

**Generation question**: *Can the system construct a valid and intent-compliant CAD model?*
Pipeline → Solver/Sketch Validity → KQP Intent Compliance.

**Repair question**: *Can the system turn a failed CAD model into a valid one efficiently and with minimal edits?*
Success → Convergence → Quality Improvement → Minimal Editing → Cost.

The primary repair metric is **Success@3 (= KQP_success on iter ≤ 3)**, with **CED_declared** as the primary editing-cost metric.  Generation metrics are reported per-method to support the no-feedback baseline (M0) which can only be evaluated at the initial generation level.

---

## 9. Result Schema

```json
{
  "method": "M2_KQP_only",
  "sample_id": "100243_9fb796fe_0005",
  "initial_kqp_pass": false,
  "iter_records": [
    {"iter": 0, "kqp_status": "fail", "solver_status": "skipped",
     "agent_called": true, "ced_raw": 1.0, "ced_normalized": 0.1667,
     "wallclock_s": 4.3, "tokens": {"input": 2400, "output": 350}},
    ...
  ],
  "final_status": "success",
  "success_kqp": true,
  "strict_success": true,
  "n_iterations_to_success": 1,
  "final_kqp_pass_rate": 1.0,
  "remaining_failed_queries": 0,
  "ced_declared_trajectory": [1.0],
  "repair_cost": 1.0,
  "runtime_cost_s": 8.6,
  "token_cost_total": 2750
}
```

A `benchmark_summary.json` is also produced per method, aggregating all
samples' `result_schema` into the metric set defined in §5–7.

---

## 10. Artifact Save Protocol

For each `(method, sample_id)` pair, save:

```
experiments/results/<method>/<sample_id>/
  iter_<NN>/
    IR_t.json             ← input IR
    IR_t1.json            ← output IR
    ced.json              ← CED_declared, CED_executed, CED_text
    solver_feedback.json  ← Solver Feedback (skipped if not run)
    kqp_feedback.json     ← KQP Feedback (skipped if not run)
    generated_script.py
    generated.step
    adapter_report.json
    declared_trace.json
    executed_trace.json
    stdout.txt
    stderr.txt
    agent_request.json   ← LLM prompt + token counts
    agent_response.json  ← LLM response
    timing.json           ← per-stage wall-clock
  repair_summary.json
```

A top-level `experiments/reports/benchmark_<method>_summary.json` aggregates
all `(method, sample_id)` results into the metric set.

---

## 11. Acceptance

1. `doc/experiment_contract_v0.1.md` complete
2. `doc/frozen_components_for_repair_benchmark.md` complete
3. `experiments/config/benchmark_config_v0.1.json` complete
4. 4 methods (M0/M1/M2/M3) clearly defined
5. Main metrics defined and the metric base code is built
6. Result schema implemented
7. Files organized in `experiments/` directory tree (config/, results/, reports/)
8. CED implementation reused from `cad_edit_distance/`
9. Success criteria clearly stated
10. Artifact save protocol documented

---

## 12. Reproducibility rules

1. **No silent patches** during the experiment.  Any modification of
   frozen components requires a version bump and re-running the affected
   ablation.
2. **Same LLM** (ZHIPU glm-5.1), **same temperature** (0.0), **same
   max_iter** (3), **same input format** for all 4 methods.
3. **No tweaking** the prompt or metric to favor a particular method.
4. Each method runs in a **separate subprocess** to avoid LLM state
   leakage between methods.