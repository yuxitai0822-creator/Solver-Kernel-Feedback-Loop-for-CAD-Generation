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
    # The rectangle is centered at origin in the uv-plane, with u along x, v along y, w along z.
    # The profile vertices in uv coordinates: (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
    # Note: The uv coordinates appear to be in cm (since the plan says cm_to_mm x10).
    # The actual dimensions in mm: length_u = 2438.4 mm, width_v = 1219.2 mm.
    # The uv coordinates given are 121.92 and 60.96, which are 1/20 of the full dimensions.
    # This suggests the profile is defined in a normalized or scaled coordinate system.
    # To get the correct size, we multiply the uv coordinates by 10 to convert cm to mm, then by 2 to get full span.
    # Actually, the uv coordinates represent half-dimensions in cm: 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm.
    # So the full rectangle in mm is: width along u = 2*1219.2 = 2438.4 mm, width along v = 2*609.6 = 1219.2 mm.
    # We'll build the rectangle directly using the full dimensions.

    # Build the plate centered at origin
    result = (
        cq.Workplane("XY")
        .rect(2438.4, 1219.2)
        .extrude(12.7)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108412_8de2f9c3_0000\\ex2/generated.step")

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
