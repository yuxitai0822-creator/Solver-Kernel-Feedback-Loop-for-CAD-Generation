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

    # Design Plan: extruded rectangle plate
    # Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle corners in uv plane:
    #   (127.82976131535646, -66.34402294937294) to (7.829761315356478, -6.344022949372942)
    #   => width_u = 120.0, width_v = 60.0 (in uv coords)
    #   But dimensions say 1200.0 x 600.0 mm -> scaling factor 10x from cm to mm already applied?
    #   The uv coordinates are in cm? Let's use the explicit dimensions: 1200 x 600 mm
    #   The profile coordinates in the design plan are in cm (since compiler notes say cm_to_mm x10)
    #   So we use the explicit dimensions: 1200 mm x 600 mm, extrude 20 mm

    # Build the plate centered at origin for simplicity, then translate to match bbox_min_corner convention
    # The design plan origin_convention is bbox_min_corner, but we can place it anywhere as long as dimensions match

    # Create workplane on XZ plane (since v_dir is [0,0,-1], w_dir is [0,1,0], u_dir is [1,0,0])
    # Actually: u along X, v along -Z, w along Y -> sketch plane is XZ
    wp = cq.Workplane("XZ")

    # Rectangle centered at origin, dimensions 1200 x 600
    plate = wp.center(0, 0).rect(1200.0, 600.0).extrude(20.0)

    # The plate is now centered at origin, spanning [-600, 600] in X, [-300, 300] in Z, [0, 20] in Y
    # But the design plan expects bbox_min_corner convention. We'll translate so min corner is at origin
    # Current bbox: xmin=-600, ymin=0, zmin=-300
    # Translate by (600, 0, 300) to make min corner at (0,0,0)
    result = plate.translate((600.0, 0.0, 300.0))

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0004\neg_01\iter_00/generated.step"
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
