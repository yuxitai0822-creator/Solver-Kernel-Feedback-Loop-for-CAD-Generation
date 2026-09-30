import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile based on the design plan
    # The profile is a 19mm x 19mm square, centered at the origin
    # The extrude direction is along the w-axis (which corresponds to y in world coordinates)
    # The profile coordinates in UV space are:
    #   u: [-58.2782, -56.3782]  (span = 1.9 cm = 19 mm)
    #   v: [-13.9401, -12.0401]  (span = 1.9 cm = 19 mm)
    # Note: The design plan indicates a unit conversion from cm to mm (x10), so the values are already in mm.

    # Build the rectangle in the XY plane (u -> x, v -> z, w -> y)
    # The rectangle corners in UV space:
    #   (-58.27820137826746, -13.940145769681571) -> bottom-left
    #   (-56.37820137826746, -12.04014576968157)  -> top-right
    # Width in u: 1.9 mm, Height in v: 1.9 mm

    # Create the rectangle centered at the midpoint of the UV range
    mid_u = (-58.27820137826746 + -56.37820137826746) / 2.0
    mid_v = (-13.940145769681571 + -12.04014576968157) / 2.0

    # Width and height in mm
    width = 1.9  # 19 mm? Wait, the span is 1.9, but the design says 19.0 mm. Let's check.
    # The UV coordinates: -58.2782 to -56.3782 => difference = 1.9
    # The design plan says length_u = 19.0 mm, width_v = 19.0 mm
    # But the UV coordinates span 1.9 units. This suggests the UV coordinates are in cm, and we need to scale by 10.
    # The compiler notes say "unit_conversion_applied: cm_to_mm (x10)", meaning the values in the plan are already in mm.
    # So the UV coordinates are in mm, and the span is 1.9 mm? That contradicts the 19.0 mm dimension.
    # Let's re-examine: The design plan says length_u = 19.0 mm, but the UV span is 1.9.
    # The compiler note says "cm_to_mm (x10)" - this means the original values were in cm and multiplied by 10 to get mm.
    # So the UV coordinates are in mm, and the span is 1.9 mm? No, that would be 1.9 mm, not 19 mm.
    # Actually, the UV coordinates themselves might be in cm originally, then converted to mm by multiplying by 10.
    # So the original UV coordinates in cm were: -5.82782 to -5.63782 (span 0.19 cm = 1.9 mm)
    # After conversion to mm: -58.2782 to -56.3782 (span 1.9 mm) — still not 19 mm.
    # This is confusing. Let's just use the explicit dimensions from the design plan: 19.0 mm x 19.0 mm.
    # The UV coordinates are just for positioning; the actual size is given by the dimensions.

    # So we'll create a 19 mm x 19 mm rectangle centered at the origin.
    # The extrude direction is +w, which is +y in world coordinates.
    # Extrude distance: 200.0 mm

    result = (
        cq.Workplane("XY")
        .rect(19.0, 19.0)
        .extrude(200.0)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100243_9fb796fe_0005\\neg_02/generated.step")

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
