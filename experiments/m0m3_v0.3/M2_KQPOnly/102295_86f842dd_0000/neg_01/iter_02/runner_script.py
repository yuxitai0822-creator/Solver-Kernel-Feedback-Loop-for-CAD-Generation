import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_01\iter_02\generated.step"

    # Design parameters from the design plan
    straight_length = 28.0
    radius = 10.0
    extrude_distance = 4.0

    # The design plan's frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means the profile is in the XZ plane (u=X, v=Z), extruded along Y (w)
    # The profile should span 48 mm along u (X) and 20 mm along v (Z)
    # The stadium consists of:
    # - Left arc centered at (radius, 0) with radius, from 0° to 180° (top to bottom in UV)
    # - Bottom line from (radius, -radius) to (radius + straight_length, -radius)
    # - Right arc centered at (radius + straight_length, 0) with radius, from 0° to 180°
    # - Top line from (radius + straight_length, radius) to (radius, radius)

    # The total span along u (X) is: 2*radius + straight_length = 2*10 + 28 = 48 mm
    # The total span along v (Z) is: 2*radius = 20 mm

    wp = cq.Workplane("XZ")

    # Build the stadium profile using the discretization approach
    N_ARC = 128

    # Start at the bottom-left point: (radius, -radius) = (10, -10)
    wp = wp.moveTo(radius, -radius)

    # Bottom line to (radius + straight_length, -radius) = (38, -10)
    wp = wp.lineTo(radius + straight_length, -radius)

    # Right arc: center (radius + straight_length, 0) = (38, 0), radius 10, from -90° to 90°
    for k in range(1, N_ARC + 1):
        t = -math.pi/2 + (math.pi) * (k / N_ARC)  # from -90° to 90°
        px = (radius + straight_length) + radius * math.cos(t)
        py = 0 + radius * math.sin(t)
        wp = wp.lineTo(px, py)

    # Top line to (radius, radius) = (10, 10)
    wp = wp.lineTo(radius, radius)

    # Left arc: center (radius, 0) = (10, 0), radius 10, from 90° to -90° (clockwise)
    for k in range(1, N_ARC + 1):
        t = math.pi/2 - (math.pi) * (k / N_ARC)  # from 90° down to -90°
        px = radius + radius * math.cos(t)
        py = 0 + radius * math.sin(t)
        wp = wp.lineTo(px, py)

    # Close the wire
    wp = wp.close()

    # Extrude along Y (w_dir = [0,1,0]) by the design plan's distance
    result = wp.extrude(extrude_distance)

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
