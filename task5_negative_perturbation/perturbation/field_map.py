"""field_map.py — Maps history JSON fields to Design Plan fields.

Defines which history JSON fields can be perturbed, and which Design Plan
attributes they map to. This ensures perturbations stay within the boundary
of fields that propagate to the Design Plan.

History-JSON schema (Fusion360 Gallery reconstruction):
    Sketch.curves[*].{radius, start_point, end_point, center_point}
    Sketch.points[*].{x,y,z}
    Sketch.profiles[*].loops[*].{is_outer, profile_curves}
    ExtrudeFeature.extent_one.distance.value
    ExtrudeFeature.extent_type
"""
from __future__ import annotations

FIELD_MAP = {
    "profile_u": {
        "history_path": "sketch.points[*].x",
        "design_plan_path": "$.global_envelope.bbox.u",
        "expected_query_intent": "bbox_size",
        "axis": "u",
        "perturbable": True,
        "applicable_to": ["rectangle", "stadium", "rectangular_frame",
                          "polygon_with_fillets", "arbitrary_closed"],
        "min_abs_delta_mm": 0.1,
    },
    "profile_v": {
        "history_path": "sketch.points[*].y",
        "design_plan_path": "$.global_envelope.bbox.v",
        "expected_query_intent": "bbox_size",
        "axis": "v",
        "perturbable": True,
        "applicable_to": ["rectangle", "stadium", "rectangular_frame",
                          "polygon_with_fillets", "arbitrary_closed"],
        "min_abs_delta_mm": 0.1,
    },
    "extrude_depth": {
        "history_path": "extrude.extent_one.distance.value",
        "design_plan_path": "$.solid_bodies[0].dimensions.extrude_distance.value",
        "expected_query_intent": "bbox_size",
        "axis": "w",
        "perturbable": True,
        "applicable_to": ["all"],
        "min_abs_delta_mm": 0.1,
    },
    "circle_radius": {
        "history_path": "sketch.curves[*].radius (SketchCircle)",
        "design_plan_path": "$.solid_bodies[0].profiles[0].radius.value",
        "expected_query_intent": "cylinder_radius",
        "perturbable": True,
        "applicable_to": ["circle"],
        "min_abs_delta_mm": 0.1,
    },
    "annulus_outer_radius": {
        "history_path": "sketch.curves[*].radius (SketchCircle, outer)",
        "design_plan_path": "$.solid_bodies[0].profiles[0].outer_radius.value",
        "expected_query_intent": "cylinder_radius",
        "perturbable": True,
        "applicable_to": ["annulus"],
        "min_abs_delta_mm": 0.1,
    },
    "annulus_inner_radius": {
        "history_path": "sketch.curves[*].radius (SketchCircle, inner)",
        "design_plan_path": "$.solid_bodies[0].profiles[0].inner_radius.value",
        "expected_query_intent": "cylinder_radius",
        "perturbable": True,
        "applicable_to": ["annulus"],
        "min_abs_delta_mm": 0.1,
    },
    "stadium_arc_radius": {
        "history_path": "sketch.curves[*].radius (SketchArc)",
        "design_plan_path": "$.solid_bodies[0].profiles[0].stadium_radius.value",
        "expected_query_intent": "cylinder_radius",
        "perturbable": True,
        "applicable_to": ["stadium"],
        "min_abs_delta_mm": 0.1,
    },
    "inner_loop": {
        "history_path": "sketch.profiles[*].loops[is_outer==false]",
        "design_plan_path": "$.solid_bodies[0].profiles[0].inner_loop_count.value",
        "expected_query_intent": "through_void_count",
        "perturbable": True,
        "applicable_to": ["annulus", "rectangular_frame", "polygon_with_fillets"],
    },
    "extent_type": {
        "history_path": "extrude.extent_type",
        "design_plan_path": "$.solid_bodies[0].extrude.extent_type",
        "expected_query_intent": "symmetric_about_plane",
        "perturbable": True,
        "applicable_to": ["extent_type==symmetric"],
    },
    "extrude_zero": {
        "history_path": "extrude.extent_one.distance.value",
        "design_plan_path": "$.solid_bodies[0].dimensions.extrude_distance.value",
        "expected_query_intent": "is_solid, occt_valid",
        "perturbable": True,
        "applicable_to": ["all"],
        "action": "set_zero",
    },
    "inner_radius_too_large": {
        "history_path": "sketch.curves[*].radius (SketchCircle, inner)",
        "design_plan_path": "$.solid_bodies[0].profiles[0].inner_radius.value",
        "expected_query_intent": "is_solid, occt_valid",
        "perturbable": True,
        "applicable_to": ["annulus"],
        "action": "set_above_outer",
    },
}


def get_field_meta(field_name: str) -> dict:
    if field_name not in FIELD_MAP:
        raise KeyError(f"Unknown field: {field_name}")
    return FIELD_MAP[field_name]


def get_perturbable_fields_for_profile(profile_type: str) -> list[str]:
    return [name for name, meta in FIELD_MAP.items()
            if profile_type in meta.get("applicable_to", []) or
               "all" in meta.get("applicable_to", [])]


def check_field_applicable(field_name: str, profile_type: str) -> bool:
    if field_name not in FIELD_MAP:
        return False
    applicable = FIELD_MAP[field_name].get("applicable_to", [])
    return profile_type in applicable or "all" in applicable
