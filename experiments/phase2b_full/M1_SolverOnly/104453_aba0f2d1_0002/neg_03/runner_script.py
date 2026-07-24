import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded_stadium
    # Dimensions:
    #   straight_length = 500.0 mm (inferred from point span)
    #   radius = 50.0 mm (from curve_field)
    #   extrude_distance = 100.0 mm
    #
    # The stadium profile is defined in the UV plane (u = x, v = y).
    # The profile consists of:
    #   - Arc at left end: center (0,0), radius 5.0, from 0° to 180° (top half)
    #   - Top line: from (0,5) to (50,5)
    #   - Arc at right end: center (50,0), radius 5.0, from 0° to 180° (top half)
    #   - Bottom line: from (50,-5) to (0,-5)
    #
    # However, the dimensions section says straight_length=500.0 and radius=50.0.
    # The curves in the profile use radius=5.0 and straight length=50.0 (from (0,-5) to (50,-5)).
    # This is a scaling inconsistency: the curves describe a small stadium (total length 60, width 10),
    # but the dimensions say 500x100. The design plan likely intends the larger size.
    # We will scale the profile to match the dimensions: straight_length=500, radius=50.
    # So the profile becomes:
    #   - Arc left: center (0,0), radius 50, from 0° to 180° (top half)
    #   - Top line: from (0,50) to (500,50)
    #   - Arc right: center (500,0), radius 50, from 0° to 180° (top half)
    #   - Bottom line: from (500,-50) to (0,-50)
    #
    # The extrude is along +w (z-axis) by 100 mm.

    # Build the stadium profile using CadQuery's 2D construction.
    # We'll create a workplane on the XY plane (z=0).

    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(0, 50)  # start at top of left arc
        .threePointArc((0, -50), (0, -50))  # left arc from top to bottom (180°)
        .lineTo(500, -50)  # bottom line
        .threePointArc((500, 50), (500, 50))  # right arc from bottom to top (180°)
        .lineTo(0, 50)  # top line back to start
        .close()
        .extrude(100.0)  # extrude along +z by 100 mm
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\104453_aba0f2d1_0002\neg_03/generated.step")

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
