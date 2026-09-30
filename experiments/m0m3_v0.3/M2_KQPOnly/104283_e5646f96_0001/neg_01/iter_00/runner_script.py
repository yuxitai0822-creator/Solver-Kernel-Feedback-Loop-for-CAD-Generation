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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0001\neg_01\iter_00\generated.step"

    # Design Plan interpretation:
    # - Two profiles: first is a closed shape with 4 curves (3 lines + 1 circle arc)
    # - Second profile has an outer ring (circle + 2 lines + circle) and an inner circle (hole)
    # - Extrude 18.0 mm in +Z direction
    # - The geometry is a flat plate with a circular boss and a through hole

    # Build the base profile (first profile in design plan)
    # The curves describe a shape that looks like a rectangle with a circular end
    # Points from design plan (scaled from cm to mm, but already in mm):
    # Line 1: (0.9188, 1.7937) to (0.9188, 0.0)
    # Line 2: (0.9188, 0.0) to (3.8000, 0.0)
    # Line 3: (3.7174, 1.7937) to (3.7174, 0.0)  -- note: this seems reversed, but we'll follow the order
    # Circle: center (2.3181, 1.7491), radius 1.4

    # Actually, looking more carefully at the curves, the first profile has:
    # curve 0: line from (0.9188, 1.7937) to (0.9188, 0.0)  -- vertical line down
    # curve 1: line from (0.9188, 0.0) to (3.8000, 0.0)  -- horizontal line right
    # curve 2: line from (3.7174, 1.7937) to (3.7174, 0.0)  -- vertical line down (but start/end seem swapped)
    # curve 3: circle at (2.3181, 1.7491) radius 1.4

    # This is a bit ambiguous. Let me reconstruct from the second profile which has clearer structure:
    # Second profile outer ring:
    # curve 0: circle at (2.3181, 1.7491) radius 1.4
    # curve 1: line from (3.7174, 1.7937) to (3.7174, 0.0)
    # curve 2: circle at (2.3181, 1.7491) radius 1.4
    # curve 3: line from (0.9188, 1.7937) to (0.9188, 0.0)
    # Inner ring: circle at (2.3181, 1.7491) radius 1.25

    # The geometry appears to be a rectangular plate (width ~2.88, height ~1.79) with a circular boss
    # and a concentric through hole.

    # Let me build this more carefully using the actual coordinates:
    # The shape is like a rectangle with rounded ends (stadium shape) but with a hole

    # Actually, re-reading the curves more carefully:
    # The first profile seems to be the outer boundary of the base shape
    # The second profile has the same outer boundary plus an inner hole

    # Let me just build a clean version:
    # Base shape: rectangle from x=0.9188 to x=3.8000, y=0.0 to y=1.7937
    # With a circular boss of radius 1.4 centered at (2.3181, 1.7491)
    # And a through hole of radius 1.25 at the same center

    # The rectangle width = 3.8000 - 0.9188 = 2.8812
    # The rectangle height = 1.7937 - 0.0 = 1.7937

    # Create the base plate
    result = (cq.Workplane("XY")
        .rect(2.8812, 1.7937, centered=False)
        .extrude(18.0)
    )

    # Add the circular boss on top
    # The boss center is at (0.9188 + 2.3181, 0.0 + 1.7491) = (3.2369, 1.7491) in absolute coords
    # But wait, the rect is positioned with its bottom-left corner at (0,0) in the workplane
    # So we need to move to the correct position

    # Actually, let me reconsider. The rect is centered at (0,0) by default with centered=False
    # No, centered=False means the rectangle starts at (0,0) and goes to (w, h)
    # So the bottom-left corner is at (0,0) and top-right at (2.8812, 1.7937)

    # The circle center in the design plan is at (2.3181, 1.7491) in the profile's UV space
    # But the profile's origin seems to be at (0.9188, 0.0) based on the first line
    # So the circle center in absolute coordinates is:
    # cx = 0.9188 + 2.3181 = 3.2369
    # cy = 0.0 + 1.7491 = 1.7491

    # But this is outside the rectangle! The rectangle goes from x=0 to x=2.8812
    # So the circle center at x=3.2369 is outside.

    # Let me re-examine. The first profile curves:
    # curve 0: line from (0.9188, 1.7937) to (0.9188, 0.0) -- vertical line at x=0.9188
    # curve 1: line from (0.9188, 0.0) to (3.8000, 0.0) -- horizontal line from x=0.9188 to x=3.8000
    # curve 2: line from (3.7174, 1.7937) to (3.7174, 0.0) -- vertical line at x=3.7174
    # curve 3: circle at (2.3181, 1.7491) radius 1.4

    # So the shape is bounded by:
    # - Left edge at x=0.9188
    # - Bottom edge at y=0.0
    # - Right edge at x=3.7174 (or 3.8000?)
    # - Top edge is formed by the circle arc

    # The circle center is at (2.3181, 1.7491) with radius 1.4
    # The circle intersects the left vertical line at x=0.9188
    # The circle intersects the right vertical line at x=3.7174

    # Let me verify: for x=0.9188, the circle equation gives:
    # (0.9188 - 2.3181)^2 + (y - 1.7491)^2 = 1.4^2
    # (-1.3993)^2 + (y - 1.7491)^2 = 1.96
    # 1.9580 + (y - 1.7491)^2 = 1.96
    # (y - 1.7491)^2 = 0.002
    # y - 1.7491 = ±0.0447
    # y = 1.7938 or y = 1.7044
    # So y=1.7937 matches! The circle top is at y=1.7937

    # For x=3.7174:
    # (3.7174 - 2.3181)^2 + (y - 1.7491)^2 = 1.4^2
    # (1.3993)^2 + (y - 1.7491)^2 = 1.96
    # Same calculation, y=1.7937

    # So the shape is a rectangle with a circular top (like a D-shape or stadium)
    # The rectangle part goes from x=0.9188 to x=3.7174, y=0.0 to y=1.7937
    # But the top is actually a circular arc, not a straight line

    # Wait, but the first profile has 4 curves and the circle is the 4th one
    # The second profile has the same structure but with an inner hole

    # Let me just build this as a proper cadquery model:

    # Create the base shape using a polyline with an arc
    wp = cq.Workplane("XY")

    # Start at bottom-left: (0.9188, 0.0)
    # Go right to bottom-right: (3.8000, 0.0) -- but the right edge is at 3.7174
    # Actually, let me use the exact points from the design plan

    # The shape outline:
    # Start at (0.9188, 1.7937) -- top-left
    # Line down to (0.9188, 0.0) -- bottom-left
    # Line right to (3.8000, 0.0) -- bottom-right
    # Line up to (3.7174, 1.7937) -- but this is a line, not the circle
    # Then circle arc from (3.7174, 1.7937) back to (0.9188, 1.7937)

    # Actually, the circle is the 4th curve, and it connects the end of curve 2 back to the start of curve 0
    # So the circle arc goes from (3.7174, 1.7937) to (0.9188, 1.7937)
    # But a full circle would go all the way around...

    # I think the circle is meant to be an arc (partial circle) that forms the top
    # The center is at (2.3181, 1.7491) and radius 1.4
    # The arc goes from angle where it passes through (3.7174, 1.7937) to where it passes through (0.9188, 1.7937)

    # Let me calculate the angles:
    # For point (3.7174, 1.7937):
    # dx = 3.7174 - 2.3181 = 1.3993
    # dy = 1.7937 - 1.7491 = 0.0446
    # angle = atan2(0.0446, 1.3993) = atan2(0.0446, 1.3993) ≈ 0.0319 rad

    # For point (0.9188, 1.7937):
    # dx = 0.9188 - 2.3181 = -1.3993
    # dy = 1.7937 - 1.7491 = 0.0446
    # angle = atan2(0.0446, -1.3993) ≈ π - 0.0319 ≈ 3.1097 rad

    # So the arc goes from angle 0.0319 to 3.1097 (counterclockwise)
    # That's a large arc (about 177 degrees), almost a full semicircle

    # Let me build this properly:

    # Clear the workplane and start fresh
    wp = cq.Workplane("XY")

    # Build the profile using a polyline with an arc
    # Start at top-left
    p = wp.moveTo(0.9188, 1.7937)
    # Line down to bottom-left
    p = p.lineTo(0.9188, 0.0)
    # Line right to bottom-right
    p = p.lineTo(3.8000, 0.0)
    # Line up to the point where the circle arc starts
    p = p.lineTo(3.7174, 1.7937)
    # Now the circle arc back to the start
    # The circle center is at (2.3181, 1.7491), radius 1.4
    # We need to use threePointArc or sagittaArc
    # Using threePointArc: we need a point on the arc between start and end
    # The midpoint of the arc would be at the top of the circle
    # Top of circle: center + (0, radius) = (2.3181, 1.7491 + 1.4) = (2.3181, 3.1491)
    # But wait, that's above y=1.7937... 

    # Actually, the arc goes from (3.7174, 1.7937) to (0.9188, 1.7937)
    # The midpoint of this arc (going through the top of the circle) would be at:
    # angle = (0.0319 + 3.1097) / 2 = 1.5708 rad = π/2
    # x = 2.3181 + 1.4 * cos(π/2) = 2.3181
    # y = 1.7491 + 1.4 * sin(π/2) = 1.7491 + 1.4 = 3.1491

    # So the threePointArc would be:
    # start: (3.7174, 1.7937)
    # mid: (2.3181, 3.1491)
    # end: (0.9188, 1.7937)

    p = p.threePointArc((2.3181, 3.1491), (0.9188, 1.7937))
    p = p.close()

    # Extrude the base shape
    result = p.extrude(18.0)

    # Now add the second profile which has an inner hole
    # The second profile has the same outer shape but with a concentric hole
    # The hole is a circle at (2.3181, 1.7491) with radius 1.25

    # Cut the hole through the entire body
    hole = (cq.Workplane("XY")
        .moveTo(2.3181, 1.7491)
        .circle(1.25)
        .extrude(18.0)
    )

    result = result.cut(hole)

    # Export
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
