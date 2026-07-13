# Phase 2 — Deterministic Adaptor v0.1 — Freeze Report

> **Date**: 2026-07-09
> **Module**: `cad_ir/adaptor/`
> **Backend**: `cadquery 2.8.0` (in `cad_subproject1` env)
> **Status**: PHASE 2 PASS

---

## 1. Background

The IR emitted by the Code Agent is a **declarative** description of what
to build.  It must be **rendered** into an executable CAD script that
the actual CAD backend can run.  Allowing the LLM to write the script
directly was tried previously (per task spec §3.1) and rejected because
of:

* syntax errors
* API version drift
* unrecoverable failure on partial inputs

**Phase 2 solution**: a **Deterministic Adaptor** that maps each IR
operation to backend-specific calls via a renderer per `op_type`, and
stitches the result into a runnable Python module.

---

## 2. Pipeline (per IR)

```
IR (cad_ir_v0.1 JSON)
   ↓
1. validate(ir)  ← cad_ir/validator (Phase 1)
   ↓
2. declared_trace = build_declared_trace(ir)
   ↓
3. for op in ir.operations:
     renderer = RENDERERS[op.op_type]
     stmts = renderer(op, ctx, ctx_id)
     append stmts + try/except wrappers
   ↓
4. rewrite export_step.path → out_dir/...
   ↓
5. subprocess.run(python generated_script.py, timeout=60)
   ↓
6. executed_trace = parse stdout for OP_ERROR lines
   ↓
7. emit declared_operation_trace.json, executed_operation_trace.json,
     adapter_report.json, generated.step, stdout.txt, stderr.txt
```

---

## 3. Renderers

`cad_ir/adaptor/cadquery_backend.py` exposes one renderer per
`op_type`:

| Renderer | Output pattern |
|---|---|
| `sketch_rectangle`        | `cq.Workplane("XY").center(cx, cy).rect(w, h)` |
| `sketch_circle`           | `Workplane.circle(r)` |
| `sketch_annulus`          | `Workplane.circle(R).circle(r)` (dual pending wires → hole on extrude) |
| `sketch_rectangular_frame`| `Workplane.rect(W, H).rect(w, h)` |
| `sketch_stadium`          | `Workplane.polyline([...arc_pts...]) close()` |
| `sketch_polygon`          | `Workplane.polyline(vertices).close()` |
| `extrude`                 | `.extrude(d)` (one-side) / `.extrude(d/2, both=True)` (symmetric) |
| `cut`                     | `.cut(tool)` after sketching the cutting face and extruding it |
| `join`                    | `.union(tool)` |
| `add_constraint`          | `pass` (cadquery v0.1 ignores — constraints are baked into geometry) |
| `set_dimension`           | `pass` (cadquery v0.1 ignores — dimensions are baked into geometry) |
| `export_step`             | `cq.exporters.export(body, path)` |

**Key design rule**: profile renderers (annulus, frame, stadium, polygon)
return a **wire Workplane** — they do **NOT** pre-extrude. The single
extrude op consumes ALL pending wires, producing the final solid.
This avoids the `extrude-after-extrude` failure that pre-extruding caused
in the first iteration.

---

## 4. Trace builders

`cad_ir/adaptor/trace_builder.py`:

* `build_declared_trace(ir)` → trace with `status='declared'` for each op
* `build_executed_trace(ir, results, failed_at)` → trace with `runtime_status ∈ {success, failed, skipped, error}` based on stdout parsing

OP_ERROR line format emitted by the adapted script:
```
OP_ERROR: op='op_002' type='extrude' exc=ValueError('No pending wires present')
```

The adaptor parses these lines to determine `failed_at` (the first op
that failed in the chain).

---

## 5. Outcomes (48/48 PASS)

```
total                : 48
schema_pass         : 48  (100.0%)
semantic_pass       : 48  (100.0%)
script_syntax_pass  : 48  (100.0%)
execution_pass      : 48  (100.0%)
step_export_pass    : 48  (100.0%)
adapter_success     : 48  (100.0%)
```

### 5.1 Per-profile success

| profile | n | success |
|---|---|---|
| rectangle | 21 | 21 |
| circle | 10 | 10 |
| annulus | 7 | 7 |
| rectangular_frame | 5 | 5 |
| stadium | 2 | 2 |
| arbitrary_closed (polygon) | 1 | 1 |
| + manual_demo_annulus_with_cut | 1 | 1 |
| + manual_demo_constraint_dim | 1 | 1 |

