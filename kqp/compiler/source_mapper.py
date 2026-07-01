"""source_mapper.py — Generate source_field path for queries.

The KQP schema v0.2 accepts:
  - dotted: solid_bodies.0.dimensions.extrude_distance.value
  - bracket: solid_bodies[0].dimensions.profiles[0].length_u.value
  - computed suffix: <path> (computed: <expr>)
  - inferred suffix: <path> (inferred_from_point_span)
  - (implicit) / (implicit: <note>)

This module decides the canonical form for each query.
"""
from __future__ import annotations
from typing import Optional


class SourceMapper:
    """Build source_field strings deterministically.

    Convention: emit BRACKET form (`a[0].b[1].c`) for consistency with the
    schema's documented canonical form. Bracket form is fully equivalent to
    dot form under v0.2.
    """

    BRACKET = True  # emit solid_bodies[0].x.y[0] form; set False for dotted

    @staticmethod
    def path(parts: list, bracket: Optional[bool] = None) -> str:
        """Join path parts into a JSONPath string.

        parts: list of (str, int | str) tuples OR plain strings.
              Strings -> 'key'; ints -> '[N]'.
        """
        if bracket is None:
            bracket = SourceMapper.BRACKET
        out = []
        for p in parts:
            if isinstance(p, int):
                out.append(f"[{p}]")
            elif isinstance(p, str) and p.startswith("[") and p.endswith("]"):
                out.append(p)
            else:
                if bracket and out and not out[-1].endswith("]") and not out[-1] == "":
                    out.append(f".{p}")
                elif bracket and (out == [] or out[-1] == ""):
                    out.append(str(p))
                else:
                    if out:
                        out.append(f".{p}")
                    else:
                        out.append(str(p))
        # remove any leading "." from first segment
        if out and out[0].startswith("."):
            out[0] = out[0][1:]
        return "".join(out)

    @classmethod
    def body_count(cls) -> str:
        return "$.target.body_count"

    @classmethod
    def extrude_distance(cls) -> str:
        return "$.solid_bodies[0].dimensions.extrude_distance.value"

    @classmethod
    def length_u(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].length_u.value"

    @classmethod
    def width_v(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].width_v.value"

    @classmethod
    def outer_length_u(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].outer_length_u.value"

    @classmethod
    def outer_width_v(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].outer_width_v.value"

    @classmethod
    def radius(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].radius.value"

    @classmethod
    def outer_radius(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value"

    @classmethod
    def inner_radius(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].inner_radius.value"

    @classmethod
    def straight_length(cls) -> str:
        return "$.solid_bodies[0].dimensions.profiles[0].straight_length.value"

    @classmethod
    def void_count(cls) -> str:
        return "$.solid_bodies[0].profiles[0].rings[*].role=='inner' count"

    @classmethod
    def computed(cls, base_path: str, expr: str) -> str:
        """Wrap a base path with a computed expression."""
        return f"{base_path} (computed: {expr})"

    @classmethod
    def inferred(cls, base_path: str) -> str:
        return f"{base_path} (inferred_from_point_span)"

    @classmethod
    def implicit(cls, note: str | None = None) -> str:
        if note is None:
            return "(implicit)"
        return f"(implicit: {note})"
