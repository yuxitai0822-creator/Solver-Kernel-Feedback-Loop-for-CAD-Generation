import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0004\neg_03\iter_01\generated.step"

    # Design Plan: rectangular prism with dimensions 8.5mm x 18.0mm x 2.5mm
    # The profile is a rectangle centered at origin in the XY plane
    # Extrude in +Z direction by 2.5mm
    #
    # Kernel feedback from iteration 0 showed that the bbox axes were swapped:
    #   - expected v (Y) span = 18.0, actual = 2.5
    #   - expected w (Z) span = 2.5, actual = 18.0
    # This indicates the rectangle was created with width=8.5 (X) and height=18.0 (Y),
    # but the extrude direction was +Z, which is correct. The issue is that the
    # Design Plan's frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0].
    # So the rectangle's 'width' (8.5) maps to u (X), 'height' (18.0) maps to v (Z negative),
    # and extrude direction is +w = +Y.
    # To match the expected bbox: u=8.5 (X), v=18.0 (Z), w=2.5 (Y).
    # We create the rectangle on the XZ plane (front) with width=8.5 (X) and height=18.0 (Z),
    # then extrude in +Y direction by 2.5.

    # Create workplane on XZ plane (front)
    wp = cq.Workplane("XZ")

    # Create rectangle centered at origin with width=8.5 (along X) and height=18.0 (along Z)
    profile = wp.center(0, 0).rect(8.5, 18.0)

    # Extrude in +Y direction by 2.5mm
    result = profile.extrude(2.5)

    # Export to STEP file
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
