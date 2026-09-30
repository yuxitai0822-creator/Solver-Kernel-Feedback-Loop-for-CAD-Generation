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

    # Design Plan: extruded stadium
    # Dimensions:
    #   straight_length = 28.0 mm (inferred from point span)
    #   radius = 10.0 mm (explicit)
    #   extrude_distance = 4.0 mm (explicit, after unit conversion from 0.4 cm)
    #
    # The stadium profile consists of:
    #   - Left arc: center at (10, 0), radius 10, from 0° to 180°
    #   - Top line: from (10, 10) to (38, 10)
    #   - Right arc: center at (38, 0), radius 10, from 0° to 180°
    #   - Bottom line: from (38, -10) to (10, -10)
    #
    # The profile lies in the XZ plane (Y is extrusion direction).
    # Extrude 4.0 mm in the +Y direction.

    # Parameters
    R = 10.0  # radius
    L = 28.0  # straight length (distance between arc centers)
    extrude_dist = 4.0  # mm

    # Arc centers
    left_center = (R, 0.0)  # (10, 0)
    right_center = (R + L, 0.0)  # (38, 0)

    # Create the stadium profile as a closed wire
    # Start at bottom-left of left arc (angle 180° = π)
    pts = []

    # Left arc: from 180° to 0° (counterclockwise)
    N = 64
    for i in range(N + 1):
        theta = math.pi - (math.pi * i / N)  # 180° to 0°
        x = left_center[0] + R * math.cos(theta)
        z = left_center[1] + R * math.sin(theta)
        pts.append((x, z))

    # Top line: from (10, 10) to (38, 10)
    # Already at (10, 10) after arc, so just add end point
    pts.append((right_center[0], R))  # (38, 10)

    # Right arc: from 0° to 180° (counterclockwise)
    for i in range(1, N + 1):
        theta = math.pi * i / N  # 0° to 180°
        x = right_center[0] + R * math.cos(theta)
        z = right_center[1] + R * math.sin(theta)
        pts.append((x, z))

    # Bottom line: from (38, -10) to (10, -10)
    # Already at (38, -10) after arc, so add end point
    pts.append((left_center[0], -R))  # (10, -10)

    # Build the wire and face
    wp = cq.Workplane("XZ")
    wire = wp.moveTo(pts[0][0], pts[0][1])
    for p in pts[1:]:
        wire = wire.lineTo(p[0], p[1])
    wire = wire.close()

    # Extrude in the +Y direction
    result = wire.extrude(extrude_dist)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102295_86f842dd_0000\neg_01\iter_02\generated.step"
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
