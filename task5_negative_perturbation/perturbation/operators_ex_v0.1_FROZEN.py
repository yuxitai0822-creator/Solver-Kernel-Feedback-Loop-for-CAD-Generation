"""operators_ex.py — EX1, EX2 execution-level perturbation operators.

Per ``doc/execution_level_perturbation_plan_v0.1.md``.  These perturb
the sketch's *placement* and *coordinate axes* — properties the
Fusion360 Gallery DesignPlan does NOT carry — so M0 (Design-Plan
self-diagnosis only) cannot detect them, while the KQP execution can.

The Design Plan is **never modified** by EX perturbations: only the
``entities.Sketch.reference_plane`` / ``transform`` / ``points`` fields
change.
"""
from __future__ import annotations

import copy
import math
import random
from typing import Any


# ---------------------------------------------------------------------------
# Vector3D helpers (Fusion360 Gallery schema)
# ---------------------------------------------------------------------------

def _to_vector3(v) -> list[float]:
    """Normalize Vector3D dict / list / nested shape → flat [x, y, z] floats."""
    if isinstance(v, list):
        return [float(c) for c in v]
    if isinstance(v, dict):
        if "x" in v and "y" in v and "z" in v:
            return [float(v["x"]), float(v["y"]), float(v["z"])]
        if all(str(i) in v for i in range(3)):
            return [float(v[str(i)]) for i in range(3)]
    raise ValueError(f"unrecognised vector shape: {v!r}")


def _v3(xyz, length: float = 1.0) -> dict:
    """Build a Fusion360 Vector3D dict from a flat [x, y, z] list."""
    return {"type": "Vector3D", "x": float(xyz[0]),
              "y": float(xyz[1]), "z": float(xyz[2]),
              "length": float(length)}


def _v3_v(v, length: float = 1.0) -> dict:
    """Build a Vector3D dict from an existing list / dict / Vector3D."""
    if isinstance(v, dict) and v.get("type") == "Vector3D":
        return v
    return _v3(_to_vector3(v), length)


