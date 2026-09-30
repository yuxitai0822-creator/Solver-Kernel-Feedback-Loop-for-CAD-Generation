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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102295_86f842dd_0000\neg_02\iter_02\generated.step"

    # Build the stadium profile in the XZ plane (u=1,0,0; v=0,0,-1; w=0,1,0)
    # The design plan specifies:
    #   - straight_length = 28.0 mm (distance between arc centers)
    #   - radius = 10.0 mm (arc radius)
    #   - extrude distance = 4.0 mm along +w (Y direction)
    # The profile is centered such that the overall span along u is 48.0 mm and along v is 20.0 mm.

    # Create workplane on XZ plane (normal = Y axis)
    wp = cq.Workplane("XZ")

    # Build the stadium: two arcs (radius 10) connected by two lines.
    # Arc centers at (10.0, 0.0) and (38.0, 0.0) in XZ plane (u,v).
    # The straight length is 28.0, so centers are 28 apart.
    # The overall width along u is 2*radius + straight_length = 20 + 28 = 48.
    # The height along v is 2*radius = 20.

    # Build the profile using a polyline with arc discretization (128 segments per arc)
    N_ARC = 128
    r = 10.0

    # Start at the bottom-left corner (10, -10)
    wp = wp.moveTo(10.0, -10.0)

    # Bottom line: to (38, -10)
    wp = wp.lineTo(38.0, -10.0)

    # Right arc: from (38, -10) to (38, 10), center (38, 0), radius 10, from angle -90 to 90
    cx2, cy2 = 38.0, 0.0
    sa2 = -math.pi/2
    ea2 = math.pi/2
    for k in range(1, N_ARC+1):
        t = sa2 + (ea2 - sa2) * (k / N_ARC)
        px = cx2 + r * math.cos(t)
        py = cy2 + r * math.sin(t)
        wp = wp.lineTo(px, py)

    # Top line: from (38, 10) to (10, 10)
    wp = wp.lineTo(10.0, 10.0)

    # Left arc: from (10, 10) to (10, -10), center (10, 0), radius 10, from angle 90 to -90
    cx1, cy1 = 10.0, 0.0
    sa3 = math.pi/2
    ea3 = -math.pi/2
    for k in range(1, N_ARC+1):
        t = sa3 + (ea3 - sa3) * (k / N_ARC)
        px = cx1 + r * math.cos(t)
        py = cy1 + r * math.sin(t)
        wp = wp.lineTo(px, py)

    wp = wp.close()

    # Extrude along +Y (w direction) by 4.0 mm
    result = wp.extrude(4.0)

    # Export
    importers = None
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
