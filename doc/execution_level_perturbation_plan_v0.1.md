# Execution-Level Perturbation Plan v0.1

> **Date**: 2026-07-17
> **Status**: READY FOR EXECUTION
> **Owner**: execution agent
> **Predecessors**: B-006 fix (annulus solver) must land first
> **Goal**: add a class of execution-level perturbations that break the
> Design-Plan self-diagnosis shortcut (B-007), so the ablation can actually
> measure feedback value (RQ1/RQ2/RQ3).

---

## 0. Why this plan exists

The pilot proved that the current E1–E6 perturbation battery is
**information-redundant with the Design Plan**: every perturbed value
(bbox, radius, void count) has a matching field in the Design Plan, so
M0 (no feedback) can self-diagnose by reading the Design Plan and
comparing numbers — producing M0 ≡ M1 ≡ M2 ≡ M3 (B-007).

To measure feedback value we need perturbations where:

1. **DP has no direct field** — the perturbed quantity is not stored in
   the Design Plan, so M0 cannot self-diagnose by field comparison.
2. **LLM prior fails** — the error is not inferable from reading the IR
   + Design Plan alone; it requires executing the CAD and measuring the
   resulting geometry.
3. **KQP can detect it** — the error manifests as a queryable geometric
   property (bbox span, centroid, void count, etc.) that the KQP runner
   already supports.

This document specifies two such perturbation classes, selected after
auditing the 50-sample sanity set and the KQP runner's capabilities.

---

## 1. Feasibility audit (already done — read this before implementing)

### 1.1 Sanity-set constraints (from `Reconstruction_results/*/input_history.json`)

| Property | Finding | Implication |
|---|---|---|
| Feature types | 50× Sketch + 50× ExtrudeFeature, **0 Cut/Boolean/Join** | "boolean order error" perturbation is INFEASIBLE — no boolean ops to reorder |
| Extrude operation | all 50 are `NewBodyFeatureOperation` | no join/cut target to mis-select |
| extent_type | 48 OneSide, 1 Symmetric, 1 TwoSides | direction-flip perturbation works on the 48 OneSide samples |
| start_extent | all 50 are `ProfilePlaneStartDefinition` | uniform structure — perturbation logic can be generic |
| Sketch structure | has `reference_plane` (XY/XZ/YZ) + `transform` (origin, x_axis, y_axis) + `points` | plane-swap and coordinate-flip are directly editable |

### 1.2 KQP runner capabilities (from `kqp/runner/`)

| Intent | Backend function | Can it detect execution-level errors? |
|---|---|---|
| `bbox_size` | `get_axis_aligned_bbox` + frame-axis projection | ✅ detects plane-swap, coordinate-flip, center-offset |
| `cylinder_radius` | `get_cylinder_radii` | ✅ but only for circle/annulus samples |
| `through_void_count` | `get_through_void_count` (wire heuristic) | ✅ detects missing/extra inner loops |
| `symmetric_about_plane` | `is_symmetric_about_plane` (centroid on plane) | ✅ detects direction-flip on symmetric extents |
| `body_count` | `get_solid_count` | ✅ but always 1 in this sanity set |
| `is_solid` / `occt_valid` | `is_solid_shape` / `is_occt_valid` | ✅ health checks |
| (available in backend) `get_centroid` | `get_centroid` | ✅ available but NOT yet wired to a KQP intent — see §5 |

### 1.3 Design-Plan field audit (from `DesignPlan/compiler/instances_v6/`)

The Design Plan stores: `global_envelope.bbox` (u/v/w spans), base
geometry, feature counts, basic dimensions, basic spatial relations. It
does **NOT** store: sketch plane identity (XY vs XZ), coordinate-axis
assignment, extrude direction sign, profile center coordinates as
absolute values (only relative bbox). This confirms the DP blind spot
needed for execution-level perturbations.

---

## 2. Selected perturbation classes

Two classes are selected. Both satisfy all three feasibility conditions.

