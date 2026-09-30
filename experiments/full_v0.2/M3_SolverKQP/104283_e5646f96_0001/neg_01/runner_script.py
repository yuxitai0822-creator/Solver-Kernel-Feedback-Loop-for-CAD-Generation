import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Extruded profile with a circular hole
    # The profile consists of an outer shape (rectangle with rounded corners approximated by a circle at the top)
    # and an inner circular hole.
    # Based on the design plan, the profile is defined in the UV plane (XY plane in CadQuery).
    # The outer profile is a composite of lines and a circle (arc).
    # The inner profile is a circle.
    # Extrude distance: 18.0 mm in the +Z direction.

    # Define the points for the outer profile based on the design plan curves.
    # The curves are:
    # 1. Line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
    # 2. Line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
    # 3. Line from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
    # 4. Circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.4
    # Note: The circle at the top connects the two vertical lines, forming a rounded top.
    # The circle center is at y=1.749, radius 1.4, so it extends from y=0.349 to y=3.149.
    # The vertical lines end at y=1.7937, which is close to the circle's top (1.749+1.4=3.149).
    # This suggests the circle is tangent to the vertical lines.
    # We'll construct the outer wire using lines and an arc.

    # However, the design plan shows two profiles: one outer ring and one inner ring.
    # The outer ring has 4 curves: line, line, line, circle.
    # The inner ring is a circle with radius 1.25, concentric with the outer circle.

    # Let's reconstruct the outer profile as a closed wire.
    # The outer shape is like a rectangle with a circular top.
    # Bottom: from (0.9188, 0) to (3.8000, 0) - horizontal line
    # Right side: from (3.7174, 0) to (3.7174, 1.7937) - vertical line
    # Top: circular arc from (3.7174, 1.7937) to (0.9188, 1.7937) with center (2.3181, 1.7491) radius 1.4
    # Left side: from (0.9188, 1.7937) to (0.9188, 0) - vertical line

    # Note: The circle radius is 1.4, center y=1.7491, so the circle extends from y=0.3491 to y=3.1491.
    # The vertical lines end at y=1.7937, which is on the circle (distance from center: sqrt((3.7174-2.3181)^2 + (1.7937-1.7491)^2) = sqrt(1.3993^2 + 0.0446^2) ≈ 1.4).
    # So the circle passes through the endpoints of the vertical lines.

    # We'll build the profile using CadQuery's 2D construction.

    # Create the outer wire
    outer_wire = (
        cq.Workplane("XY")
        .moveTo(0.9188335453558412, 1.7936743887554851)  # start at top-left
        .lineTo(0.9188335453558412, 0.0)  # left side down
        .lineTo(3.8000000566244125, 0.0)  # bottom edge
        .lineTo(3.7174115708793822, 0.0)  # move to right side start (note: this is a redundant point, but we follow the plan)
        .lineTo(3.7174115708793822, 1.7936743887554851)  # right side up
        .threePointArc(
            (2.3181225581176115, 3.149062072471865),  # top point of circle (center + radius in y)
            (0.9188335453558412, 1.7936743887554851)  # back to start
        )
        .close()
        .wire()
    )

    # Create the inner circle (hole)
    inner_circle = (
        cq.Workplane("XY")
        .circle(1.2500000000000002)
        .wire()
    )

    # Combine into a face with a hole
    # We need to create a planar face from the outer wire and subtract the inner circle.
    # Using CadQuery's approach: create a workplane, add the outer wire, cut the inner circle.

    # Build the base face
    result = (
        cq.Workplane("XY")
        .moveTo(0.9188335453558412, 1.7936743887554851)
        .lineTo(0.9188335453558412, 0.0)
        .lineTo(3.8000000566244125, 0.0)
        .lineTo(3.7174115708793822, 0.0)
        .lineTo(3.7174115708793822, 1.7936743887554851)
        .threePointArc(
            (2.3181225581176115, 3.149062072471865),
            (0.9188335453558412, 1.7936743887554851)
        )
        .close()
        .extrude(18.0)  # extrude the outer shape
    )

    # Now cut the inner hole
    # The inner hole is a circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.25
    # We need to extrude a circle through the entire part.
    result = (
        result
        .faces(">Z")  # select the top face
        .workplane()
        .circle(1.2500000000000002)
        .cutThruAll()  # cut through the entire part
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104283_e5646f96_0001\\neg_01/generated.step")

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
