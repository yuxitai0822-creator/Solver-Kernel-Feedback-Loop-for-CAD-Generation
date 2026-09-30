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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101269_f084ba14_0023\neg_02\iter_00\generated.step"

    # Design Plan parameters (all in mm)
    # Rectangle profile in UV frame:
    #   U direction: [1.0, 0.0, 0.0] (X axis)
    #   V direction: [0.0, 0.0, -1.0] (negative Z axis)
    #   W direction: [0.0, 1.0, 0.0] (Y axis)
    # Profile rectangle corners in UV coordinates:
    #   (0.0, 0.0), (9.525, 0.0), (9.525, 57.15), (0.0, 57.15)
    #   Note: The perturbed value 11.43 replaces 9.525 for the U dimension
    # Extrude distance: 19.05 mm in +W direction (Y axis)

    # Build the rectangle on the XZ plane (since V is -Z, U is X)
    # The rectangle spans:
    #   U: from 0 to 11.43 (perturbed value)
    #   V: from 0 to 57.15
    # In world coordinates (X, Z):
    #   X: 0 to 11.43
    #   Z: -57.15 to 0 (since V direction is -Z, V=0 maps to Z=0, V=57.15 maps to Z=-57.15)

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Build the rectangle centered at (5.715, -28.575) with width 11.43 and height 57.15
    # Center in X: (0 + 11.43) / 2 = 5.715
    # Center in Z: (0 + (-57.15)) / 2 = -28.575
    result = wp.moveTo(5.715, -28.575).rect(11.43, 57.15, centered=True).extrude(19.05)

    # Export to STEP
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
