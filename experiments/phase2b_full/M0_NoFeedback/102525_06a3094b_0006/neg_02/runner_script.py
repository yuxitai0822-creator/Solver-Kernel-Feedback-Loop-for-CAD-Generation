import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
    # The profile is a rectangle centered at origin in the u-v plane.
    # u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # Extrude in +w direction (positive y) by 3.0mm

    # Create the rectangle profile on the XZ plane (since v_dir is -Z, w_dir is Y)
    # The rectangle spans from -5.65 to 5.65 in u (X) and -1.05 to 1.05 in v (Z)
    # But note: v_dir = (0,0,-1), so positive v maps to negative Z.
    # The start_uv and end_uv coordinates are given in the profile curves.
    # Let's build the rectangle directly using CadQuery's 2D primitives.

    # We'll work in the XZ plane (normal = Y axis), then extrude in +Y direction.
    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .rect(11.3, 2.1)  # length_u=11.3, width_v=2.1? Wait, width_v is 21.0, but the profile shows v from -1.05 to 1.05 = 2.1mm?
        # Actually the design plan says width_v = 21.0, but the profile curves show v range [-1.05, 1.05] which is 2.1.
        # There's a discrepancy: the profile curves are in uv space, and the dimensions say width_v=21.0.
        # The unit conversion note says cm_to_mm (x10). So the profile uv values are in cm? 
        # The profile curves show v from -1.05 to 1.05 (cm) which becomes -10.5 to 10.5 mm = 21.0 mm. Yes!
        # Similarly u from -0.565 to 0.565 (cm) becomes -5.65 to 5.65 mm = 11.3 mm.
        # So we need to scale the profile by 10x to get mm.
        # Let's use the dimensions directly: length_u=11.3, width_v=21.0
        .rect(11.3, 21.0)
        .extrude(3.0)  # extrude in +Y (w direction) by 3.0mm
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102525_06a3094b_0006\neg_02/generated.step")

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
