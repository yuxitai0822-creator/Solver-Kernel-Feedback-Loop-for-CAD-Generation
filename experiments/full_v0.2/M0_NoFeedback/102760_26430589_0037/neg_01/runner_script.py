import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: disk with radius 0.8 mm and height 4.0 mm
    # The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the extrusion is along -w, i.e., along negative y-axis.
    # However, for a simple disk, we can create a cylinder along the y-axis.

    # Create a cylinder with radius 0.8 mm and height 4.0 mm
    # The cylinder is centered at origin, axis along y-direction
    result = cq.Workplane("XY").circle(0.8).extrude(4.0)

    # The above creates a cylinder along Z. To match the frame orientation:
    # u_dir = X, v_dir = -Z, w_dir = Y, so we need to rotate the cylinder
    # to align its axis with Y (w_dir).
    # Actually, the extrusion direction is -w = -Y, so the cylinder axis should be Y.
    # Let's create it properly:
    result = cq.Workplane("XZ").circle(0.8).extrude(4.0)  # extrudes along Y

    # Now the cylinder is centered at origin, radius 0.8, height 4.0 along Y
    # The span along u (X) = 1.6, v (Z) = 1.6, w (Y) = 4.0, matching validation intents

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102760_26430589_0037\neg_01/generated.step")

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
