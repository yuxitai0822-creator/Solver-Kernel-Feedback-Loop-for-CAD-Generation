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
    RADIUS = 0.8  # mm (from dimensions.profiles[0].radius.value)
    EXTRUDE_DISTANCE = 4.0  # mm (from dimensions.extrude_distance.value)

    # Build the part: a simple disk (extruded circle)
    # The coordinate system: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means the sketch plane is XZ (u,v) and extrusion is along w (Y axis)
    # But for simplicity, we use the default XY plane and extrude along Z, then rotate if needed.
    # Actually, the design plan says the frame has w_dir = [0,1,0], so extrusion is along Y.
    # We'll build on XY plane and extrude along Y to match the frame.

    # Create workplane on XY plane
    wp = cq.Workplane("XY")

    # Create the circle profile at origin with radius 0.8 mm
    profile = wp.circle(RADIUS)

    # Extrude along Y axis (positive direction) by 4.0 mm
    result = profile.extrude(EXTRUDE_DISTANCE)

    # The result is a cylinder with axis along Z (since we used XY plane and extrude along Z by default).
    # But the design plan expects extrusion along Y (w_dir = [0,1,0]).
    # So we need to rotate the result so that the cylinder axis aligns with Y.
    # Rotate 90 degrees around X axis: Z -> Y
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Now the cylinder axis is along Y, matching the design plan.
    # The dimensions: radius 0.8, length 4.0 along Y.
    # Span along u (X) = 2*radius = 1.6, span along v (Z) = 2*radius = 1.6, span along w (Y) = 4.0

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102760_26430589_0037\neg_02\iter_00/generated.step"
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
