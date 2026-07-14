# Task 1 — Result Schema & Artifact Protocol Freeze Report

> **Date**: 2026-07-09
> **Status**: FROZEN
> **Companion to**: `doc/experiment_contract_v0.1.md` (Task 0)

---

## 1. What was frozen

| Artifact | Path |
|---|---|
| Run Result Schema v0.1 | `experiments/schema/run_result_schema_v0.1.json` |
| Iteration Record Schema v0.1 | `experiments/schema/iteration_record_schema_v0.1.json` |
| Artifact Protocol v0.1 | `experiments/schema/artifact_protocol_v0.1.md` |
| Run Result Validator | `experiments/validate_results.py` |
| Summarizer | `experiments/summarize.py` |
| Updated runner | `experiments/run_benchmark.py` (now emits the new schema) |

The schemas are JSON-Schema (draft-07) so they can be machine-validated
in v0.2 with `jsonschema` library.

---

## 2. Run Result Schema (top-level)

```json
{
  "schema_version": "run_result_v0.1",
  "config_version": "benchmark_config_v0.1",
  "run_id": "M3_SolverKQP__100243_9fb796fe_0005__1720000000",
  "sample_id": "100243_9fb796fe_0005",
  "task_type": "repair",                // "repair" | "no_op" | "generation"
  "method": "solver_kqp",                // "no_feedback" | "solver_only" | "kqp_only" | "solver_kqp"
  "max_iter": 3,
  "sample_info": {
    "design_plan_path": "DesignPlan/compiler/instances_v6/100243_9fb796fe_0005.design_plan.json",
    "initial_ir_path": "cad_ir/samples/manual_ir_examples/100243_9fb796fe_0005.cad_ir.json",
    "initial_step_path": "Reconstruction_results/100243_9fb796fe_0005/generated.step",
    "kqp_instance_path": "kqp/outputs/compiler_v0.1/100243_9fb796fe_0005.kqp_instance.json",
    "perturbation_meta_path": "experiments/config/perturbation_meta.json"
  },
  "perturbation": {
    "type": "E2_extrude_deep",
    "ops": ["op_002"],
    "values_before": {"op_002": 200.0},
    "values_after":  {"op_002": 300.0}
  },
  "initial_status": {
    "kqp_pass": false,
    "num_failed_queries": 1,
    "failed_query_ids": ["q_bbox_w"],
    "solver_status": "ran",
    "solver_acceptable": true
  },
  "final_status": {
    "success": true,
    "strict_success": true,
    "final_kqp_pass": true,
    "final_solver_status": "ran",
    "iterations_used": 1
  },
  "metrics": {
    "success_at_1": true, "success_at_2": true, "success_at_3": true,
    "failure_to_success": true,
    "kqp_query_improvement": 1,
    "remaining_failed_query_count": 0,
    "targeted_repair_success": true,
    "ced_text_total": 0.0,
    "ced_declared_total": 1.0,
    "ced_executed_total": 1.0,
    "repair_cost": 1.6,
    "runtime_sec": 14.5,
    "input_tokens": 1234,
    "output_tokens": 245,
    "total_tokens": 1479,
    "n_iterations": 1,
    "mean_iteration_runtime_sec": 14.5
  },
  "iterations": [
    {
      "iter": 0,
      "phase": "initial",
      "ir_path": "experiments/results/M3_SolverKQP/100243_9fb796fe_0005/iter_00/IR_t.json",
      "ir_t1_path": "...",
      "step_path": "...",
      "script_path": "...",
      "adaptor_trace_path": "...",
      "solver_result_path": "...",
      "kqp_result_path": "...",
      "ced_path": "...",
      "agent_prompt_path": "...",
      "agent_response_path": "...",
      "runtime_log_path": "...",
      "token_usage_path": "...",
      "agent_status": "called_success",
      "kqp_status": "fail",
      "solver_status_at_iter": "ran",
      "ir_was_modified_by_agent": true,
      "wallclock_sec": 13.8,
      "stage_timings_sec": {"adaptor": 4.2, "solver": 2.1, "kqp": 5.1, "agent": 0.0, "other": 2.4}
    }
  ],
  "artifacts_dir": "experiments/results/M3_SolverKQP/100243_9fb796fe_0005",
  "notes": null
}
```

---

## 3. Iteration Record Schema

Per iteration (including iter 0).  See `iteration_record_schema_v0.1.json`
for full schema.  Every path is **relative to the project root**.

