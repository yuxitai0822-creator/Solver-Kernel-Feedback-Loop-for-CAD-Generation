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

    # Design Plan: extruded rectangle
    # Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle corners in UV space:
    #   start_uv = (121.17356129030935, 31.299551148092803)
    #   end_uv = (-0.7464387096940412, 31.299551148092803)  -> line along U
    #   start_uv = (121.17356129030935, 290.379551148076)
    #   end_uv = (121.17356129030935, 31.299551148092803)    -> line along V
    #   start_uv = (-0.7464387096940412, 290.379551148076)
    #   end_uv = (121.17356129030935, 290.379551148076)      -> line along U
    #   start_uv = (-0.7464387096940412, 31.299551148092803)
    #   end_uv = (-0.7464387096940412, 290.379551148076)      -> line along V
    #
    # The UV coordinates define a rectangle with:
    #   U span = 121.17356129030935 - (-0.7464387096940412) = 121.92 cm = 1219.2 mm
    #   V span = 290.379551148076 - 31.299551148092803 = 259.08 cm = 2590.8 mm
    #
    # The extrude direction is +w = [0,1,0] (Y axis in world)
    # The sketch plane is XZ (since v_dir = [0,0,-1] means V maps to -Z, u_dir = [1,0,0] means U maps to X)
    # So we work on Workplane("XZ") and extrude in Y direction.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108244_329b1876_0000\neg_03\iter_00/generated.step"

    # Rectangle dimensions in mm
    length_u = 1219.2  # along X
    width_v = 2590.8   # along Z (since v_dir = [0,0,-1], positive V maps to negative Z)
    extrude_dist = 44.45  # along Y

    # Build the rectangle on XZ plane
    # The rectangle corners in UV space:
    #   U range: [-0.7464387096940412, 121.17356129030935]  (in cm, but we work in mm)
    #   V range: [31.299551148092803, 290.379551148076]     (in cm, but we work in mm)
    #
    # Convert to mm: multiply by 10 (since 1 cm = 10 mm)
    # But the dimensions already match: 121.92 cm = 1219.2 mm, 259.08 cm = 2590.8 mm
    # So the UV coordinates in the design plan are in cm, but we need to convert to mm.
    # Actually, the design plan says unit is mm, but the compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # The UV coordinates given are in cm (since 121.92 cm = 1219.2 mm).
    # So we need to multiply by 10 to get mm.

    # Let's compute center and size in mm
    u_min_cm = -0.7464387096940412
    u_max_cm = 121.17356129030935
    v_min_cm = 31.299551148092803
    v_max_cm = 290.379551148076

    # Convert to mm
    u_min_mm = u_min_cm * 10
    u_max_mm = u_max_cm * 10
    v_min_mm = v_min_cm * 10
    v_max_mm = v_max_cm * 10

    # Rectangle center in UV space (mm)
    center_u_mm = (u_min_mm + u_max_mm) / 2
    center_v_mm = (v_min_mm + v_max_mm) / 2

    # Rectangle size in UV space (mm)
    size_u_mm = u_max_mm - u_min_mm  # should be 1219.2
    size_v_mm = v_max_mm - v_min_mm  # should be 2590.8

    # Map UV to world coordinates:
    # U -> X (u_dir = [1,0,0])
    # V -> -Z (v_dir = [0,0,-1])
    # So center in world: (center_u_mm, 0, -center_v_mm)
    # Rectangle on XZ plane: width along X = size_u_mm, length along Z = size_v_mm
    # But since V maps to -Z, the rectangle extends from -v_max_mm to -v_min_mm in Z
    # So center Z = -(v_min_mm + v_max_mm)/2 = -center_v_mm

    # Build the workplane
    result = (
        cq.Workplane("XZ")
        .center(center_u_mm, -center_v_mm)
        .rect(size_u_mm, size_v_mm)
        .extrude(extrude_dist)
    )

    # Export
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
