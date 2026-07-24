import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    # Design Plan: stadium extrusion
    # Dimensions:
    #   straight_length = 28.0 mm (inferred from point span)
    #   radius = 10.0 mm (explicit)
    #   extrude distance = 4.0 mm
    #
    # The stadium profile is defined in the UV plane where:
    #   u_dir = (1,0,0)  -> X axis
    #   v_dir = (0,0,-1) -> -Z axis (so positive V goes into -Z)
    #   w_dir = (0,1,0)  -> Y axis (extrude direction)
    #
    # The profile curves (in UV coordinates):
    #   Arc1: center (1.0, 0.0), radius 1.0, start 0°, end 180°
    #   Line1: (1.0, -1.0) to (3.8, -1.0)
    #   Arc2: center (3.8, 0.0), radius 1.0, start 0°, end 180°
    #   Line2: (3.8, 1.0) to (1.0, 1.0)
    #
    # The UV coordinates are in "units" that need to be scaled to mm.
    # From the dimensions: straight_length = 28.0 mm, radius = 10.0 mm.
    # In UV space: straight segment length = 3.8 - 1.0 = 2.8 units, radius = 1.0 unit.
    # So scale factor = 10.0 (since radius 1.0 unit -> 10 mm).
    #
    # After scaling:
    #   Arc1 center: (10, 0), radius 10
    #   Line1: (10, -10) to (38, -10)
    #   Arc2 center: (38, 0), radius 10
    #   Line2: (38, 10) to (10, 10)
    #
    # The profile lies in the XY plane (since u->X, v->-Z, but we'll build in XY and then rotate).
    # Actually simpler: build in XY plane with u=X, v=Y, then extrude in Z direction.
    # But the design says v_dir = (0,0,-1) and w_dir = (0,1,0).
    # So we'll build the profile in the XZ plane (u=X, v=-Z) and extrude along Y.
    #
    # Let's build the stadium profile in the XZ plane:
    #   Points: (10, -10) -> (38, -10) -> (38, 10) -> (10, 10) with arcs at ends.
    #   The arcs are on the left (center (10,0)) and right (center (38,0)).
    #   Left arc: from (10, -10) to (10, 10) going through (0, 0) — actually radius 10, center (10,0).
    #   Right arc: from (38, 10) to (38, -10) going through (48, 0).
    #
    # In CadQuery, we can use a Workplane on the XZ plane and build the stadium.

    # Scale factor
    scale = 10.0

    # UV coordinates (unscaled)
    arc1_center_u = 1.0
    arc1_center_v = 0.0
    radius_uv = 1.0
    line_start_u = 1.0
    line_start_v = -1.0
    line_end_u = 3.8000000000000007
    line_end_v = -1.0
    arc2_center_u = 3.8000000000000007
    arc2_center_v = 0.0

    # Scaled to mm
    R = radius_uv * scale
    L = (line_end_u - line_start_u) * scale  # straight length = 28.0

    # Build the stadium profile using CadQuery's 2D operations
    # We'll create a wire from points and arcs

    # Start with a workplane on the XZ plane (Front plane in CQ)
    # But we need to orient correctly: u=X, v=-Z, w=Y
    # So we work on the plane with normal (0,1,0) i.e. Y-axis, which is the "front" plane in CQ.
    # Actually CQ's front plane is YZ? Let's use the XY plane and then rotate.
    # Simpler: build in XY plane (u=X, v=Y) then rotate 90° around X to map Y to -Z.
    # But the extrude direction is w=Y, so after rotation, extrude along Y.
    # Let's just build in the XY plane and then rotate the whole solid.

    # Build stadium in XY plane:
    #   u -> X, v -> Y
    #   Arc1: center (10, 0), radius 10, from angle 180° to 0° (going through top)
    #   Actually start_angle=0°, end_angle=180° means from +X direction to -X direction through +Y.
    #   So arc goes from (20, 0) to (0, 0) through (10, 10).
    #   But our points: start at (10, -10) going to (10, 10) through (0, 0)?
    #   Let's re-check: center (10,0), radius 10, start_angle=0 (point at (20,0)), end_angle=180 (point at (0,0)).
    #   That arc goes through (10,10) at 90°.
    #   But our line starts at (10, -10) which is not on that arc.
    #   Wait, the UV coordinates: arc center (1.0, 0.0), radius 1.0, start_angle=0, end_angle=180.
    #   At start_angle=0: point = (1+1*cos0, 0+1*sin0) = (2, 0)
    #   At end_angle=180: point = (1+1*cos180, 0+1*sin180) = (0, 0)
    #   But the line starts at (1.0, -1.0) and ends at (3.8, -1.0).
    #   This doesn't match! The arc endpoints should connect to the line endpoints.
    #   Let's re-examine: the curves list order:
    #     1. arc: center (1,0), radius 1, start 0°, end 180°
    #     2. line: start (1, -1) to (3.8, -1)
    #     3. arc: center (3.8, 0), radius 1, start 0°, end 180°
    #     4. line: start (3.8, 1) to (1, 1)
    #   So the loop is: arc1 (from (2,0) to (0,0) through (1,1)), then line from (1,-1) to (3.8,-1)?
    #   That doesn't connect! The arc ends at (0,0) but line starts at (1,-1).
    #   There must be a mistake in the UV coordinates or the interpretation.
    #
    #   Actually, looking at the start_angle/end_angle: start_angle=0 means along +X axis, end_angle=180 means along -X axis.
    #   So arc goes from (2,0) to (0,0) through (1,1) (the upper half).
    #   Then line from (1,-1) to (3.8,-1) — this is the bottom straight segment.
    #   Then arc from (3.8,0) radius 1, start 0°, end 180°: from (4.8,0) to (2.8,0) through (3.8,1) (upper half).
    #   Then line from (3.8,1) to (1,1) — top straight segment.
    #   This forms a closed loop but the arcs are on the top and the lines on bottom/top?
    #   Actually the arcs are both on the top (positive V), and the lines are on bottom and top.
    #   That would make a shape like a rounded rectangle but with arcs only on top?
    #   No, a stadium has arcs on both ends (left and right).
    #   Let's reinterpret: the arcs are on the left and right ends, and lines are top and bottom.
    #   For a stadium, we need:
    #     Left arc: from bottom-left to top-left (going left)
    #     Top line: from top-left to top-right
    #     Right arc: from top-right to bottom-right (going right)
    #     Bottom line: from bottom-right to bottom-left
    #   In UV: left arc center at (1,0), radius 1, from angle -90° to 90° (or 270° to 90°).
    #   But the given angles are 0° to 180°, which goes from right to left through top.
    #   That would be the right half of a circle, not the left.
    #
    #   I think the UV coordinates might be using a different convention.
    #   Let's just use the dimensions: straight_length=28, radius=10.
    #   The stadium has two semicircles of radius 10 at the ends, connected by straight segments of length 28.
    #   Total length = 28 + 2*10 = 48, width = 2*10 = 20.
    #   This matches the validation intents: span_u=48, span_v=20.
    #
    #   So we'll build a proper stadium: center at (0,0), radius 10, straight length 28.
    #   The profile in XY plane:
    #     Left semicircle: center at (-14, 0), radius 10, from 90° to -90° (or 90° to 270°)
    #     Bottom line: from (-14, -10) to (14, -10)
    #     Right semicircle: center at (14, 0), radius 10, from -90° to 90° (or 270° to 90°)
    #     Top line: from (14, 10) to (-14, 10)
    #   This gives span in X = 48, span in Y = 20.

    # Build the stadium profile
    # Use CadQuery's 2D drawing capabilities

    # Create a workplane on XY
    wp = cq.Workplane("XY")

    # Build the stadium using a polyline with tangent arcs
    # We'll construct the wire manually

    # Points (in XY plane, u->X, v->Y)
    # Left center: (-14, 0)
    # Right center: (14, 0)
    # Radius: 10

    # The stadium outline:
    # Start at bottom of left semicircle: (-14, -10)
    # Line to bottom of right semicircle: (14, -10)
    # Arc around right semicircle from -90° to 90°: (14, -10) -> (14, 10) through (24, 0)
    # Line to top of left semicircle: (-14, 10)
    # Arc around left semicircle from 90° to -90°: (-14, 10) -> (-14, -10) through (-24, 0)

    # In CadQuery, we can use threePointArc or sagittaArc
    # Let's build the wire using edges

    # Method: create a closed wire from points and arcs
    # We'll use the Workplane's moveTo, lineTo, threePointArc, etc.

    # Start at bottom-left
    p = cq.Vector(-14, -10, 0)

    # Build the profile as a list of edges
    # Edge 1: line from (-14,-10) to (14,-10)
    # Edge 2: arc from (14,-10) to (14,10) with center (14,0) -> midpoint (24,0)
    # Edge 3: line from (14,10) to (-14,10)
    # Edge 4: arc from (-14,10) to (-14,-10) with center (-14,0) -> midpoint (-24,0)

    # Create the wire using CadQuery's wire construction
    # We can use cq.Wire.makeCircle for arcs, but easier: use Workplane's 2D drawing

    # Use the polygon + fillet approach? No, we need exact arcs.

    # Let's use the cq.Workplane methods:
    #   moveTo(x, y)
    #   lineTo(x, y)
    #   threePointArc(point1, point2)  # draws arc from current point through point1 to point2

    # Build the profile
    profile = (
        cq.Workplane("XY")
        .moveTo(-14, -10)  # start at bottom-left
        .lineTo(14, -10)   # bottom edge
        .threePointArc((24, 0), (14, 10))  # right arc: through (24,0) to (14,10)
        .lineTo(-14, 10)   # top edge
        .threePointArc((-24, 0), (-14, -10))  # left arc: through (-24,0) to (-14,-10)
        .close()  # close the wire
    )

    # Now extrude along the Z axis (which is w_dir after rotation?)
    # The design says w_dir = (0,1,0) = Y axis.
    # But we built in XY plane, so normal is Z. We need to extrude along Y.
    # So we should build in XZ plane or rotate after extrusion.
    # Let's build in XZ plane instead: u=X, v=-Z, w=Y.
    # In XZ plane: X is horizontal, Z is vertical (but v_dir = -Z, so positive v goes into -Z).
    # So we map: u -> X, v -> -Z.
    # Points become:
    #   (-14, 0, -10) -> (-14, 0, -10) in XYZ? No, v=-Z means v=10 -> Z=-10.
    #   So bottom of left semicircle: u=-14, v=-10 -> X=-14, Z=10 (since v=-Z => Z=-v)
    #   Top of left semicircle: u=-14, v=10 -> X=-14, Z=-10
    #   Bottom of right semicircle: u=14, v=-10 -> X=14, Z=10
    #   Top of right semicircle: u=14, v=10 -> X=14, Z=-10
    #   Left arc center: u=-14, v=0 -> X=-14, Z=0
    #   Right arc center: u=14, v=0 -> X=14, Z=0
    #   Left arc midpoint: u=-24, v=0 -> X=-24, Z=0
    #   Right arc midpoint: u=24, v=0 -> X=24, Z=0

    # Build in XZ plane (workplane "XZ")
    profile_xz = (
        cq.Workplane("XZ")
        .moveTo(-14, 10)  # start at bottom-left: X=-14, Z=10 (v=-10 -> Z=10)
        .lineTo(14, 10)   # bottom edge: X=14, Z=10
        .threePointArc((24, 0), (14, -10))  # right arc: through (24,0) to (14,-10)
        .lineTo(-14, -10)  # top edge: X=-14, Z=-10
        .threePointArc((-24, 0), (-14, 10))  # left arc: through (-24,0) to (-14,10)
        .close()
    )

    # Now extrude along Y (w_dir) by 4.0 mm
    result = profile_xz.extrude(4.0)

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD Generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102295_86f842dd_0000\ex2/generated.step")

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
