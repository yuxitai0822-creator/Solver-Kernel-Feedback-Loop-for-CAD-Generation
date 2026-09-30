import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: SoapCutterBackBar1 v1
    # Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
    # The profile is a rectangle in the XZ plane (u along X, v along Z, extrude along Y)
    # Profile coordinates from design plan (uv space):
    #   (0.0, 5.08) -> (0.0, 0.0) -> (27.94, 0.0) -> (27.94, 5.08) -> back to start
    # Note: The design plan dimensions show length_u=279.4, width_v=50.8
    # The uv coordinates given are 27.94 x 5.08, which is 1/10 of the actual dimensions.
    # This is because the original source was in cm and converted to mm (x10).
    # The actual rectangle should be 279.4 mm x 50.8 mm.
    # The uv coordinates in the design plan are in cm (27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm).
    # We'll build the rectangle directly with the correct mm dimensions.

    # Build the rectangle in the XZ plane (u along X, v along Z)
    # The rectangle spans from (0, 0) to (279.4, 50.8) in the XZ plane
    # Extrude along Y (positive direction) by 19.05 mm

    result = (
        cq.Workplane("XZ")
        .rect(279.4, 50.8, centered=False)
        .extrude(19.05)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0007\neg_03\iter_00/generated.step"
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
