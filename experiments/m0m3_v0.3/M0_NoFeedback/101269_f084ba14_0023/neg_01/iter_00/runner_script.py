import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101269_f084ba14_0023\neg_01\iter_00/generated.step"

    # Design Plan dimensions (in mm, after cm->mm conversion x10):
    # Rectangle: 95.25 mm (u) x 571.5 mm (v)
    # Extrude: 19.05 mm (w direction)
    # The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # So the rectangle lies in the XZ plane (u along X, v along -Z)
    # Extrude along +w = +Y direction

    # Build the rectangle in the XZ plane
    # The rectangle corners in UV space: (0,0), (9.525,0), (9.525,57.15), (0,57.15)
    # But these are in UV coordinates. The actual dimensions are:
    # u span = 95.25 mm, v span = 571.5 mm
    # The UV coordinates given are scaled by 10 (since original was in cm, converted to mm)
    # Actually, looking at the curves: start_uv and end_uv values are 9.525 and 57.15
    # These are the actual mm values after conversion (0.9525 cm * 10 = 9.525 mm? No, that's wrong)
    # Let's re-examine: The design plan says length_u = 95.25 mm, width_v = 571.5 mm
    # But the curves show values like 9.525 and 57.15. This is because the original was in cm
    # and the compiler multiplied by 10. So 9.525 cm = 95.25 mm, 57.15 cm = 571.5 mm.
    # The curves already have the mm values. So the rectangle is 95.25 x 571.5 mm.

    # Create workplane on XZ plane (since v_dir = [0,0,-1], the sketch plane normal is along v cross u?)
    # Actually, the frame says: u_dir = X, v_dir = -Z, w_dir = Y
    # So the sketch plane is the XZ plane (u and v axes), extrude along Y (w)

    # Build the rectangle centered at origin for simplicity
    # Rectangle dimensions: 95.25 mm (along X) x 571.5 mm (along Z)
    # But v_dir is [0,0,-1], so the v dimension goes along -Z
    # We'll build the rectangle in the XZ plane

    result = (
        cq.Workplane("XZ")
        .rect(95.25, 571.5, centered=True)
        .extrude(19.05)  # extrude along +Y (w direction)
    )

    # Verify the result is a valid solid
    if not result.val().isValid():
        # Fallback: build from points to ensure correct orientation
        pts = [
            (-95.25/2, -571.5/2),
            (95.25/2, -571.5/2),
            (95.25/2, 571.5/2),
            (-95.25/2, 571.5/2),
        ]
        result = (
            cq.Workplane("XZ")
            .polyline(pts)
            .close()
            .extrude(19.05)
        )

    exporters.export(result, OUT_STEP_PATH)

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
