"""code2oper/taxonomy.py — Operation taxonomy for the AST-based parser.

Phase 2A Task A2.1.  Each cadquery API call detected by the parser is
mapped to one of these operation types with a small set of expected
parameters.  The taxonomy is a CONSTRAINT, not a parser requirement:
the parser may also detect API calls that don't fit (recorded as
``unknown``) without aborting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# API → operation mapping.  Each entry maps a method name (string) to
# the operation kind + the set of arg positions / keyword names to
# extract as parameters.
API_OP_MAP = {
    # Sketch (Workplane methods)
    "rect": ("rectangle", ["width", "height"]),
    "rect": ("rectangle", ["width", "height"]),  # Workplane.rect(w, h, ...)
    "circle": ("circle", ["radius"]),
    "polygon": ("polygon", ["sides", "radius"]),
    "lineTo": ("line", ["x", "y"]),
    "lineTo": ("line", ["x", "y"]),
    "line": ("line", ["x1", "y1", "x2", "y2"]),
    "hLine": ("line", ["distance"]),
    "vLine": ("line", ["distance"]),
    "hLineTo": ("line", ["x"]),
    "vLineTo": ("line", ["y"]),
    "threePointArc": ("arc", ["point1", "point2"]),
    "radiusArc": ("arc", ["end_point", "radius"]),
    "tangentArcPoint": ("arc", ["point"]),
    # Feature (Workplane methods)
    "extrude": ("extrude", ["distance"]),
    "cut": ("cut", ["distance"]),
    "shell": ("shell", ["thickness"]),
    "fillet": ("fillet", ["radius"]),
    "chamfer": ("chamfer", ["length"]),
    "union": ("union", []),
    "combine": ("union", []),
    "intersect": ("union", []),  # treat as boolean op
    # Transform
    "translate": ("translate", ["vec"]),
    "rotate": ("rotate", ["axis", "angle"]),
    "mirror": ("mirror", ["axis"]),
}


# Operations that have a 1D "size" parameter (for the CED weight)
SIZE_PARAM_KEY = {
    "rectangle": ("width", "height"),
    "circle": ("radius",),
    "polygon": ("radius",),
    "extrude": ("distance",),
    "cut": ("distance",),
    "shell": ("thickness",),
    "fillet": ("radius",),
    "chamfer": ("length",),
}


@dataclass
class Operation:
    """A single extracted operation, output of the parser."""
    operation: str                # "rectangle" | "circle" | "extrude" | ...
    parameters: dict[str, Any]   # extracted parameters (numeric + symbolic)
    source: dict[str, str] = field(default_factory=dict)
    # source: {"api": "cq.Workplane.rect", "argument": "width"}

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "parameters": self.parameters,
            "source": self.source,
        }


def param_to_dict(p: Any) -> Any:
    """Convert a Python param to a JSON-serialisable value (best-effort)."""
    if isinstance(p, (int, float, str, bool, type(None))):
        return p
    if isinstance(p, (list, tuple)):
        return [param_to_dict(x) for x in p]
    if isinstance(p, dict):
        return {k: param_to_dict(v) for k, v in p.items()}
    # cadquery Vector, Location, etc.  Try attr-dump.
    try:
        return {"__repr__": repr(p)}
    except Exception:
        return None
