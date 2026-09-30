import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: flat_plate_or_panel, extruded rectangle
    # Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
    # The profile rectangle corners in UV space are:
    #   (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
    # These are in UV coordinates where U is along x-axis, V along y-axis.
    # The rectangle spans from -121.92 to 121.92 in U (total 243.84) and -60.96 to 60.96 in V (total 121.92).
    # However, the design plan dimensions say length_u = 2438.4 and width_v = 1219.2.
    # This is a 10x scaling factor. The UV coordinates in the profile are in cm (converted from original cm to mm?)
    # Actually, the compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # So the original dimensions were 243.84 cm x 121.92 cm x 1.27 cm, which become 2438.4 mm x 1219.2 mm x 12.7 mm.
    # The UV coordinates given (121.92, -60.96) etc. are in cm? Let's check: 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm.
    # But the rectangle from -121.92 to 121.92 in U gives 243.84 total, not 2438.4.
    # So the UV coordinates are in some other unit. The design plan says unit is mm.
    # The profile curves show start_uv and end_uv values. These define the shape in the sketch plane.
    # The dimensions section says length_u = 2438.4 mm, width_v = 1219.2 mm.
    # So the rectangle should span 2438.4 mm in U and 1219.2 mm in V.
    # The UV coordinates given are likely in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm).
    # But the span from -121.92 to 121.92 is 243.84, not 2438.4. So there's a factor of 10 discrepancy.
    # Actually, 121.92 * 10 = 1219.2, and 60.96 * 10 = 609.6. So the UV coordinates are in cm, and we need to multiply by 10 to get mm.
    # But the rectangle from -121.92 to 121.92 in U gives 243.84 cm = 2438.4 mm. Yes! That matches.
    # So the UV coordinates are in cm, and we need to scale by 10 to get mm.
    # Let's build the rectangle centered at origin with dimensions 2438.4 x 1219.2 mm.

    # Build the plate
    result = (
        cq.Workplane("XY")
        .rect(2438.4, 1219.2, centered=True)
        .extrude(12.7)
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108412_8de2f9c3_0000\neg_03\iter_00\generated.step"
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
