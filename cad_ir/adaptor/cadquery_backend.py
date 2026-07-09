"""cadquery_backend.py — Render a single IR operation to cadquery code.

Each `render_*` function takes the op dict + a context dict (mapping op_id
→ local variable name in the generated script) and returns a list of
Python statements (strings) plus a list of (op_id, status) tuples that
the trace builder consumes.

The backend does NOT execute code; it only emits it.  Execution is the
adaptor's job.
"""
from __future__ import annotations

import math
from typing import Any


def _plane_vector(plane: str) -> tuple[str, float]:
    """Map a plane name (XY/XZ/YZ/XY_NEG/...) to (cadquery-workplane, offset_z)."""
    if plane in ("XY", "XY_NEG"):
        return ("XY", -0.0)
    if plane in ("XZ", "XZ_NEG"):
        return ("XZ", -0.0)
    if plane in ("YZ", "YZ_NEG"):
        return ("YZ", -0.0)
    return ("XY", -0.0)


def _center_xy(center):
    cx, cy = center
    return f"({cx}, {cy})"


def render_sketch_rectangle(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    wid, hgt = float(p["width"]), float(p["height"])
    cx, cy = p["center"]
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    # Emit:
    #   var_wpl = cq.Workplane("XY")
    #   var     = var_wpl.center(cx, cy).rect(wid, hgt)
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.center({cx}, {cy}).rect({wid}, {hgt})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_sketch_circle(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    r = float(p["radius"])
    cx, cy = p["center"]
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.center({cx}, {cy}).circle({r})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_sketch_annulus(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """Build an annulus as a wire Workplane (outer + inner circle on the same
    level) — the subsequent ``extrude`` op consumes both wires and produces
    a plate-with-hole.  We do NOT pre-extrude here."""
    p = op["params"]
    ir_r, or_r = float(p["inner_radius"]), float(p["outer_radius"])
    cx, cy = p["center"]
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.center({cx}, {cy}).circle({or_r}).circle({ir_r})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_sketch_rectangular_frame(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """Build a rectangular frame as a wire Workplane (outer + inner rect on
    the same level).  Subsequent extrude op produces the plate-with-rect-hole."""
    p = op["params"]
    ow, oh = float(p["outer_width"]), float(p["outer_height"])
    iw, ih = float(p["inner_width"]), float(p["inner_height"])
    cx, cy = p["center"]
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.center({cx}, {cy}).rect({ow}, {oh}).rect({iw}, {ih})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_sketch_stadium(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """Build a stadium-shaped profile as a closed polyline wire; subsequent
    extrude op consumes the polyline."""
    p = op["params"]
    L = float(p["length"])
    r = float(p["radius"])
    cx, cy = p["center"]
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    n_arc = 8
    hx = L / 2
    pts = []
    for i in range(n_arc + 1):
        ang = math.pi/2 - math.pi * (i / n_arc)
        pts.append((hx - r + r * math.cos(ang),
                     -r + r * math.sin(ang)))
    for i in range(n_arc + 1):
        ang = -math.pi/2 + math.pi * (i / n_arc)
        pts.append((-hx + r + r * math.cos(ang),
                     -r + r * math.sin(ang)))
    pts_str = ", ".join(f"({x:.4f}, {y:.4f})" for x, y in pts)
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.center({cx}, {cy}).polyline([{pts_str}]).close()",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_sketch_polygon(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """Build a polygon profile as a closed polyline wire."""
    p = op["params"]
    verts = p["vertices"]
    pts_str = ", ".join(f"({v[0]}, {v[1]})" for v in verts)
    plane = op.get("plane", "XY")
    wpl_name = _plane_vector(plane)[0]
    var = f"sk_{op['op_id']}"
    var_wpl = f"wp_{op['op_id']}"
    statements = [
        f"{var_wpl} = cq.Workplane({wpl_name!r})",
        f"{var} = {var_wpl}.polyline([{pts_str}]).close()",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_extrude(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    d = float(p["distance"])
    extent = p.get("extent_type", "one_side")
    direction = p.get("direction", "+normal")
    operation = p.get("operation", "new_body")
    input_op_id = op.get("input")
    if not input_op_id or input_op_id not in ctx_id:
        raise ValueError(f"extrude {op['op_id']} has invalid input "
                          f"{input_op_id!r}")
    in_var = ctx_id[input_op_id]
    var = f"body_{op['op_id']}"

    if extent == "one_side":
        statements = [f"{var} = {in_var}.extrude({d})"]
    elif extent == "symmetric":
        statements = [f"{var} = {in_var}.extrude({d / 2}, both=True)"]
    elif extent == "two_sides":
        statements = [f"{var} = {in_var}.extrude({d / 2}, both=True)"]
    else:
        raise ValueError(f"unsupported extent_type {extent!r}")

    if operation == "new_body":
        pass  # default cadquery behavior creates a new solid
    elif operation == "join":
        # In cadquery, .union() merges solids; default is new_body already
        pass
    elif operation == "cut":
        # Need a target — not handled at sketch → extrude level; use cut op.
        pass

    ctx_id[op["op_id"]] = var
    return statements


def render_cut(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    d = float(p["distance"])
    target_id = p["target"]
    tool_id = p.get("tool") or op.get("input")
    if target_id not in ctx_id:
        raise ValueError(f"cut {op['op_id']} target {target_id!r} missing")
    if not tool_id or tool_id not in ctx_id:
        raise ValueError(f"cut {op['op_id']} tool {tool_id!r} missing")
    var = f"cut_{op['op_id']}"
    statements = [
        f"_tool_{op['op_id']} = {ctx_id[tool_id]}.extrude({d})",
        f"{var} = {ctx_id[target_id]}.cut(_tool_{op['op_id']})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_join(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    target_id = p["target"]
    tool_id = p.get("tool") or op.get("input")
    if target_id not in ctx_id:
        raise ValueError(f"join {op['op_id']} target {target_id!r} missing")
    if not tool_id or tool_id not in ctx_id:
        raise ValueError(f"join {op['op_id']} tool {tool_id!r} missing")
    var = f"join_{op['op_id']}"
    statements = [
        f"{var} = {ctx_id[target_id]}.union({ctx_id[tool_id]})",
    ]
    ctx_id[op["op_id"]] = var
    return statements


def render_add_constraint(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """V0.1 placeholder: emits a no-op.  Constraints in cadquery are
    baked into the geometry calls; we don't emit a separate constraint op."""
    return ["pass  # add_constraint: cadquery v0.1 ignores constraint ops "
             "(baked into sketch geometry)"]


def render_set_dimension(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    """V0.1 placeholder: dimensions are set when the sketch op is created."""
    return ["pass  # set_dimension: cadquery v0.1 ignores dimension ops "
             "(baked into sketch parameter values)"]


def render_export_step(op: dict, ctx: dict, ctx_id: dict) -> list[str]:
    p = op["params"]
    path = p["path"]
    input_id = p.get("input")
    if input_id is None:
        # Find the last extrude/join/cut as the export target.
        for op_id in reversed(list(ctx_id.keys())):
            if op_id.startswith("body_") or op_id.startswith("cut_") or \
               op_id.startswith("join_"):
                input_id = op_id
                break
    if input_id is None or input_id not in ctx_id:
        # Last available
        last_id = list(ctx_id.keys())[-1] if ctx_id else None
        if last_id is None:
            return [f"# export_step path={path!r} skipped (no body)"]
        input_id = last_id
    var = ctx_id[input_id]
    return [
        f'cq.exporters.export({var}, {path!r})'
    ]


RENDERERS = {
    "sketch_rectangle": render_sketch_rectangle,
    "sketch_circle": render_sketch_circle,
    "sketch_annulus": render_sketch_annulus,
    "sketch_rectangular_frame": render_sketch_rectangular_frame,
    "sketch_stadium": render_sketch_stadium,
    "sketch_polygon": render_sketch_polygon,
    "extrude": render_extrude,
    "cut": render_cut,
    "join": render_join,
    "add_constraint": render_add_constraint,
    "set_dimension": render_set_dimension,
    "export_step": render_export_step,
}

UNSUPPORTED_OP_WEIGHT = {
    "sketch_rectangle": 2,
    "sketch_circle": 2,
    "sketch_annulus": 2,
    "sketch_rectangular_frame": 2,
    "sketch_stadium": 2,
    "sketch_polygon": 2,
    "extrude": 3,
    "cut": 4,
    "join": 4,
    "add_constraint": 2,
    "set_dimension": 2,
    "export_step": 1,
}