### 2.1 EX1 — Sketch Plane Swap

**Perturbation**: change the sketch's `reference_plane` and `transform`
so the profile is built on a different principal plane (e.g., XY → XZ,
or XY → YZ), while keeping all profile dimensions and extrude distance
identical.

**Effect on CAD**: the extruded body is oriented along the wrong axis.
E.g., a profile meant to extrude along Z now extrudes along Y. The bbox
spans swap between axes (e.g., the "height" that should be along Z
appears along Y instead).

**Why it defeats DP self-diagnosis**:
- The Design Plan says `bbox.u = 80, bbox.v = 50, bbox.w = 20` but does
  NOT say which world axis u/v/w correspond to.
- M0 reading the Design Plan sees "bbox 80×50×20" and the IR's extrude
  distance = 20 — numbers match, no discrepancy detected.
- But the actual STEP has bbox X=80, Y=20, Z=50 (swapped) because the
  plane was changed. Only KQP's per-axis bbox query catches this.

**Why KQP catches it**: KQP `bbox_size` queries are per-axis (u/v/w with
frame directions). When the plane swaps, the frame-axis projection no
longer matches the expected span. The runner's "best-match" strategy
(query_dispatcher L72-83) may mask a pure swap if two spans are equal —
so we must check the sample's three bbox spans are distinct before
applying EX1 (see §4.3 eligibility).

**KQP expected values**: unchanged — the Design Plan's bbox field is the
ground truth, and the perturbation must NOT alter Design Plan (§3.2 of
the main perturbation spec: only history JSON is perturbed).

### 2.2 EX2 — Coordinate Axis Flip (x↔y within the sketch plane)

**Perturbation**: within the sketch's `transform`, swap `x_axis` and
`y_axis`, and correspondingly swap the x/y coordinates of all sketch
`points`. Keep `reference_plane` unchanged.

**Effect on CAD**: the profile is mirrored/rotated within its plane. For
a non-square profile (width ≠ height), this produces a bbox where the
two in-plane spans are swapped. E.g., a 80×50 rectangle becomes 50×80.

**Why it defeats DP self-diagnosis**:
- Same as EX1: DP has bbox spans but no axis assignment.
- For a square or near-square profile (width ≈ height), EX2 is
  invisible — must check eligibility (§4.3).

**Why KQP catches it**: the per-axis bbox spans swap; if the two spans
differ by more than tolerance, the `bbox_size` query for the affected
axis fails.

### 2.3 Why these two and not others

| Rejected alternative | Reason |
|---|---|
| Boolean order error | sanity set has 0 boolean ops (§1.1) |
| Profile selection error | no multi-profile / cut operations in sanity set |
| Extrude direction flip (sign) | only detectable on Symmetric extents (1 sample) and via `symmetric_about_plane`; too narrow |
| Profile center offset | KQP `bbox_size` detects size, not position; would need `get_centroid` wired as a new intent — larger scope, defer to §5 |

EX1 and EX2 are the minimal pair that: use only the existing KQP
`bbox_size` intent, work on the existing sanity-set structure, and
require no new KQP schema.

---

## 3. Relationship to existing E1–E6 battery

EX1/EX2 are a **new perturbation class**, not replacements for E1–E6.
They are added alongside:

```
Existing parameter-level battery (E1–E6):
  - detectable by DP self-diagnosis (B-007 problem)
  - keep as-is for completeness / upper-bound on M0

New execution-level battery (EX1–EX2):
  - NOT detectable by DP self-diagnosis
  - the battery where feedback value should manifest
```

The full benchmark will report results **separately** for the two
batteries. The hypothesis is:

- On E1–E6: M0 ≈ M2 (DP self-diagnosis suffices) — confirmed by pilot.
- On EX1–EX2: M0 ≪ M2 (feedback required) — to be validated.

If the second hypothesis holds, the ablation measures feedback value.
If it does not hold even on EX1–EX2, the RQ itself needs reframing
(the LLM prior is stronger than expected across the board).

