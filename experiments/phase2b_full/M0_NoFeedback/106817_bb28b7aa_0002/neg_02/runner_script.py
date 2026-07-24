import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: thumb screw (disk)
    # Extruded circle with radius 4.87045 mm and height 6.8707 mm
    # The profile circle center is at (11.43, 0) in UV, but the frame indicates
    # u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # The circle center_uv = [11.430000364780426, 0.0] and radius = 0.48704499999999984
    # Wait, the profile radius is 0.487, but the dimension says radius = 4.87045.
    # The profile curves have radius 0.487, but the dimensions say radius 4.87045.
    # The compiler notes unit conversion cm_to_mm (x10). So the profile radius 0.487 cm = 4.87 mm.
    # The center_uv = [11.43, 0] in cm? Actually 11.43 cm = 114.3 mm, but dimensions show center_uv = [114.300004, 0.0] in mm.
    # So the profile curves radius is 0.48704499999999984 (in cm? or mm?) 
    # Let's use the explicit dimension radius = 4.87045 mm and center at (114.3, 0) mm.
    # But the frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # The circle is in the UV plane, so it lies in the X-Z plane (since v_dir is along Z negative).
    # Extrude direction is +w = (0,1,0) i.e. along Y axis.
    # So we create a circle centered at (114.3, 0) in the X-Z plane, radius 4.87045, then extrude along Y by 6.8707 mm.

    result = (
        cq.Workplane("XZ")
        .circle(4.87045)
        .extrude(6.8707)
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\106817_bb28b7aa_0002\neg_02/generated.step")

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
