import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded stadium (ArmRest v1)
    # Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
    # Note: The design plan uses a stadium profile with two arcs (radius 5.0) and two lines (length 50.0).
    # However, the dimensions section says straight_length=500.0 and radius=50.0.
    # The profile curves show radius=5.0 and line from (0,-5) to (50,-5) => length 50.
    # This is inconsistent: the curves describe a small stadium (total length 60, width 10),
    # but the dimensions say straight_length=500, radius=50.
    # We follow the explicit dimensions (straight_length=500, radius=50) as the intended size.
    # The profile curves in the plan are likely a scaled representation; we use the dimension values.

    # Build stadium profile: two semicircles of radius 50, connected by lines of length 500.
    # Total width = 2*radius = 100, total length = straight_length + 2*radius = 600.
    # Center the profile at origin for convenience.

    radius = 50.0
    straight_length = 500.0
    extrude_distance = 100.0

    # Create the stadium profile using CadQuery's 2D construction
    # We'll build a wire from arcs and lines

    # Points:
    # Left arc center at (0, 0), right arc center at (straight_length, 0)
    # Left arc from angle 90 to -90 (top to bottom) -> actually from 90 to -90 going clockwise
    # But easier: use CadQuery's two-point arc or build with workplane

    # Approach: Use a workplane and sketch the stadium
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(0, radius)  # start at top of left arc
        .threePointArc((0, -radius), (0, -radius))  # arc from top to bottom through leftmost point? No, need proper arc
    )

    # Better: Use the built-in slot function which creates a stadium shape
    # cq.Workplane("XY").slot2D(straight_length + 2*radius, radius, angle=0)
    # But slot2D creates a slot with total length = length + 2*radius, width = 2*radius
    # That matches: total length = straight_length + 2*radius = 600, width = 2*radius = 100

    result = (
        cq.Workplane("XY")
        .slot2D(straight_length + 2*radius, radius, angle=0)  # creates a stadium shape centered at origin
        .extrude(extrude_distance)
    )

    # The slot2D creates a shape with total length = straight_length + 2*radius = 600, width = 2*radius = 100
    # This matches the validation intents: span_u=600, span_v=100, span_w=100

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0002\\neg_03/generated.step")

import cadquery as _cq_auto
_INSTANTIATED_WORKPLANES = []
_orig_wp_init = _cq_auto.Workplane.__init__
def _hooked_wp_init(self, *args, **kwargs):
    _INSTANTIATED_WORKPLANES.append(self)
    return _orig_wp_init(self, *args, **kwargs)
_cq_auto.Workplane.__init__ = _hooked_wp_init

def _export_latest_wp(OUT_STEP_PATH):
    if not _INSTANTIATED_WORKPLANES:
        return False, "no_workplane_created"
    wp = _INSTANTIATED_WORKPLANES[-1]
    try:
        solid_or_compound = wp.val() if hasattr(wp, "val") else wp
        _cq_auto.exporters.export(solid_or_compound, OUT_STEP_PATH)
        return True, "ok"
    except Exception as e:
        return False, f"export_error: {e}"

try:
    _user_main()
    out_path = os.environ.get("OUT_STEP_PATH", "")
    if out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(json.dumps({"status": "ok", "out_step": out_path}))
    else:
        ok, reason = _export_latest_wp(out_path) if out_path else (False, "no_out_path")
        if ok and out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            print(json.dumps({"status": "ok_autoexport", "out_step": out_path}))
        else:
            print(json.dumps({"status": "no_step_written", "out_step": out_path, "autoexport_reason": reason}))
except Exception as e:
    print(json.dumps({"status": "exception",
                       "error": str(e),
                       "traceback": traceback.format_exc()[-500:]}))
