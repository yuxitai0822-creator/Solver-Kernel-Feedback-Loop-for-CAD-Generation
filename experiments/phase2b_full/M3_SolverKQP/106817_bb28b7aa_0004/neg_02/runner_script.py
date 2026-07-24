import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: washer (extruded annulus)
    # Dimensions (in mm):
    #   Outer radius = 5.5372 mm
    #   Inner radius = 1.9812 mm
    #   Thickness (extrude distance) = 1.3208 mm
    #   Center in UV plane: u=-25.400001, v=12.7
    #   Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    #   Extrude direction: +w (positive y in world)

    # Build the washer by creating a 2D annulus in the XY plane, then extruding along Z.
    # Then rotate/translate to match the design frame.

    # Step 1: Create the outer circle (radius 5.5372) and inner circle (radius 1.9812)
    # We'll use a workplane on XY, draw the outer circle, then cut the inner circle.

    result = (
        cq.Workplane("XY")
        .circle(5.5372)  # outer circle
        .circle(1.9812)  # inner circle (cut)
        .extrude(1.3208)  # extrude along Z (positive direction)
    )

    # Step 2: Transform to match the design frame.
    # The design frame has:
    #   u_dir = (1,0,0)  -> world X
    #   v_dir = (0,0,-1) -> world -Z
    #   w_dir = (0,1,0)  -> world Y
    # Our current part has its normal along Z (extrude direction).
    # We need to rotate so that the normal aligns with w_dir = (0,1,0).
    # That means we rotate -90 degrees about X axis: Z -> Y.
    # Also, the center in UV is at u=-25.400001, v=12.7.
    # In our current coordinate system (before rotation), u = X, v = Y (since we used XY plane).
    # After rotation, u = X, v = -Z, w = Y.
    # So we need to translate by (-25.400001, 0, -12.7) in the rotated frame?
    # Let's think carefully:
    #   After rotation, the part's local frame matches the design frame.
    #   The center in UV is (-25.400001, 12.7).
    #   In the design frame, that means u = -25.400001, v = 12.7.
    #   Since u_dir = X, v_dir = -Z, the world translation is:
    #     world_x = -25.400001
    #     world_z = -12.7 (because v_dir = -Z, so v=12.7 maps to world_z = -12.7)
    #   w = 0 (no offset in w direction).
    # So we translate by (-25.400001, 0, -12.7).

    result = result.rotate((0,0,0), (1,0,0), -90)  # rotate so Z -> Y
    result = result.translate((-25.400001, 0, -12.7))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0004\\neg_02/generated.step")

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
