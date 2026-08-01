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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0005\neg_03\iter_00/generated.step"

    # Design Plan: extruded rectangle (square strut)
    # Profile: rectangle 19.0mm x 19.0mm (after unit conversion from cm)
    # Extrude: 200.0mm along +w direction (which is +Y in world frame)
    # The frame has u_dir = +X, v_dir = -Z, w_dir = +Y
    # So we work on XZ plane and extrude in +Y direction

    # Build the rectangle profile on XZ plane
    # From the curves, the rectangle spans from x=-58.278 to x=-56.378 (width=1.9cm=19mm)
    # and z from -13.940 to -12.040 (height=1.9cm=19mm)
    # But the design plan says length_u=19.0, width_v=19.0, so we use those dimensions
    # centered at the midpoint of the given coordinates

    x_center = (-58.27820137826746 + -56.37820137826746) / 2.0  # = -57.32820137826746
    z_center = (-13.940145769681571 + -12.04014576968157) / 2.0  # = -12.99014576968157
    width = 19.0  # mm (1.9 cm converted)
    height = 19.0  # mm

    # Create workplane on XZ (since v_dir = -Z, u_dir = X, normal = Y)
    result = (cq.Workplane("XZ")
              .center(x_center, z_center)
              .rect(width, height)
              .extrude(200.0))  # extrude along +Y (normal of XZ plane)

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
