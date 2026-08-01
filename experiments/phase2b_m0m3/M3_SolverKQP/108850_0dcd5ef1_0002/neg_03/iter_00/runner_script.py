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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108850_0dcd5ef1_0002\neg_03\iter_00\generated.step"

    # Design Plan parameters (all in mm)
    # Rectangle profile: length_u = 171.45, width_v = 38.1
    # Extrude distance: 6.35
    # The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means: u = X, v = -Z, w = Y
    # The profile is defined in UV space, where:
    #   start_uv = (0.0, 3.81) -> end_uv = (0.0, 0.0)  (v direction)
    #   start_uv = (0.0, 0.0) -> end_uv = (17.145, 0.0) (u direction)
    #   start_uv = (17.145, 0.0) -> end_uv = (17.145, 3.81) (v direction)
    #   start_uv = (17.145, 3.81) -> end_uv = (0.0, 3.81) (u direction)
    # Note: The UV coordinates are given in cm (from compiler notes: cm_to_mm x10)
    # So we multiply by 10 to get mm:
    #   u values: 0.0, 17.145 -> 0.0, 171.45 mm
    #   v values: 0.0, 3.81 -> 0.0, 38.1 mm
    # The rectangle in UV space has width = 171.45 mm (u), height = 38.1 mm (v)
    #
    # Mapping to world coordinates:
    #   u -> X
    #   v -> -Z (since v_dir = [0,0,-1])
    #   w -> Y (extrude direction)
    #
    # So the rectangle lies in the XZ plane, with:
    #   X from 0 to 171.45
    #   Z from -38.1 to 0 (since v=0 maps to Z=0, v=38.1 maps to Z=-38.1)
    # Extrude in +Y direction by 6.35 mm

    # Build the rectangle in the XZ plane
    # Using Workplane("XZ") which gives us the XZ plane
    wp = cq.Workplane("XZ")

    # The rectangle corners in world coordinates:
    # (0, 0, 0) -> (171.45, 0, 0) -> (171.45, 0, -38.1) -> (0, 0, -38.1)
    # Center at (85.725, 0, -19.05)
    # Width = 171.45 (along X), Height = 38.1 (along Z)

    # Create the rectangle centered at the midpoint
    result = (
        wp
        .center(85.725, -19.05)  # center in XZ plane
        .rect(171.45, 38.1, centered=True)
        .extrude(6.35)  # extrude in +Y direction
    )

    # Export
    importers = None
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
