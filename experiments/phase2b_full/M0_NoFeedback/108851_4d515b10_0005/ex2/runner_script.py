import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: SoapCutterBedBack1 v1
    # Part: flat_plate_or_panel, extruded rectangle
    # Dimensions: length_u=307.848 mm, width_v=19.05 mm, extrude_distance=12.7 mm
    # Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    # Origin at bbox_min_corner, so we place the rectangle in the XY plane (u,v) and extrude along w (Y axis)

    # Create the rectangular profile in the XY plane (u = X, v = Z, but v_dir is (0,0,-1) so we use Z negative)
    # The profile is defined in UV space: u from 0 to 307.848, v from 0 to 19.05
    # Since v_dir is (0,0,-1), v=0 maps to Z=0, v=19.05 maps to Z=-19.05
    # We'll create the rectangle with width along X and height along Z (negative direction)

    result = (
        cq.Workplane("XY")
        .rect(307.848, 19.05)  # width along X, height along Z
        .extrude(12.7)  # extrude along Y (positive direction)
    )

    # The resulting part should have:
    # - Span along X: 307.848 mm
    # - Span along Z: 19.05 mm
    # - Span along Y: 12.7 mm
    # This matches the design plan dimensions.

    import cadquery as cq
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0005\\ex2/generated.step")

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
