import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
    # The rectangle is centered on the origin in the XY plane, extruded in +Z direction.

    # Create the rectangle profile centered at origin
    # The profile vertices from the plan (in UV coordinates) are:
    #   (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
    # These are in cm? Actually the plan says unit_conversion_applied: cm_to_mm (x10)
    # So the original cm values were 12.192 x 6.096 cm, converted to mm: 121.92 x 60.96 mm
    # But the dimensions say length_u = 2438.4 mm, width_v = 1219.2 mm
    # 2438.4 / 121.92 = 20, 1219.2 / 60.96 = 20
    # So the profile coordinates are in a different scale? Let's check:
    # The profile curves show start_uv/end_uv values like 121.92, -60.96 etc.
    # The dimensions say length_u = 2438.4, width_v = 1219.2
    # 2438.4 / 2 = 1219.2, 1219.2 / 2 = 609.6
    # So the half-dimensions should be 1219.2 and 609.6, not 121.92 and 60.96
    # The profile coordinates appear to be in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm)
    # But the plan says unit_conversion_applied: cm_to_mm (x10), meaning the values were multiplied by 10
    # So original cm: 12.192 x 6.096 cm -> mm: 121.92 x 60.96 mm? That doesn't match 2438.4 x 1219.2
    # Let's re-read: the profile curves have start_uv/end_uv in the frame's UV space.
    # The dimensions explicitly state length_u = 2438.4 mm, width_v = 1219.2 mm
    # The profile coordinates are likely in the local UV frame, and the actual size is given by dimensions.
    # So we should use the explicit dimensions: 2438.4 x 1219.2 mm rectangle, extruded 12.7 mm.

    # Build the rectangle centered at origin
    length_u = 2438.4  # mm
    width_v = 1219.2   # mm
    thickness = 12.7   # mm

    # Create the plate
    result = (
        cq.Workplane("XY")
        .rect(length_u, width_v)
        .extrude(thickness)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108412_8de2f9c3_0000\\neg_03/generated.step")

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
