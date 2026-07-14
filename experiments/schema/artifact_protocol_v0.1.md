# Artifact Protocol v0.1

> **Date**: 2026-07-09
> **Status**: FROZEN
> **Companion to**: `run_result_schema_v0.1.json`, `iteration_record_schema_v0.1.json`

---

## 1. Purpose

The full benchmark run produces dozens of intermediate artifacts per
sample × method × iteration.  Without a fixed protocol for what to save
and where, downstream aggregation (`summarize.py`) cannot reliably
recompute metrics, attribute failures, or audit LLM behavior.

This document freezes:
1. The file layout under `experiments/results/<method>/<sample_id>/`
2. The set of artifacts that must be saved **per iteration**
3. The path conventions used by the schema

---

## 2. Directory Layout

```
experiments/results/
  <method>/                       # one of M0_NoFeedback, M1_SolverOnly, M2_KQPOnly, M3_SolverKQP
    <sample_id>/
      run_result.json              # the top-level record (run_result_schema_v0.1)
      sample_info.json             # cached frozen input paths
      iter_<NN>/
        IR_t.json
        IR_t1.json                 # may equal IR_t if no agent call
        generated_script_t.py
        generated_step_t.step
        adaptor_trace_t.json        # declared_operation_trace + executed_operation_trace
        solver_result_t.json       # FreeCAD Solver Feedback (or "skipped" placeholder)
        kqp_result_t.json          # KQP runner output (or "skipped" placeholder)
        ced_t_to_t_plus_1.json      # CED_declared, CED_executed, CED_text
        agent_prompt_t.txt         # raw LLM prompt (or empty for M0)
        agent_response_t.txt        # raw LLM response (or empty for M0)
        runtime_log_t.json          # per-stage wall-clock times
        token_usage_t.json          # input_tokens, output_tokens, total_tokens
        stderr.txt
        stdout.txt
```

---

## 3. Per-Iteration Artifact Inventory

For every iteration `t` (including iter 0):

| File | Required | Producer | Description |
|---|---|---|---|
| `IR_t.json` | ✅ | upstream / previous iter | Input IR for this iteration |
| `IR_t1.json` | ✅ | agent | Output IR (may equal IR_t if no agent) |
| `generated_script_t.py` | ✅ | Adaptor | CadQuery script produced from IR_t |
| `generated_step_t.step` | ✅ | Adaptor | STEP file from running the script |
| `adaptor_trace_t.json` | ✅ | Adaptor | declared+executed trace dict |
| `solver_result_t.json` | ✅ | FreeCAD Solver Feedback | `{"status": "ran"\|"skipped", ...}` |
| `kqp_result_t.json` | ✅ | KQP runner | `{"overall_status": "pass"\|"fail", "query_results": [...]}` |
| `ced_t_to_t_plus_1.json` | ✅ (or null on iter-final-success) | compute_ced | CED_declared, CED_executed, CED_text |
| `agent_prompt_t.txt` | ✅ (or empty for M0) | LLM agent | Raw prompt sent to LLM |
| `agent_response_t.txt` | ✅ (or empty for M0) | LLM agent | Raw LLM response text |
| `runtime_log_t.json` | ✅ | framework | Per-stage wall-clock times |
| `token_usage_t.json` | ✅ (zero for M0 / no-call) | LLM agent | Token counts |
| `stdout.txt` / `stderr.txt` | ✅ | Adaptor | Subprocess I/O |

For `iter 0` (the initial verification), the agent artifacts are
`agent_prompt_t.txt=""` and `agent_response_t.txt=""`.  All other files
are populated normally.

For `iter K` where the loop terminated because `KQP pass` was achieved
at this iter, the IR_t1 may equal IR_t; the CED path is `null`.

---

## 4. Top-Level Artifacts (per `(method, sample_id)`)

| File | Required | Description |
|---|---|---|
| `run_result.json` | ✅ | The full v0.1 record (per `run_result_schema_v0.1.json`) |
| `sample_info.json` | ✅ | Frozen input paths (design_plan, initial_ir, initial_step, kqp_instance) |

The `run_result.json` embeds the per-iteration records directly under
`iterations[]`, so the file is self-contained for re-analysis.

---

## 5. Path Conventions

* All paths in `run_result.json` and `iteration_record.json` are
  **relative to the project root** (the directory containing
  `doc/`, `experiments/`, `Reconstruction_results/`, etc.).
* Absolute paths are forbidden in v0.1 to support migration across
  machines.
* `artifacts_dir` is set to `experiments/results/<method>/<sample_id>`.

---

## 6. Solver / KQP "skipped" Placeholder

When a method disables a feedback channel (e.g. M0 has neither solver
nor KQP; M1 has solver only; M2 has KQP only; M3 has both), the
disabled channel's `*_result_t.json` is filled with a placeholder
saying "skipped" (not an error), e.g.:

```json
{
  "status": "skipped",
  "reason": "method disables solver feedback (run_solver_feedback=false)"
}
```

This is a **valid** artifact, not a failure.  The runner distinguishes
"skipped" from "ran" from "errored" via the top-level `status` field.

---

## 7. Reproducibility rules

1. The artifacts above are saved **before** the next iteration starts
   (i.e., even if the loop is interrupted, the partial trace is
   preserved).
2. `IR_t.json` and `IR_t1.json` are byte-identical across methods
   (deterministic IR serialization: 4-decimal float rounding,
   sorted-key normalization).
3. The `iter_<NN>` folder name uses zero-padded 2-digit iter index
   (`iter_00`, `iter_01`, `iter_02`).
4. `run_result.json` is updated only at termination of the run
   (i.e., once success reached OR max_iter exhausted).  Mid-run
   updates are NOT done in v0.1.

---

## 8. Aggregator Compatibility

The `experiments/summarize.py` script reads all `run_result.json`
files in `experiments/results/*/*/run_result.json` and produces:

* `experiments/reports/benchmark_<method>_summary.json`
* `experiments/reports/benchmark_master_summary.json`

The aggregator depends ONLY on the schema fields, not on the artifact
files.  Artifacts are kept for human / debug inspection.

---

## 9. Validation

A run is "schema-valid" iff:
1. `run_result.json` validates against `run_result_schema_v0.1.json`.
2. Every per-iter file listed in §3 is present in `iter_<NN>/`.
3. `IR_t.json` and `IR_t1.json` are valid against `cad_ir_schema_v0.1.json`.

The validator lives in `experiments/validate_results.py`.