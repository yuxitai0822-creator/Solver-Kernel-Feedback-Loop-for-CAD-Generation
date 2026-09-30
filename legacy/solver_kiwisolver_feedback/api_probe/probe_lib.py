"""probe_lib.py — Shared probe library for solver_feedback api_probe tests.

Since FreeCAD Sketcher is NOT available in this environment, we use **kiwisolver**
as the 2D constraint-solver backend.  kiwisolver is a Cassowary-based solver
that ships with kivy.  This module:

  1. Provides a tiny abstract constraint system (variables + simple constraints)
     that maps to kiwisolver's primitives.
  2. Maps each of the 10 Fusion360 sketch constraint types we support to a
     linear (or simple non-linear) kiwisolver expression.
  3. Exposes a `probe_solve_system()` helper that returns raw solve outcome,
     DOF estimate, conflict set, redundant set, and invalid-constraint set.

This is *not* the production solver_feedback pipeline (that lives in
`solver_feedback/core/`).  This module is only used to verify the backend's
capability BEFORE building the production modules.
"""
from __future__ import annotations

import sys
from typing import Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Variable naming convention
# ---------------------------------------------------------------------------
# A 2D point has two variables: point_<uuid>.x, point_<uuid>.y
# A 2D line has two endpoint points: line_<uuid>.start (point uuid),
#                                    line_<uuid>.end (point uuid).
# A 2D circle has center point + radius: circle_<uuid>.cx, circle_<uuid>.cy,
#                                        circle_<uuid>.r.
# Constraint variables are exposed by name in the kiwisolver system.

def point_var(prefix: str, uuid: str, axis: str) -> str:
    return f"{prefix}_{uuid}.{axis}"


# ---------------------------------------------------------------------------
# Geometry / constraint spec types (Python dict, then mapped to kiwisolver)
# ---------------------------------------------------------------------------

@dataclass
class PointSpec:
    uuid: str
    x: float = 0.0
    y: float = 0.0


@dataclass
class CircleSpec:
    uuid: str
    cx_uuid: str | None = None  # if None, use inline cx/cy
    cy_uuid: str | None = None
    cx: float = 0.0
    cy: float = 0.0
    radius: float = 1.0


@dataclass
class LineSpec:
    uuid: str
    start_uuid: str
    end_uuid: str


@dataclass
class ConstraintSpec:
    """Fusion360-style constraint spec."""
    id: str
    type: str   # 'Horizontal', 'Vertical', 'Coincident', 'Tangent',
                # 'Perpendicular', 'Parallel', 'Concentric', 'Equal',
                # 'Offset', 'MidPoint', 'DiameterDimension',
                # 'LinearDimension'
    entities: list[str] = field(default_factory=list)
    value: float | None = None  # for Offset / Dimension


# ---------------------------------------------------------------------------
# Build kiwisolver system from geometry + constraint specs
# ---------------------------------------------------------------------------

def build_kiwi_system(points: dict[str, PointSpec],
                        lines: dict[str, LineSpec],
                        circles: dict[str, CircleSpec],
                        constraints: list[ConstraintSpec],
                        deleted_entities: set[str] | None = None
                        ) -> tuple[Any, dict[str, Any], list[str]]:
    """Return (Solver, var_dict, invalid_constraint_ids).

    var_dict: name -> kiwisolver.Variable
    invalid_constraint_ids: list of constraint ids whose entity references
        include a uuid in `deleted_entities` (or that fails to map).
    """
    import kiwisolver as ks

    solver = ks.Solver()
    var: dict[str, Any] = {}
    invalid: list[str] = []

    # 1. Register variables with their initial values as suggestion.
    for p in points.values():
        var[point_var("pt", p.uuid, "x")] = ks.Variable(f"pt_{p.uuid}.x")
        var[point_var("pt", p.uuid, "y")] = ks.Variable(f"pt_{p.uuid}.y")
        solver.addEditVariable(var[point_var("pt", p.uuid, "x")],  ks.strength.weak)
        solver.addEditVariable(var[point_var("pt", p.uuid, "y")],  ks.strength.weak)
        solver.suggestValue(var[point_var("pt", p.uuid, "x")], p.x)
        solver.suggestValue(var[point_var("pt", p.uuid, "y")], p.y)

    for ln in lines.values():
        if ln.start_uuid not in points or ln.end_uuid not in points:
            invalid.append(f"line_{ln.uuid}_missing_endpoint")
        # No new variables for lines (they are derived from endpoint points).

    for c in circles.values():
        var[f"cir_{c.uuid}.cx"] = ks.Variable(f"cir_{c.uuid}.cx")
        var[f"cir_{c.uuid}.cy"] = ks.Variable(f"cir_{c.uuid}.cy")
        var[f"cir_{c.uuid}.r"]  = ks.Variable(f"cir_{c.uuid}.r")
        solver.addEditVariable(var[f"cir_{c.uuid}.cx"], ks.strength.weak)
        solver.addEditVariable(var[f"cir_{c.uuid}.cy"], ks.strength.weak)
        solver.addEditVariable(var[f"cir_{c.uuid}.r"],  ks.strength.weak)
        solver.suggestValue(var[f"cir_{c.uuid}.cx"], c.cx)
        solver.suggestValue(var[f"cir_{c.uuid}.cy"], c.cy)
        solver.suggestValue(var[f"cir_{c.uuid}.r"],  c.radius)

    # 2. Translate constraints.  A constraint may produce multiple
    # kiwisolver.Constraint objects (e.g. concentric = 2 equations).
    for c in constraints:
        try:
            kcs = _translate_constraint(c, points, lines, circles, var)
        except _InvalidConstraint as e:
            invalid.append(f"{c.id}:{e}")
            continue
        if kcs is None:
            invalid.append(f"{c.id}:untranslatable")
            continue
        if not isinstance(kcs, list):
            kcs = [kcs]
        for kc in kcs:
            try:
                solver.addConstraint(kc)
            except Exception as e:
                invalid.append(f"{c.id}:add_failed:{type(e).__name__}")

    return solver, var, invalid


