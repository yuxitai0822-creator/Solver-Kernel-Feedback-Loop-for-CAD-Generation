import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: SOP-28 (1) rectangular prism
    # Dimensions: length_u = 8.5 mm, width_v = 18.0 mm, extrude_distance = 2.5 mm
    # Frame: u_dir = [1, 0, 0], v_dir = [0, 0, -1], w_dir = [0, 1, 0]
    # Origin convention: bbox_min_corner

    # The profile rectangle spans from u=-0.425 to u=0.425 (length 8.5mm) and v=-0.9 to v=0.9 (width 18.0mm).
    # In CadQuery, we sketch on the XZ plane (u=X, v=Z) centered at origin, then extrude along Y (w_dir).
    # Since v_dir is [0, 0, -1], the Z axis in CadQuery maps to -v. 
    # To ensure the bbox_min_corner is at the origin, we shift the sketch by half the dimensions in the positive Z direction.

    result = (
        cq.Workplane("XZ")
        .center(0, 9.0)  # Shift center up by half width (18.0/2 = 9.0) so bbox Z_min is 0
        .rect(8.5, 18.0)  # Length along X (u), Width along Z (v)
        .extrude(2.5)     # Extrude along +Y (w_dir)
    )

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102525_06a3094b_0004\neg_01/generated.step"
    cq.exporters.export(result, OUT_STEP_PATH)

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
