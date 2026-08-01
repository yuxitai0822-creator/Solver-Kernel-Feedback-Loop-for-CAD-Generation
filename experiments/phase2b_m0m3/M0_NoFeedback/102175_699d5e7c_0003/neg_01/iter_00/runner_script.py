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

    # Design Plan: rectangular prism with dimensions 39.0 x 68.0 x 10.0 mm
    # The profile is a rectangle from (-3.9, 6.8) to (0.0, 0.0) in UV space
    # After unit conversion (cm to mm x10), this becomes (-39.0, 68.0) to (0.0, 0.0)
    # Extrude distance is 10.0 mm (from design plan, not the perturbed 15.0)

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

    # Build the rectangle profile
    # The rectangle corners in UV space: (-3.9, 0.0), (0.0, 0.0), (0.0, 6.8), (-3.9, 6.8)
    # After cm->mm conversion: (-39.0, 0.0), (0.0, 0.0), (0.0, 68.0), (-39.0, 68.0)
    # Width = 39.0 mm, Height = 68.0 mm

    # Create workplane and draw rectangle
    result = (cq.Workplane("XY")
        .moveTo(-39.0, 0.0)
        .lineTo(0.0, 0.0)
        .lineTo(0.0, 68.0)
        .lineTo(-39.0, 68.0)
        .close()
        .extrude(10.0)  # Extrude 10.0 mm in +Z direction
    )

    # Export to STEP
    cq.exporters.export(result, OUT_STEP_PATH)

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
