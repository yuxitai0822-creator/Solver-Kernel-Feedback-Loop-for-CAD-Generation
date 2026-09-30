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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_03\iter_00/generated.step"

    # Design Plan: extruded rectangle (square strut)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile: rectangle in uv-plane, centered at origin
    # Rectangle dimensions: length_u=19.0, width_v=19.0
    # Extrude distance: 130.0 mm along +w (y-axis)

    # Build on XY plane, then rotate to match frame orientation
    # Frame: u=x, v=-z, w=y
    # So we sketch on XZ plane (u,v) and extrude along Y (w)

    # Rectangle corners in uv coordinates (from design plan curves):
    # u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9? Wait, that's 1.9 not 19.0
    # Actually the design plan says length_u=19.0, width_v=19.0
    # The curves show a small rectangle: width = -56.378 - (-58.278) = 1.9, height = -12.04 - (-13.94) = 1.9
    # But the dimensions say 19.0. The perturbation changed 1.9 to 1.52 (20% reduction)
    # The original was 1.9 cm = 19 mm, perturbed to 1.52 cm = 15.2 mm
    # So we use 15.2 mm for both sides

    # Let's center the rectangle at origin for simplicity
    # The frame says u_dir=[1,0,0], v_dir=[0,0,-1], so sketch on XZ plane
    # Rectangle centered at origin, size 15.2 x 15.2

    size = 15.2  # mm (perturbed from 19.0)
    extrude_dist = 130.0  # mm

    # Build on XZ plane (cq.Workplane("XZ"))
    # rect() creates rectangle centered at current point
    result = (cq.Workplane("XZ")
              .rect(size, size)
              .extrude(extrude_dist))

    # The extrusion direction is along Y (normal to XZ plane), which matches w_dir=[0,1,0]
    # The rectangle is centered at origin, which is fine

    exporters.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
