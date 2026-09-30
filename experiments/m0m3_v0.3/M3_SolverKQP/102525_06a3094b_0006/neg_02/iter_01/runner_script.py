import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: rectangular prism 11.3 x 21.0 x 3.0 mm
    # The kernel feedback showed that the previous script had the axes swapped:
    #   - expected v (width) = 21.0, but got 3.0 (the extrude distance)
    #   - expected w (height) = 3.0, but got 21.0 (the rectangle width)
    # This indicates the rectangle was drawn on the wrong plane or the extrude direction was wrong.
    # The design plan specifies:
    #   - u_dir = [1,0,0] (X axis)
    #   - v_dir = [0,0,-1] (negative Z axis)
    #   - w_dir = [0,1,0] (Y axis)
    # So the profile lies in the XZ plane, and extrude is along Y (w direction).
    # We need to create the rectangle on the XZ plane and extrude along Y.

    # Build the rectangular prism: length_u=11.3 (X), width_v=21.0 (Z), extrude_w=3.0 (Y)
    result = (
        cq.Workplane("XZ")
        .rect(11.3, 21.0)
        .extrude(3.0)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0006\neg_02\iter_01\generated.step"
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