def _translate_constraint(c: ConstraintSpec, points, lines, circles, var):
    """Return a kiwisolver.Constraint or a list of them, or raise _InvalidConstraint."""
    t = c.type
    ents = c.entities

    if t == "Horizontal":
        ln = lines.get(ents[0])
        if ln is None:
            raise _InvalidConstraint(f"line {ents[0]} missing")
        ys = var[point_var("pt", ln.start_uuid, "y")]
        ye = var[point_var("pt", ln.end_uuid, "y")]
        return ys == ye

    if t == "Vertical":
        ln = lines.get(ents[0])
        if ln is None:
            raise _InvalidConstraint(f"line {ents[0]} missing")
        xs = var[point_var("pt", ln.start_uuid, "x")]
        xe = var[point_var("pt", ln.end_uuid, "x")]
        return xs == xe

    if t == "Coincident":
        a, b = ents
        pa, pb = points.get(a), points.get(b)
        if pa is None or pb is None:
            raise _InvalidConstraint(f"point {a} or {b} missing")
        xa = var[point_var("pt", a, "x")]
        ya = var[point_var("pt", a, "y")]
        xb = var[point_var("pt", b, "x")]
        yb = var[point_var("pt", b, "y")]
        return [xa == xb, ya == yb]

    if t == "Equal":
        la, lb = lines.get(ents[0]), lines.get(ents[1])
        if la is None or lb is None:
            raise _InvalidConstraint(f"line {ents[0]} or {ents[1]} missing")
        len_a = ((var[point_var("pt", la.start_uuid, "x")]
                   - var[point_var("pt", la.end_uuid, "x")]) ** 2
                  + (var[point_var("pt", la.start_uuid, "y")]
                       - var[point_var("pt", la.end_uuid, "y")]) ** 2)
        len_b = ((var[point_var("pt", lb.start_uuid, "x")]
                   - var[point_var("pt", lb.end_uuid, "x")]) ** 2
                  + (var[point_var("pt", lb.start_uuid, "y")]
                       - var[point_var("pt", lb.end_uuid, "y")]) ** 2)
        return len_a == len_b

    if t == "Concentric":
        ca, cb = circles.get(ents[0]), circles.get(ents[1])
        if ca is None or cb is None:
            raise _InvalidConstraint(f"circle {ents[0]} or {ents[1]} missing")
        return [
            var[f"cir_{ca.uuid}.cx"] == var[f"cir_{cb.uuid}.cx"],
            var[f"cir_{ca.uuid}.cy"] == var[f"cir_{cb.uuid}.cy"],
        ]

    if t == "MidPoint":
        p_uuid = ents[0]
        ln = lines.get(ents[1])
        if ln is None or p_uuid not in points:
            raise _InvalidConstraint(f"midpoint missing entity")
        xm = var[point_var("pt", p_uuid, "x")]
        ym = var[point_var("pt", p_uuid, "y")]
        xs = var[point_var("pt", ln.start_uuid, "x")]
        ys = var[point_var("pt", ln.start_uuid, "y")]
        xe = var[point_var("pt", ln.end_uuid, "x")]
        ye = var[point_var("pt", ln.end_uuid, "y")]
        return [(xs + xe) == 2 * xm, (ys + ye) == 2 * ym]

    if t == "Offset":
        # entities = [point_a, point_b], value = signed distance along axis.
        # The caller may pass axis='x' (default) or axis='y' via entities[2].
        a, b = ents[0], ents[1]
        axis = "x"
        if len(ents) > 2 and ents[2] in ("x", "y"):
            axis = ents[2]
        if a not in points or b not in points:
            raise _InvalidConstraint(f"offset missing point {a} or {b}")
        if c.value is None:
            raise _InvalidConstraint("offset requires value")
        pa = var[point_var("pt", a, axis)]
        pb = var[point_var("pt", b, axis)]
        return (pb - pa) == c.value

    if t in ("Parallel", "Perpendicular", "Tangent"):
        return _NonLinearUntranslated(c)

    raise _InvalidConstraint(f"unsupported constraint type {t}")