# The 3 principal plane normals, as UnitVector coordinates (length 1)
PRINCIPAL_PLANES = {
    "XY": ([0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]),
    "XZ": ([0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
    "YZ": ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
}


def _normal_to_plane(normal) -> str:
    n = _to_vector3(normal)
    n_mag = math.sqrt(sum(c * c for c in n))
    if n_mag < 1e-9:
        raise ValueError(f"normal vector magnitude < eps: {n}")
    n = [c / n_mag for c in n]
    axis_index = max(range(3), key=lambda i: abs(n[i]))
    return {0: "YZ", 1: "XZ", 2: "XY"}[axis_index]


def _get_current_plane(sketch: dict) -> tuple[str, list[float], list[float], list[float]]:
    rp = sketch.get("reference_plane") or {}
    plane = rp.get("plane") or {}
    normal_raw = plane.get("normal")
    if normal_raw is None:
        z = (sketch.get("transform") or {}).get("z_axis")
        if z is not None:
            normal_raw = z
    normal = _to_vector3(normal_raw) if normal_raw is not None else [0.0, 0.0, 1.0]
    x_raw = (plane.get("x_axis")
                or (sketch.get("transform") or {}).get("x_axis")
                or [1.0, 0.0, 0.0])
    y_raw = (plane.get("y_axis")
                or (sketch.get("transform") or {}).get("y_axis")
                or [0.0, 1.0, 0.0])
    x_axis = _to_vector3(x_raw)
    y_axis = _to_vector3(y_raw)
    return _normal_to_plane(normal), normal, x_axis, y_axis


def _find_sketch(history: dict) -> dict | None:
    for _eid, e in history.get("entities", {}).items():
        if e.get("type") == "Sketch":
            return e
    return None


def _select_swap_target(current_plane: str, history: dict) -> str:
    alternatives = [p for p in ("XY", "XZ", "YZ") if p != current_plane]
    return alternatives[0]


# ---------------------------------------------------------------------------
# EX1 — Sketch Plane Swap
# ---------------------------------------------------------------------------

def op_EX1_sketch_plane_swap(history: dict, design_plan: dict,
                                  *, target_plane: str | None = None,
                                  random_seed: int | None = None
                                  ) -> tuple[dict, dict, dict]:
    """Swap the sketch's reference plane to a different principal plane.

    The DP-blind property: bbox field in the DP says ``{u: 80, v: 50,
    w: 20}`` but does not say which world axis u/v/w correspond to.
    After EX1 the body is built along a different world axis; the
    *numbers* in DP still match the (old-frame) bbox but the KQP
    per-axis projection no longer aligns.
    """
    h = copy.deepcopy(history)
    sketch = _find_sketch(h)
    if sketch is None:
        raise ValueError("no Sketch entity in history")

    current_plane, _normal, _x, _y = _get_current_plane(sketch)
    if target_plane is None:
        target_plane = _select_swap_target(current_plane, h)

    if target_plane == current_plane:
        raise ValueError(f"target_plane {target_plane!r} == current_plane")

    new_normal, new_x, new_y = PRINCIPAL_PLANES[target_plane]
    sketch.setdefault("reference_plane", {})
    old_plane = sketch["reference_plane"].get("plane", {})
    # Preserve plane.origin (the plane's reference point) and any other
    # fields the reconstruction engine reads (type, u_direction/v_direction).
    # The reconstruction engine reads:
    #   plane.origin  (translation of the plane)
    #   plane.normal  (the plane's normal)
    #   plane.u_direction / plane.v_direction  (in-plane axes)
    # We rewrite normal + u_direction/v_direction; we keep origin.
    new_plane = dict(old_plane)  # start with original to preserve origin
    new_plane["normal"] = _v3(new_normal)
    new_plane["u_direction"] = _v3(new_x)
    new_plane["v_direction"] = _v3(new_y)
    # Also write x_axis / y_axis for downstream consumers that read those.
    new_plane["x_axis"] = _v3(new_x)
    new_plane["y_axis"] = _v3(new_y)
    sketch["reference_plane"]["plane"] = new_plane
    sketch["reference_plane"]["plane_name"] = target_plane

    sketch.setdefault("transform", {})
    sketch["transform"]["x_axis"] = _v3(new_x)
    sketch["transform"]["y_axis"] = _v3(new_y)
    sketch["transform"]["z_axis"] = _v3(new_normal)

    meta = {
        "perturbation_type": "EX1_sketch_plane_swap",
        "error_category": "EX1_plane_swap",
        "original_plane": current_plane,
        "perturbed_plane": target_plane,
        "target_intent": "bbox_size",
        "expected_failed_queries": ["q_bbox_u", "q_bbox_v"],
        "allowed_secondary_failed_queries": ["q_bbox_w"],
        "source_design_plan_field": "$.global_envelope.bbox",
        "should_reconstruct": True,
        "should_fail_kqp": True,
        "operator": "EX1_sketch_plane_swap",
    }
    return h, copy.deepcopy(design_plan), meta


# ---------------------------------------------------------------------------
# EX2 — Coordinate Axis Flip
# ---------------------------------------------------------------------------

def _dominant_axis_index(v: list[float]) -> int:
    return max(range(3), key=lambda i: abs(v[i]))


def _coord_keys_for_axes(coords: dict, world_x_idx: int, world_y_idx: int):
    if "x" in coords and "y" in coords and "z" in coords:
        axis_to_key = {0: "x", 1: "y", 2: "z"}
    elif "0" in coords and "1" in coords and "2" in coords:
        axis_to_key = {0: "0", 1: "1", 2: "2"}
    else:
        return None
    return axis_to_key[world_x_idx], axis_to_key[world_y_idx]


def op_EX2_coordinate_flip(history: dict, design_plan: dict,
                               *, random_seed: int | None = None
                               ) -> tuple[dict, dict, dict]:
    """Within the sketch plane, swap the local x and y axes.

    For each sketch point, swap the coordinates in the two world
    axes that the local x and y point along.
    """
    h = copy.deepcopy(history)
    sketch = _find_sketch(h)
    if sketch is None:
        raise ValueError("no Sketch entity in history")

    current_plane, _n, old_x, old_y = _get_current_plane(sketch)
    world_x_idx = _dominant_axis_index(old_x)
    world_y_idx = _dominant_axis_index(old_y)
    if world_x_idx == world_y_idx:
        raise ValueError(f"local x and y are degenerate (both = axis {world_x_idx})")

    t = sketch.setdefault("transform", {})
    t["x_axis"], t["y_axis"] = _v3_v(old_y), _v3_v(old_x)

    points = sketch.get("points") or {}
    n_swapped = 0
    for _pid, p in points.items():
        if not isinstance(p, dict):
            continue
        coord_key_for_world_axis = _coord_keys_for_axes(p, world_x_idx, world_y_idx)
        if coord_key_for_world_axis is None:
            continue
        kx, ky = coord_key_for_world_axis
        vx = p.get(kx)
        vy = p.get(ky)
        if vx is None or vy is None:
            continue
        p[kx], p[ky] = vy, vx
        n_swapped += 1

    rp = sketch.setdefault("reference_plane", {})
    rp.setdefault("plane", {})
    rp["plane"]["x_axis"] = _v3_v(old_y)
    rp["plane"]["y_axis"] = _v3_v(old_x)

    meta = {
        "perturbation_type": "EX2_coordinate_flip",
        "error_category": "EX2_axis_flip",
        "swapped_axes": f"axis_{world_x_idx}<->axis_{world_y_idx}",
        "target_intent": "bbox_size",
        "expected_failed_queries": ["q_bbox_u", "q_bbox_v"],
        "allowed_secondary_failed_queries": [],
        "source_design_plan_field": "$.global_envelope.bbox",
        "should_reconstruct": True,
        "should_fail_kqp": True,
        "operator": "EX2_coordinate_flip",
        "n_points_swapped": n_swapped,
    }
    return h, copy.deepcopy(design_plan), meta


# ---------------------------------------------------------------------------
# Operator registry
# ---------------------------------------------------------------------------

def all_ex_operators() -> dict:
    return {
        "EX1_sketch_plane_swap": op_EX1_sketch_plane_swap,
        "EX2_coordinate_flip": op_EX2_coordinate_flip,
    }
