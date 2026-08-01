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

    # Design parameters from the design plan (unit: mm)
    # Outer radius: 5.5372 mm
    # Inner radius: 1.9812 mm
    # Extrude distance: 1.3208 mm
    # Center in UV frame: (-25.400001, 12.7) but we'll center at origin for simplicity

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0004\neg_01\iter_00/generated.step"

    # Create the washer as an extruded annulus
    # Workplane: XZ plane (as in original script)
    wp = cq.Workplane("XZ")

    # Build outer circle
    outer = wp.moveTo(0, 0).circle(5.5372)

    # Build inner circle (cutout)
    inner = wp.moveTo(0, 0).circle(1.9812)

    # Create the washer by extruding the outer circle and cutting the inner circle
    # Extrude distance: 1.3208 mm in the +Y direction (normal to XZ plane)
    result = outer.extrude(1.3208)

    # Cut the inner hole
    # Create a cutting prism from the inner circle, extruded slightly more than the body
    cut_prism = inner.extrude(1.3208 * 1.5)
    result = result.cut(cut_prism)

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
