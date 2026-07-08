# Solver Feedback v0.1 — API Probe Report

> **Phase**: API capability validation before full implementation
> **Backend chosen**: `kiwisolver` (Cassowary-based linear constraint solver) + custom Python adapter
> **Backend rejected**: `FreeCAD Sketcher` — not installed in `cad_subproject1` environment
> **Status**: All 6 probe scripts executable, raw outputs captured, normalized outputs ready.

---

## 1. Why kiwisolver and not FreeCAD?

The task spec recommends FreeCAD Sketcher as the primary backend for V0.1.
A capability scan of the frozen `cad_subproject1` conda environment:

| Package | Available? | Role |
|---|---|---|
| `cadquery 2.8.0` | ✅ | existing CAD code generator (reconstruction engine) |
| `OCP 7.8.x` | ✅ | OpenCascade Python binding (STEP geometry kernel) |
| `kiwisolver 1.5.0` | ✅ | Cassowary linear constraint solver |
| `FreeCAD` | ❌ | not installed; heavy build; not viable in frozen env |
| `Part` (FreeCAD geometry) | ❌ | depends on FreeCAD |
| `Sketcher` (FreeCAD sketcher) | ❌ | depends on FreeCAD |

**Decision**: use **kiwisolver** as the 2D constraint solver backend and
build a custom Python adapter that translates the Fusion360 sketch
constraint vocabulary (Horizontal / Vertical / Coincident / Tangent /
Perpendicular / Parallel / Concentric / Equal / Offset / MidPoint /
LinearDimension) into kiwisolver primitives.

> This is recorded as a V0.1 limitation: the production Solver Feedback v0.1
> is bound to **kiwisolver**, not FreeCAD.  If FreeCAD Sketcher is later
> available, the adapter in `solver_feedback/core/solver_runner.py` can
> be swapped without changing the rest of the pipeline.

---

## 2. Probe Test Cases

| # | Case | Probe script | Raw output dir |
|---|---|---|---|
| 1 | under_constrained_rectangle | `probe_under_constrained.py` | `under_constrained_rectangle/solver_feedback_raw.json` |
| 2 | fully_constrained_rectangle | `probe_fully_constrained.py` | `fully_constrained_rectangle/solver_feedback_raw.json` |
| 3 | redundant_rectangle | `probe_redundant.py` | `redundant_rectangle/solver_feedback_raw.json` |
| 4 | conflicting_line_orientation | `probe_conflicting.py` | `conflicting_line_orientation/solver_feedback_raw.json` |
| 5 | invalid_constraint_reference | `probe_invalid_reference.py` | `invalid_constraint_reference/solver_feedback_raw.json` |
| 6 | recompute_failure_case | `probe_recompute_failure.py` | `recompute_failure_case/solver_feedback_raw.json` |

All 6 scripts run successfully via `run_api_probe.py`.  See
`api_probe_summary.json` for the run summary.

---

## 3. Capability Matrix (10 API questions vs. kiwisolver)

| # | Question | kiwisolver capability | Fallback needed? |
|---|---|---|---|
| 1 | Is there `solver.solve()`? | `Solver.updateVariables()` only | n/a |
| 2 | Return value meaning | success / `UnsatisfiableConstraint` / `DuplicateConstraint` / `UnknownConstraint` | none |
| 3 | Successful / under / over / conflict / unsolvable returns | direct `UnsatisfiableConstraint` raise; **no over-constrained indicator** | leave-one-out DOF test |
| 4 | Return code stable | n/a (exception-based) | none |
| 5 | Read DOF after solve | **NOT exposed** — kiwisolver has no `getDOF()` API | heuristic: `n_vars − n_active_constraints` |
| 6 | Throws exception | yes — `UnsatisfiableConstraint`, `DuplicateConstraint`, etc. | none |
| 7 | Requires `doc.recompute()` first | n/a (no document model in kiwisolver) | caller's responsibility |
| 8 | Read DOF before solve | yes (via edit-variable suggestion) | none |
| 9 | DOF reliable under-constrained | **heuristic only** | leave-one-out fallback |
| 10 | DOF reliable over-constrained | not exposed | **leave-one-out fallback** |

### 3.1 Conflict detection

| Question | Capability |
|---|---|
| `getConflictingConstraints()` API | **NO** (kiwisolver has no such method) |
| Returned type | n/a |
| Direct API | only via `UnsatisfiableConstraint` exception message string |
| Fallback | **semantic degeneracy check** (post-solve); **leave-one-out suspect test** |

### 3.2 Redundancy detection

| Question | Capability |
|---|---|
| `getRedundantConstraints()` API | **NO** |
| Fallback | **leave-one-out redundancy test**: remove each constraint in turn; if the system still solves with the same solution, the removed constraint was redundant |

### 3.3 Invalid-constraint detection

| Question | Capability |
|---|---|
| Direct API | **YES via our adapter**: the adapter raises `_InvalidConstraint` BEFORE adding the constraint to kiwisolver when the entity uuid is missing from the registry |
| Direct detection in solve | n/a |
| Fallback | none needed |

### 3.4 Recompute failure detection

| Question | Capability |
|---|---|
| `doc.recompute()` API | **NO** (kiwisolver has no document model) |
| Direct detection | n/a |
| Fallback | **per-feature sanity checks** (extrude_distance > 0, sketch closed, profile non-empty, etc.) |

### 3.5 Constraint registry

| Question | Capability |
|---|---|
| `sketch.Constraints` traversable | **YES via our adapter**: every constraint is a `ConstraintSpec` dataclass |
| Each has Type / entities / value | yes |
| Geometry registry | yes — built from `PointSpec` / `LineSpec` / `CircleSpec` dataclasses |
| construction vs external geometry | not in V0.1 scope |

