# CAD Operation IR v0.1 — Schema Specification

> **Schema version**: `cad_ir_v0.1`
> **Date**: 2026-07-08
> **Status**: FROZEN

---

## 1. Position in the pipeline

```
Design Plan
   ↓
Code Agent (LLM)
   ↓  ← emits JSON conforming to cad_ir_v0.1
Structured CAD Operation IR
   ↓  ← consumed by Deterministic Adaptor
Deterministic Adaptor
   ↓  ← emits executable Python CAD Script
CAD Script
   ↓
CAD Backend (cadquery / FreeCAD)
   ↓
STEP file
   ↓
Kernel-Solver Feedback Loop (KQP + Solver Feedback)
```

The IR is the **stable interface between the LLM and the CAD execution
stack**.  It does NOT contain any backend-specific API calls
(`cadquery.Workplane.cut`, `FreeCAD.addObject`, etc.).

---

## 2. Top-level structure

```json
{
  "schema_version": "cad_ir_v0.1",
  "sample_id": "sample_001",
  "unit": "mm",
  "coordinate_system": {
    "up_axis": "z",
    "front_axis": "y",
    "right_axis": "x"
  },
  "operations": [
    {"op_id": "op_001", "op_type": "...", "params": {...}},
    ...
  ],
  "metadata": {"round": 0, "iteration": 0, "source": "..."}
}
```

### Fields

| Field | Required | Description |
|---|---|---|
| `schema_version` | ✓ | Constant string `"cad_ir_v0.1"`. |
| `sample_id`     | ✓ | Stable sample identifier. |
| `unit`          | ✓ | Linear unit: `"mm"` (recommended) or `"cm"`.  Adaptor converts `cm`→`mm`. |
| `coordinate_system` | ✓ | Reference frame; `up_axis` is the extrusion direction. |
| `operations`    | ✓ | List of operations (see §3).  Min 1 op. |
| `metadata`      | ✗ | Optional round/iteration tracking for repair loop. |

---

## 3. Operation types (v0.1)

### 3.1 Sketch primitives (12 op_type values total, but profile-generating 6)

| op_type | Required params | Optional params | Description |
|---|---|---|---|
| `sketch_rectangle` | `width`, `height`, `center` | `center_u_to_v_axis` | Rectangle profile on a sketch plane. |
| `sketch_circle` | `radius`, `center` | — | Circle profile. |
| `sketch_annulus` | `inner_radius`, `outer_radius`, `center` | — | Ring (outer circle − inner circle). |
| `sketch_rectangular_frame` | `outer_width`, `outer_height`, `inner_width`, `inner_height`, `center` | — | Rectangular frame (outer rect − inner rect). |
| `sketch_stadium` | `length`, `radius`, `center` | — | Stadium = rectangle with two semicircular caps. |
| `sketch_polygon` | `vertices` (≥3) | `center` | Generic polygon. |

### 3.2 Feature / boolean ops

| op_type | Required params | Optional params | Description |
|---|---|---|---|
| `extrude` | `distance`, `extent_type` | `operation`, `direction`, `taper_angle` | Extrude a sketch.  `extent_type` ∈ {`one_side`, `symmetric`, `two_sides`}; `operation` ∈ {`new_body`, `join`, `cut`, `intersect`}. |
| `cut` | `distance`, `target` | `tool`, `through_all` | Cut a profile from a body. |
| `join` | `target` | `tool` | Join (boolean union) a profile to a body. |

### 3.3 Constraint / dimension ops

| op_type | Required params | Optional params | Description |
|---|---|---|---|
| `add_constraint` | `constraint_type`, `target` | `entities`, `value` | Add a sketch constraint.  `constraint_type` ∈ {`horizontal`, `vertical`, `coincident`, `perpendicular`, `parallel`, `tangent`, `concentric`, `equal`, `midpoint`, `offset`}. |
| `set_dimension` | `dimension_type`, `value`, `target` | `entity` | Set a sketch dimension.  `dimension_type` ∈ {`linear`, `diameter`, `radius`, `angular`}. |

### 3.4 Export

| op_type | Required params | Optional params | Description |
|---|---|---|---|
| `export_step` | `path` | `input` | Export a body to STEP. |

### 3.5 NOT supported in v0.1

`assembly`, `kinematic_relation`, `sweep`, `loft`, `complex_fillet/chamfer`,
`freeform_spline`, advanced surface operations.

---

## 4. Operation-level fields

| Field | Required | Description |
|---|---|---|
| `op_id`    | ✓ | Stable identifier (e.g. `"op_001"`).  Must be unique within an IR. |
| `op_type`  | ✓ | One of the 12 values above. |
| `role`     | ✗ | Semantic role (e.g. `base_profile`, `base_body`, `inner_void`).  Used by operation matching in CED. |
| `input`    | ✗ | `op_id` of the predecessor.  Most ops have a single predecessor. |
| `plane`    | ✗ | Required for sketch ops: `XY`, `XZ`, `YZ`, or `*_NEG` for negative normal. |
| `params`   | ✓ | Operation-specific parameters (see §3). |

---

## 5. Validator layers

The validator runs in two stages:

### 5.1 Schema check (mandatory)

Verifies JSON structure via JSON-Schema:
* Required fields present
* Field types correct
* `op_type` ∈ allowed enum
* `op_id` uniqueness within `operations`
* `input` reference existence (when present)
* `plane` ∈ allowed values for sketch ops

### 5.2 Semantic validation

Verifies domain constraints:
* Numeric params positive: `width > 0`, `height > 0`, `radius > 0`, etc.
* `inner_radius < outer_radius` for `sketch_annulus`
* `inner_* < outer_*` for `sketch_rectangular_frame`
* `extrude.distance != 0`
* Polygon has at least 3 distinct vertices
* `cut.target` op_id exists and is an extrude/join result
* `export_step.input` (if specified) op_id exists

---

## 6. Sample operation sequence

```json
{
  "schema_version": "cad_ir_v0.1",
  "sample_id": "demo_rect_strut",
  "unit": "mm",
  "coordinate_system": {
    "up_axis": "z",
    "front_axis": "y",
    "right_axis": "x"
  },
  "operations": [
    {
      "op_id": "op_001",
      "op_type": "sketch_rectangle",
      "role": "base_profile",
      "plane": "XY",
      "params": {
        "width": 19.0,
        "height": 19.0,
        "center": [-571.0, -129.0]
      }
    },
    {
      "op_id": "op_002",
      "op_type": "extrude",
      "role": "base_body",
      "input": "op_001",
      "params": {
        "distance": 200.0,
        "extent_type": "one_side",
        "operation": "new_body",
        "direction": "+normal"
      }
    },
    {
      "op_id": "op_003",
      "op_type": "export_step",
      "input": "op_002",
      "params": {"path": "demo_rect_strut.step"}
    }
  ]
}
```

---

## 7. Repository layout

```
cad_ir/
  schema/
    cad_ir_schema_v0.1.json       # JSON Schema
    cad_ir_schema_v0.1_spec.md     # this file
  validator/
    validator.py                  # schema + semantic checks
  samples/
    manual_ir_examples/           # 45+ hand-written IR examples
  adaptor/
    adapter.py                    # cad_ir → cadquery script
    semantic_validator.py         # (re-exported from validator/)
    trace_builder.py              # declared / executed trace builders
    cadquery_backend.py           # backend-specific CAD-API calls
    run_adaptor.py                # CLI entry
  results/                        # generated scripts / STEPs / reports
  reports/
    schema_validation_report.json
    adaptor_v0.1_report.md
```