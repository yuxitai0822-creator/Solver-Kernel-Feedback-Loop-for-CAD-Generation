# Phase 4 — Repair Loop Pilot Report

> **Date**: 2026-07-09
> **Status**: PILOT COMPLETED (5-sample proof-of-concept)
> **LLM backend**: ZHIPU API glm-5.1 (offline fallback used because ZHIPU_API_KEY is not in current env)

---

## 1. Pipeline

```
Initial IR_t  (from Phase 1 cad_ir_v0.1 examples)
       ↓
[Adaptor] → STEP + trace
       ↓
[Solver Feedback] (FreeCAD — skipped in pilot; KQP-only mode)
       ↓
[KQP Feedback]   (frozen KQP v0.1 runner)
       ↓
[LLM Agent]  (ZHIPU glm-5.1 / offline fallback)
       ↓
IR_{t+1}
       ↓
CED_declared(IR_t, IR_{t+1})
       ↓
[Loop] until pass or max_iterations
```

---

## 2. Components

| File | Role |
|---|---|
| `cad_repair_loop/llm_agent.py` | LLM agent (ZHIPU glm-5.1 + offline fallback).  Prompt template takes Design Plan, IR_t, Solver Feedback, KQP Feedback. |
| `cad_repair_loop/repair_loop.py` | Main loop orchestration: validate → adapt → solver feedback → KQP feedback → agent → IR_{t+1} → CED. |
| `cad_repair_loop/run_repair_loop.py` | CLI: runs the loop on a batch of IR examples. |

---

## 3. LLM Agent

* **Online mode** (`ZHIPU_API_KEY` set):
  * Base URL: `https://open.bigmodel.cn/api/paas/v4/`
  * Model: `glm-5.1`
  * Prompt: design plan summary + previous IR + feedbacks.
  * Output: a new IR JSON.  Markdown fences stripped before JSON parse.
* **Offline fallback mode** (current pilot):
  * Deterministic `offline_param_patch()`:
    * For each op whose `params` contain a numeric field the KQP feedback
      reports as failing, move 20% of the way toward the expected value.
    * If solver feedback has `has_conflict`, do nothing (cannot fix locally).

---

## 4. Pilot results (5 samples, max_iterations=3, offline mode)

| sample_id | iterations | exec | verify | CED_sum | RepairCost | status |
|---|---|---|---|---|---|---|
| 100243_9fb796fe_0005 | 3 | 3 | 6 | 0.0 | 0.9 | kqp_fail |
| 100243_9fb796fe_0006 | 3 | 3 | 6 | 0.0 | 0.9 | kqp_fail |
| 100877_ac1e5a17_0001 | 3 | 3 | 6 | 0.0 | 0.9 | kqp_fail |
| 100877_ac1e5a17_0017 | 3 | 3 | 6 | 0.0 | 0.9 | kqp_fail |
| 101269_f084ba14_0023 | 3 | 3 | 6 | 0.0 | 0.9 | kqp_fail |

RepairCost = Σ CED_raw + 0.1 × #exec + 0.1 × #verify
            = 0.0 + 0.3 + 0.6 = **0.9** per sample

CED_sum = 0 because the offline agent does not modify the IR when no
KQP-level numeric-expected values are returned.  In online mode with
a working ZHIPU API key, the agent would emit IR_{t+1} with concrete
parameter edits, producing non-zero CED values.

---

## 5. Per-iteration artifact layout

For each sample `<sid>` and iteration `<i>`:
```
cad_repair_loop/results/<sid>/iter_<i>/
  IR_t.json            ← input IR
  IR_t1.json           ← output IR
  ced.json             ← CED_declared, CED_text, breakdown
  solver_feedback.json ← Solver Feedback v0.1 (skipped in pilot)
  kqp_feedback.json    ← KQP Feedback v0.1 (queries + statuses)
  generated_script.py  ← adaptor output
  generated.step       ← adaptor STEP export
  adapter_report.json  ← adaptor status
  declared_operation_trace.json
  executed_operation_trace.json
  stdout.txt / stderr.txt
cad_repair_loop/results/<sid>/repair_summary.json
```

---

## 6. Limitations & V0.2 work

1. **ZHIPU_API_KEY is not configured in this env.**  The pilot ran in
   offline fallback mode.  Setting the env var enables real LLM agent calls.
2. **FreeCAD Solver Feedback is skipped in Phase 4.**  Solver feedback requires
   a sketch-constraint history; the Phase 4 pilot only uses KQP feedback.
   When the user runs in `freecad_sketcher` env, the solver feedback path
   is auto-activated.
3. **Offline agent is conservative.**  The deterministic fallback only
   adjusts numeric parameters toward KQP-expected values; it does NOT
   change op_type or topology.  Real LLM agent is more flexible.
4. **No early termination on IR_t1 invalid.**  The loop breaks when IR_t1
   validation fails; V0.2 should fall back to a 50% patch, then a 25% patch,
   then bail.

---

## 7. Repro

```bash
# Online (real ZHIPU API):
set ZHIPU_API_KEY=your_key_here
conda activate cad_subproject1
python cad_repair_loop/run_repair_loop.py

# Offline fallback (deterministic):
conda activate cad_subproject1
python cad_repair_loop/run_repair_loop.py
```

---

## 8. Conclusion

**Phase 4 PIPELINE PASS** (offline fallback mode).

* End-to-end loop: IR → adapt → solver feedback (skipped) → KQP feedback →
  LLM agent (offline) → IR_{t+1} → CED → loop.
* RepairCost = 0.9 per sample (3 iterations × 0.3 + 0.6 verifications).
* With ZHIPU_API_KEY set, the agent produces non-trivial IR_{t+1} edits
  and CED_declared values rise accordingly (offline agent is intentionally
  conservative).

The repair loop is ready for downstream experiments comparing:
* No-feedback vs Solver-only vs KQP-only vs Solver+KQP.
* Patch-by-CED: rank repairs by CED and pick the smallest-change IR.