---

## 4. Implementation specification

### 4.1 Module location

```
task5_negative_perturbation/
  perturbation/
    operators_ex.py        ← NEW: EX1, EX2 operators
    field_map_ex.py        ← NEW: field map for execution-level perturbations
    sampler_ex.py          ← NEW: eligibility + sampling for EX1/EX2
    perturb_history_ex.py  ← NEW: entry point, parallels perturb_history.py
  reports/
    ex_perturbation_summary.json   ← NEW
```

### 4.2 EX1 operator — `op_sketch_plane_swap`

**Input**: clean history JSON.
**Output**: perturbed history JSON + perturbation_meta.

**Logic**:
1. Find the Sketch entity in `entities`.
2. Read `reference_plane.plane.normal` — determine current plane (XY if
   normal≈(0,0,1), XZ if normal≈(0,1,0), YZ if normal≈(1,0,0)).
3. Choose a target plane different from current. Prefer the swap that
   produces the most distinct bbox rearrangement (see §4.3).
4. Rewrite `reference_plane` (name + plane.normal + plane.origin).
5. Rewrite `transform.x_axis` and `transform.y_axis` to match the new
   plane's axes.
6. **Do NOT rewrite `points`** — the sketch points are in the sketch's
   local 2D coordinate system embedded in 3D; the transform handles
   placement. (Verify this with the history2ir compiler — see §6.1.)
7. Leave ExtrudeFeature unchanged (distance, extent_type, operation all
   stay the same).

**perturbation_meta fields**:
```json
{
  "perturbation_type": "EX1_sketch_plane_swap",
  "error_category": "EX1_plane_swap",
  "original_plane": "XY",
  "perturbed_plane": "XZ",
  "target_intent": "bbox_size",
  "expected_failed_queries": ["q_bbox_u", "q_bbox_v"],
  "allowed_secondary_failed_queries": ["q_bbox_w"],
  "source_design_plan_field": "$.global_envelope.bbox",
  "should_reconstruct": true,
  "should_fail_kqp": true
}
```

### 4.3 EX2 operator — `op_coordinate_axis_flip`

**Input**: clean history JSON.
**Output**: perturbed history JSON + perturbation_meta.

**Logic**:
1. Find the Sketch entity.
2. Read `transform.x_axis` and `transform.y_axis`.
3. Swap them: new_x_axis = old_y_axis, new_y_axis = old_x_axis.
4. For every point in `points`, swap its (x, y) coordinates *in the
   sketch-local frame*. Since points are stored as Point3D in the
   sketch plane, the swap must respect the plane: for an XY-plane
   sketch, swap point.x ↔ point.y; for XZ-plane, swap point.x ↔
   point.z; etc. (Derive from `transform.x_axis` which world axes the
   local x/y map to.)
5. Leave `reference_plane` and ExtrudeFeature unchanged.

**perturbation_meta fields**:
```json
{
  "perturbation_type": "EX2_coordinate_flip",
  "error_category": "EX2_axis_flip",
  "swapped_axes": "x<->y",
  "target_intent": "bbox_size",
  "expected_failed_queries": ["q_bbox_u", "q_bbox_v"],
  "allowed_secondary_failed_queries": [],
  "source_design_plan_field": "$.global_envelope.bbox",
  "should_reconstruct": true,
  "should_fail_kqp": true
}
```

### 4.4 Eligibility filter (critical — prevents invisible perturbations)

Before applying EX1 or EX2 to a sample, verify the perturbation will
actually be KQP-detectable. This is the single most important guard —
it is what prevents a repeat of B-007.

**EX1 eligibility** (plane swap detectable):
- Compute the clean STEP's three bbox spans (X, Y, Z).
- The target plane swap must produce a configuration where at least one
  expected bbox query value differs from the actual by > 5× tolerance.
