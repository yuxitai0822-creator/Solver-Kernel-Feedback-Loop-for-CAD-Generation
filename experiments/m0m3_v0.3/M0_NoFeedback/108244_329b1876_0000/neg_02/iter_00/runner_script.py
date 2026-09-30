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

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # Profile rectangle corners in UV space:
    #   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
    # Note: The design plan coordinates are in UV space; we need to map to XYZ.
    #   U -> X, V -> -Z (since v_dir = [0,0,-1]), W -> Y
    # So rectangle in XZ plane: X from -0.7464 to 121.1736, Z from -290.3796 to -31.2996
    # Width in X = 121.92, Width in Z = 259.08 (but expected spans are 1219.2 and 2590.8)
    # The design plan says unit conversion cm->mm (x10), so the UV values are in cm?
    # Actually the plan says "unit_conversion_applied": "cm_to_mm (x10)"
    # So the UV coordinates are in cm, need to multiply by 10 to get mm.
    # Let's check: span in U = 121.1736 - (-0.7464) = 121.92 cm = 1219.2 mm ✓
    # Span in V = 290.3796 - 31.2996 = 259.08 cm = 2590.8 mm ✓
    # So we scale UV coordinates by 10 to get mm.

    scale = 10.0

    # UV corners in cm
    uv_corners = [
        (121.17356129030935, 31.299551148092803),
        (-0.7464387096940412, 31.299551148092803),
        (-0.7464387096940412, 290.379551148076),
        (121.17356129030935, 290.379551148076)
    ]

    # Convert to XYZ in mm: X = U*scale, Z = -V*scale (since v_dir = [0,0,-1]), Y = 0 (sketch plane)
    pts_mm = [(u*scale, 0.0, -v*scale) for u, v in uv_corners]

    # Build the rectangle on XZ plane (Y=0)
    result = (
        cq.Workplane("XZ")
        .moveTo(pts_mm[0][0], pts_mm[0][2])
        .lineTo(pts_mm[1][0], pts_mm[1][2])
        .lineTo(pts_mm[2][0], pts_mm[2][2])
        .lineTo(pts_mm[3][0], pts_mm[3][2])
        .close()
        .extrude(44.45)  # extrude along Y (positive Y = +w direction)
    )

    # Export
    out_path = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108244_329b1876_0000\neg_02\iter_00/generated.step"
    exporters.export(result, out_path)

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
