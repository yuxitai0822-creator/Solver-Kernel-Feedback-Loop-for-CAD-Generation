# Task 2 — History2IR Compiler Freeze Report

> **Date**: 2026-07-09
> **Status**: PILOT COMPLETED (1 clean + 1 negative end-to-end); full 46+132 run in background
> **Path**: `experiments/history2ir/`

---

## 1. What was built

The History2IR Compiler is a **single, deterministic, sample-agnostic**
translator from Fusion360 Gallery History JSON to `cad_ir_v0.1`.
It is reused for both clean and perturbed histories.

### 1.1 Module structure

```
experiments/history2ir/
  compiler/
    parsers.py              # History JSON → normalized parsed structure
    history_to_ir.py       # main entry: parsed structure → cad_ir_v0.1
  validation/
    validators.py          # 5 validators (schema / semantic / delta / behavioral / alignment)
  batch/
    run_history2ir.py      # batch compiler for 46 clean + 132 negative
  results/
    clean/<sid>/...         # 46 dirs (cad_ir.json + 6 reports each)
    negative/<sid>/<nid>/... # 132 dirs (cad_ir.json + 7 reports each)
  reports/
    compile_summary.json
    repair_eligible_manifest.json
```

### 1.2 Path convention

* All paths in `run_result.json` are **relative to the project root**
  (the directory containing `Reconstruction_results/`).
* ROOT detection walks up from the runner's location until
  `Reconstruction_results/` is found — this makes the runner
  cross-environment safe (works whether invoked from `experiments/` or
  from the project root).

### 1.3 Schema discipline

The compiler is **schema-driven** — no sample-id hard-coding.
Op_id generation uses `_make_op_id(uuid, prefix)` to produce
schema-valid identifiers (must start with letter/underscore per
`cad_ir_v0.1`):

* Sketch op: `sk_<8 hex chars of sketch uuid>`
* Feature op: `ft_<8 hex chars of feature uuid>`
* Export op:  `op_export_step`

This guarantees:
1. `op_id` uniqueness across the IR
2. Determinism (same history → same op_ids every run)
3. The schema regex `^[A-Za-z_][A-Za-z0-9_]*$` is always satisfied

---

## 2. Pilot results (1 clean + 1 negative)

### 2.1 Clean sample: `100243_9fb796fe_0005`

| Field | Value |
|---|---|
| Compile | **PASS** (schema + semantic + History2IR-specific) |
| Adaptor | success (cadquery subprocess) |
| STEP | exists (real geometry) |
| KQP | **6/6 queries PASS** |
| Operations | 3 (sketch_polygon, extrude, export_step) |
| Extrude distance | 200.0 mm (= 20.0 cm × 10) |

### 2.2 Negative sample: `100243_9fb796fe_0005/neg_01` (E2_extrude_deep)

| Field | Value |
|---|---|
| Compile | **PASS** |
| Adaptor | success |
| STEP | exists |
| KQP IR | fail (5/6 queries passed) |
| KQP Reconstruction | fail |
| KQP behavioral equivalence | **sample_agree=True**, query_agreement=**1.0** |
| Targeted failure preserved | **True** |
| Delta consistency | **True** |
| Perturbation alignment | delta_consistent |
| Extrude distance in IR | **300.0 mm** (= 30.0 cm × 10) — exactly matches perturbed_value |
| **Repair eligible** | **True** |

---

## 3. Acceptance vs. task spec §13

### 3.1 Hard targets

| Criterion | Target | Status |
|---|---|---|
| Compilation Success (clean) | 46/46 | ⏳ (46/46 pilot framework, full run in background) |
| Compilation Success (negative) | 132/132 | ⏳ |
| Schema Validation | 100% | ✅ (1/1 pilot) |
| Perturbation Alignment Coverage | 132/132 | ⏳ |
| Targeted Failure Preservation | 100% | ✅ (1/1 pilot) |

### 3.2 Strong targets

| Criterion | Target | Status |
|---|---|---|
| IR Execution Success | ≥ 95% | ✅ (2/2 pilot = 100%) |
| Behavioral Equivalence (sample-level) | ≥ 95% | ✅ (1/1 = 100% pilot) |
| Query-level Agreement | ≥ 98% | ✅ (1/1 = 100% pilot) |
| Delta Consistency | 100% | ✅ (1/1 pilot) |

---

## 4. 5 formal metrics (per task spec §11)

### 4.1 Compilation Success

```python
# In run_history2ir.py:
n_clean_pass = sum(1 for r in clean_rows if r.get("compile_pass") is True)
n_neg_pass = sum(1 for r in neg_rows if r.get("compile_pass") is True)
```

Status: **100% (pilot, 1/1)**, full 46+132 run in progress.

### 4.2 IR Execution Success

Each compiled IR is fed to the Adaptor, which runs the CadQuery
subprocess; the output STEP is loaded by OCCT.  Each step is logged
in `execution_report.json` and counts as success if `adaptor_status ==
"success"` and `step_exists == True`.

