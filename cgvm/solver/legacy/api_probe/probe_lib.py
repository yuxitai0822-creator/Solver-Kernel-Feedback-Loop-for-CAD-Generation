"""probe_lib.py — FreeCAD Sketcher probe library.

Builds a minimal FreeCAD sketch + document from an abstract spec
(lines, points, constraints), then probes all required Sketcher APIs
and returns a raw diagnostic dict.

FreeCAD APIs available (verified 2026-07-08 in `freecad_sketcher` env):
  * sketch.solve()                        — return code 0/-1/-2/-3/-4/-5
  * sketch.DoF                            — int (degrees of freedom)
  * sketch.RedundantConstraints           — list of constraint indices
  * sketch.ConflictingConstraints         — list of constraint indices
  * sketch.PartiallyRedundantConstraints  — list of constraint indices
  * sketch.MalformedConstraints           — list of constraint indices
  * sketch.MissingVerticalHorizontalConstraints
  * sketch.MissingLineEqualityConstraints
  * sketch.MissingPointOnPointConstraints
  * sketch.MissingRadiusConstraints
  * sketch.Constraints                    — list of constraint objects
  * sketch.Geometry                       — list of geometry objects
  * sketch.GeometryCount                  — int
  * sketch.ConstraintCount                — int
  * doc.recompute()                       — recompute; raises on failure

All 6 spec test cases use these direct APIs — no fallback analyzer is
needed because FreeCAD exposes the underlying solver state directly.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

def setup_freecad_env() -> None:
    """Add FreeCAD Library/bin to sys.path & PATH.  Idempotent."""
    freecad_dir = r'D:/Anaconda/envs/freecad_sketcher/Library'
    bin_dir = os.path.join(freecad_dir, 'bin')
    lib_dir = os.path.join(freecad_dir, 'lib')
    if bin_dir not in sys.path:
        sys.path.insert(0, bin_dir)
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    if bin_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = bin_dir + ';' + os.environ.get('PATH', '')


def get_modules():
    setup_freecad_env()
    import FreeCAD as app  # type: ignore
    import Part  # type: ignore
    import Sketcher  # type: ignore
    return app, Part, Sketcher


# ---------------------------------------------------------------------------
# Abstract spec (Python-only; not dependent on FreeCAD at import time)
# ---------------------------------------------------------------------------

@dataclass
class LineSpec:
    uuid: str
    start: tuple[float, float]
    end: tuple[float, float]


@dataclass
class CircleSpec:
    """A FreeCAD Sketcher circle (B-006 fix).

    (cx, cy) is the centre in mm; radius in mm.  Use ``Concentric`` /
    ``Radius`` constraints to fully constrain an annulus (two circles).
    """
    uuid: str
    center: tuple[float, float]
    radius: float


@dataclass
class ConstraintSpec:
    """A FreeCAD Sketcher-style constraint spec."""
    type: str      # 'Horizontal' | 'Vertical' | 'Coincident' | 'Equal' |
                   # 'DistanceX' | 'DistanceY' | 'Angle' | 'Perpendicular' |
                   # 'Parallel' | 'Symmetric' | 'Radius' | 'Diameter' |
                   # 'Concentric'  (B-006 fix)
    params: tuple[Any, ...] = ()
    """Constructor arguments AFTER (geoId1, posId1).
    E.g. for Coincident(a, b): params = (geoId2, posId2)
    For Concentric(a, b): params = (geoId2,)
    For Radius(a, value): params = (value,)
    """
    target_geo: int = -1  # for Orientation constraints (Horizontal/Vertical): the geo id
    target_pos: int = -1  # for pos-tagged constraints


@dataclass
class PadSpec:
    """A downstream Pad feature to test recompute."""
    length: float = 10.0


# ---------------------------------------------------------------------------
# Build sketch from spec
# ---------------------------------------------------------------------------

def build_sketch(spec: dict) -> dict:
    """Build a sketch in a fresh document and apply constraints.

    spec = {
      'lines': [LineSpec(...), ...],
      'circles': [CircleSpec(...), ...],   # B-006 fix:  added
      'constraints': [ConstraintSpec(...), ...],
      'pad': PadSpec(...) | None,        # optional downstream feature
    }

    Returns:
        {'doc': doc, 'sketch': sketch, 'pad': pad_or_None, 'geometry_ids': [int]}
    """
    app, Part, Sketcher = get_modules()
    doc = app.newDocument()
    sketch = doc.addObject('Sketcher::SketchObject', 'TestSketch')
    geo_ids: list[int] = []
    for ln in spec.get('lines', []):
        p1 = app.Vector(ln.start[0], ln.start[1], 0.0)
        p2 = app.Vector(ln.end[0], ln.end[1], 0.0)
        gid = sketch.addGeometry(Part.LineSegment(p1, p2), False)
        geo_ids.append(gid)
    for ci in spec.get('circles', []):                       # B-006 fix
        cx, cy = ci.center
        # Part.Circle requires Vector objects (not tuples) for centre & axis
        geom = Part.Circle(app.Vector(cx, cy, 0.0),
                             app.Vector(0, 0, 1),
                             ci.radius)
        gid = sketch.addGeometry(geom, False)
        geo_ids.append(gid)
    for c in spec.get('constraints', []):
        _add_constraint(sketch, c, geo_ids, Sketcher)

    # Optional Pad feature to test recompute.
    pad = None
    if 'pad' in spec and spec['pad']:
        pad = doc.addObject('PartDesign::Pad', 'Pad')
        pad.Profile = sketch
        pad.Length = spec['pad'].length

    return {'doc': doc, 'sketch': sketch, 'pad': pad,
              'geometry_ids': geo_ids,
              'num_lines': len(spec.get('lines', [])),
              'num_circles': len(spec.get('circles', []))}


def _add_constraint(sketch, c: ConstraintSpec, geo_ids: list[int],
                      Sketcher) -> int:
    """Add one constraint to the sketch."""
    if c.type == 'Horizontal':
        return sketch.addConstraint(Sketcher.Constraint('Horizontal', c.target_geo))
    if c.type == 'Vertical':
        return sketch.addConstraint(Sketcher.Constraint('Vertical', c.target_geo))
    if c.type == 'Coincident':
        geoId1, posId1, geoId2, posId2 = c.target_geo, c.target_pos, c.params[0], c.params[1]
        return sketch.addConstraint(
            Sketcher.Constraint('Coincident', geoId1, posId1, geoId2, posId2))
    if c.type == 'DistanceX':
        geoId, posId, value = c.target_geo, c.target_pos, c.params[0]
        return sketch.addConstraint(
            Sketcher.Constraint('DistanceX', geoId, posId, value))
    if c.type == 'DistanceY':
        geoId, posId, value = c.target_geo, c.target_pos, c.params[0]
        return sketch.addConstraint(
            Sketcher.Constraint('DistanceY', geoId, posId, value))
    if c.type == 'Angle':
        geoId1, geoId2, value = c.params[0], c.params[1], c.params[2]
        return sketch.addConstraint(
            Sketcher.Constraint('Angle', geoId1, geoId2, value,
                                  Sketcher.AngleType.AnglePlain))
    if c.type == 'Perpendicular':
        return sketch.addConstraint(
            Sketcher.Constraint('Perpendicular', c.params[0], c.params[1]))
    if c.type == 'Parallel':
        return sketch.addConstraint(
            Sketcher.Constraint('Parallel', c.params[0], c.params[1]))
    if c.type == 'Radius':
        # Sketcher.Constraint('Radius', geoId, value)
        return sketch.addConstraint(
            Sketcher.Constraint('Radius', c.target_geo, c.params[0]))
    if c.type == 'Diameter':
        return sketch.addConstraint(
            Sketcher.Constraint('Diameter', c.target_geo, c.params[0]))
    if c.type == 'Concentric':                      # B-006 fix
        # The current FreeCAD build's Sketcher.Constraint does NOT accept
        # the 'Concentric' name in this binding (it returns "Constraint
        # type and index" as the only valid signature).  We achieve the
        # same semantics by Coincident-locking the two circle centres
        # (pos index 3 is the centre of a circle in Sketcher).
        return sketch.addConstraint(
            Sketcher.Constraint('Coincident', c.target_geo, 3, c.params[0], 3))
    raise ValueError(f"unsupported constraint type {c.type}")


# ---------------------------------------------------------------------------
# Probe solver state via FreeCAD's direct APIs
# ---------------------------------------------------------------------------

# Solve() return code → status name mapping (per FreeCAD docs)
SOLVE_RETURN_CODES = {
    0: "success",
    -1: "solver_error",
    -2: "redundant",
    -3: "conflicting",
    -4: "over_constrained",
    -5: "malformed",
}


def probe_sketch_state(doc, sketch, pad=None,
                         run_recompute: bool = True) -> dict:
    """Run FreeCAD's solve() and recompute() then capture raw state."""
    rc = sketch.solve()
    state = {
        "solve_return_code": int(rc),
        "solve_status_str": SOLVE_RETURN_CODES.get(rc, f"unknown_{rc}"),
        "dof": int(sketch.DoF),
        "redundant_constraints": list(sketch.RedundantConstraints or []),
        "conflicting_constraints": list(sketch.ConflictingConstraints or []),
        "partially_redundant_constraints":
            list(sketch.PartiallyRedundantConstraints or []),
        "malformed_constraints": list(sketch.MalformedConstraints or []),
        "missing_vertical_horizontal_constraints":
            list(getattr(sketch, "MissingVerticalHorizontalConstraints", None) or []),
        "missing_line_equality_constraints":
            list(getattr(sketch, "MissingLineEqualityConstraints", None) or []),
        "missing_point_on_point_constraints":
            list(getattr(sketch, "MissingPointOnPointConstraints", None) or []),
        "missing_radius_constraints":
            list(getattr(sketch, "MissingRadiusConstraints", None) or []),
        "constraint_count": int(sketch.ConstraintCount),
        "geometry_count": int(sketch.GeometryCount),
        "constraints_summary": _summarize_constraints(sketch),
    }

    if run_recompute:
        try:
            doc.recompute()
            state["recompute_success"] = True
            state["recompute_exception"] = None
        except Exception as e:
            state["recompute_success"] = False
            state["recompute_exception"] = f"{type(e).__name__}: {e}"

    # Capture pad Invalid state if a pad is present.
    if pad is not None:
        try:
            pad_state = list(pad.State)  # e.g. ['Touched', 'Invalid']
            state["pad_state"] = pad_state
            state["pad_invalid"] = ('Invalid' in pad_state)
            state["pad_length"] = float(pad.Length)
        except Exception as e:
            state["pad_state_error"] = f"{type(e).__name__}: {e}"

    return state


def _summarize_constraints(sketch) -> list[dict]:
    """Per-constraint description (id, type, value, GeoId pair)."""
    out = []
    for i, c in enumerate(sketch.Constraints):
        d = {"index": i, "type": str(c.Type),
              "first": c.First, "second": getattr(c, 'Second', None),
              "third": getattr(c, 'Third', None)}
        try:
            d["value"] = float(c.Value) if hasattr(c, 'Value') else None
        except Exception:
            d["value"] = None
        out.append(d)
    return out