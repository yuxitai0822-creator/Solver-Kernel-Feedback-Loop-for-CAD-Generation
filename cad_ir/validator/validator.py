"""validator.py — Schema check + semantic validation for cad_ir_v0.1.

Two stages:
  1. Schema check     — JSON-Schema structural validation
  2. Semantic check   — domain-specific constraints (positive dims,
                        annulus inner<outer, polygon ≥3 vertices, etc.)

Both stages return a list of issues.  An IR passes validation iff
the issue list is empty.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


SCHEMA_PATH = (Path(__file__).resolve().parents[1] / "schema"
                / "cad_ir_schema_v0.1.json")

OP_TYPE_PARAMS = {
    "sketch_rectangle": {"width", "height", "center"},
    "sketch_circle": {"radius", "center"},
    "sketch_annulus": {"inner_radius", "outer_radius", "center"},
    "sketch_rectangular_frame": {"outer_width", "outer_height",
                                   "inner_width", "inner_height", "center"},
    "sketch_stadium": {"length", "radius", "center"},
    "sketch_polygon": {"vertices"},
    "extrude": {"distance", "extent_type"},
    "cut": {"distance", "target"},
    "join": {"target"},
    "add_constraint": {"constraint_type", "target"},
    "set_dimension": {"dimension_type", "value", "target"},
    "export_step": {"path"},
}


# ---------------------------------------------------------------------------
# Schema check
# ---------------------------------------------------------------------------

def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def schema_check(ir: dict) -> list[str]:
    """Return list of schema issues (empty = pass)."""
    issues: list[str] = []

    # Top-level required fields
    for k in ("schema_version", "sample_id", "unit", "coordinate_system",
                "operations"):
        if k not in ir:
            issues.append(f"schema: missing top-level field '{k}'")

    if ir.get("schema_version") != "cad_ir_v0.1":
        issues.append(f"schema: schema_version must be 'cad_ir_v0.1', "
                       f"got {ir.get('schema_version')!r}")
    if ir.get("unit") not in ("mm", "cm", "m", "in"):
        issues.append(f"schema: invalid unit {ir.get('unit')!r}")

    cs = ir.get("coordinate_system", {})
    for k in ("up_axis", "front_axis", "right_axis"):
        if cs.get(k) not in ("x", "y", "z"):
            issues.append(f"schema: coordinate_system.{k} must be x/y/z")

    ops = ir.get("operations", [])
    if not isinstance(ops, list) or len(ops) == 0:
        issues.append("schema: operations must be a non-empty list")
        return issues

    # op_id uniqueness + presence
    seen_ids: set[str] = set()
    for i, op in enumerate(ops):
        opid = op.get("op_id")
        if not opid:
            issues.append(f"schema: op[{i}] missing op_id")
            continue
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(opid)):
            issues.append(f"schema: op[{i}] op_id '{opid}' is not a "
                           f"valid identifier")
        if opid in seen_ids:
            issues.append(f"schema: op_id '{opid}' is not unique "
                           f"(appears at index {i})")
        seen_ids.add(opid)

    for i, op in enumerate(ops):
        optype = op.get("op_type")
        if optype not in OP_TYPE_PARAMS:
            issues.append(f"schema: op[{i}] op_type '{optype}' is not "
                           f"a valid v0.1 op_type")
        if not isinstance(op.get("params"), dict):
            issues.append(f"schema: op[{i}] params must be a dict")

    # input references exist
    for i, op in enumerate(ops):
        ref = op.get("input")
        if ref is not None and ref not in seen_ids:
            issues.append(f"schema: op[{i}] input '{ref}' references "
                           f"a missing op_id")

    # Optional JSON-Schema validation if available.  Wrapped in try/except
    # because newer jsonschema versions removed the legacy RefResolver
    # signature; we fall back to our own hand-written checks above.
    if HAVE_JSONSCHEMA:
        try:
            schema = _load_schema()
            jsonschema.validate(instance=ir, schema=schema)
        except jsonschema.ValidationError as e:
            issues.append(f"json-schema: {e.message} at path {list(e.path)}")
        except Exception as e:
            issues.append(f"json-schema: {type(e).__name__}: {e}")

    return issues


# ---------------------------------------------------------------------------
# Semantic check
# ---------------------------------------------------------------------------

def semantic_check(ir: dict) -> list[str]:
    """Return list of semantic issues (empty = pass)."""
    issues: list[str] = []

    if not ir.get("operations"):
        return ["semantic: no operations to check"]

    ids = {op["op_id"] for op in ir["operations"] if "op_id" in op}

    for i, op in enumerate(ir.get("operations", [])):
        optype = op.get("op_type")
        params = op.get("params", {})

        # Numeric positive checks
        if optype == "sketch_rectangle":
            if params.get("width", 0) <= 0:
                issues.append(f"semantic: op[{i}] rectangle width must be > 0")
            if params.get("height", 0) <= 0:
                issues.append(f"semantic: op[{i}] rectangle height must be > 0")
        elif optype == "sketch_circle":
            if params.get("radius", 0) <= 0:
                issues.append(f"semantic: op[{i}] circle radius must be > 0")
        elif optype == "sketch_annulus":
            ir_r = params.get("inner_radius", 0)
            or_r = params.get("outer_radius", 0)
            if ir_r <= 0:
                issues.append(f"semantic: op[{i}] annulus inner_radius must be > 0")
            if or_r <= 0:
                issues.append(f"semantic: op[{i}] annulus outer_radius must be > 0")
            if ir_r >= or_r:
                issues.append(
                    f"semantic: op[{i}] annulus inner_radius ({ir_r}) must "
                    f"be < outer_radius ({or_r})")
        elif optype == "sketch_rectangular_frame":
            for k in ("outer_width", "outer_height",
                       "inner_width", "inner_height"):
                if params.get(k, 0) <= 0:
                    issues.append(f"semantic: op[{i}] frame {k} must be > 0")
            if params.get("inner_width", 0) >= params.get("outer_width", 0):
                issues.append(f"semantic: op[{i}] frame inner_width must be "
                               f"< outer_width")
            if params.get("inner_height", 0) >= params.get("outer_height", 0):
                issues.append(f"semantic: op[{i}] frame inner_height must be "
                               f"< outer_height")
        elif optype == "sketch_stadium":
            if params.get("length", 0) <= 0:
                issues.append(f"semantic: op[{i}] stadium length must be > 0")
            if params.get("radius", 0) <= 0:
                issues.append(f"semantic: op[{i}] stadium radius must be > 0")
        elif optype == "sketch_polygon":
            verts = params.get("vertices", [])
            if len(verts) < 3:
                issues.append(f"semantic: op[{i}] polygon needs at least "
                               f"3 vertices, got {len(verts)}")
            else:
                seen_v = set()
                for v in verts:
                    if not (isinstance(v, (list, tuple)) and len(v) == 2):
                        issues.append(f"semantic: op[{i}] polygon vertex "
                                       f"must be [x, y]")
                        continue
                    seen_v.add(tuple(v))
                if len(seen_v) < 3:
                    issues.append(f"semantic: op[{i}] polygon has "
                                   f"< 3 distinct vertices")
        elif optype == "extrude":
            d = params.get("distance", 0)
            if d == 0:
                issues.append(f"semantic: op[{i}] extrude distance must "
                               f"not be 0")
            if params.get("extent_type") not in ("one_side", "symmetric",
                                                   "two_sides"):
                issues.append(f"semantic: op[{i}] extrude extent_type "
                               f"must be one_side/symmetric/two_sides")
        elif optype == "cut":
            d = params.get("distance", 0)
            if d <= 0:
                issues.append(f"semantic: op[{i}] cut distance must be > 0")
            tgt = params.get("target")
            if tgt not in ids:
                issues.append(f"semantic: op[{i}] cut.target '{tgt}' "
                               f"references a missing op_id")
        elif optype == "join":
            tgt = params.get("target")
            if tgt not in ids:
                issues.append(f"semantic: op[{i}] join.target '{tgt}' "
                               f"references a missing op_id")
        elif optype == "add_constraint":
            if params.get("constraint_type") not in (
                "horizontal", "vertical", "coincident", "perpendicular",
                "parallel", "tangent", "concentric", "equal", "midpoint",
                "offset"):
                issues.append(f"semantic: op[{i}] constraint_type invalid")
            tgt = params.get("target")
            if tgt not in ids:
                issues.append(f"semantic: op[{i}] add_constraint.target "
                               f"'{tgt}' references a missing op_id")
        elif optype == "set_dimension":
            if params.get("dimension_type") not in ("linear", "diameter",
                                                      "radius", "angular"):
                issues.append(f"semantic: op[{i}] dimension_type invalid")
            if params.get("value", 0) <= 0:
                issues.append(f"semantic: op[{i}] dimension value must be > 0")
            tgt = params.get("target")
            if tgt not in ids:
                issues.append(f"semantic: op[{i}] set_dimension.target "
                               f"'{tgt}' references a missing op_id")
        elif optype == "export_step":
            if not params.get("path"):
                issues.append(f"semantic: op[{i}] export_step.path required")
            inp = params.get("input")
            if inp is not None and inp not in ids:
                issues.append(f"semantic: op[{i}] export_step.input "
                               f"'{inp}' references a missing op_id")

    return issues


# ---------------------------------------------------------------------------
# Top-level entry
# ---------------------------------------------------------------------------

def validate(ir: dict, *, semantic: bool = True) -> dict:
    """Run schema + (optional) semantic validation.

    Returns dict with keys:
      schema_status:       'pass' | 'fail'
      schema_issues:       list[str]
      semantic_status:     'pass' | 'fail' | 'skipped'
      semantic_issues:     list[str]
      overall:             'pass' | 'fail'
    """
    schema_issues = schema_check(ir)
    if semantic:
        semantic_issues = semantic_check(ir)
        sem_status = "pass" if not semantic_issues else "fail"
    else:
        semantic_issues = []
        sem_status = "skipped"

    overall = "pass" if (not schema_issues
                          and sem_status in ("pass", "skipped")) else "fail"
    return {
        "schema_status": "pass" if not schema_issues else "fail",
        "schema_issues": schema_issues,
        "semantic_status": sem_status,
        "semantic_issues": semantic_issues,
        "overall": overall,
    }


def validate_file(path: str | Path, *, semantic: bool = True) -> dict:
    ir = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate(ir, semantic=semantic)