class _InvalidConstraint(Exception):
    pass


class _NonLinearUntranslated:
    """Marker returned for constraints kiwisolver cannot directly translate."""

    def __init__(self, constraint_spec: ConstraintSpec):
        self.constraint_spec = constraint_spec


# ---------------------------------------------------------------------------
# Solver raw probe
# ---------------------------------------------------------------------------

def probe_solve_system(solver, var, invalid_constraint_ids,
                         all_constraints, deleted_entities,
                         degeneracy_check: dict | None = None
                         ) -> dict:
    """Run the system through kiwisolver and capture raw diagnostics.

    `degeneracy_check` is an optional dict that lets the caller supply
    semantic post-conditions that kiwisolver cannot express directly.
    For example:
        degeneracy_check = {
            "non_degenerate_line_lengths": {
                "l0": ("p0", "p1"),   # line uuid -> (start_pt, end_pt)
                ...
            },
            "non_degenerate_circle_radii": {
                "cir_0": 5.0,         # circle uuid -> suggested radius
                ...
            },
        }
    After solve, the analyzer checks: if a line's start point == end point
    (within tolerance) AND a Horizontal+Vertical pair constrains the line,
    the result is a semantic conflict (line collapsed to a point).
    """
    import kiwisolver as ks

    raw_solve = {"return_code": 0, "exception": None, "message": ""}
    var_values = {}
    try:
        solver.updateVariables()
        raw_solve["return_code"] = 0
        raw_solve["message"] = "kiwisolver updateVariables succeeded"
    except ks.exceptions.UnsatisfiableConstraint as e:
        raw_solve["return_code"] = -1
        raw_solve["exception"] = "UnsatisfiableConstraint"
        raw_solve["message"] = str(e)
    except Exception as e:
        raw_solve["return_code"] = -2
        raw_solve["exception"] = type(e).__name__
        raw_solve["message"] = str(e)

    for k, v in var.items():
        try:
            var_values[k] = v.value()
        except Exception:
            var_values[k] = None

    n_vars = len(var)
    dof = max(0, n_vars - len(all_constraints) - len(invalid_constraint_ids))

    # Post-solve degeneracy check (fallback_analyzer counterpart).
    semantic_conflicts = []
    if degeneracy_check and raw_solve["return_code"] == 0:
        tol = 1e-6
        for ln_uuid, (start_pt, end_pt) in degeneracy_check.get(
                "non_degenerate_line_lengths", {}).items():
            xs = var_values.get(point_var("pt", start_pt, "x"))
            ys = var_values.get(point_var("pt", start_pt, "y"))
            xe = var_values.get(point_var("pt", end_pt, "x"))
            ye = var_values.get(point_var("pt", end_pt, "y"))
            if None in (xs, ys, xe, ye):
                continue
            if abs(xs - xe) < tol and abs(ys - ye) < tol:
                semantic_conflicts.append(
                    f"line_{ln_uuid}_collapsed_to_point: "
                    f"start=({xs},{ys}) end=({xe},{ye})")
        for cir_uuid, _ in degeneracy_check.get(
                "non_degenerate_circle_radii", {}).items():
            r = var_values.get(f"cir_{cir_uuid}.r")
            if r is not None and abs(r) < tol:
                semantic_conflicts.append(f"circle_{cir_uuid}_degenerate_radius={r}")

    return {
        "raw_solve": raw_solve,
        "var_values": var_values,
        "dof_estimate": dof,
        "invalid_constraint_ids": invalid_constraint_ids,
        "deleted_entities_referenced": list(deleted_entities),
        "semantic_conflicts": semantic_conflicts,
        "method": "kiwisolver+python_adapter+degeneracy_check",
    }