- Concretely: if clean bbox is (80, 50, 20) and we swap XY→XZ, the new
  bbox becomes (80, 20, 50). The Design Plan expects u=80, v=50, w=20
  (mapped to the original frame). After swap, the frame-axis projection
  yields different spans → detectable.
- **Reject** the sample if any two of its three bbox spans are within
  2× tolerance of each other (the swap would be masked by the
  best-match strategy).

**EX2 eligibility** (axis flip detectable):
- The two in-plane spans must differ by > 5× tolerance.
- I.e., for a rectangle, width and height must be sufficiently
  different; near-square profiles are rejected.

**Eligibility check method**: run the clean history through
ReconstructionEngine → get clean STEP → run KQP → read actual bbox
spans. This is offline (no LLM), cheap, and must be done before
perturbation. Record eligibility per sample in
`ex_perturbation_summary.json`.

### 4.5 Sampling plan

Target: from the 46 clean samples, produce EX1 and EX2 negatives.

- For each clean sample, attempt EX1 and EX2.
- Apply the §4.4 eligibility filter.
- Expected yield: EX1 eligible on ~30–40 samples (most samples have
  distinct bbox spans); EX2 eligible on ~30–40 samples (most profiles
  are non-square).
- Target total: ≥ 60 execution-level negatives (EX1 + EX2 combined).
- If yield < 60, document which samples were rejected and why.

Each sample gets up to 2 EX negatives (one EX1, one EX2), distinct
from its 3 E1–E6 negatives. The sample's total negative count becomes
up to 5.

---

## 5. Open item — centroid query (defer, do not block)

EX1/EX2 are detectable via `bbox_size` alone. A future `centroid`
intent (using the already-implemented `geometry_backend.get_centroid`)
would enable a "profile center offset" perturbation (EX3), but this
requires:
- adding `centroid` to `kqp_schema_v0.2` → v0.3,
- adding a dispatcher branch,
- adding a KQP compiler rule to emit centroid queries from Design Plan.

This is out of scope for the current plan. EX1+EX2 suffice to test the
feedback-value hypothesis. EX3 is a Phase-2 extension.

---

## 6. Verification & acceptance

### 6.1 Behavioral equivalence (must hold for EX negatives too)

Per the main contract §13 / Task 2, every negative must satisfy:
```
KQP(ReconstructionEngine(perturbed_history))
  ≡
KQP(Execute(Adaptor(History2IR(perturbed_history))))
```

For EX1/EX2 this is especially important because the perturbation
touches `transform` / `reference_plane`, which the history2ir compiler
must faithfully translate. **Before running the ablation**, verify on
3 EX1 + 3 EX2 samples that:
1. `compile_history_to_ir(perturbed_history)` produces an IR whose
   sketch plane / transform field reflects the perturbation.
2. The adaptor-generated STEP, when KQP-queried, fails the expected
   bbox queries.
3. The history-reconstruction path produces the same KQP failure
   signature.

If history2ir drops the transform change (a real risk — it dropped
radius changes per the earlier 14-sample finding), EX1/EX2 will be
invisible at the IR layer and the ablation will fail silently. This
verification is the gate.

### 6.2 Acceptance criteria

1. `operators_ex.py` implements EX1 and EX2 per §4.2/§4.3.
2. Eligibility filter (§4.4) runs on all 46 clean samples; ≥60 EX
   negatives produced; rejected samples documented.
3. Behavioral equivalence (§6.1) verified on 6 samples (3 EX1 + 3 EX2);
   all pass.
4. Each EX negative has a valid `perturbation_meta.json` with
   `target_intent=bbox_size` and `expected_failed_queries` populated.
5. KQP detection rate on EX negatives ≥ 80% (per the main Task 5
   threshold). If lower, investigate whether history2ir is dropping
   the perturbation.
6. EX negatives are added to the repair-eligible manifest alongside
   the existing E1–E6 negatives, flagged with `battery: execution_level`.

### 6.3 Pilot re-run after EX battery is ready

