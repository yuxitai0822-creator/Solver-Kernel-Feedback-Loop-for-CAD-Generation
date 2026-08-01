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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0004\neg_01\iter_00/generated.step"

    # Design Plan: extruded rectangle
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Rectangle in uv-plane: u from 7.82976 to 127.82976, v from -66.34402 to -6.34402
    # Extrude along +w (y-axis) by 20.0 mm

    # Compute rectangle parameters
    x_min = 7.829761315356478
    y_min = -66.34402294937294
    x_max = 127.82976131535646
    y_max = -6.344022949372942

    width = x_max - x_min  # 120.0 mm
    height = y_max - y_min  # 60.0 mm (but design says 600? Let's check: v span = 60.0, but design says 600.0? Actually v_dir is [0,0,-1], so v is along z. The uv coordinates: v from -66.34 to -6.34 = 60.0. But design says width_v=600.0. There's a 10x factor from cm->mm conversion. The original data was in cm, converted to mm by x10. So 60.0 cm = 600.0 mm. But the uv coordinates are already in mm? Let's check: start_uv = [127.82976, -66.34402] - these are in mm after conversion? Actually the design plan says unit_conversion_applied: cm_to_mm (x10). So the uv coordinates are in mm. The span in u is 120.0 mm, but design says 1200.0 mm. There's inconsistency. Let's use the design plan dimensions: length_u=1200.0, width_v=600.0, extrude=20.0. The uv coordinates are just for placement. We'll center the rectangle at the midpoint of the uv coordinates.

    # Actually, let's use the design plan dimensions directly
    length_u = 1200.0  # mm
    width_v = 600.0    # mm
    extrude_depth = 20.0  # mm

    # Frame: u=x, v=-z, w=y
    # So rectangle in xz-plane, extruded along y
    # Center at midpoint of uv coordinates
    cx = (x_min + x_max) / 2  # 67.82976
    cy = (y_min + y_max) / 2  # -36.34402

    # But v_dir is [0,0,-1], so v coordinate maps to -z
    # So center in xz: x=cx, z=-cy
    center_x = cx
    center_z = -cy  # 36.34402

    # Build the plate
    result = (
        cq.Workplane("XZ")
        .moveTo(center_x, center_z)
        .rect(length_u, width_v, centered=True)
        .extrude(extrude_depth)
    )

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
