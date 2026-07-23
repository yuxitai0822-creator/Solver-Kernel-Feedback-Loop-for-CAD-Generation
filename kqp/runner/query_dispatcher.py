"""query_dispatcher.py — route KQP queries to geometry_backend functions.

For each KQP query (intent + params), this module:
1. Calls the appropriate geometry_backend function on the loaded STEP shape
2. Returns the 'actual' value
3. Compares actual to expected (using tolerance)
4. Returns a (status, actual, error, feedback) tuple

The dispatcher needs:
- shape: the loaded TopoDS_Shape
- query: the KQP query dict (intent, expected, tolerance, axis, params, ...)
- frame: (u_dir, v_dir, w_dir) for bbox_size queries
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geometry_backend as gb


def dispatch_query(shape, query: dict, frame: dict) -> dict:
    """Execute a single KQP query against the STEP shape.

    Returns a result dict with keys:
      status: 'pass' | 'fail' | 'error' | 'unsupported'
      actual: the value returned by the backend (or None)
      expected: the expected value from the KQP query
      error: |actual - expected| (numeric) or None
      feedback: dict with error_type + message (if status != 'pass')
    """
    intent = query.get("intent")
    expected = query.get("expected")
    tolerance = query.get("tolerance")
    axis = query.get("axis")
    params = query.get("params", {}) or {}

    try:
        if intent == "body_count":
            actual = gb.get_solid_count(shape)
            return _build_result(actual, expected, 0, query)

        elif intent == "bbox_size":
            # B-009 + B-010 fix (2026-07-17): the pre-fix code used a
            # "best-match" strategy for axis-aligned frames — it picked the
            # world axis with the closest span to the expected value.  This
            # was a safety net for mislabeled frames but it ALSO masked
            # execution-level perturbations (EX1 plane swap, EX2 axis
            # flip) where the body is rotated relative to the design
            # plan's frame.
            #
            # Post-fix: ALWAYS use the frame-axis projection.  For clean
            # samples (where the body is correctly oriented and the DP
            # compiler correctly extracted the frame), the projection
            # gives a value that matches the design plan's expected value.
            # For EX1/EX2 perturbed samples, the projection produces a
            # value that does NOT match the expected, making the
            # perturbation detectable.
            u_dir = frame.get("u_dir", [1, 0, 0])
            v_dir = frame.get("v_dir", [0, 1, 0])
            w_dir = frame.get("w_dir", [0, 0, 1])
            actual = gb.get_bbox_size_along_frame_axis(shape, axis,
                                                       u_dir, v_dir, w_dir)
            return _build_result(actual, expected, tolerance, query)

        elif intent == "cylinder_radius":
            selector = params.get("selector", "")
            actual = gb.get_cylinder_radius_by_selector(shape, selector)
            if actual is None:
                return _error_result(query, "no_cylinder_face", "No cylindrical face found in shape.")
            return _build_result(actual, expected, tolerance, query)

        elif intent == "through_void_count":
            actual = gb.get_through_void_count(shape)
            return _build_result(actual, expected, 0, query)

        elif intent == "is_solid":
            actual = gb.is_solid_shape(shape)
            return _build_result(actual, expected, None, query)

        elif intent == "occt_valid":
            actual = gb.is_occt_valid(shape)
            return _build_result(actual, expected, None, query)

        elif intent == "symmetric_about_plane":
            w_dir = frame.get("w_dir", [0, 0, 1])
            # plane origin is (0,0,0) in part-local (we don't have absolute world origin)
            # For symmetric check, we just verify centroid is near the sketch plane.
            # Since the STEP is in world coords, we use the bbox center as plane origin.
            xmin, ymin, zmin, xmax, ymax, zmax = gb.get_axis_aligned_bbox(shape)
            # The sketch plane is at the midpoint of the extrude axis
            # For symmetric, centroid should be at midpoint -> centroid on plane
            # We check: |centroid projection onto w_dir - midpoint projection onto w_dir| < tol
            cx, cy, cz = gb.get_centroid(shape)
            mid_proj = (xmin + xmax) / 2 * w_dir[0] + (ymin + ymax) / 2 * w_dir[1] + (zmin + zmax) / 2 * w_dir[2]
            centroid_proj = cx * w_dir[0] + cy * w_dir[1] + cz * w_dir[2]
            dist = abs(centroid_proj - mid_proj)
            tol = tolerance if tolerance is not None else 0.01
            actual = dist < tol
            return _build_result(actual, expected, None, query)

        else:
            return _error_result(query, "unsupported_intent", f"Intent '{intent}' not supported by runner.")

    except Exception as e:
        return _error_result(query, "runner_exception", str(e))


def _build_result(actual, expected, tolerance, query: dict) -> dict:
    """Compare actual vs expected and build a pass/fail result."""
    intent = query.get("intent")

    # Boolean comparison
    if isinstance(expected, bool) or isinstance(actual, bool):
        status = "pass" if bool(actual) == bool(expected) else "fail"
        error = 0 if status == "pass" else 1
        return {
            "status": status,
            "actual": actual,
            "expected": expected,
            "error": error,
            "tolerance": tolerance,
            "feedback": _build_feedback(status, query, actual, expected, tolerance),
        }

    # Integer comparison
    if isinstance(expected, int) and isinstance(actual, int):
        status = "pass" if actual == expected else "fail"
        error = abs(actual - expected)
        return {
            "status": status,
            "actual": actual,
            "expected": expected,
            "error": error,
            "tolerance": tolerance,
            "feedback": _build_feedback(status, query, actual, expected, tolerance),
        }

    # Numeric comparison with tolerance
    try:
        exp_f = float(expected)
        act_f = float(actual)
    except (ValueError, TypeError):
        status = "pass" if actual == expected else "fail"
        return {
            "status": status,
            "actual": actual,
            "expected": expected,
            "error": None,
            "tolerance": tolerance,
            "feedback": _build_feedback(status, query, actual, expected, tolerance),
        }

    err = abs(act_f - exp_f)
    tol = float(tolerance) if tolerance is not None else 0.0
    status = "pass" if err <= tol else "fail"
    return {
        "status": status,
        "actual": round(act_f, 6),
        "expected": exp_f,
        "error": round(err, 6),
        "tolerance": tol,
        "feedback": _build_feedback(status, query, act_f, exp_f, tol),
    }


def _build_feedback(status, query, actual, expected, tolerance) -> dict | None:
    """Build feedback dict if status != 'pass', else None."""
    if status == "pass":
        return None
    intent = query.get("intent", "")
    ft = query.get("feedback_template", "")
    # Format the template with actual/expected
    try:
        msg = ft.replace("{actual}", str(actual)).replace("{expected}", str(expected))
    except Exception:
        msg = f"Query '{intent}' failed: expected={expected}, actual={actual}"
    return {
        "error_type": _classify_error(intent),
        "message": msg,
    }


def _classify_error(intent: str) -> str:
    """Classify the error type for repair-loop consumption."""
    mapping = {
        "body_count": "topology_mismatch",
        "bbox_size": "dimension_mismatch",
        "cylinder_radius": "dimension_mismatch",
        "through_void_count": "feature_mismatch",
        "is_solid": "health_violation",
        "occt_valid": "health_violation",
        "symmetric_about_plane": "symmetry_violation",
    }
    return mapping.get(intent, "unknown_error")


def _error_result(query: dict, error_type: str, message: str) -> dict:
    """Build an error result (runner couldn't execute)."""
    return {
        "status": "error",
        "actual": None,
        "expected": query.get("expected"),
        "error": None,
        "tolerance": query.get("tolerance"),
        "feedback": {"error_type": error_type, "message": message},
    }
