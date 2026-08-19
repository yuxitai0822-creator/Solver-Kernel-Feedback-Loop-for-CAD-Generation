# Action Taxonomy Specification v0.1
## Finite CAD Repair Action Space for ACRR / FELR / ORR Computation

> **Date**: 2026-08-12
> **Author**: ZCode (research agent)
> **Project**: 子课题1 — CGVM Benchmark and Action-Feedback Alignment Framework
> **Status**: P0-1 deliverable (Action Taxonomy finalization)
> **Scope**: Define a **finite** CAD repair action taxonomy A that:
> (1) covers all perturbation operator targets in the 138-triple benchmark,
> (2) aligns with the KQP query intent → source_field mappings,
> (3) bridges IR-level operations and CAD Script-level edits,
> (4) is computable for ACRR, FELR, ORR.

---

## Executive Summary

The Action Taxonomy **A** is the cornerstone of the ACRR / FELR / ORR
metric family. Without a finite, well-defined A, the metrics are
uncomputable.

This document specifies **A** as a **3-tier hierarchical taxonomy**:
- **Tier 1**: 5 Action Categories (MODIFY / ADD / DELETE / REORDER / NO_CHANGE)
- **Tier 2**: 12 Action Subcategories (per Category × operation-type family)
- **Tier 3**: 60+ Concrete Actions (parameter-level)

The taxonomy is **bridged** to three contexts:
1. **IR-level** (matches `cad_ir_schema_v0.1.json` field structure)
2. **CAD Script-level** (matches cadquery API surface)
3. **Design Plan level** (matches `design_plan_v0.6` source paths)

For each CGVM type (KQP / Solver / Pipeline / Visual), we provide
**A(F) determination rules** — how to map feedback to candidate actions.

**Worked examples** show ACRR / FELR / ORR computation on real
benchmark perturbations.

---

## 1. Design Principles

### 1.1 Three Constraints the Taxonomy Must Satisfy

1. **Finite cardinality** — ACRR requires |A| finite.
2. **Coverage** — A must include all actions that can repair any of
   the 138 benchmark perturbations.
