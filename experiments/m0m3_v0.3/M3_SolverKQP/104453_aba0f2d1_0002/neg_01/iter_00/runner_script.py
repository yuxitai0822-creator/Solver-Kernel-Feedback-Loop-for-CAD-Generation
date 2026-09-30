import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math
    from pathlib import Path

    OUT_STEP_PATH = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_01\iter_00") / "generated.step"

    # Design parameters from the design plan:
    # Stadium profile: straight_length=500.0 mm, radius=50.0 mm
    # Extrude distance: 100.0 mm (one side, +w direction)
    # Note: The design plan says straight_length=500.0, but the curves show straight segment from (0,-5) to (50,-5) which is 50 units.
    # The dimensions section says straight_length=500.0, radius=50.0. This matches the curves if we scale by 10x (cm->mm conversion).
    # The curves in the plan: line from (0,-5) to (50,-5) -> length 50 in UV space, but actual straight_length=500.0 mm.
    # So the UV coordinates are in cm? Actually the plan says unit=mm, so the curves are in mm.
    # Let's use the explicit dimensions: straight_length=500.0 mm, radius=50.0 mm.
    # The stadium consists of two arcs (radius 50) and two lines (length 500).

    straight_length = 500.0  # mm
    radius = 50.0  # mm
    extrude_distance = 100.0  # mm

    # Build the stadium profile
    # Start at the bottom-left corner of the straight section
    # The stadium is centered along the x-axis for convenience
    # Left arc center at (0, 0), right arc center at (straight_length, 0)

    wp = cq.Workplane("XY")

    # Build the stadium profile using a polyline with arcs discretized
    # We'll create the profile as a closed wire

    # Number of segments for arc discretization
    N = 64

    # Build the profile points
    pts = []

    # Left arc (from 180° to 0°, going counterclockwise? Actually start_angle=0, end_angle=180 in the plan)
    # The plan says: arc center_uv=[0,0], radius=5, start_angle=0, end_angle=180
    # But with radius=50, start_angle=0 (point at (50,0)), end_angle=180 (point at (-50,0))
    # This creates a semicircle on the left side
    for i in range(N + 1):
        t = math.radians(180.0 * i / N)  # 0 to 180 degrees
        x = radius * math.cos(t)
        y = radius * math.sin(t)
        pts.append((x, y))

    # Bottom line from left arc end to right arc start
    # Left arc ends at (-50, 0) at 180°, but we need to go from (0, -50) to (500, -50)
    # Actually the plan curves: line from (0,-5) to (50,-5) -> scaled: (0,-50) to (500,-50)
    # So we need to adjust: the left arc goes from (50,0) to (-50,0) (top to bottom)
    # Then line from (-50,0) to (500,-50)? No, that doesn't match.

    # Let's re-read the plan curves carefully:
    # Curve 0: arc, center_uv=[0,0], radius=5, start_angle=0, end_angle=180
    #   This draws a semicircle from (5,0) to (-5,0) going through (0,5) (top half)
    # Curve 1: line, start_uv=[0,-5], end_uv=[50,-5]
    #   This draws a line from (0,-5) to (50,-5) (bottom straight)
    # Curve 2: arc, center_uv=[50,0], radius=5, start_angle=0, end_angle=180
    #   This draws a semicircle from (55,0) to (45,0) going through (50,5) (top half)
    # Curve 3: line, start_uv=[50,5], end_uv=[0,5]
    #   This draws a line from (50,5) to (0,5) (top straight)

    # So the stadium is: left semicircle (top half), top line, right semicircle (top half), bottom line
    # Wait, that doesn't close properly. Let me trace:
    # Start at (5,0) [arc start], go to (-5,0) [arc end] via top
    # Then line from (0,-5) to (50,-5) - but we're at (-5,0), not (0,-5). Hmm.

    # Actually the arcs are drawn with start_angle=0 (point at (radius,0)) to end_angle=180 (point at (-radius,0))
    # So arc 0: from (5,0) to (-5,0) going through (0,5) [top semicircle]
    # Then line from (0,-5) to (50,-5) - but we're at (-5,0), not (0,-5). There's a gap!

    # I think the UV coordinates are in a different scale. The dimensions say straight_length=500, radius=50.
    # So the curves should be scaled by 10x: radius=50, straight=500.
    # Arc 0: center=(0,0), radius=50, from (50,0) to (-50,0) via top
    # Line 1: from (0,-50) to (500,-50)
    # Arc 2: center=(500,0), radius=50, from (550,0) to (450,0) via top
    # Line 3: from (500,50) to (0,50)

    # This still has a gap: arc ends at (-50,0), line starts at (0,-50). 
    # I think the arcs are actually the bottom semicircles, not top.
    # If start_angle=0, end_angle=180 goes from (50,0) to (-50,0) via bottom (0,-50), then:
    # Arc 0: from (50,0) to (-50,0) via (0,-50) [bottom semicircle]
    # Line 1: from (0,-50) to (500,-50) [bottom straight]
    # Arc 2: from (500,-50) to (500,50)? No, center=(500,0), radius=50, start=0, end=180 goes from (550,0) to (450,0) via (500,-50)
    #   Actually: start_angle=0 -> (550,0), end_angle=180 -> (450,0), via (500,-50) [bottom semicircle]
    # Line 3: from (500,50) to (0,50) [top straight]

    # This still doesn't close. Let me think differently.
    # The stadium shape: two parallel lines connected by two semicircles.
    # The lines are at y=-50 and y=+50, from x=0 to x=500.
    # The left semicircle connects (0,-50) to (0,50) with center at (0,0), radius=50.
    # The right semicircle connects (500,-50) to (500,50) with center at (500,0), radius=50.

    # So the correct curves should be:
    # Arc 0: center=(0,0), radius=50, from (0,-50) to (0,50) via (-50,0) [left semicircle]
    #   start_angle=-90°, end_angle=90°
    # Line 1: from (0,50) to (500,50) [top straight]
    # Arc 2: center=(500,0), radius=50, from (500,50) to (500,-50) via (550,0) [right semicircle]
    #   start_angle=90°, end_angle=270°
    # Line 3: from (500,-50) to (0,-50) [bottom straight]

    # But the plan says start_angle=0, end_angle=180 for both arcs.
    # With start_angle=0 (point at (radius,0)) and end_angle=180 (point at (-radius,0)):
    # Arc 0: from (50,0) to (-50,0) via (0,50) [top semicircle]
    # Then line from (0,-50) to (500,-50) - doesn't connect!

    # I think the plan's UV coordinates are just a template and the actual dimensions override them.
    # Let's just build the correct stadium shape using the explicit dimensions.

    # Build a proper stadium: two lines at y=-50 and y=50, from x=0 to x=500,
    # connected by semicircles at the ends.

    # Method: use cadquery's built-in capabilities
    # We can create a 2D sketch with lines and arcs

    # Clear and rebuild
    wp = cq.Workplane("XY")

    # Build the stadium profile using center point and then offset
    # Actually, let's use a simpler approach: create a rectangle and fillet the corners
    # But that gives quarter-circles, not semicircles.

    # Better: create the profile manually
    s = cq.Workplane("XY")

    # Start at bottom-left of the straight section: (0, -radius)
    s = s.moveTo(0, -radius)

    # Bottom line to (straight_length, -radius)
    s = s.lineTo(straight_length, -radius)

    # Right semicircle (bottom to top)
    # Center at (straight_length, 0), radius=radius
    # From angle -90° to 90° (going through 0°)
    for i in range(1, N + 1):
        t = math.radians(-90 + 180 * i / N)
        x = straight_length + radius * math.cos(t)
        y = radius * math.sin(t)
        s = s.lineTo(x, y)

    # Top line from (straight_length, radius) to (0, radius)
    s = s.lineTo(0, radius)

    # Left semicircle (top to bottom)
    # Center at (0, 0), radius=radius
    # From angle 90° to 270° (going through 180°)
    for i in range(1, N + 1):
        t = math.radians(90 + 180 * i / N)
        x = radius * math.cos(t)
        y = radius * math.sin(t)
        s = s.lineTo(x, y)

    # Close the profile
    s = s.close()

    # Extrude
    result = s.extrude(extrude_distance)

    # Export
    cq.exporters.export(result, str(OUT_STEP_PATH))

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
