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

    # Design Plan parameters
    # Body: extruded circle
    # Profile: circle, radius 0.8 mm (from dimensions.profiles[0].radius.value)
    # Extrude: one_side, direction -w, distance 4.0 mm (from dimensions.extrude_distance.value)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # The sketch plane is defined by u and v axes: u (x-axis) and v (z-axis negative)
    # So the sketch plane is XZ (with v reversed, but that's just orientation)
    # Extrude direction is -w = -[0,1,0] = [0,-1,0] (negative Y)

    # Build the result
    result = (
        cq.Workplane("XZ")  # sketch plane: XZ (u=x, v=z)
        .circle(0.8)  # radius from design plan
        .extrude(4.0)  # extrude distance along normal (Y direction)
    )

    # The extrude direction in the design plan is -w = -[0,1,0] = [0,-1,0]
    # In CadQuery, Workplane("XZ") extrudes along +Y by default.
    # To extrude along -Y, we need to negate the distance.
    # But the design plan says distance_total = 4.0, direction = -w.
    # So we should extrude -4.0 in Y direction.
    # Let's rebuild with correct direction:
    result = (
        cq.Workplane("XZ")
        .circle(0.8)
        .extrude(-4.0)  # negative Y direction
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_01\iter_00/generated.step"
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
