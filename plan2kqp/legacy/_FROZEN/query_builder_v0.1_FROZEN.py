"""query_builder.py — Build KQP queries deterministically from a PlanReader.

Emission rules (derived from analysis of 50 manual instances):
  R1. body_count:  always
  R2. bbox_size u/v/w:  always (using profile-specific derivation)
  R3. cylinder_radius:  iff ptype in (circle, annulus)
  R4. through_void_count:  iff n_inner_rings > 0
  R5. is_solid:  always
  R6. occt_valid:  always
  R7. symmetric_about_plane:  iff extent_type == 'symmetric'

Tolerance rules (size-bracket based):
  bbox_size u/v (rectangle):
    expected < 60       -> 0.01
    60  <= expected < 600  -> 0.05
    600 <= expected < 1930 -> 0.1
    expected >= 1930    -> 0.5
  bbox_size w (rectangle):
    expected < 3        -> 0.005
    3  <= expected < 100 -> 0.01
    expected >= 100      -> 0.05
  bbox_size (circle/annulus): 0.01 (default); 0.05 iff expected >= 100
  cylinder_radius: 0.01
  body_count / is_solid / occt_valid: no tolerance
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

# Make sibling modules importable when run as script
sys.path.insert(0, str(Path(__file__).parent))
from plan_reader import PlanReader
from source_mapper import SourceMapper as SM
from feedback_builder import FeedbackBuilder as FB


# ----- Tolerance rules (size-bracket) -----
def _tol_bbox_uv_rectangle(expected: float) -> float:
    if expected < 60:
        return 0.01
    if expected < 600:
        return 0.05
    if expected < 1930:
        return 0.1
    return 0.5


def _tol_bbox_w_rectangle(expected: float) -> float:
    if expected < 3:
        return 0.005
    if expected < 100:
        return 0.01
    return 0.05


def _tol_bbox_circle_or_annulus(expected: float) -> float:
    return 0.05 if expected >= 100 else 0.01


# ----- Query construction helpers -----
def _q_body_count(pr: PlanReader) -> dict:
    return {
        "id": "q_body_count",
        "category": "A_topology",
        "intent": "body_count",
        "expected": pr.body_count,
        "source_field": SM.body_count(),
        "feedback_enabled": True,
        "feedback_template": FB.body_count(pr.body_count),
    }


def _q_bbox(pr: PlanReader, axis: str, expected: float) -> dict:
    ptype = pr.ptype
    # Determine source_field & tolerance
    if axis == "u":
        if ptype == "rectangle":
            sf = SM.length_u()
            tol = _tol_bbox_uv_rectangle(expected)
            extra = ""
        elif ptype == "rectangular_frame":
            sf = SM.outer_length_u()
            tol = _tol_bbox_uv_rectangle(expected)
            extra = ""
        elif ptype == "circle":
            r = pr.dim_radius()
            sf = SM.computed(SM.radius(), "2*r")
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (2*r)"
        elif ptype == "annulus":
            ro = pr.dim_outer_radius()
            sf = SM.computed(SM.outer_radius(), "2*r")
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (2*r)"
        elif ptype == "stadium":
            sf = SM.computed(
                f"{SM.straight_length()} + {SM.radius()}", "straight + 2*r"
            )
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (=straight+2*r)"
        else:
            return None
    elif axis == "v":
        if ptype == "rectangle":
            sf = SM.width_v()
            tol = _tol_bbox_uv_rectangle(expected)
            extra = ""
        elif ptype == "rectangular_frame":
            sf = SM.outer_width_v()
            tol = _tol_bbox_uv_rectangle(expected)
            extra = ""
        elif ptype == "circle":
            r = pr.dim_radius()
            sf = SM.computed(SM.radius(), "2*r")
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (2*r)"
        elif ptype == "annulus":
            ro = pr.dim_outer_radius()
            sf = SM.computed(SM.outer_radius(), "2*r")
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (2*r)"
        elif ptype == "stadium":
            r = pr.dim_radius()
            sf = SM.computed(SM.radius(), "2*r")
            tol = _tol_bbox_circle_or_annulus(expected)
            extra = " (=2*r)"
        else:
            return None
    elif axis == "w":
        sf = SM.extrude_distance()
        if ptype == "rectangle":
            tol = _tol_bbox_w_rectangle(expected)
        elif ptype in ("circle", "annulus", "stadium"):
            tol = 0.01
        elif ptype == "rectangular_frame":
            tol = _tol_bbox_w_rectangle(expected)
        else:
            tol = 0.01
        # Extrude-direction extras (negative, symmetric, degenerate)
        ext = pr.extrude
        extra = ""
        if ext["direction"] == "-w":
            extra = " (negative extrude)"
        elif ext["extent_type"] == "symmetric":
            extra = " (symmetric extrude, body straddles plane)"
        elif ext["extent_type"] == "degenerate_two_side":
            extra = " (degenerate two_side, extent_two=0)"
    else:
        return None

    return {
        "id": f"q_bbox_{axis}",
        "category": "B_geometry_dim",
        "intent": "bbox_size",
        "axis": axis,
        "expected": round(expected, 6),
        "tolerance": tol,
        "source_field": sf,
        "feedback_enabled": True,
        "feedback_template": FB.bbox_size(axis, round(expected, 6), extra=extra),
    }


def _q_cylinder_radius(pr: PlanReader, role: str, expected: float) -> dict:
    """Emit a cylinder_radius query.

    role: "outer" | "inner" | "" (empty = plain circle, no selector).
    """
    if role == "outer":
        sf = SM.outer_radius()
        role_str = "outer"
    elif role == "inner":
        sf = SM.inner_radius()
        role_str = "inner"
    elif role == "":
        # plain circle: no selector, single radius
        sf = SM.radius()
        role_str = ""
    else:
        return None
    q = {
        "id": f"q_{role_str}_radius" if role_str else "q_radius",
        "category": "B_geometry_dim",
        "intent": "cylinder_radius",
        "expected": round(expected, 6),
        "tolerance": 0.01,
        "source_field": sf,
        "feedback_enabled": True,
        "feedback_template": FB.cylinder_radius(round(expected, 6), role=role_str) if role_str else FB.cylinder_radius(round(expected, 6)),
    }
    if role_str:
        q["params"] = {"selector": role_str}
    return q


def _q_void_count(pr: PlanReader) -> dict:
    n = pr.n_inner_rings
    return {
        "id": "q_void_count",
        "category": "C_feature",
        "intent": "through_void_count",
        "expected": n,
        "tolerance": 0,
        "source_field": SM.void_count(),
        "feedback_enabled": True,
        "feedback_template": FB.through_void_count(n),
    }


def _q_health_is_solid() -> dict:
    return {
        "id": "q_is_solid",
        "category": "D_health",
        "intent": "is_solid",
        "expected": True,
        "source_field": SM.implicit("valid extrude implies solid"),
        "feedback_enabled": True,
        "feedback_template": FB.is_solid(),
    }


def _q_health_occt_valid() -> dict:
    return {
        "id": "q_occt_valid",
        "category": "D_health",
        "intent": "occt_valid",
        "expected": True,
        "source_field": SM.implicit(),
        "feedback_enabled": True,
        "feedback_template": FB.occt_valid(),
    }


def _q_health_symmetric() -> dict:
    return {
        "id": "q_symmetric",
        "category": "D_health",
        "intent": "symmetric_about_plane",
        "expected": True,
        "tolerance": None,
        "source_field": SM.implicit("design_plan specifies symmetric extrude"),
        "feedback_enabled": True,
        "feedback_template": FB.symmetric_about_plane(),
    }


# ----- Main builder: applies emission rules R1-R7 -----
def build_queries(pr: PlanReader) -> list[dict]:
    """Build the full KQP query list from a PlanReader.

    Order: body_count, then bbox_size (u, v, w), then cylinder_radius (circle/annulus),
    then void_count, then is_solid, then occt_valid, then symmetric_about_plane.
    """
    queries: list[dict] = []

    # R1: body_count
    queries.append(_q_body_count(pr))

    # R2: bbox_size u/v/w
    bu = pr.bbox_u_size()
    bv = pr.bbox_v_size()
    bw = pr.bbox_w_size()
    for axis, val in (("u", bu), ("v", bv), ("w", bw)):
        if val is None:
            continue
        q = _q_bbox(pr, axis, val)
        if q is not None:
            queries.append(q)

    # R3: cylinder_radius
    ptype = pr.ptype
    if ptype == "circle":
        r = pr.dim_radius()
        if r is not None:
            queries.append(_q_cylinder_radius(pr, "", r))  # role="" for circle (no selector)
    elif ptype == "annulus":
        ro = pr.dim_outer_radius()
        ri = pr.dim_inner_radius()
        if ro is not None:
            queries.append(_q_cylinder_radius(pr, "outer", ro))
        if ri is not None:
            queries.append(_q_cylinder_radius(pr, "inner", ri))

    # R4: through_void_count
    if pr.n_inner_rings > 0:
        queries.append(_q_void_count(pr))

    # R5, R6: is_solid, occt_valid
    queries.append(_q_health_is_solid())
    queries.append(_q_health_occt_valid())

    # R7: symmetric_about_plane
    if pr.is_symmetric:
        queries.append(_q_health_symmetric())

    return queries
