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

    # Design Plan: stadium extrusion
    # Stadium profile: two arcs (radius=10mm) connected by two lines (straight_length=28mm)
    # Extrude 4.0mm in +w direction (which is +Y in world coordinates)
    # The profile lies in the XZ plane (u=x, v=z, w=y)

    # Build the stadium profile in the XZ plane
    # Arc centers at (10, 0) and (38, 0) in UV (XZ) coordinates
    # Radius = 10mm, straight length = 28mm (distance between centers = 28mm)
    # Start with the left arc (center at x=10, z=0), from angle 0 to 180 degrees (top to bottom)
    # Then line from (10, -10) to (38, -10) in XZ
    # Then right arc (center at x=38, z=0), from angle 0 to 180 degrees (bottom to top)
    # Then line from (38, 10) to (10, 10) in XZ

    # Use Workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Build the profile using polyline and arc approximation
    # Start at left arc top: (10 + 10*cos(0), 0 + 10*sin(0)) = (20, 0)
    # But we need to go around the profile in order: left arc (top to bottom), bottom line, right arc (bottom to top), top line

    # Left arc: center (10, 0), radius 10, from 0 to 180 degrees (counterclockwise)
    # Start at (20, 0), end at (0, 0) in XZ
    # Right arc: center (38, 0), radius 10, from 0 to 180 degrees (counterclockwise)
    # Start at (28, 0), end at (48, 0) in XZ

    # Build the wire manually
    pts = []
    # Left arc: from angle 0 to 180, 32 segments
    N = 64
    for i in range(N + 1):
        t = math.pi * i / N
        x = 10 + 10 * math.cos(t)
        z = 0 + 10 * math.sin(t)
        pts.append((x, z))

    # Bottom line: from (0, -10) to (28, -10)
    # But we already have the last point of left arc at (0, -10) (t=pi)
    # Add intermediate points for the line
    for i in range(1, N + 1):
        t = i / N
        x = 0 + 28 * t
        z = -10
        pts.append((x, z))

    # Right arc: from angle 0 to 180, center (38, 0)
    # Start at (28, -10) (t=pi), end at (48, 0) (t=0)
    # But we need to go from bottom to top, so angle from pi to 0 (decreasing)
    for i in range(N + 1):
        t = math.pi * (1 - i / N)  # from pi to 0
        x = 38 + 10 * math.cos(t)
        z = 0 + 10 * math.sin(t)
        pts.append((x, z))

    # Top line: from (48, 0) to (20, 0)
    # But we already have the last point of right arc at (48, 0) (t=0)
    # Add intermediate points for the line
    for i in range(1, N + 1):
        t = i / N
        x = 48 - 28 * t
        z = 0
        pts.append((x, z))

    # Close the loop by adding the first point again
    pts.append(pts[0])

    # Create the wire from points
    wire = cq.Workplane("XZ").polyline(pts).close().extrude(4.0)

    # Alternative: use the simpler approach with two arcs and two lines
    # Build the profile using cadquery's built-in operations
    # Start with a rectangle for the straight section, then add arcs

    # Actually, let's use a cleaner approach:
    # Build the stadium profile as a single wire using the points

    # Create the profile as a closed wire
    wp = cq.Workplane("XZ")

    # Use the polyline approach with the points we computed
    # But we need to ensure the wire is closed properly

    # Let's use a simpler method: build the profile using two arcs and two lines
    # Start at the top-left of the left arc: (20, 0)
    # Go along left arc (counterclockwise) to bottom: (0, -10)
    # Line to bottom-right: (28, -10)
    # Go along right arc (counterclockwise) to top: (48, 0)
    # Line back to start: (20, 0)

    # Build the wire segment by segment
    s = cq.Workplane("XZ")

    # Start point
    s = s.moveTo(20, 0)

    # Left arc: center (10, 0), radius 10, from 0 to 180 degrees
    # Use three-point arc: start (20, 0), mid (10, 10), end (0, 0)
    # But that's a 180-degree arc, which is tricky. Use two 90-degree arcs instead.
    # Actually, let's use the discretized approach with many points

    # Build the entire profile as a polyline with many points
    pts = []
    # Left arc: from angle 0 to 180 (top to bottom)
    for i in range(33):
        t = math.pi * i / 32
        x = 10 + 10 * math.cos(t)
        z = 0 + 10 * math.sin(t)
        pts.append((x, z))
    # Bottom line: from (0, -10) to (28, -10)
    for i in range(1, 33):
        t = i / 32
        x = 0 + 28 * t
        z = -10
        pts.append((x, z))
    # Right arc: from angle pi to 0 (bottom to top)
    for i in range(33):
        t = math.pi * (1 - i / 32)
        x = 38 + 10 * math.cos(t)
        z = 0 + 10 * math.sin(t)
        pts.append((x, z))
    # Top line: from (48, 0) to (20, 0)
    for i in range(1, 33):
        t = i / 32
        x = 48 - 28 * t
        z = 0
        pts.append((x, z))

    # Create the wire
    wp = cq.Workplane("XZ")
    for i, (x, z) in enumerate(pts):
        if i == 0:
            wp = wp.moveTo(x, z)
        else:
            wp = wp.lineTo(x, z)
    wp = wp.close()

    # Extrude in the +Y direction (which is +w in the design plan)
    result = wp.extrude(4.0)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102295_86f842dd_0000\neg_03\iter_00\generated.step"
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
