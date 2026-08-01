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
    # The previous script used 25.4 x 19.05 mm for the rectangle, but the design plan's
    # dimensions table specifies 254.0 x 190.5 mm. The curves in the design plan are
    # in cm (2.54 x 1.905 cm) which convert to 25.4 x 19.05 mm, but the explicit
    # dimensions table overrides this with 254.0 x 190.5 mm. We use the explicit dimensions.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_01\iter_02\generated.step"

    # Create workplane
    wp = cq.Workplane("XY")

    # Build rectangle using the explicit dimensions from the design plan
    # length_u = 254.0 mm, width_v = 190.5 mm
    # Center the rectangle at the origin for simplicity
    wp = wp.rect(254.0, 190.5, centered=True)

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
