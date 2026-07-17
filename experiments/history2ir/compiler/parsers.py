"""parsers.py — History JSON → normalized intermediate dict (the "parsed structure").

This module extracts entities, sketches, and features from a Fusion360
Gallery history JSON.  It does NOT produce CAD IR directly; that is the
job of `history_to_ir.py`.

Key principles:
  * No sample-id hard-coding; all logic is schema-driven (entity type,
    field structure, feature type).
  * Reusable for both clean and perturbed histories.
"""
from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _round(v: Any) -> Any:
    if isinstance(v, float):
        return round(v, 4)
    if isinstance(v, list):
        return [_round(x) for x in v]
    if isinstance(v, dict):
        return {k: _round(x) for k, x in sorted(v.items())}
    return v


def _stable_dict(d: dict) -> dict:
    """Deterministic dict representation: keys sorted, floats rounded to 4 dp."""
    return _round(d)


# ---------------------------------------------------------------------------
# Top-level reader
# ---------------------------------------------------------------------------

def read_history(history: dict) -> dict:
    """Parse a Fusion360 Gallery history JSON.

    Returns a normalized dict with keys:
        sample_id, unit, entities, timeline, features
    where:
        entities: dict[entity_uuid -> EntityDict]
        timeline: list[TimelineEntry]   (entity_uuid, type, name)
        features: dict[entity_uuid -> FeatureDict]
    """
    entities_raw = history.get("entities", {})
    timeline_raw = history.get("timeline", [])

    entities: dict[str, dict] = {}
    timeline: list[dict] = []
    for ev in timeline_raw:
        eid = ev.get("entity", "")
        e = entities_raw.get(eid, {})
        if not e:
            continue
        entities[eid] = e
        timeline.append({
            "index": ev.get("index"),
            "entity": eid,
            "type": e.get("type"),
            "name": e.get("name"),
        })

    features: dict[str, dict] = _parse_features(entities)

    return {
        "sample_id": _find_sample_id(history),
        "unit": "mm",   # Gallery uses cm, but we map to mm in the IR
        "entities": entities,
        "timeline": timeline,
        "features": features,
    }


def _find_sample_id(history: dict) -> str:
    md = history.get("metadata", {}) or {}
    if "parent_project" in md:
        return md["parent_project"]
    if "component_name" in md:
        return md["component_name"]
    return "unknown"


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def _parse_features(entities: dict) -> dict[str, dict]:
    """Walk entities and pull out the features we care about (ExtrudeFeature,
    Cut, Boolean, Fillet, etc.).  Returns dict[feature_uuid -> FeatureDict]."""
    out: dict[str, dict] = {}
    for eid, e in entities.items():
        et = e.get("type", "")
        if et == "ExtrudeFeature":
            out[eid] = _parse_extrude(eid, e)
        elif et in ("CutFeature", "BooleanFeature"):
            out[eid] = _parse_boolean(eid, e)
        elif et == "FilletFeature":
            out[eid] = _parse_fillet(eid, e)
    return out


def _parse_extrude(eid: str, e: dict) -> dict:
    eo = e.get("extent_one") or {}
    dist_obj = eo.get("distance") or {} if isinstance(eo, dict) else {}
    return {
        "feature_id": eid,
        "type": "ExtrudeFeature",
        "operation": e.get("operation", "NewBodyFeatureOperation"),
        "extent_type": e.get("extent_type", ""),
        "distance": dist_obj.get("value") if isinstance(dist_obj, dict) else None,
        "taper_angle": eo.get("taper_angle", {}).get("value")
                            if isinstance(eo, dict) and isinstance(eo.get("taper_angle"), dict) else 0,
        "direction": "positive" if eo.get("type", "") == "DistanceExtentDefinition"
                        else "symmetric" if e.get("extent_type") == "SymmetricFeatureExtentType"
                        else "unknown",
        "profiles": e.get("profiles", []),
        "extrude_faces": e.get("extrude_faces", []),
        "name": e.get("name"),
    }


def _parse_boolean(eid: str, e: dict) -> dict:
    return {
        "feature_id": eid,
        "type": e.get("type"),
        "operation": e.get("operation", ""),
        "tools": e.get("tools", []),
        "target_bodies": e.get("target_bodies", []),
        "name": e.get("name"),
    }


def _parse_fillet(eid: str, e: dict) -> dict:
    return {
        "feature_id": eid,
        "type": "FilletFeature",
        "edge_sets": e.get("edge_sets", []),
        "name": e.get("name"),
    }


# ---------------------------------------------------------------------------
# Sketch extraction
# ---------------------------------------------------------------------------