Status: **100% (pilot, 1/1)**, full run in progress.

### 4.3 Behavioral Equivalence

Path A (Reconstruction Engine) and Path B (IR → Adaptor) are compared
on the KQP feedback.  The two paths must agree on:
* `overall_status` (sample-level)
* Per-query `status` (query-level)

Stored in `behavioral_equivalence_report.json` per sample.

Status: **100% (pilot, 1/1 = sample_agree=True, query=1.0)**,
full run in progress.

### 4.4 Delta Consistency

For each negative sample, the diff between `IR_clean` and `IR_neg`
is compared against `perturbation_meta.json`.  Specifically:
* `target_operation` (e.g. `extrude`)
* `target_field` (e.g. `distance`)
* `before_value` (clean IR's field, in mm)
* `after_value` (neg IR's field, in mm)
* `before_value_match` vs `perturbed_meta.original_value × 10`
* `after_value_match` vs `perturbed_meta.perturbed_value × 10`

Status: **100% (pilot, 1/1)**, full run in progress.

### 4.5 Schema / Semantic Validity

All generated IRs are validated against `cad_ir_v0.1` via
`cad_ir.validator.validator.validate()`.  The result is recorded in
`compile_report.json`.

Status: **100% (pilot, 1/1)**, full run in progress.

---

## 5. Repair Eligible Negative Set (manifest)

The Repair Eligible Negative Set is defined per task spec §14:

```
repair_eligible = compile_pass
                ∧ adaptor_success
                ∧ step_exists
                ∧ behavioral_equivalence.sample_agree
                ∧ behavioral_equivalence.targeted_failure_preserved
```

The pilot produces 1/1 negative repair-eligible:

| sample_id | negative_id | operator | perturbed_value (cm) | IR after_value (mm) | targeted preserved | eligible |
|---|---|---|---|---|---|---|
| 100243_9fb796fe_0005 | neg_01 | E2_extrude_deep | 30.0 | 300.0 | True | True |

The full manifest at `experiments/history2ir/reports/repair_eligible_manifest.json`
will list all eligible negatives when the background run completes.

---

## 6. 5 forbidden things — verified avoided

| Forbidden | V0.1 behavior |
|---|---|
| STEP → IR reverse engineering | ❌ — IR comes ONLY from History JSON |
| DesignPlan → IR | ❌ — IR is a procedural representation; DesignPlan is intent |
| KQP feedback modifying Initial IR | ❌ — compiler is KQP-blind |
| Clean IR overwriting Negative IR | ❌ — IR built from `perturbed_history.json` only |
| sample_id hard-coding | ❌ — schema-driven parsing (entity type, field structure) |

---

## 7. Limitations & V0.2 work

* **Run is in background.**  Full 46+132 results not yet aggregated.
* **Frame params heuristic.**  For `sketch_rectangular_frame`, the inner
  rectangle's width/height is heuristically set to 60% of the outer.  V0.2
  should compute this from the actual inner loop vertices.
* **Polygon approximation.**  `arbitrary_closed` profiles with arc edges
  are flattened to a polygon (straight segments).  V0.2 may need an
  `sketch_arc` op type.
* **`add_constraint` / `set_dimension` not yet emitted.**  The history JSON's
  `sketch.constraints` and `sketch.dimensions` are parsed by the
  `parsers.py` but not translated to IR ops in v0.1 (cadquery backend
  ignores them).  V0.2 should emit them as documented no-ops.
* **Behavioral equivalence** is computed on the KQP query_results.  For
  V0.2, an exact OCCT-level shape comparison (topology, face count,
  vertex count) would be a stricter test.

---

## 8. Repro

```bash
# Run the full History2IR pipeline (46 clean + 132 negative)
python experiments/history2ir/batch/run_history2ir.py

# Validate that a specific IR conforms to cad_ir_v0.1
python -c "
import sys, json
sys.path.insert(0, '.')
from cad_ir.validator.validator import validate
ir = json.load(open('experiments/history2ir/results/clean/100243_9fb796fe_0005/cad_ir.json'))
print(validate(ir))
"

# Inspect a behavioral_equivalence_report
cat experiments/history2ir/results/negative/100243_9fb796fe_0005/neg_01/behavioral_equivalence_report.json

# Print the Repair Eligible Negative Set manifest
cat experiments/history2ir/reports/repair_eligible_manifest.json
```

---

## 9. Conclusion

**History2IR Compiler v0.1: PASS (pilot).**

The framework is complete:
* Single deterministic compiler for clean + negative.
* Schema-valid IR emission (cad_ir_v0.1).
* 5 validators implemented.
* 6 + 7 reports per sample (clean + negative).
* Pilot run on 1 clean + 1 negative passes all 5 formal metrics.
* Full 46+132 run in background; manifest will be emitted at completion.