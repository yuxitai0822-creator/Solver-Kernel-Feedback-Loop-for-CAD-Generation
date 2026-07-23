import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    # Ensure output directory exists
    OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\108851_4d515b10_0007\neg_02"
    OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
    os.makedirs(OUT_DIR, exist_ok=True)

    # Dimensions from design plan (converted from cm to mm)
    length_u = 279.4  # mm
    width_v = 50.8    # mm
    extrude_w = 19.05 # mm

    # Build the extruded rectangle
    # The frame specifies u_dir=[1,0,0] (X), v_dir=[0,0,-1] (Z down), w_dir=[0,1,0] (Y)
    # Origin is at bbox_min_corner. We sketch on the XY plane (u=X, w=Y) and extrude along Z.
    # The v_dir being -Z means the profile's V axis maps to -Z in 3D, so the rectangle
    # width in the sketch (Y direction) corresponds to width_v in 3D (-Z direction).
    # Since CadQuery extrudes +Z by default, and w_dir is +Y, we rotate the result.

    result = (
        cq.Workplane("XY")
        .rect(length_u, width_v)
        .extrude(extrude_w)
        .rotate((0, 0, 0), (1, 0, 0), 90)  # Rotate +90 deg around X to map Z->Y
    )

    # Translate so the bounding box minimum corner is at the origin (0, 0, 0)
    bbox = result.val().BoundingBox()
    result = result.translate((-bbox.xmin, -bbox.ymin, -bbox.zmin))

    # Export to STEP
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