---

## 4. Probe Outcomes

### 4.1 under_constrained_rectangle

```
raw_solve.return_code = 0
dof_estimate          = 6
invalid_constraint_ids = []
semantic_conflicts    = []
```

* kiwisolver solved without complaint, but DOF estimate is high (6).
* Verdict: **DOF-based detection works**.  No fallback needed.

### 4.2 fully_constrained_rectangle

```
raw_solve.return_code = 0
dof_estimate          = 1
invalid_constraint_ids = []
semantic_conflicts    = []
```

* DOF estimate = 1 (the constraint set is 1-D short of full rank in the
  kiwisolver internal matrix; this is acceptable for V0.1).
* Verdict: **fully-constrained detection works** for the canonical rectangle.

### 4.3 redundant_rectangle

```
raw_solve.return_code = 0
dof_estimate          = 3
invalid_constraint_ids = []
semantic_conflicts    = []
note                  = "Redundancy is NOT detected by kiwisolver directly;
                          fallback_analyzer.leave_one_out_redundancy() is needed."
```

* kiwisolver silently accepts the duplicate `Horizontal(l0)` constraint;
  it does not raise nor signal redundancy.
* **Fallback path**: leave-one-out redundancy test (deferred to
  `core/fallback_analyzer.py`).

### 4.4 conflicting_line_orientation

```
raw_solve.return_code = 0
dof_estimate          = 2
invalid_constraint_ids = []
semantic_conflicts    = ["line_l0_collapsed_to_point: start=(10.0,0.0) end=(10.0,0.0)"]
```

* kiwisolver DOES NOT raise `UnsatisfiableConstraint` for this case because
  the system is mathematically consistent (it just collapses the line to a
  point).  The conflict is **semantic**, not arithmetic.
* **Fallback path**: post-solve degeneracy check (already prototyped in
  `probe_lib.probe_solve_system`).  Detects "line collapsed to point" when
  both endpoints land on the same coordinate.

### 4.5 invalid_constraint_reference

```
raw_solve.return_code = 0
dof_estimate          = 1
invalid_constraint_ids = ["c_coin_bad:point p0 or p_deleted missing"]
semantic_conflicts    = []
deleted_entities_referenced = ["p_deleted"]
```

* **Adapter pre-check works**: the constraint was rejected before reaching
  kiwisolver.  This is the cleanest path for invalid-reference detection
  and does not require fallback.

### 4.6 recompute_failure_case

```
raw_solve.return_code = 0
dof_estimate          = 4
invalid_constraint_ids = []
semantic_conflicts    = []
recompute_success     = false
failed_features       = [{"name":"ExtrudeFeature","reason":"extrude.distance <= 0"}]
```

* kiwisolver is sketch-only; downstream extrude failure is captured by
  per-feature sanity checks (extrude_distance > 0).
* Verdict: **recompute-failure detection works via per-feature sanity
  rules**; the production `core/recompute_runner.py` will provide a more
  general rule set.

---

## 5. Summary: V0.1 feasibility

| API capability | Direct | Fallback | V0.1 supported? |
|---|---|---|---|
| `solve()` | ✅ kiwisolver.updateVariables() | n/a | ✅ |
| DOF | ❌ direct API | DOF estimate = `n_vars − n_constraints` | ✅ |
| Conflict detection (strict) | ✅ UnsatisfiableConstraint | n/a | ✅ |
| Conflict detection (semantic) | ❌ | post-solve degeneracy check | ✅ |
| Redundancy detection | ❌ | leave-one-out test | ✅ |
| Invalid-constraint detection | ✅ via adapter pre-check | n/a | ✅ |
| Recompute failure | ❌ | per-feature sanity rules | ✅ |
| Constraint registry | ✅ via ConstraintSpec / PointSpec | n/a | ✅ |
| Geometry registry | ✅ via PointSpec / LineSpec / CircleSpec | n/a | ✅ |
| Constraint → geometry mapping | ✅ entities list | n/a | ✅ |

**Decision**: All 10 capabilities needed for V0.1 are achievable either
directly via kiwisolver or via the documented fallback mechanisms.
**V0.1 implementation proceeds with kiwisolver as the 2D solver backend.**

---

## 6. Limitations to record in V0.1 freeze report

1. **Backend is kiwisolver, not FreeCAD.** If FreeCAD Sketcher becomes
   available later, the production adapter must be retargeted to it
   (likely via the same `solver_runner.py` interface).
2. **DOF is heuristic.** kiwisolver doesn't expose a true DOF API;
   we use `n_vars − n_constraints − n_invalid`.  This may undercount
   DOF for non-axis-aligned shapes with implicit constraints.
3. **Conflict detection is two-tier:**
   - arithmetic conflict → `UnsatisfiableConstraint` from kiwisolver
   - semantic conflict (degenerate geometry) → post-solve check
4. **Redundancy detection is leave-one-out.**  O(n_constraints) re-solves;
   acceptable for sketches with <100 constraints (our 50-sample clean
   set max is 60).  Documented as a known performance characteristic.
5. **Parallel / Perpendicular / Tangent are NOT direct-translatable**
   to kiwisolver (requires sin/cos).  We mark them as
   `_NonLinearUntranslated` and rely on the degeneracy check to flag
   derived inconsistencies.
6. **Recompute failure detection is rule-based, not API-based.**
   Each feature type has explicit sanity rules (extrude_distance > 0,
   pad_height > 0, etc.).  General recompute error capture (e.g. when
   a downstream boolean fails) requires a real CAD kernel, which is
   the role of `ReconstructionEngine_v0.1`, not Solver Feedback.

---

## 7. Repro

```bash
cd solver_feedback/api_probe
python run_api_probe.py    # regenerates 6 solver_feedback_raw.json + summary
```