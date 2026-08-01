import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: Drone Leg Left - square strut
    # Extruded rectangle with dimensions 19mm x 19mm x 200mm
    # The profile is defined in UV coordinates where:
    #   u_dir = [1,0,0] (X axis)
    #   v_dir = [0,0,-1] (negative Z axis)
    #   w_dir = [0,1,0] (Y axis)
    # The rectangle corners in UV are:
    #   (-58.2782, -12.0401) to (-56.3782, -13.9401)
    #   Width in U = 1.9, Width in V = 1.9 (but scaled by 10 from cm to mm = 19mm)
    # Extrude distance = 200.0 mm along +w (Y axis)

    # Build on XY plane, then rotate to match frame orientation
    # Frame: u=X, v=-Z, w=Y
    # So we sketch on XZ plane (u,v) and extrude along Y (w)

    # Create the rectangle on XZ plane
    # The UV coordinates are given in cm, converted to mm by multiplying by 10
    # But the values already appear to be in mm (since they span ~1.9 units)
    # Actually the compiler notes say cm_to_mm (x10) was applied
    # The UV values: -58.2782 to -56.3782 = 1.9 in U direction
    #                -12.0401 to -13.9401 = 1.9 in V direction
    # These are already in mm after conversion

    # Center of rectangle in UV:
    center_u = (-58.27820137826746 + -56.37820137826746) / 2.0
    center_v = (-12.04014576968157 + -13.940145769681571) / 2.0
    width_u = 19.0  # 1.9 * 10
    width_v = 19.0  # 1.9 * 10

    # Create workplane on XZ (since v_dir = -Z, we use XZ plane)
    # The rectangle is centered at (center_u, center_v) in UV space
    # In world coordinates: u=X, v=-Z
    # So center in world: (center_u, 0, -center_v)

    result = (
        cq.Workplane("XZ")
        .center(center_u, -center_v)  # v is negative Z
        .rect(width_u, width_v)
        .extrude(200.0)  # extrude along Y (w direction)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0005\neg_01\iter_00/generated.step"
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
