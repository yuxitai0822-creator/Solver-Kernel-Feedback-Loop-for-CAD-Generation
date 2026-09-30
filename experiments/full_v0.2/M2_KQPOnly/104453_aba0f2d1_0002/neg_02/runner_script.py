import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded stadium (ArmRest v1)
    # Dimensions:
    #   straight_length = 500.0 mm (inferred from point span)
    #   radius = 50.0 mm (from curve field)
    #   extrude distance = 100.0 mm
    # Note: The plan's profiles use radius=5.0 and straight_length=50.0 in UV,
    # but the dimensions section says straight_length=500.0 and radius=50.0.
    # The UV coordinates in the curves are scaled by 0.1 relative to the final dimensions.
    # We build the stadium using the explicit dimensions: straight_length=500, radius=50, extrude=100.

    # Build stadium profile: two semicircles of radius 50 connected by lines of length 500.
    # The total width (v-direction) = 2*radius = 100.
    # The total length (u-direction) = straight_length + 2*radius = 500 + 100 = 600.

    # We'll create the profile on the XY plane, then extrude in Z.

    # Points for the stadium:
    # Start at left semicircle center at (0,0), radius 50, from angle 0 to 180 (top semicircle).
    # Then line from (0,50) to (500,50)
    # Then right semicircle center at (500,0), radius 50, from angle 0 to 180 (bottom semicircle? Actually from 180 to 360? Let's trace carefully)
    # The UV curves in the plan:
    #   arc1: center (0,0), radius 5, start_angle=0, end_angle=180 -> top half
    #   line1: (0,-5) to (50,-5) -> bottom line? Wait start_uv (0,-5) to (50,-5) is bottom line.
    #   arc2: center (50,0), radius 5, start_angle=0, end_angle=180 -> top half again? That would overlap.
    #   line2: (50,5) to (0,5) -> top line.
    # Actually the plan's UV coordinates are scaled: radius=5, straight=50. The dimensions say radius=50, straight=500.
    # So we scale by 10.
    # The intended shape: left semicircle (top half), top line from left top to right top, right semicircle (top half? No, bottom half to close), bottom line back.
    # Let's reinterpret: The arcs are both drawn from 0 to 180 degrees, which is the upper semicircle. That would make both arcs on the same side, which is wrong.
    # Actually a stadium shape has two semicircles on opposite ends. One arc is the left end (top half), the other is the right end (bottom half).
    # The start_angle/end_angle in the plan might be relative to the local coordinate system.
    # For a proper stadium: left semicircle from 90 to 270 (or 0 to 180 if oriented differently), right semicircle from 270 to 90 (or 180 to 360).
    # Given the lines: bottom line from (0,-5) to (50,-5) and top line from (50,5) to (0,5), the arcs must connect them.
    # So left arc connects (0,-5) to (0,5) via a semicircle (center (0,0), radius 5, from -90 to 90 degrees? Or from 180 to 0?)
    # Right arc connects (50,5) to (50,-5) via a semicircle (center (50,0), radius 5, from 90 to -90?)
    # The plan says both arcs have start_angle=0, end_angle=180. That would give the upper half for both, which doesn't match the lines.
    # This is likely a coordinate system issue. We'll build the correct stadium shape using the explicit dimensions.

    # Build using CadQuery's built-in methods for simplicity and robustness.

    # Create a workplane
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .stadium(straight_length=500.0, radius=50.0)
        .extrude(100.0)
    )

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0002\\neg_02/generated.step")

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
