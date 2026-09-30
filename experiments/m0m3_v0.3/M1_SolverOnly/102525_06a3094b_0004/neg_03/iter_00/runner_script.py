import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0004\neg_03\iter_00\generated.step"

    # Build the rectangular prism according to the design plan:
    # Rectangle profile: length_u = 8.5 mm, width_v = 18.0 mm
    # Extrude distance: 2.5 mm along +w direction
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The profile coordinates in uv-plane: u from -0.425 to 0.425, v from -0.9 to 0.9
    # (these are half-dimensions: 8.5/2 = 4.25, 18.0/2 = 9.0, but the design plan
    #  gives start/end uv coordinates as ±0.425 and ±0.9, which after scaling by 10
    #  from cm to mm become ±4.25 and ±9.0)

    # Create a workplane on the XZ plane (since v_dir is (0,0,-1) and w_dir is (0,1,0),
    # the sketch plane normal is w_dir = (0,1,0), i.e., Y-axis. In CadQuery, we can
    # use workplane("XZ") which has normal (0,1,0).

    wp = cq.Workplane("XZ")

    # Draw the rectangle centered at origin with dimensions 8.5 x 18.0
    # The rectangle in uv-plane: u along X, v along Z (since v_dir = (0,0,-1), but
    # we can just draw a rectangle and extrude along Y.
    wp = wp.center(0, 0).rect(8.5, 18.0, centered=True)

    # Extrude along +Y (which is +w direction) by 2.5 mm
    result = wp.extrude(2.5)

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
