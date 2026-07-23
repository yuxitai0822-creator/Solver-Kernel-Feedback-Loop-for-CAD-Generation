import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\101427_a9bcb09c_0001\neg_02"
    OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

    # Ensure output directory exists
    os.makedirs(OUT_DIR, exist_ok=True)

    # Outer rectangle dimensions (from outer ring UV coordinates)
    outer_length = 198.0  # 195.5 - (-2.5) = 198.0 mm
    outer_width = 60.0    # 57.5 - (-2.5) = 60.0 mm

    # Inner rectangle dimensions (from inner ring UV coordinates)
    inner_length = 193.0  # 193.0 - 0.0 = 193.0 mm
    inner_width = 55.0    # 55.0 - 0.0 = 55.0 mm

    # Extrude distance
    extrude_dist = 25.0

    # Build the rectangular frame by extruding the difference of outer and inner rectangles
    result = (cq.Workplane("XY")
                .rect(outer_length, outer_width)
                .rect(inner_length, inner_width)
                .extrude(extrude_dist))

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
