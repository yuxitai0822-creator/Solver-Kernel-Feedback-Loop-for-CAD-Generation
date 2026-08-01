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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0004\neg_03\iter_00/generated.step"

    # Design Plan: extruded rectangle
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Rectangle dimensions: length_u=1200.0 mm, width_v=600.0 mm
    # Extrude distance: 20.0 mm along +w direction
    # The rectangle profile is defined in UV space with corners:
    #   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
    #   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
    #   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
    #   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
    # The UV coordinates span: u from 7.82976 to 127.82976 (delta=120.0), v from -66.34402 to -6.34402 (delta=60.0)
    # But the design plan says length_u=1200.0 and width_v=600.0, so there's a scaling factor of 10x.
    # The original data was in cm and converted to mm (x10). The UV coordinates appear to be in cm originally.
    # We'll build the rectangle with the correct dimensions in mm.

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # The frame: u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
    # So the sketch plane is XZ, and extrude direction is +Y (w_dir)

    # Create the rectangle centered at origin with dimensions 1200 x 600
    result = (
        cq.Workplane("XZ")
        .rect(1200.0, 600.0, centered=True)
        .extrude(20.0)
    )

    # Export to STEP
    import os
    os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
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