After EX1/EX2 land and pass §6.2, re-run the pilot (18 samples) but
**draw the 18 from the EX battery only** (or a 50/50 mix of EX and
E1–E6). The success criterion for this re-run is:

- **On EX-stratum samples: M0 ≪ M2** (M2's KQP feedback produces
  measurably higher Success@3 than M0's DP self-diagnosis).
- **On E1–E6-stratum samples: M0 ≈ M2** (confirmed by the original
  pilot).

If both hold, the ablation design is validated and the full 104+EX
benchmark can proceed. If M0 ≈ M2 even on EX samples, escalate — the
RQ may need reframing.

---

## 7. Execution sequence (hand-off to execution agent)

**Prerequisite**: B-006 (annulus solver) must be fixed and verified
first. EX1/EX2 do not depend on B-006, but the ablation re-run does
(annulus samples must be solver-valid for a fair comparison).

**Steps** (in order):

1. **Verify B-006 is fixed.** Run the 7 annulus pilot samples through
   the solver; confirm `solver_acceptable=True` on all 7. If not fixed,
   stop and fix B-006 first (per execution agent's option A: add
   Concentric + Radius constraints to annulus translation in
   `Freecadsolver_feedback/core/solver_runner.py`).

2. **Implement EX1 + EX2 operators** per §4.2/§4.3 in
   `task5_negative_perturbation/perturbation/operators_ex.py`.

3. **Implement eligibility filter** per §4.4 in `sampler_ex.py`. Run on
   all 46 clean samples; produce `ex_perturbation_summary.json` with
   per-sample eligibility + chosen target plane / swap.

4. **Generate EX negatives.** For each eligible sample, produce
   perturbed history + perturbation_meta + reconstructed STEP. Save
   under `task5_negative_perturbation/perturbations/<sid>/ex1/` and
   `.../ex2/` (parallel to existing `neg_01/` etc.).

5. **Run behavioral equivalence check** (§6.1) on 6 samples. If any
   fail, investigate history2ir transform handling BEFORE proceeding.
   Do NOT skip this step — it is the gate that prevents a silent
   B-007 repeat.

6. **Run KQP detection** on all EX negatives. Confirm ≥80% detection
   rate. Investigate any false-pass cases.

7. **Compile EX negatives to IR** via the existing history2ir compiler.
   Add to `repair_eligible_manifest.json` with `battery: execution_level`
   flag.

8. **Re-run pilot** (18 samples, drawn per §6.3). Check the M0 vs M2
   separation on EX-stratum samples.

9. **Report** in `ex_perturbation_report.md`: eligibility yield,
   detection rate, behavioral-equivalence results, pilot M0-vs-M2
   separation.

**Do NOT** proceed to the full 104+EX benchmark until step 8 shows
M0 ≪ M2 on the EX stratum. If it does not, stop and escalate — the
experimental design needs review before spending full-benchmark tokens.

---

## 8. What not to do

1. **Do not skip the eligibility filter (§4.4).** Applying EX1/EX2 to
   a near-square or near-cubic sample produces an invisible perturbation
   — exactly the B-007 failure mode.
2. **Do not skip behavioral equivalence (§6.1).** history2ir has a
   known habit of dropping perturbation fields; EX1/EX2 touch the
   transform, which is a new perturbation surface. Unverified = silent
   failure.
3. **Do not modify the Design Plan.** EX1/EX2 perturb history JSON only.
   The Design Plan remains the ground truth that KQP expected values
   come from. Modifying DP would defeat the entire point (KQP would
   then expect the wrong thing).
4. **Do not mix EX negatives into the E1–E6 battery without a flag.**
   The two batteries answer different questions and must be reported
   separately. Use the `battery` field in perturbation_meta.
5. **Do not run the full benchmark before the pilot re-run (step 8).**
   The pilot re-run is the cheap check that the design works; the full
   benchmark is expensive and should only run on a validated design.
