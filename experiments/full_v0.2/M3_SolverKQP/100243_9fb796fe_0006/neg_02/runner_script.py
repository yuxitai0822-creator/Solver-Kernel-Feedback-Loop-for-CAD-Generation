import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (square strut)
    # Profile: rectangle 19mm x 19mm, extrude 130mm along w direction
    # Frame: u = (1,0,0), v = (0,0,-1), w = (0,1,0)
    # Origin convention: bbox_min_corner -> profile center at (0,0,0) after shift

    # Build the rectangle profile in the uv-plane (u=x, v=-z)
    # Profile vertices from design plan (in uv coordinates):
    #   (-58.2782, -12.0401) to (-58.2782, -13.9401) etc.
    # But these are absolute positions; we want a 19x19 rectangle centered at origin.
    # The design plan dimensions: length_u=19, width_v=19.
    # So we create a rectangle centered at (0,0) with size 19x19.

    # Create workplane on XY plane, then adjust to match frame orientation.
    # Frame: u = X, v = -Z, w = Y.
    # So we sketch on XZ plane (since v = -Z) but we need v direction = (0,0,-1).
    # Simpler: use XY plane, then rotate/translate.
    # Actually, we can just create the rectangle on XY plane and extrude along Y (w direction).
    # But the profile uv coordinates are in the plane with normal w = (0,1,0).
    # So the profile lies in the XZ plane (since u=x, v=-z).
    # Let's use workplane on XZ plane (front plane in cq).

    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .rect(19.0, 19.0)
        .extrude(130.0)
    )

    # The resulting solid is centered at origin in X and Z, extends 130mm in Y.
    # This matches the design plan: span_u=19 (X), span_v=19 (Z), span_w=130 (Y).

    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\100243_9fb796fe_0006\neg_02/generated.step")

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
