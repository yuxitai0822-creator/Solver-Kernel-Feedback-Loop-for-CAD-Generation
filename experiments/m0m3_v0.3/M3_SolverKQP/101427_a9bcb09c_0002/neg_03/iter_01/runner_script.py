import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: extruded rectangle
    # Dimensions: length_u = 1930.0 mm, width_v = 550.0 mm, extrude_distance = 50.0 mm
    # The design plan explicitly states length_u=1930.0 and width_v=550.0 in the dimensions section.
    # The compiler notes indicate cm_to_mm conversion (x10), but the dimensions are already in mm.
    # The curves in the profiles show 193.0 and 55.0, but those are in UV space (which may be in cm).
    # The validation intents expect spans of 1930.0, 550.0, and 50.0.
    # The previous iteration failed because it used 193.0 and 55.0 instead of 1930.0 and 550.0.
    # We follow the explicit dimensions from the design plan: 1930.0 x 550.0 mm, extruded 50.0 mm.

    # Create the rectangle on the XZ plane (as per previous script's WORKPLANE = 'XZ')
    # The rectangle spans from (0,0) to (1930.0, 550.0) in UV coordinates
    # U direction = X axis, V direction = Z axis (negative), W direction = Y axis
    # So rectangle is in XZ plane, extruded along Y axis

    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .rect(1930.0, 550.0, centered=False)
        .extrude(50.0)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0002\neg_03\iter_01\generated.step"
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