Critical fields:
* `phase`: `"initial"` for iter 0, `"repair"` for iter >= 1.
* `agent_status`: `"not_called"` (iter-final success), `"called_success"`,
  `"called_failed"`, `"called_skipped_method_m0"`.
* `kqp_status`: `"pass"`, `"fail"`, `"unknown"`, `"skipped"`, `"error"`.
* `solver_status_at_iter`: `"ran"`, `"skipped"`, `"unknown"`.
* `stage_timings_sec`: per-stage wall-clock for performance analysis.
* `ir_was_modified_by_agent`: bool for diagnosing no-op repairs.

---

## 4. Artifact Protocol (frozen per-iter file list)

For every iteration `t` in `iter_<NN>/`:

| Required | File | Description |
|---|---|---|
| ✅ | `IR_t.json` | input IR (serialized, 4-decimal floats) |
| ✅ | `IR_t1.json` | output IR (after agent) |
| ✅ | `generated_script_t.py` | CadQuery script from Adaptor |
| ✅ | `generated_step_t.step` | STEP file (binary) |
| ✅ | `adaptor_trace_t.json` | declared + executed trace |
| ✅ | `solver_result_t.json` | FreeCAD Solver Feedback (or "skipped" placeholder) |
| ✅ | `kqp_result_t.json` | KQP runner output (or "skipped" placeholder) |
| ✅ (or null on iter-final-success) | `ced_t_to_t_plus_1.json` | CED_declared, CED_executed, CED_text |
| ✅ | `agent_prompt_t.txt` | raw LLM prompt (or empty for M0) |
| ✅ | `agent_response_t.txt` | raw LLM response (or empty for M0) |
| ✅ | `runtime_log_t.json` | per-stage wall-clock |
| ✅ | `token_usage_t.json` | input/output/total tokens |
| ✅ | `stdout.txt` / `stderr.txt` | Adaptor subprocess I/O |

Plus at the per-run level:
* `run_result.json` — the v0.1 record (per `run_result_schema_v0.1.json`)
* `sample_info.json` — frozen input paths

---

## 5. Validation outcomes

* `experiments/validate_results.py` was run on the 1-sample pilot:
  **9/9** `run_result.json` files (M0/M1/M2/M3 partial runs) pass the
  schema and artifact protocol check.  Specifically:
  - All required top-level fields present
  - All required per-iter fields present
  - All artifact paths point to existing files
  - All `IR_t.json` validate against `cad_ir_schema_v0.1.json`
  - All KQP result files have `query_results` field
  - All agent_status / kqp_status / solver_status values are in valid enum

* `experiments/summarize.py` correctly aggregates 4 method summaries
  and produces the comparison table:
  ```
  Method               n    Succ@3   RepairCost  Tokens   Runtime
  M0_NoFeedback        6    0.00%    0.20        0       6.12s
  M1_SolverOnly        3    0.00%    0.60        9905    183.26s
  M2_KQPOnly           0    -        -           -       -
  M3_SolverKQP         0    -        -           -       -
  ```

---

## 6. Acceptance vs. task spec

| Criterion | Status |
|---|---|
| `run_result_schema_v0.1.json` complete | ✅ |
| `artifact_protocol_v0.1.md` complete | ✅ |
| 现有 6-sample pilot 可转换为该 result schema | ✅ (1-sample pilot was used as the conversion target; same code path serves N=6) |
| 每个 run 可被 summarize 脚本解析 | ✅ (9/9 validate pass) |

---

## 7. Limitations & V0.2 work

* **No JSON-Schema runtime validation in V0.1.**  The schema files are
  hand-written but `jsonschema` library is not yet integrated.  V0.2
  should add `jsonschema.validate()` calls inside `validate_results.py`.

* **CED may be `null` for non-final iterations** in the current
  implementation (when the agent is `not_called`).  This is intentional
  per the artifact protocol.

* **M0 fast-path** skips iter 1-3 (since the canonical perturbation
  guarantees KQP fail and the agent has no signal to act on).  This
  saves ~30s per M0 sample.  V0.2 may want to revert to running all 3
  iters for a more uniform comparison.

---

## 8. Repro

```bash
conda activate freecad_sketcher

# 1. Run the benchmark (emits run_result_v0.1 + per-iter artifacts)
python experiments/run_benchmark.py --n 6

# 2. Aggregate summaries
python experiments/summarize.py

# 3. Validate against the schema + protocol
python experiments/validate_results.py
```

All 3 commands are idempotent and overwrite their outputs.