---

## 6. Key findings

### 6.1 Pre-extruding annulus/frame caused `extrude-after-extrude` failures

The first iteration of the renderers used `.extrude(H=1.0)` to give the
profile "thickness" before the actual extrude op ran.  This was
intuitive for CAD users, but cadquery's `extrude()` on an already-extruded
solid complains "No pending wires present" because the .extrude() call
expects pending wires on the workplane, not a previously-extruded solid.

**Resolution**: render profile ops as **wire Workplane only**.  The
final `extrude` op consumes all pending wires (1 for the simple profiles,
2 for annulus / frame) and produces the right solid in one shot.

### 6.2 Path issues across Windows backslashes and f-string quoting

The export step generates `cq.exporters.export(body, '<path>')` where
`<path>` is the absolute path of the STEP file.  Two issues arose:

* `f-string` quoting conflict when emitting `OP_ERROR: op={op_id!r}` — the
  inner `repr(op_id)` adds single quotes that break the outer single-quote
  f-string.  Fix: use double-quoted f-strings with explicit string
  concatenation: `f'OP_ERROR: op=' + repr(op_id) + ...`.
* Windows path backslashes (\P, \C) are interpreted as escape sequences
  in regular Python strings.  Fix: emit raw strings (`r'...'`) so the
  generated script writes to the absolute path correctly.

### 6.3 Empty statements for constraint/dimension ops broke try blocks

`add_constraint` and `set_dimension` originally returned only a comment
line.  When wrapped in `try/except`, this yielded
```
try:
   # comment only
except Exception:
   ...
```
which is a Python `IndentationError`.  Fix: explicit `pass` statement in
the comment.

### 6.4 Outer-rect + inner-rect on same Workplane => frame with hole

Cadquery's pattern for a plate-with-rect-hole uses two `.rect()` calls on
the same workplane and a single `.extrude()`:
```python
Workplane("XY").center(0, 0).rect(80, 60).rect(40, 30).extrude(H)
```
The first rect defines the outer boundary; the second rect defines the
hole.  This works with no extra `cut()` step.

Same pattern for annulus: `.circle(R).circle(r).extrude(H)`.
This is the only way the CadQuery backend can natively express annulus
and frame in V0.1.

### 6.5 Stadium and polygon are polyline approximations

V0.1 stadium is built as a 16-segment closed polyline (8 per half-arc).
Polygon is a flat n-gon.  Both trade off geometric fidelity for
implementation simplicity.  **If KQP feedback detects significant bbox
deviation, the rendering will need to be upgraded to use
`Workplane.spline()` / `Workplane.ellipse()` / parametric arc
approximations in V0.2.**

### 6.6 No sample-specific hardcoding

`grep sample_id cad_ir/adaptor/*.py` returns no special-case branches.
The same code path renders every one of the 48 IRs.

---

## 7. Limitations & V0.2 work

1. **`add_constraint` and `set_dimension` are no-ops.**  Cadquery doesn't
   expose explicit constraint objects.  V0.2 should either (a) target the
   FreeCAD adapter (which exposes Sketcher constraints natively), or
   (b) maintain an in-IR constraint cache and emit equivalent
   dimensions in geometry calls.
2. **Per-op error isolation is incomplete.**  A failing op that corrupts
   subsequent variables may produce false-positive success statuses for
   later ops (which reference stale variables).  V0.2 should reset the
   context after each failure.
3. **Subprocess timeout 60s is short.**  Some samples with stadium/
   polygon extrude depth > 1e3 mm may exceed 60s.  V0.2 should derive
   timeout from IR.extrude distance.

---

## 8. Acceptance vs. task spec §5.8

| Criterion | Status |
|---|---|
| ≥20 manual IR / 100% schema pass | ✅ 48 / 100% |
| ≥95% script generation | ✅ 100% |
| ≥95% script syntax | ✅ 100% |
| ≥90% execution | ✅ 100% |
| ≥90% STEP export | ✅ 100% |
| declared trace 100% complete | ✅ all ops have declared + executed status |
| No sample-specific hardcoding | ✅ verified |
| unsupported op recorded | ✅ adapter_status captures warnings |