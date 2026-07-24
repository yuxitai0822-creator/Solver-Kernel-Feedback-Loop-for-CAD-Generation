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
    # The stadium profile consists of:
    #   - Two arcs (radius 1.0 in UV, but scaled by 10 from cm to mm conversion)
    #   - Two lines connecting them
    #
    # The UV coordinates in the plan are:
    #   Arc1: center (1.0, 0.0), radius 1.0, start 0°, end 180°
    #   Line1: (1.0, -1.0) to (3.8, -1.0)
    #   Arc2: center (3.8, 0.0), radius 1.0, start 0°, end 180°
    #   Line2: (3.8, 1.0) to (1.0, 1.0)
    #
    # After cm->mm conversion (x10), these become:
    #   Arc1: center (10, 0), radius 10, start 0°, end 180°
    #   Line1: (10, -10) to (38, -10)
    #   Arc2: center (38, 0), radius 10, start 0°, end 180°
    #   Line2: (38, 10) to (10, 10)
    #
    # The straight_length = 28 mm (distance between arc centers = 38-10 = 28)
    # The radius = 10 mm
    # Extrude in +w direction (which is +y in our coordinate system) by 4 mm

    # Build the stadium profile in the XY plane (z=0)
    # We'll use workplane and then extrude along Z, then rotate if needed.
    # Actually, the frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # So the profile lies in the UV plane (XZ plane in world), and extrudes along W (Y).
    # Let's build on plane XZ and extrude along Y.

    # Create the stadium profile as a wire
    # Start with the first arc (top arc in UV, but in XZ plane)
    # Arc1: center (10, 0) in UV, radius 10, from 0° to 180°
    # In XZ plane: center at (10, 0), arc from (20, 0) to (0, 0) going through (10, 10)
    # Actually start_angle=0 means point at (center.x + r, center.y) = (20, 0)
    # end_angle=180 means point at (center.x - r, center.y) = (0, 0)
    # The arc goes counterclockwise from 0 to 180, so it goes through (10, 10)

    # Line1: from (20, 0) to (20, -10)? Wait, let's re-check UV coordinates.
    # In UV: Arc1 center (1,0), radius 1, start 0°, end 180°
    #   start_uv = (1+1, 0) = (2, 0)  -> after scaling: (20, 0)
    #   end_uv = (1-1, 0) = (0, 0)    -> after scaling: (0, 0)
    # Line1: start_uv (1, -1) -> (10, -10), end_uv (3.8, -1) -> (38, -10)
    # But wait, the arc end is at (0,0) and line starts at (10,-10)? That doesn't match.
    # Let's re-examine: the curves are ordered sequentially.
    # Curve 0: arc from angle 0 to 180, center (1,0), radius 1
    #   start point: (1+1*cos(0), 0+1*sin(0)) = (2, 0)
    #   end point: (1+1*cos(180), 0+1*sin(180)) = (0, 0)
    # Curve 1: line from (1, -1) to (3.8, -1)
    # But the arc ends at (0,0) and line starts at (1,-1) — not connected!
    # This suggests the UV coordinates are in a different orientation.
    # Let's look at the actual dimensions: straight_length=28, radius=10.
    # After cm->mm: straight_length=28, radius=10.
    # The arc centers should be separated by straight_length = 28.
    # Arc1 center at (0,0), Arc2 center at (28,0) would give radius 10.
    # But the plan says Arc1 center (1,0) and Arc2 center (3.8,0) — difference 2.8.
    # After x10 scaling: 10 and 38 — difference 28. That matches!
    # So the UV coordinates are already in cm, and we scale by 10.
    # But the arc radius is 1 in UV, which becomes 10 mm — matches.
    # The line endpoints: (1,-1) to (3.8,-1) become (10,-10) to (38,-10).
    # But the arc ends at (0,0) after scaling? No, arc ends at (10-10, 0) = (0,0).
    # The line starts at (10,-10). These don't connect.
    # 
    # I think the issue is that the arc start/end angles might be defined differently.
    # Let's try: start_angle=0 means point at (center.x, center.y + r) if we consider
    # the arc going upward. But the standard is (center.x + r*cos(a), center.y + r*sin(a)).
    # 
    # Actually, looking at the profile: it's a stadium shape.
    # The typical stadium has two semicircles connected by straight lines.
    # The straight lines are at the top and bottom (in UV).
    # So the arcs should be at the left and right ends.
    # Arc1 center (1,0) radius 1: left semicircle from (1, -1) to (1, 1) going left.
    #   start_angle=0: (1+1*cos(0), 0+1*sin(0)) = (2, 0) — that's to the right, not left.
    #   end_angle=180: (1+1*cos(180), 0+1*sin(180)) = (0, 0) — that's to the left.
    # So the arc goes from right to left through the bottom? No, from 0 to 180 goes
    # counterclockwise: (2,0) -> (2,1) -> (0,1) -> (0,0)? No, that's not right.
    # Actually cos(0)=1, sin(0)=0; cos(90)=0, sin(90)=1; cos(180)=-1, sin(180)=0.
    # So the arc goes from (2,0) up to (1,1) then to (0,0). That's a semicircle on the right side.
    # But we want the left side semicircle. So maybe the arc is defined differently.
    # 
    # Let's just build the stadium from the given dimensions: straight_length=28, radius=10.
    # The profile in UV: two semicircles of radius 10 at centers (10,0) and (38,0).
    # The straight lines connect (10, -10) to (38, -10) and (10, 10) to (38, 10).
    # This forms a valid stadium.

    # Build using CadQuery's built-in methods
    result = (
        cq.Workplane("XZ")
        .center(24, 0)  # center of the stadium (midpoint between arc centers)
        .stadium(28, 10)  # length=straight_length, width=2*radius
        .extrude(4.0)  # extrude along Y (which is +w direction)
    )

    # The stadium is now centered at (24, 0, 0) in XZ plane, extruded along Y from -2 to 2.
    # But we need to verify orientation: the plan says v_dir = (0,0,-1), w_dir = (0,1,0).
    # So the profile is in UV plane (XZ), extrude along W (Y).
    # The stadium function creates a shape centered at the workplane center.
    # We need to ensure the shape matches the expected spans:
    #   span_u (X): 48 mm (from 0 to 48)
    #   span_v (Z): 20 mm (from -10 to 10)
    #   span_w (Y): 4 mm (from 0 to 4)
    # The current result is centered at (24,0,0) with span 48 in X, 20 in Z, 4 in Y.
    # But the Y span goes from -2 to 2, not 0 to 4.
    # We need to shift so that the bottom is at Y=0.

    result = result.translate((0, 2.0, 0))  # move so Y goes from 0 to 4

    # Also need to shift in X so that the leftmost point is at X=0.
    # The stadium spans from 24-24=0 to 24+24=48 in X, so it's already at X from 0 to 48.
    # Actually center at 24, length 28 means the straight part goes from 24-14=10 to 24+14=38.
    # The arcs extend 10 more: leftmost at 0, rightmost at 48. So X span is 48. Good.
    # Z span: from -10 to 10, so span is 20. Good.

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102295_86f842dd_0000\neg_01/generated.step")

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