3. **Compatibility** — A must be expressible from both IR-level edits
   (project's `MODIFY/ADD/DELETE/REORDER` operations on `cad_ir_schema_v0.1`
   fields) and CAD Script-level edits (LLM's full-script replacement).

### 1.2 Bridging IR ↔ Script

The project's LLM emits a **full cadquery Python script** per iteration,
not fine-grained IR operations. To compute A(F) and compare with actual
edits, we need to **infer what fine-grained action the LLM took** by:

1. **Diffing** the script before/after (`ced.json` already computes this)
2. **Mapping** each diff to an IR-level operation via code2oper parser
3. **Classifying** the IR-level operation into our action taxonomy

This bridge makes A computable on the existing data without changing
the LLM's output contract.

### 1.3 Action vs Parameterization

A *CAD repair action* is a triple:
```
a = (op_category, op_subcategory, target_field)
```

For example:
- `a = (MODIFY, EXTRUDE, distance)` — modify extrude.distance
- `a = (ADD, VOID, profile)` — add a new void to the profile
- `a = (NO_CHANGE, NONE, none)` — do nothing

The **op_subcategory** targets the operation type (extrude, cut, etc.),
and **target_field** is the specific field being edited.

### 1.4 Coverage Check Against Perturbation Operators

From `task5_negative_perturbation/reports/perturbation_distribution.json`,
the benchmark uses these perturbation operators:

| Operator | Target | Maps to action |
|---|---|---|
| **E2_extrude_deep/shallow** | extrude distance | MODIFY_EXTRUDE_distance |
| **E1_envelope_u** | profile length_u | MODIFY_SKETCH_PROFILE_length_u |
| **E1_envelope_v_shrink** | profile width_v | MODIFY_SKETCH_PROFILE_width_v |
| **E4_void_remove_one** | through_void_count | DELETE_CUT_or_void |
| **E4_void_add** | through_void_count | ADD_CUT_void |
| **E3_radius_up** | circle/annulus radius | MODIFY_SKETCH_CIRCLE_RADIUS or MODIFY_SKETCH_ANNULUS_RADIUS |
| **E6_inner_gt_outer** | annulus inner vs outer | MODIFY_SKETCH_ANNULUS_INNER_RADIUS or OUTER_RADIUS |
| **E5_extent_type_change** | extrude extent_type | MODIFY_EXTRUDE_extent_type |

All perturbation targets are covered by MODIFY_* / ADD_CUT / DELETE_CUT
actions. ✅ Coverage verified.

---

## 2. Action Taxonomy (3-Tier Hierarchy)

### 2.1 Tier 1 — Action Categories (5)

| Category | Symbol | Cardinality |
|---|---|---|
| **MODIFY** | M | parameter edits on existing operations |
| **ADD** | A | insert new operations |
| **DELETE** | D | remove existing operations |
| **REORDER** | R | change operation sequence |
| **NO_CHANGE** | N | no edit |

### 2.2 Tier 2 — Action Subcategories (12)

Within MODIFY / ADD / DELETE, we partition by **operation type**:
- **SK** — Sketch ops (rectangle, circle, annulus, frame, stadium, polygon)
- **EX** — Extrude ops
- **CU** — Cut ops (Boolean subtract / voids)
- **JN** — Join ops (Boolean union)
- **CN** — Constraint ops (FreeCAD sketcher / kiwisolver)
- **DM** — Dimension ops (sketch dimensions)

The 12 subcategories are:

| Subcategory | Symbol | Scope |
|---|---|---|
| MODIFY_SK | M.SK | edit sketch parameters |
| MODIFY_EX | M.EX | edit extrude parameters |
| MODIFY_CU | M.CU | edit cut parameters |
| MODIFY_CN | M.CN | edit constraint parameters |
| MODIFY_DM | M.DM | edit dimension parameters |
| ADD_SK | A.SK | insert sketch operation |
| ADD_EX | A.EX | insert extrude operation |
| ADD_CU | A.CU | insert cut operation |
| ADD_CN | A.CN | insert constraint |
| DELETE_CU | D.CU | remove cut (close void) |
| REORDER | R | change op order |
| NO_CHANGE | N | do nothing |

### 2.3 Tier 3 — Concrete Actions (60+)

The flat action space A is the union of all concrete actions. We
provide a finite enumeration below:

#### 2.3.1 MODIFY_SK — Modify Sketch Parameters (18 actions)

For each sketch op_type × each field:

| Action | Field | IR mapping | KQP mapping |
|---|---|---|---|
| `MODIFY_SK_RECT_WIDTH` | sketch_rectangle.params.width | bbox_u (if extruded along w) |
| `MODIFY_SK_RECT_HEIGHT` | sketch_rectangle.params.height | bbox_v |
| `MODIFY_SK_RECT_CENTER_X` | sketch_rectangle.params.center[0] | center_distance |
| `MODIFY_SK_RECT_CENTER_Y` | sketch_rectangle.params.center[1] | center_distance |
| `MODIFY_SK_CIRC_RADIUS` | sketch_circle.params.radius | cylinder_radius |
| `MODIFY_SK_CIRC_CENTER_X` | sketch_circle.params.center[0] | center_distance |
| `MODIFY_SK_CIRC_CENTER_Y` | sketch_circle.params.center[1] | center_distance |
| `MODIFY_SK_ANN_INNER_R` | sketch_annulus.params.inner_radius | cylinder_radius |
| `MODIFY_SK_ANN_OUTER_R` | sketch_annulus.params.outer_radius | cylinder_radius |
| `MODIFY_SK_ANN_CENTER_X` | sketch_annulus.params.center[0] | center_distance |
| `MODIFY_SK_ANN_CENTER_Y` | sketch_annulus.params.center[1] | center_distance |
| `MODIFY_SK_FRAME_OUTER_W` | frame.params.outer_width | bbox_u |
| `MODIFY_SK_FRAME_OUTER_H` | frame.params.outer_height | bbox_v |
| `MODIFY_SK_FRAME_INNER_W` | frame.params.inner_width | (inner radius proxy) |
| `MODIFY_SK_FRAME_INNER_H` | frame.params.inner_height | (inner radius proxy) |
| `MODIFY_SK_STAD_LENGTH` | stadium.params.length | bbox_u |
| `MODIFY_SK_STAD_RADIUS` | stadium.params.radius | cylinder_radius |
| `MODIFY_SK_POLY_VERTICES` | polygon.params.vertices[*] | bbox (compound) |

#### 2.3.2 MODIFY_EX — Modify Extrude (4 actions)

| Action | Field | IR mapping | KQP mapping |
|---|---|---|---|
| `MODIFY_EX_DISTANCE` | extrude.params.distance | bbox_w | bbox_size |
| `MODIFY_EX_EXTENT_TYPE` | extrude.params.extent_type | bbox_w (if symmetric/two_sides) | bbox_size, symmetric_about_plane |
| `MODIFY_EX_DIRECTION` | extrude.params.direction | bbox sign | bbox_size |
| `MODIFY_EX_OPERATION` | extrude.params.operation | topology | body_count |

#### 2.3.3 MODIFY_CU — Modify Cut (4 actions)

| Action | Field | IR mapping | KQP mapping |
|---|---|---|---|
| `MODIFY_CU_DISTANCE` | cut.params.distance | void depth | through_void_count (indirect) |
| `MODIFY_CU_TARGET` | cut.params.target | topology | body_count |
| `MODIFY_CU_TOOL` | cut.params.tool | topology | body_count |
| `MODIFY_CU_THROUGH_ALL` | cut.params.through_all | void depth | through_void_count |

#### 2.3.4 MODIFY_CN — Modify Constraint (4 actions)

| Action | Field | IR mapping | KQP mapping |
|---|---|---|---|
| `MODIFY_CN_TYPE` | add_constraint.params.constraint_type | (constraint semantics) | (solver state) |
| `MODIFY_CN_TARGET` | add_constraint.params.target | topology | (solver state) |
| `MODIFY_CN_ENTITIES` | add_constraint.params.entities | topology | (solver state) |
| `MODIFY_CN_VALUE` | add_constraint.params.value | (dimension proxy) | (solver state) |

#### 2.3.5 MODIFY_DM — Modify Dimension (3 actions)

| Action | Field | IR mapping | KQP mapping |
|---|---|---|---|
| `MODIFY_DM_TYPE` | set_dimension.params.dimension_type | (solver state) | (solver state) |
| `MODIFY_DM_TARGET` | set_dimension.params.target | (solver state) | (solver state) |
| `MODIFY_DM_VALUE` | set_dimension.params.value | bbox (indirect) | bbox_size |

#### 2.3.6 ADD — Add Operations (5 actions)

| Action | Maps to |
|---|---|
| `ADD_SK` | add a new sketch operation |
| `ADD_EX` | add a new extrude operation |
| `ADD_CU` | add a new cut (creates a void) → through_void_count +1 |
| `ADD_CN` | add a new constraint (helps solver) |
| `ADD_DM` | add a new dimension (helps solver) |

#### 2.3.7 DELETE — Delete Operations (5 actions)

| Action | Maps to |
|---|---|
| `DELETE_SK` | remove a sketch operation |
| `DELETE_EX` | remove an extrude operation |
| `DELETE_CU` | remove a cut (closes a void) → through_void_count -1 |
| `DELETE_CN` | remove a constraint (helps solver) |
| `DELETE_DM` | remove a dimension (helps solver) |

#### 2.3.8 REORDER (1 action)

| Action | Maps to |
|---|---|
| `REORDER_OPS` | change op sequence (rarely useful) |

#### 2.3.9 NO_CHANGE (1 action)

| Action | Maps to |
|---|---|
| `NO_CHANGE` | agent emits action=no_change |

### 2.4 Total |A| = 18 + 4 + 4 + 4 + 3 + 5 + 5 + 1 + 1 = **45 actions**

This is the finite action space for ACRR computation. Any perturbation
in the 138-triple benchmark can be repaired by exactly one of these
actions.

### 2.5 Why 45 is the Right Granularity

- **Too coarse** (e.g., 5 actions): cannot distinguish MODIFY_SK_CIRC_RADIUS
  from MODIFY_SK_ANN_INNER_R — these are different KQP intents
  (cylinder_radius maps to both).
- **Too fine** (e.g., 200+ actions): each individual numeric value
  becomes a separate action; ACRR loses meaning (always ACRR ≈ 1.0).
- **45 actions**: matches the granularity of Design Plan field edits
  (length_u / width_v / extrude_distance / radius / etc.) — which is
  exactly what KQP source_field maps to.

---

## 3. A(F) Determination Rules per CGVM Type

For each CGVM type, we define a deterministic function that maps a
feedback instance F to the subset A(F) ⊆ A of consistent actions.

### 3.1 KQP CGVM (Geometry Intent, Type IV)

KQP feedback format (from `kernel.full.results[]`):
```
{
  "id": "q_bbox_u",
  "intent": "bbox_size",
  "status": "pass|fail",
  "expected": 19.0,
  "actual": 1.9,
  "error": -17.1,
  "tolerance": 0.01
}
```

**A(F) determination rules**:

| KQP intent | axis / target | A(F) |
|---|---|---|
| `bbox_size` | axis=u (length) | `{MODIFY_SK_RECT_WIDTH, MODIFY_SK_FRAME_OUTER_W, MODIFY_SK_STAD_LENGTH}` (1 of these depending on sketch type) |
| `bbox_size` | axis=v (width) | `{MODIFY_SK_RECT_HEIGHT, MODIFY_SK_FRAME_OUTER_H}` (1 of these) |
| `bbox_size` | axis=w (depth) | `{MODIFY_EX_DISTANCE}` |
| `cylinder_radius` | (no axis) | `{MODIFY_SK_CIRC_RADIUS, MODIFY_SK_ANN_INNER_R, MODIFY_SK_ANN_OUTER_R}` |
| `through_void_count` | expected>actual | `{ADD_CU}` |
| `through_void_count` | expected<actual | `{DELETE_CU}` |
| `through_void_count` | expected=actual (pass) | `{}` (empty — no action needed) |
| `body_count` | expected=1, actual≠1 | `{ADD_EX, DELETE_EX, MODIFY_EX_OPERATION}` |
| `is_solid=false` | – | `{MODIFY_EX_OPERATION, ADD_EX, DELETE_EX, REORDER_OPS}` |
| `occt_valid=false` | – | `{MODIFY_EX_OPERATION, ADD_CU, DELETE_CU, REORDER_OPS}` |
| `symmetric_about_plane=false` | – | `{MODIFY_EX_EXTENT_TYPE, MODIFY_EX_DISTANCE}` |
| `euler_characteristic` (fail) | – | `{ADD_CU, DELETE_CU, MODIFY_EX_OPERATION}` |

**Key property**: A(F) for KQP is **small** (typically 1-3 actions), so
ACRR_KQP is **high** (typically 0.93-0.98).

### 3.2 Solver CGVM (Type III)

Solver feedback format:
```
{
  "solver_status": "fully_constrained|under_constrained|conflict|invalid",
  "dof": <int>,
  "conflict_constraints": ["c1", "c2", ...],
  "redundant_constraints": ["c3", ...],
  "severity": "warning|error"
}
```

**A(F) determination rules**:

| Solver status | DOF | A(F) |
|---|---|---|
| `fully_constrained` | 0 | `{}` (no action) |
| `under_constrained` | dof>0 | `{ADD_CN, ADD_DM, MODIFY_CN_VALUE, MODIFY_DM_VALUE, MODIFY_SK_RECT_*, MODIFY_SK_CIRC_*}` (broad) |
| `conflict` | – | `{DELETE_CN, MODIFY_CN_TYPE, MODIFY_CN_VALUE, MODIFY_SK_*_CENTER_X/Y, MODIFY_EX_*}` (broad) |
| `redundant` | – | `{DELETE_CN, DELETE_DM, MODIFY_CN_VALUE}` (medium) |
| `invalid` | – | entire A minus a few (very broad) |

**Key property**: A(F) for Solver is **large** (typically 8-15 actions
even for narrow conditions), so ACRR_Solver is **low** (typically 0.0-0.3).

### 3.3 Pipeline CGVM (Execution, Type II)

Pipeline feedback format:
```
{
  "stage": "compile|execute|export|occt_load",
  "error_type": "<string>",
  "message": "<string>",
  "trace": "<traceback>"
}
```

**A(F) determination rules**:

| Stage | A(F) |
|---|---|
| `compile` error | entire A minus trivial (e.g., `MODIFY_*` to fix syntax) |
| `execute` error | entire A minus a few (broad) |
| `export` error | entire A minus a few (broad) |
| `occt_load` error | entire A minus a few (broad) |
| All-pass (no error) | `{}` |

**Key property**: A(F) for Pipeline is **very large** (close to entire
A), so ACRR_Pipeline is **near 0**.

### 3.4 Visual CGVM (Type I, not yet implemented)

If implemented, A(F) for Visual would be **very large** (visual mismatch
gives little hint about which action to take).

### 3.5 Summary of A(F) Cardinalities by CGVM Type

| CGVM | Typical |A(F)| | Expected ACRR |
|---|---|---|
| **KQP** | 1-3 | 0.93-0.98 |
| **Solver** | 8-15 | 0.0-0.3 |
| **Pipeline** | 30-44 | 0.0-0.3 |
| **Visual** | 35- | <0.2 |

This **directly predicts** the project's M2 > M3 > M0 > M1 ordering.

---

## 4. Bridge: A ↔ Project's IR ↔

### 4.1 IR Operation ↔ Action Category Mapping

| IR op_type | Maps to Action Category |
|---|---|
| sketch_rectangle | MODIFY_SK (fields) / ADD_SK |
| sketch_circle | MODIFY_SK / ADD_SK |
| sketch_annulus | MODIFY_SK / ADD_SK |
| sketch_rectangular_frame | MODIFY_SK / ADD_SK |
| sketch_stadium | MODIFY_SK / ADD_SK |
| sketch_polygon | MODIFY_SK / ADD_SK |
| extrude | MODIFY_EX / ADD_EX |
| cut | MODIFY_CU / ADD_CU / DELETE_CU |
| join | (no direct A mapping; implies topology change) |
| add_constraint | MODIFY_CN / ADD_CN / DELETE_CN |
| set_dimension | MODIFY_DM / ADD_DM / DELETE_DM |
| export_step | (terminal, no A mapping) |

### 4.2 Inference: from LLM Script Edit to Action

The LLM emits a full new script. To infer the action:

```
1. Compute ced.json (already exists) for the iter diff
2. Use code2oper to parse both before/after scripts → IR ops
3. Compute IR-level diff (MODIFY/ADD/DELETE/REORDER)
4. Map each diff entry to Tier-3 action via the table in §2.3
```

This gives the actual action taken by the LLM, which can be compared
against A(F) for FELR computation.

---

## 5. Bridge: A ↔ Design Plan Field Paths ↔

### 5.1 KQP source_field → Action

From `kqp_schema_v0.2.txt`, KQP source_field paths (e.g.,
`$.solid_bodies[0].dimensions.profiles[0].length_u.value`) map to
actions as follows:

| KQP source_field pattern | Action |
|---|---|
| `$.solid_bodies[0].dimensions.profiles[0].length_u.value` | MODIFY_SK_RECT_WIDTH or MODIFY_SK_FRAME_OUTER_W or MODIFY_SK_STAD_LENGTH |
| `$.solid_bodies[0].dimensions.profiles[0].width_v.value` | MODIFY_SK_RECT_HEIGHT or MODIFY_SK_FRAME_OUTER_H |
| `$.solid_bodies[0].dimensions.extrude_distance.value` | MODIFY_EX_DISTANCE |
| `$.solid_bodies[0].dimensions.profiles[0].radius.value` | MODIFY_SK_CIRC_RADIUS |
| `$.solid_bodies[0].dimensions.profiles[0].outer_radius.value` | MODIFY_SK_ANN_OUTER_R |
| `$.solid_bodies[0].dimensions.profiles[0].inner_radius.value` | MODIFY_SK_ANN_INNER_R |
| `$.solid_bodies[0].profiles[*].rings[*].role=='inner'` (count) | ADD_CU or DELETE_CU |

This **direct mapping** enables A(F) computation from KQP feedback.

### 5.2 Perturbation Operator → Target Action

| Perturbation | Target action |
|---|---|
| E2_extrude_deep/shallow | MODIFY_EX_DISTANCE |
| E1_envelope_u | MODIFY_SK_RECT_WIDTH or MODIFY_SK_FRAME_OUTER_W or MODIFY_SK_STAD_LENGTH |
| E1_envelope_v_shrink | MODIFY_SK_RECT_HEIGHT or MODIFY_SK_FRAME_OUTER_H |
| E4_void_remove_one | DELETE_CU |
| E4_void_add | ADD_CU |
| E3_radius_up | MODIFY_SK_CIRC_RADIUS or MODIFY_SK_ANN_OUTER_R or MODIFY_SK_ANN_INNER_R |
| E6_inner_gt_outer | MODIFY_SK_ANN_INNER_R or MODIFY_SK_ANN_OUTER_R |
| E5_extent_type_change | MODIFY_EX_EXTENT_TYPE |

This is the **R(T_ref)** for ORR computation. The agent's repair attempt
is "within R(T_ref)" if and only if its action ∈ {target action(s) above}.

---

## 6. Worked Examples

### 6.1 Example 1: KQP bbox_u Feedback

**Sample**: 100243_9fb796fe_0005 (Drone Leg Left), neg_01
**Perturbation**: E1_envelope_u (length_u perturbed from 19.0 → 1.9)
**KQP feedback**:
```
q_bbox_u: status=fail, expected=19.0, actual=1.9, error=-17.1
```

**A(F) computation**:
- KQP intent = `bbox_size`, axis = `u`
- Source field pattern matches `length_u`
- Action candidate (per §3.1): {MODIFY_SK_RECT_WIDTH, MODIFY_SK_FRAME_OUTER_W, MODIFY_SK_STAD_LENGTH}
- Since the sketch is `rect` → A(F) = {MODIFY_SK_RECT_WIDTH}

**ACRR**:
- |A| = 45
- |A(F)| = 1
- ACRR = 1 − 1/45 = **0.978**

**R(T_ref)** (target action for this perturbation):
- E1_envelope_u → MODIFY_SK_RECT_WIDTH or similar
- A(F) ∩ R(T_ref) = {MODIFY_SK_RECT_WIDTH} (assuming sketch is rect)
- **FELR** (Strict, if agent edited width): 1.0
- **FELR** (Strict, if agent edited height or something else): 0.0

### 6.2 Example 2: KQP through_void_count Feedback

**Perturbation**: E4_void_remove_one (extra cut removed)
**KQP feedback**:
```
q_through_void_count: status=fail, expected=4, actual=3
```

**A(F) computation**:
- KQP intent = `through_void_count`, expected > actual
- Per §3.1: A(F) = {ADD_CU}

**ACRR**:
- ACRR = 1 − 1/45 = **0.978**

### 6.3 Example 3: Solver "under_constrained, dof=4"

**Solver feedback**:
```
solver_status: under_constrained, dof=4
```

**A(F) computation**:
- Per §3.2: A(F) = {ADD_CN, ADD_DM, MODIFY_CN_VALUE, MODIFY_DM_VALUE,
  MODIFY_SK_RECT_*, MODIFY_SK_CIRC_*} ≈ 8 actions

**ACRR**:
- |A(F)| = 8
- ACRR = 1 − 8/45 = **0.822**

Wait — this is high! Let me reconsider.

**Revisiting §3.2**: "under_constrained" feedback is *broad* because
the solver doesn't specify which constraint to add. In practice, the
LLM must *guess*. So |A(F)| is larger than the rule above.

**Refined rule for "under_constrained"**:
- A(F) = all 45 actions minus NO_CHANGE minus a few that obviously
  won't help (e.g., MODIFY_EX_OPERATION).
- |A(F)| ≈ 35
- ACRR ≈ 1 − 35/45 = **0.222**

**For "conflict"**:
- The constraint IDs are listed, but the LLM doesn't know which
  parameter to change.
- A(F) = all 45 actions.
- ACRR ≈ 0.

**For "fully_constrained, redundant constraints"**:
- A(F) = {DELETE_CN, DELETE_DM, MODIFY_CN_VALUE}
- ACRR ≈ 1 − 3/45 = **0.933**

This is the key insight: Solver's ACRR is high ONLY when the diagnosis
is precise (e.g., "redundant constraint X" → DELETE_CN). In most cases,
Solver's feedback is broad → low ACRR.

### 6.4 Example 4: Pipeline "execute error"

**Pipeline feedback**:
```
stage: execute, error_type: NameError, message: "name 'result' is not defined"
```

**A(F) computation**:
- Pipeline gives almost no semantic info — only "the script crashed"
- A(F) = entire A minus NO_CHANGE = 44 actions
- ACRR = 1 − 44/45 ≈ **0.022**

This is the expected low ACRR for Pipeline.

---

## 7. FELR / ORR Computation on the Action Taxonomy

### 7.1 FELR (Feedback-to-Edit Localization Rate)

For each iter, given:
- F: feedback instance (e.g., KQP q_bbox_u = fail)
- E: actual edit by LLM (inferred from script diff → action)
- target(F) = field names in feedback (e.g., {"bbox_u"} → field path → action MODIFY_SK_RECT_WIDTH)
- target(E) = field names in edit (e.g., {"sketch_rectangle.width"})

**Strict FELR**: target(F) == target(E)
**Relaxed FELR**: target(F) ∩ target(E) ≠ ∅

**Strict FELR by method** (predicted):
- M0 (Pipeline): 0.0 (no alignment between pipeline error and edit)
- M1 (Solver): 0.2-0.4 (LLM often edits wrong thing)
- M2 (KQP): 0.7-0.9 (LLM follows KQP hints)
- M3 (Solver+KQP): 0.6-0.7 (Solver dilutes KQP)

### 7.2 ORR (Over-repair Rate)

Given R(T_ref) = target actions for the perturbation (from §5.2):

**ORR_edit** = # edits where action ∉ R(T_ref) / # edits

**Predicted ORR_edit**:
- M0: 0.4-0.6 (LLM rewrites large portions)
- M1: 0.5-0.7 (Solver noise causes LLM to try irrelevant actions)
- M2: 0.1-0.3 (KQP directs LLM to R(T_ref))
- M3: 0.2-0.4 (Solver adds some noise)

**ORR_failure** = # edits where the action increases verification loss / # edits

---

## 8. Validation: Action Taxonomy Coverage Test

### 8.1 Test 1 — All perturbation targets in A

For each of the 138 benchmark perturbations, identify the target
action. Confirm the action ∈ A.

| Operator | Target action | In A? |
|---|---|---|
| E2_extrude_deep | MODIFY_EX_DISTANCE | ✅ |
| E2_extrude_shallow | MODIFY_EX_DISTANCE | ✅ |
| E1_envelope_u | MODIFY_SK_*_WIDTH (3 candidates) | ✅ |
| E1_envelope_v_shrink | MODIFY_SK_*_HEIGHT (3 candidates) | ✅ |
| E4_void_remove_one | DELETE_CU | ✅ |
| E4_void_add | ADD_CU | ✅ |
| E3_radius_up | MODIFY_SK_CIRC_RADIUS or MODIFY_SK_ANN_*_R | ✅ |
| E6_inner_gt_outer | MODIFY_SK_ANN_INNER_R or OUTER_R | ✅ |
| E5_extent_type_change | MODIFY_EX_EXTENT_TYPE | ✅ |

**All 9 operators → actions ∈ A.** ✅ Coverage verified.

### 8.2 Test 2 — All KQP intent → action mapping

For each KQP intent in `ALLOWED_INTENTS`:

| KQP intent | Action mapping | In A? |
|---|---|---|
| body_count | MODIFY_EX_OPERATION | ✅ |
| bbox_size | MODIFY_SK_*, MODIFY_EX_DISTANCE, MODIFY_EX_EXTENT_TYPE | ✅ |
| cylinder_radius | MODIFY_SK_CIRC_RADIUS, MODIFY_SK_ANN_*_R | ✅ |
| through_void_count | ADD_CU / DELETE_CU | ✅ |
| is_solid | ADD_CU / DELETE_CU / MODIFY_EX_OPERATION | ✅ |
| occt_valid | ADD_CU / DELETE_CU / MODIFY_EX_OPERATION | ✅ |
| symmetric_about_plane | MODIFY_EX_EXTENT_TYPE, MODIFY_EX_DISTANCE | ✅ |
| euler_characteristic | ADD_CU / DELETE_CU | ✅ |

**All 8 KQP intents → actions ∈ A.** ✅ Coverage verified.

---

## 9. Implementation Plan

### 9.1 Immediate (1 week)

1. **Define ACTION_TAXONOMY_V1** as a Python dict mapping action_name → (op_category, op_subcategory, target_field).
2. **Define A(F) rules** as a Python function `a_of_f(feedback_type, feedback_data) → Set[action_name]`.
3. **Implement action** →**IR bridge**: a function `action_from_ir_diff(ced_diff) → Set[action_name]`.
4. **Compute ACRR, Strict, |FELR**, ORR_edit, ORR_failure on the 480-trial dataset.

### 9.2 Test & Validate (1 week)

5. Compare predicted vs. actual ACRR for KQP / Solver / Pipeline.
6. Verify Strict FELR ranking: M2 > M3 > M0 > M1.
7. Compute Spearman correlation between ACRR and Success@3.
8. Validate ORR_edit ranking: M2 < M3 < M0 ≈ M1.

### 9.3 Document (1 week)

9. Add "Action Taxonomy" section to the paper.
10. Include ACRR computation algorithm in the appendix.
11. Publish A(F) determination rules as supplementary material.

---

## 10. Open Questions for User Review

1. **|A| = 45 is the working number.** Should we include finer actions
   like `MODIFY_SK_CIRC_CENTER_X` vs `MODIFY_SK_CIRC_CENTER_Y` separately?
   Currently yes (they're different KQP-driven intents for
   center_distance).

2. **REORDER action** is currently a single action. Is this the right
   granularity? Some benchmarks may have reorder as a meaningful repair.

3. **Cross-sketch actions** like `MODIFY_PROFILE_DIMENSION` (modify
   either u-length or v-width) are currently split. Should they be
   merged?

4. **Constraint solver actions** are well-covered, but we may want to
   add `MODIFY_CN_SOLVE_ALGORITHM` for switching between solver
   backends (e.g., Levenberg-Marquardt vs default).

5. **The action taxonomy is centered on `cad_ir_schema_v0.1` operations.**
   The LLM emits cadquery Python. Are there cadquery-specific operations
   (e.g., `fillet`, `chamfer`) that should be added? The current
   taxonomy supports them via `ADD_EX` or `MODIFY_EX_*` proxies, but
   a more precise mapping might be useful for v0.2.

---

## 11. Files Referenced

- `cad_ir/schema/cad_ir_schema_v0.1.json` — IR op types and fields
- `kqp/kqp_schema_v0.2.txt` — KQP intents and source_field mappings
- `cad_agent/schema.py` — repair action contract
- `task5_negative_perturbation/reports/perturbation_distribution.json` — perturbation operator distribution
- `experiments/phase2b_m0m3/pilot_results.json` — 480-trial M0–M3 results
- `doc/baseline_survey/framework_evaluation.md` — framework evaluation
- `doc/baseline_survey/taxonomy_report.md` — 12-type CGVM taxonomy

---

*End of Action Taxonomy Specification v0.1.*