def extract_sketches(entities: dict) -> list[dict]:
    """Find all Sketch entities and normalize them.

    V0.1.3 fix: detect when 2 SEPARATE profiles (each a single loop)
    together form a frame (one outer + one inner rectangle).  In that
    case the classifier returns 'rectangular_frame' (matching
    BehaviourV0.1's 'frame_or_polygon_with_holes' shape).

    Returns list of:
        {sketch_id, name, profile_uuid, profile_type, geometry_count, ...}
    """
    out: list[dict] = []
    for eid, e in entities.items():
        if e.get("type") != "Sketch":
            continue
        profiles = e.get("profiles", {}) or {}
        first_pid = next(iter(profiles.keys()), None) if profiles else None
        ptype = _classify_profile(profiles, entities)
        # Detect 2 separate profile loops each with 1 loop, all line-only.
        # This means the sketch has outer rect + inner rect but in
        # different profiles — treat as rectangular_frame.
        if ptype in ("polygon", "rectangle_or_polygon", "unknown", "mixed(Line3D)") and len(profiles) >= 2:
            line_loops = []
            for pid, prof in profiles.items():
                if len(prof.get("loops", [])) == 1:
                    line_types = set()
                    for pc in prof["loops"][0].get("profile_curves", []):
                        cid = pc.get("curve")
                        for ent in entities.values():
                            if ent.get("type") == "Sketch":
                                c = ent.get("curves", {}).get(cid)
                                if c:
                                    line_types.add(c.get("type"))
                    if line_types and line_types <= {"SketchLine"}:
                        line_loops.append((pid, prof))
            if len(line_loops) >= 2:
                ptype = "rectangular_frame"
        out.append({
            "sketch_id": eid,
            "name": e.get("name"),
            "profile_uuid": first_pid,
            "profile_type": ptype,
            "geometry_count": len(e.get("curves", {}) or {}),
            "constraint_count": len(e.get("constraints", {}) or {}),
            "points": _summarize_points(e),
        })
    return out


def _classify_profile(profiles: dict, entities: dict) -> str:
    """Classify the dominant profile type from a sketch's geometry.

    V0.1.1 fix: distinguish annulus (circles) from rectangular_frame
    (lines) by inspecting the actual curve types in the loops, not just
    the loop count.
    """
    if not profiles:
        return "unknown"
    first_pid = next(iter(profiles.keys()))
    profile = profiles.get(first_pid, {})

    inner_count = 0
    all_curve_types: set[str] = set()
    # Walk all loops' profile_curves and resolve curve types via entities
    for loop in profile.get("loops", []):
        if not loop.get("is_outer", True):
            inner_count += 1
        for pc in loop.get("profile_curves", []):
            curve_uuid = pc.get("curve")
            if curve_uuid:
                # Look up the curve's type by scanning all entities
                for ent in entities.values():
                    if ent.get("type") == "Sketch":
                        c = ent.get("curves", {}).get(curve_uuid)
                        if c:
                            all_curve_types.add(c.get("type", "unknown"))
                            break
            # Also check the top-level curves dict (legacy)
            if curve_uuid in entities.get("curves", {}):
                all_curve_types.add(entities["curves"][curve_uuid].get("type", "unknown"))

    has_lines = "SketchLine" in all_curve_types
    has_circles = "SketchCircle" in all_curve_types

    if inner_count == 0:
        return _shape_from_profile_curves(profile, entities)
    # inner_count >= 1: could be annulus or frame
    if has_circles and not has_lines:
        return "annulus" if inner_count == 1 else "frame_or_polygon_with_holes"
    if has_lines and not has_circles:
        return "rectangular_frame"
    if has_lines and has_circles:
        return "polygon"
    return "annulus"  # fallback (should not happen)


def _shape_from_profile_curves(profile: dict, entities: dict) -> str:
    # Walk profile_curves
    curves = profile.get("curves", [])
    if not curves:
        return "unknown"
    types = set()
    for c in curves:
        t = c.get("type", "")
        types.add(t)
    if types == {"Line3D"}:
        return "rectangle_or_polygon"
    if types == {"Circle3D"}:
        return "circle"
    return f"mixed({','.join(sorted(types))})"


def _summarize_points(sketch_entity: dict) -> dict:
    """Return point count + bbox of the sketch (cm)."""
    pts = sketch_entity.get("points", {}) or {}
    xs, ys = [], []
    for p in pts.values():
        if isinstance(p, dict):
            xs.append(p.get("x", 0))
            ys.append(p.get("y", 0))
    if not xs:
        return {"n": 0, "x_min": 0, "x_max": 0, "y_min": 0, "y_max": 0}
    return {
        "n": len(xs),
        "x_min": round(min(xs), 4),
        "x_max": round(max(xs), 4),
        "y_min": round(min(ys), 4),
        "y_max": round(max(ys), 4),
    }
