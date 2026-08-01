import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: flat plate/panel, extruded rectangle
    # Dimensions: length_u=254.0 mm, width_v=190.5 mm, extrude_distance=3.175 mm
    # The previous script used 4.7625 mm (perturbed value). We restore the correct value.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_01\iter_00\generated.step"

    # Build the rectangle profile
    # The profile curves define a rectangle from (0,0) to (25.4, 19.05) in UV space
    # But the dimensions table says length_u=254.0, width_v=190.5 (scaled by 10 from cm to mm)
    # The curves use 25.4 and 19.05 which are 1/10 of the actual dimensions.
    # This is because the original source was in cm and converted to mm (x10).
    # The curves in the design plan show: 0.0,19.05 -> 0.0,0.0 -> 25.4,0.0 -> 25.4,19.05 -> 0.0,19.05
    # These are in mm after conversion. But the dimensions table says 254.0 and 190.5.
    # There's a discrepancy: the curves are 1/10 of the stated dimensions.
    # The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # The curves likely represent the original cm values (2.54 cm x 1.905 cm) which become 25.4 mm x 19.05 mm.
    # But the dimensions table says 254.0 x 190.5. This is inconsistent.
    # Looking at the perturbation description: original extrude=0.3175, perturbed=0.47625 (in cm?)
    # The previous script used EXTENT_TOTAL_MM = 4.7625 which is 0.47625*10.
    # The design plan says extrude_distance = 3.175 mm (which is 0.3175*10).
    # So the correct extrude is 3.175 mm.
    # For the rectangle, the curves use 25.4 and 19.05 which match the design plan curves.
    # The dimensions table values (254.0, 190.5) seem to be a different interpretation.
    # We'll use the curve values directly as they match the profile definition.

    # Create workplane
    wp = cq.Workplane("XY")

    # Build rectangle from the 4 corner points
    # Start at (0, 19.05), go to (0, 0), then (25.4, 0), then (25.4, 19.05), close back to (0, 19.05)
    wp = wp.moveTo(0, 19.05)
    wp = wp.lineTo(0, 0)
    wp = wp.lineTo(25.4, 0)
    wp = wp.lineTo(25.4, 19.05)
    wp = wp.close()

    # Extrude by 3.175 mm in +Z direction
    result = wp.extrude(3.175)

    # Export
    importers.export(result, OUT_STEP_PATH)

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
