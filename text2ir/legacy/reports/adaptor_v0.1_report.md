# Deterministic Adaptor v0.1 — Freeze Report

> **Frozen date**: 2026-07-09
> **Status**: FROZEN — V0.1 implementation completed and validated on 48 IR examples.
> **Backend**: **cadquery 2.8.0** (running in `cad_subproject1` env)
> **Source IR**: `cad_ir_v0.1` (schema_version = `cad_ir_v0.1`)

---

## 1. Goal

Translate a `cad_ir_v0.1` IR into an executable cadquery Python script, run it
in a subprocess, and emit STEP + structured trace files.

```
Structured CAD Operation IR (cad_ir_v0.1)
       ↓
Deterministic Adaptor (cad_ir/adaptor/)
       ↓
executable .py script
       ↓
cadquery subprocess
       ↓
generated.step
```

---

## 2. Modules

| File | Role |
|---|---|
| `cad_ir/adaptor/cadquery_backend.py` | Per-op renderers (one per op_type).  Stateless except for `ctx_id` mapping op_id → local variable. |
| `cad_ir/adaptor/trace_builder.py` | Builds declared trace (from IR) and executed trace (from runtime outcomes). |
| `cad_ir/adaptor/adapter.py` | Top-level `adapt(ir, out_dir)`: validate → render → execute → emit. |
| `cad_ir/adaptor/run_adaptor.py` | CLI: runs adaptor on a batch of IR examples. |
| `cad_ir/results/<sid>/` | Per-sample outputs (script, STEP, reports, traces). |

---

## 3. Pipeline per IR

