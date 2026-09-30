import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import json
    import math
    from pathlib import Path
    import cadquery as cq
    from cadquery import exporters

    # Constants from design plan
    EXTENT_TOTAL_MM = 25.0
    NORMAL = [0.0, 0.0, 1.0]
    WORKPLANE = 'XY'
    OUT_STEP = os.environ.get("OUT_STEP_PATH", "OUT_STEP = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0002\neg_02\iter_00/generated.step"".split("=")[-1].strip().strip("r").strip("\").strip("\").strip("\"))

    # Design plan specifies radius = 3.0 mm (from dimensions section)
    # The perturbed radius 0.375 is a scaling factor, not the actual radius
    # The actual radius from design plan is 3.0 mm
    RADIUS_MM = 3.0

    def main():
        # Create a simple disk: circle extruded to 25mm
        # Using the design plan dimensions directly
        result = (
            cq.Workplane(WORKPLANE)
            .circle(RADIUS_MM)
            .extrude(EXTENT_TOTAL_MM)
        )

        exporters.export(result, OUT_STEP)

    if __name__ == "__main__":
        main()

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
