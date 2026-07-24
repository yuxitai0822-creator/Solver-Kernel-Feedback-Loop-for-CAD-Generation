import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate/panel)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # The profile rectangle is defined in UV space with u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle corners in UV: 
    #   start_uv = (121.17356129030935, 31.299551148092803)
    #   end_uv = (-0.7464387096940412, 31.299551148092803)  -> this is the other corner along u
    #   Actually the curves define a rectangle with u range [-0.7464, 121.1736] and v range [31.2996, 290.3796]
    #   So width in u = 121.1736 - (-0.7464) = 121.92 cm = 1219.2 mm (matches length_u)
    #   Width in v = 290.3796 - 31.2996 = 259.08 cm = 2590.8 mm (matches width_v)
    # The extrude is along +w direction (0,1,0) by 44.45 mm

    # Build the rectangle in the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
    # To match the frame: u along X, v along -Z, w along Y
    # So the rectangle lies in the XZ plane (since u and v axes are X and -Z)
    # We'll create a rectangle on the XZ plane, then extrude along Y

    # The rectangle corners in UV: u from -0.7464387096940412 to 121.17356129030935, v from 31.299551148092803 to 290.379551148076
    # In XYZ: x = u, z = -v (since v_dir = (0,0,-1)), y = 0 initially

    # Compute corners:
    x_min = -0.7464387096940412
    x_max = 121.17356129030935
    z_min = -290.379551148076  # because v_max -> -v_max
    z_max = -31.299551148092803  # because v_min -> -v_min

    # Create the rectangle on the XZ plane (y=0)
    result = (cq.Workplane("XZ")
              .center((x_min + x_max)/2, (z_min + z_max)/2)
              .rect(x_max - x_min, z_max - z_min)
              .extrude(44.45))  # extrude along Y (positive)

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108244_329b1876_0000\neg_03/generated.step")

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