1. **Validate** — schema + semantic check via `validator.validate`.  If fails, the adaptor stops with `adapter_status=fail` and no script is generated.
2. **Declared trace** — built directly from IR.operations (status=`declared`).
3. **Render** — each op's renderer produces Python statements; `ctx_id` maps op_id → local var name (e.g. `sk_op_001`, `body_op_002`).
4. **Stitch** — emit one `<script>.py` with the import header + each op wrapped in `try/except OP_ERROR` (so a single op failure is recorded but doesn't break execution).
5. **Execute** — `subprocess.run([python, script.py], timeout=60, cwd=out_dir)`.
6. **Executed trace** — capture `OP_ERROR: op='op_XXX'` lines from stdout; map each op to `success`/`failed`/`skipped`.
7. **STEP detection** — check whether the expected STEP file was written.
8. **Adapter report** — emit `adapter_report.json` with all status flags.

---

## 4. Validation outcomes (48/48 IR examples)

| Metric | Count | Rate | Threshold |
|---|---|---|---|
| Total IR examples | 48 | — | — |
| schema_check pass | 48 | **100.0%** | = 100% |
| semantic_validation pass | 48 | **100.0%** | ≥ 90% |
| script_syntax pass | 48 | **100.0%** | ≥ 95% |
| script execution pass | 48 | **100.0%** | ≥ 90% |
| STEP export pass | 48 | **100.0%** | ≥ 90% |
| adapter success | 48 | **100.0%** | — |
| backend-specific API leakage | 0 | 0% | = 0% |
| sample-specific hardcoding | 0 | 0% | = 0% |

Profile coverage:
* 21 rectangle → 21 success
* 10 circle → 10 success
* 7 annulus → 7 success
* 5 rectangular_frame → 5 success
* 2 stadium → 2 success
* 1 arbitrary_closed (polygon) → 1 success
* 2 hand-crafted IR → 2 success

---

## 5. Output artifact layout

For each sample `<sid>`:
```
cad_ir/results/<sid>.cad_ir/
  generated_script.py              ← executable cadquery script
  generated.step                   ← exported STEP file
  adapter_report.json              ← top-level status flags
  declared_operation_trace.json    ← from IR (declared)
  executed_operation_trace.json    ← from runtime (success/failed per op)
  stdout.txt / stderr.txt          ← subprocess I/O
```

The `adapter_report.json` schema:
```json
{
  "sample_id": "<sid>",
  "schema_check": "pass",
  "semantic_validation": "pass",
  "adapter_status": "success",
  "script_syntax_status": "pass",
  "execution_status": "pass",
  "step_export_status": "pass",
  "unsupported_ops": [],
  "warnings": [],
  "return_code": 0
}
```

---

## 6. Sample execution trace

```json
{
  "sample_id": "100243_9fb796fe_0005",
  "trace_type": "executed",
  "operations": [
    {"op_id": "op_001", "op_type": "sketch_rectangle", "runtime_status": "success"},
    {"op_id": "op_002", "op_type": "extrude",         "runtime_status": "success"},
    {"op_id": "op_003", "op_type": "export_step",      "runtime_status": "success"}
  ],
  "failed_at": null
}
```

---

## 7. Coverage of op_types

| op_type | Renderer | Tests |
|---|---|---|
| `sketch_rectangle` | `cq.Workplane.rect(w,h)` | 21 samples + 1 manual |
| `sketch_circle` | `cq.Workplane.circle(r)` | 10 samples |
| `sketch_annulus` | `Workplane.circle(R).circle(r)` (2 wires on same level → hole on extrude) | 7 samples + 1 manual |
| `sketch_rectangular_frame` | `Workplane.rect(W,H).rect(w,h)` | 5 samples + 1 manual |
| `sketch_stadium` | `Workplane.polyline([...arc...arc...]).close()` | 2 samples |
| `sketch_polygon` | `Workplane.polyline(vertices).close()` | 1 sample |
| `extrude` | `.extrude(d)` / `.extrude(d/2, both=True)` | 48 samples |
| `cut` | `.cut(tool)` | (no V0.1 IR uses cut yet — API ready) |
| `join` | `.union(tool)` | (no V0.1 IR uses join yet — API ready) |
| `add_constraint` | `pass` (cadquery v0.1 doesn't model explicit constraints) | 1 manual |
| `set_dimension` | `pass` (cadquery v0.1 bakes dims into geometry calls) | 1 manual |
| `export_step` | `cq.exporters.export(body, path)` | 48 samples |

---

## 8. Limitations & V0.2 work

1. **add_constraint / set_dimension are no-ops in V0.1 cadquery backend.**  
   Cadquery does not expose explicit constraint objects; constraint semantics
   are baked into the geometry calls.  V0.2 should either (a) adopt a FreeCAD
   backend that exposes constraints or (b) emit Constraint objects that the
   runner can introspect.

2. **Per-op error isolation.**  The adaptor emits try/except wrappers
   around each op, but a single op failure may corrupt downstream variable
   references.  In V0.1 the executed trace records the failure, but the
   remaining ops may report false `success` because they reference stale
   variables.  A proper per-op context reset is V0.2 work.

3. **Stadium / polygon are polyline approximations.**  Stadium is built
   as a 16-vertex polyline (8 per half-arc); polygon is a flat n-gon.  Both
   introduce arc-vs-polyline deviation that the KQP feedback will catch.

4. **Symmetric extent_type is approximated as one-side with d/2 + both=True.**  
   Real Fusion360 `symmetric` extrude places the center plane through the
   sketch origin; cadquery's `both=True` does the same in V0.1 approximation.

5. **No background OPC kernel for sketch validation.**  The adaptor relies on
   cadquery's wire-to-face translation.  Geometrically invalid inputs (e.g.
   self-intersecting polygons) are caught by cadquery as runtime exceptions,
   which propagate to `execution_status=fail` for that sample.

---

## 9. Repro

```bash
conda activate cad_subproject1

# 1. Generate 48 IR examples (46 from clean + 2 hand-crafted)
python cad_ir/samples/generate_from_clean_samples.py

# 2. Validate all IR examples
python cad_ir/validator/run_validation.py

# 3. Run adaptor on all IR examples
python cad_ir/adaptor/run_adaptor.py

# 4. Inspect results
ls cad_ir/results/
cat cad_ir/reports/adaptor_run_summary.json
```

---

## 10. Decision

**Adaptor v0.1 PASS.**

* All 12 op_types renderable; 48/48 IR examples execute end-to-end.
* 100% schema check, semantic validation, script syntax, execution, STEP export.
* declared + executed trace builders emit schema-valid JSON.
* No sample-specific hardcoding; same code path handles all 48.
* Compatible with downstream KQP feedback (each generated STEP can be
  evaluated by the frozen KQP runner).

The module is ready for use in the Phase 4 repair loop.