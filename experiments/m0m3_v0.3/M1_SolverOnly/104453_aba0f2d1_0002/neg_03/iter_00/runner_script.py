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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_03\iter_00/generated.step"

    # Design parameters from the design plan:
    # Stadium profile: straight_length = 500.0 mm, radius = 50.0 mm
    # Extrude distance = 100.0 mm
    # The profile is defined in the XY plane (u=x, v=y, w=z)
    # The stadium consists of:
    #   - Left arc: center (0,0), radius 50, from 0° to 180° (top half)
    #   - Top line: from (0, 50) to (500, 50)
    #   - Right arc: center (500,0), radius 50, from 0° to 180° (bottom half)
    #   - Bottom line: from (500, -50) to (0, -50)
    # Note: The design plan's curves use start_angle 0 to 180 for both arcs,
    # but to form a closed stadium, one arc should be flipped (180 to 360 or 0 to -180).
    # We'll construct the profile manually using the correct geometry.

    # Build the stadium profile using a polyline approach with arc discretization
    # to avoid numerical issues with cadquery's arc construction.

    # Create a workplane
    wp = cq.Workplane("XY")

    # Parameters
    straight_length = 500.0  # mm
    radius = 50.0  # mm
    extrude_distance = 100.0  # mm

    # Number of segments for arc discretization
    N = 64

    # Build the outer wire point by point
    points = []

    # Left arc: from (0, -50) to (0, 50) going counterclockwise (through left side)
    # Center (0,0), radius 50, start angle -90° (bottom), end angle 90° (top)
    for i in range(N + 1):
        angle = -math.pi/2 + (math.pi * i / N)  # from -90° to 90°
        x = 0 + radius * math.cos(angle)
        y = 0 + radius * math.sin(angle)
        points.append((x, y))

    # Top line: from (0, 50) to (500, 50)
    points.append((straight_length, radius))

    # Right arc: from (500, 50) to (500, -50) going counterclockwise (through right side)
    # Center (500,0), radius 50, start angle 90° (top), end angle 270° (bottom)
    for i in range(1, N + 1):
        angle = math.pi/2 + (math.pi * i / N)  # from 90° to 270°
        x = straight_length + radius * math.cos(angle)
        y = 0 + radius * math.sin(angle)
        points.append((x, y))

    # Bottom line: from (500, -50) to (0, -50)
    points.append((0, -radius))

    # Create the wire from points
    wire = cq.Workplane("XY").polyline(points).close().wire()

    # Create a face from the wire
    face = cq.Workplane("XY").placeSketchOnFace(cq.Face.makeFromWires(wire))

    # Alternative: use the wire directly to make a face and extrude
    # Build the stadium using cadquery's built-in operations
    # Since the polyline approach may have issues, let's use a simpler method:
    # Create a rectangle and fillet the ends, or use two circles and a rectangle

    # Better approach: Use the design plan's explicit geometry
    # Create the profile using a combination of lines and arcs

    # Start fresh
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(0, -radius)
        .lineTo(straight_length, -radius)
        .threePointArc(
            (straight_length + radius, 0),
            (straight_length, radius)
        )
        .lineTo(0, radius)
        .threePointArc(
            (-radius, 0),
            (0, -radius)
        )
        .close()
        .extrude(extrude_distance)
    )

    # Export the result
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
