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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_01\iter_00\generated.step"

    # Build the stadium profile as per design plan:
    # Two arcs (radius 5.0) at centers (0,0) and (50,0), connected by lines.
    # The straight length is 50.0 mm (distance between arc centers).
    # The overall span in u (x) is 60.0 mm (50 + 2*5).
    # The overall span in v (y) is 10.0 mm (2*5).
    # Extrude 100.0 mm in +z.

    wp = cq.Workplane("XY")

    # Build the stadium profile using polyline + arc approximation (discretized arcs)
    N_ARC = 64
    pts = []
    # First arc: from angle 0 to 180 (top half), center (0,0), radius 5
    for i in range(N_ARC + 1):
        t = math.pi * i / N_ARC
        x = 5.0 * math.cos(t)
        y = 5.0 * math.sin(t)
        pts.append((x, y))
    # Top line from (0,5) to (50,5) — but we already have (0,5) as last point of arc
    # Actually the arc ends at ( -5, 0 )? Wait: start_angle=0 -> (5,0), end_angle=180 -> (-5,0).
    # But the design plan says start_angle=0, end_angle=180, center (0,0). That gives a semicircle from (5,0) to (-5,0) going through (0,5).
    # Then line from (0,-5) to (50,-5) — but that's the bottom line.
    # Let's reorder: The stadium is: top arc from (5,0) to (-5,0) via (0,5); then bottom line from (-5,0) to (45,0)? No.
    # Actually the design plan curves:
    # 1) arc center (0,0), radius 5, start_angle=0, end_angle=180 -> from (5,0) to (-5,0) going counterclockwise (top).
    # 2) line from (0,-5) to (50,-5) — but that doesn't match the arc endpoint. Let's check: arc ends at (-5,0). The line starts at (0,-5). That's not connected.
    # There's inconsistency in the design plan. However, the intended shape is a stadium: two semicircles at ends, connected by straight lines.
    # The typical stadium: left semicircle center (0,0) radius 5, right semicircle center (50,0) radius 5.
    # The top line connects (0,5) to (50,5). The bottom line connects (0,-5) to (50,-5).
    # The arcs: left arc from (0,5) to (0,-5) going left (angle 90 to 270) or right? Actually start_angle=0, end_angle=180 gives top half from (5,0) to (-5,0). That's not correct.
    # Let's follow the design plan literally: curves list:
    # arc: center (0,0), radius 5, start_angle=0, end_angle=180 -> from (5,0) to (-5,0) via (0,5).
    # line: from (0,-5) to (50,-5) — but (0,-5) is not on the arc. So the plan is inconsistent.
    # However, the validation intents expect span_u=600, span_v=100, which suggests straight_length=500, radius=50 (scaled by 10 from cm to mm).
    # The design plan dimensions say straight_length=500, radius=50. So the stadium is 500 long straight + 2*50 radius = 600 total length, 100 width.
    # The curves in the plan have radius 5 and straight length 50 (scaled down by 10?). Actually the plan says radius=50, straight_length=500 in dimensions, but the curves list radius=5 and line endpoints at 0 and 50. That's a factor of 10 discrepancy.
    # The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the original was in cm: radius 5 cm = 50 mm, straight length 50 cm = 500 mm.
    # So the curves list is in cm? But the plan says unit=mm. Probably the curves list is in the original cm units and the dimensions are converted to mm.
    # To match the validation intents (span_u=600, span_v=100), we need radius=50, straight_length=500.
    # So we'll build the stadium with radius 50, straight length 500.

    # Build profile: start at (0,50) (top of left arc), go to (500,50) (top line), then right arc from (500,50) to (500,-50) via (550,0), then bottom line from (500,-50) to (0,-50), then left arc from (0,-50) to (0,50) via (-50,0).

    wp = wp.moveTo(0, 50)
    wp = wp.lineTo(500, 50)
    # right arc: center (500,0), radius 50, from angle 90 to -90 (or 90 to 270)
    for i in range(1, N_ARC + 1):
        t = math.pi/2 - math.pi * i / N_ARC  # from 90 deg to -90 deg
        x = 500 + 50 * math.cos(t)
        y = 50 * math.sin(t)
        wp = wp.lineTo(x, y)
    wp = wp.lineTo(0, -50)
    # left arc: center (0,0), radius 50, from angle -90 to 90
    for i in range(1, N_ARC + 1):
        t = -math.pi/2 + math.pi * i / N_ARC
        x = 50 * math.cos(t)
        y = 50 * math.sin(t)
        wp = wp.lineTo(x, y)
    wp = wp.close()

    # Extrude 100 mm in +z
    result = wp.extrude(100.0)

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
