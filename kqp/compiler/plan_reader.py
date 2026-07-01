"""plan_reader.py — Read design_plan_v0.6, expose normalized access.

The compiler reads a design_plan_v0.6.json and converts it into a flat
representation that the rest of the compiler can use. This is the single
source of truth for plan access (avoiding scattered 'data["solid_bodies"][0]'...).

Conventions:
  - Profile is the profile.type of the first profile (the design_plan allows
    multiple, but our 50 instances all use single-profile bodies).
  - Dimension accessors return mm floats or None if missing.
  - Extrude is normalized to a dict with .extent_type / .direction / .distance_total_mm.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional


class PlanReader:
    """Read a design_plan_v0.6 and expose normalized accessors."""

    def __init__(self, plan: dict):
        self.plan = plan
        self._sb = plan.get("solid_bodies", [{}])[0]
        self._dims = self._sb.get("dimensions", {})
        self._profiles = self._sb.get("profiles", [{}])

    @classmethod
    def from_file(cls, path: str | Path) -> "PlanReader":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    @classmethod
    def from_json(cls, payload: dict) -> "PlanReader":
        return cls(payload)

    # ----- Identifiers -----
    @property
    def sample_id(self) -> str:
        return self.plan.get("sample_id", "")

    @property
    def step_file(self) -> str:
        return f"data/sanity_set_50/{self.sample_id}.step"

    # ----- Body & profile metadata -----
    @property
    def body_count(self) -> int:
        return int(self.plan.get("target", {}).get("body_count", 1))

    @property
    def ptype(self) -> str:
        """The profile.type of the primary profile (single-profile bodies)."""
        if not self._profiles:
            return "unknown"
        return self._profiles[0].get("type", "unknown")

    @property
    def rings(self) -> list[dict]:
        """All rings of the primary profile."""
        if not self._profiles:
            return []
        return self._profiles[0].get("rings", []) or []

    @property
    def n_inner_rings(self) -> int:
        return sum(1 for r in self.rings if r.get("role") == "inner")

    # ----- Extrude -----
    @property
    def extrude(self) -> dict:
        """Normalized extrude dict: {extent_type, direction, distance_total_mm}."""
        eb = self._sb.get("extrude", {}) or {}
        return {
            "extent_type": eb.get("extent_type", "one_side"),
            "direction": eb.get("direction", "+w"),
            "distance_total_mm": float(
                (self._dims.get("extrude_distance") or {}).get("value", 0.0)
            ),
        }

    @property
    def is_symmetric(self) -> bool:
        return self.extrude["extent_type"] == "symmetric"

    # ----- Frame axes (for source_path labelling) -----
    @property
    def frame(self) -> dict:
        return self._sb.get("frame", {}) or {}

    @property
    def u_dir(self) -> list[float]:
        return list(self.frame.get("u_dir", [1, 0, 0]))

    @property
    def v_dir(self) -> list[float]:
        return list(self.frame.get("v_dir", [0, 1, 0]))

    @property
    def w_dir(self) -> list[float]:
        return list(self.frame.get("w_dir", [0, 0, 1]))

    # ----- Dimension accessors (mm) -----
    def _pd(self) -> dict:
        """Profile dimensions dict (first profile)."""
        if not self._dims.get("profiles"):
            return {}
        return self._dims["profiles"][0]

    def dim_radius(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("radius", {}).get("value") if isinstance(pd.get("radius"), dict) else None

    def dim_outer_radius(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("outer_radius", {}).get("value") if isinstance(pd.get("outer_radius"), dict) else None

    def dim_inner_radius(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("inner_radius", {}).get("value") if isinstance(pd.get("inner_radius"), dict) else None

    def dim_length_u(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("length_u", {}).get("value") if isinstance(pd.get("length_u"), dict) else None

    def dim_width_v(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("width_v", {}).get("value") if isinstance(pd.get("width_v"), dict) else None

    def dim_outer_length_u(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("outer_length_u", {}).get("value") if isinstance(pd.get("outer_length_u"), dict) else None

    def dim_outer_width_v(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("outer_width_v", {}).get("value") if isinstance(pd.get("outer_width_v"), dict) else None

    def dim_straight_length(self) -> Optional[float]:
        pd = self._pd()
        return pd.get("straight_length", {}).get("value") if isinstance(pd.get("straight_length"), dict) else None

    def dim_extrude_distance(self) -> float:
        return float((self._dims.get("extrude_distance") or {}).get("value", 0.0))

    # ----- Computed bbox sizes -----
    def bbox_u_size(self) -> Optional[float]:
        """Returns bbox u-axis size in mm, or None if not derivable."""
        ptype = self.ptype
        if ptype == "rectangle":
            lu = self.dim_length_u()
            return lu
        if ptype == "rectangular_frame":
            return self.dim_outer_length_u()
        if ptype == "circle":
            r = self.dim_radius()
            return 2 * r if r is not None else None
        if ptype == "annulus":
            ro = self.dim_outer_radius()
            return 2 * ro if ro is not None else None
        if ptype == "stadium":
            sl = self.dim_straight_length()
            r = self.dim_radius()
            if sl is not None and r is not None:
                return sl + 2 * r
            return None
        return None  # polygon_with_fillets, arbitrary_closed: not derivable cleanly

    def bbox_v_size(self) -> Optional[float]:
        ptype = self.ptype
        if ptype == "rectangle":
            return self.dim_width_v()
        if ptype == "rectangular_frame":
            return self.dim_outer_width_v()
        if ptype == "circle":
            r = self.dim_radius()
            return 2 * r if r is not None else None
        if ptype == "annulus":
            ro = self.dim_outer_radius()
            return 2 * ro if ro is not None else None
        if ptype == "stadium":
            r = self.dim_radius()
            return 2 * r if r is not None else None
        return None

    def bbox_w_size(self) -> Optional[float]:
        """Returns bbox w-axis (= extrude distance) size in mm."""
        return self.dim_extrude_distance()
