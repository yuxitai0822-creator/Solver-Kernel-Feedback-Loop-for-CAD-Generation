import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

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
    # The UV coordinates are scaled by the radius (10 mm) and straight_length (28 mm).
    # The arc centers are at (1.0, 0.0) and (3.8, 0.0) in UV space.
    # The straight length in UV space is 3.8 - 1.0 = 2.8, which maps to 28 mm.
    # So scale factor = 28 / 2.8 = 10.  (Also radius = 1.0 * 10 = 10 mm, consistent.)
    #
    # In 3D: U -> X, V -> -Z, W -> Y
    # So the profile lies in the XZ plane (with V inverted).
    # Extrude along Y (positive w direction).

    scale = 10.0  # UV to mm conversion factor

    # Build the stadium profile in the XZ plane (Y=0)
    # Arc1: center at (1.0*scale, 0, 0*scale) = (10, 0, 0), radius 10, from 0 to 180 degrees
    # In the XZ plane, arc from angle 0 (pointing +X) to 180 (pointing -X).
    # But note: V direction is -Z, so positive V in UV maps to negative Z.
    # The arc start_angle=0 means along +U direction (X axis), end_angle=180 means along -U direction.
    # So arc1 goes from (center + radius*cos(0), 0, center_v + radius*sin(0)) but V is -Z.
    # Actually, in UV: center_uv = (1.0, 0.0).  Arc from angle 0 to 180.
    # At angle 0: (1.0 + 1.0*cos(0), 0.0 + 1.0*sin(0)) = (2.0, 0.0)
    # At angle 180: (1.0 + 1.0*cos(180), 0.0 + 1.0*sin(180)) = (0.0, 0.0)
    # But the line endpoints are (1.0, -1.0) and (3.8, -1.0) for the bottom line.
    # Wait, the arc goes from 0 to 180, which in UV is from (2.0, 0.0) to (0.0, 0.0)?
    # That doesn't match the line endpoints. Let's re-examine.
    #
    # The curves list:
    #   Arc: center (1.0, 0.0), radius 1.0, start_angle=0, end_angle=180
    #   Line: start (1.0, -1.0) to (3.8, -1.0)
    #   Arc: center (3.8, 0.0), radius 1.0, start_angle=0, end_angle=180
    #   Line: start (3.8, 1.0) to (1.0, 1.0)
    #
    # For arc1: center (1.0, 0.0), radius 1.0, start=0, end=180.
    #   At angle 0: (1.0+1.0*cos(0), 0.0+1.0*sin(0)) = (2.0, 0.0)
    #   At angle 180: (1.0+1.0*cos(180), 0.0+1.0*sin(180)) = (0.0, 0.0)
    # But the line starts at (1.0, -1.0) and ends at (3.8, -1.0).
    # The arc endpoints should connect to the line endpoints.
    # The arc1 endpoint at angle 180 is (0.0, 0.0), but line1 starts at (1.0, -1.0).
    # This suggests the arc might be defined differently (maybe start_angle and end_angle are swapped, or the arc goes the other way).
    # Let's check the constraints: tangent constraints between arc1 and line1, line1 and arc2, etc.
    # The arc1 at angle 0 goes to (2.0, 0.0), at angle 180 goes to (0.0, 0.0).
    # The line1 goes from (1.0, -1.0) to (3.8, -1.0).
    # For tangency, the arc at its endpoint should have tangent direction matching the line.
    # If arc1 ends at (0.0, 0.0), the tangent direction at angle 180 is upward (positive V direction).
    # But line1 goes from (1.0, -1.0) to (3.8, -1.0) which is horizontal (positive U direction).
    # That doesn't match.
    #
    # Perhaps the arc is defined with start_angle=0 at the top and goes clockwise?
    # Or maybe the UV coordinate system has V pointing up (positive Z) and the arc is drawn differently.
    # Let's look at the dimensions: straight_length = 28 mm, radius = 10 mm.
    # The UV straight length is 3.8 - 1.0 = 2.8, scale = 10.
    # The radius in UV is 1.0, scale = 10 -> 10 mm. Good.
    #
    # Let's try to reconstruct the profile from the dimensions directly.
    # A stadium shape: two semicircles of radius R connected by straight lines of length L.
    # The total width = 2*R + L, total height = 2*R.
    # Here R = 10 mm, L = 28 mm.
    # So width = 48 mm, height = 20 mm.
    # The validation intents confirm: span_u = 48, span_v = 20, span_w = 4.
    #
    # In the UV frame: U is along the length (width), V is along the height.
    # The profile spans from U=0 to U=48, V=-10 to V=10 (since height=20, centered at V=0).
    # But the UV coordinates given are scaled: arc centers at (1.0, 0.0) and (3.8, 0.0).
    # With scale=10, these become (10, 0) and (38, 0).
    # The radius is 1.0*10 = 10 mm.
    # So the left semicircle center is at (10, 0), right at (38, 0).
    # The left semicircle goes from angle 0 (pointing right) to angle 180 (pointing left).
    # At angle 0: (10+10, 0) = (20, 0)
    # At angle 180: (10-10, 0) = (0, 0)
    # The right semicircle: center (38, 0), radius 10.
    # At angle 0: (38+10, 0) = (48, 0)
    # At angle 180: (38-10, 0) = (28, 0)
    # The bottom line connects (0, -10) to (48, -10)? No, the line endpoints from UV are (1.0, -1.0) and (3.8, -1.0).
    # Scaled: (10, -10) to (38, -10).
    # The top line: (38, 10) to (10, 10).
    # So the left arc goes from (10, -10) to (10, 10) through (0, 0)?
    # Actually, arc1 center (10, 0), radius 10, from angle 0 to 180.
    # At angle -90 (pointing down): (10, -10)
    # At angle 90 (pointing up): (10, 10)
    # At angle 0 (pointing right): (20, 0)
    # At angle 180 (pointing left): (0, 0)
    # So the arc from angle -90 to 90 goes from (10, -10) up to (10, 10) via the right side (passing through (20, 0)).
    # But the line endpoints are at (10, -10) and (38, -10) for the bottom, and (38, 10) and (10, 10) for the top.
    # So the arc should connect to the line at (10, -10) and (10, 10).
    # That means the arc goes from angle -90 to 90 (or 270 to 90).
    # But the design says start_angle=0, end_angle=180.
    # This is ambiguous. Let's just build the stadium from the dimensions directly.

    # Build the stadium profile using CadQuery's built-in methods.
    # We'll create a 2D sketch in the XZ plane (Y=0), then extrude along Y.

    R = 10.0
    L = 28.0

    # Create the profile as a wire
    # Left semicircle: center at (R, 0), radius R, from -90 to 90 degrees (bottom to top)
    # Right semicircle: center at (R+L, 0), radius R, from 90 to 270 degrees (top to bottom)
    # Bottom line: from (0, -R) to (2*R+L, -R)
    # Top line: from (2*R+L, R) to (0, R)

    # But we need to be careful about the coordinate system.
    # The design plan says: u_dir = (1,0,0) = X, v_dir = (0,0,-1) = -Z, w_dir = (0,1,0) = Y.
    # So the profile is in the XZ plane, with V mapping to -Z.
    # That means positive V in UV maps to negative Z in 3D.
    # So the profile's V coordinate (height) goes from -R to R, which maps to Z from R to -R.
    # To keep things simple, we'll build the profile in the XY plane (Z=0) and then rotate if needed.
    # Actually, let's just build it in the XZ plane directly.

    # Build the stadium in the XZ plane (Y=0)
    # Left semicircle: center at (R, 0, 0), radius R, in the XZ plane, from angle -90 to 90
    #   At angle -90: (R + R*cos(-90), 0, R*sin(-90)) = (R, 0, -R)
    #   At angle 90: (R + R*cos(90), 0, R*sin(90)) = (R, 0, R)
    # Right semicircle: center at (R+L, 0, 0), radius R, from angle 90 to 270
    #   At angle 90: (R+L + R*cos(90), 0, R*sin(90)) = (R+L, 0, R)
    #   At angle 270: (R+L + R*cos(270), 0, R*sin(270)) = (R+L, 0, -R)
    # Bottom line: from (R, 0, -R) to (R+L, 0, -R)
    # Top line: from (R+L, 0, R) to (R, 0, R)

    # Use CadQuery's Workplane to build the profile
    result = (
        cq.Workplane("XY")
        .moveTo(R, -R)  # Start at bottom of left semicircle (X=R, Y=-R)
        .threePointArc((R+R, 0), (R, R))  # Arc to top of left semicircle
        .lineTo(R+L, R)  # Top line to right semicircle top
        .threePointArc((R+L+R, 0), (R+L, -R))  # Arc to bottom of right semicircle
        .lineTo(R, -R)  # Bottom line back to start
        .close()
        .extrude(4.0)  # Extrude along Z (positive w direction is Y, but we built in XY, so extrude along Z?)
    )

    # Wait, we built in XY plane (Z=0), but the design says profile is in XZ plane.
    # Let's adjust: build in XZ plane (Y=0) and extrude along Y.
    # In CadQuery, we can use workplane "XZ" to build in the XZ plane.

    result = (
        cq.Workplane("XZ")
        .moveTo(R, -R)  # Start at bottom of left semicircle (X=R, Z=-R)
        .threePointArc((R+R, 0), (R, R))  # Arc to top of left semicircle (X=R, Z=R)
        .lineTo(R+L, R)  # Top line to right semicircle top (X=R+L, Z=R)
        .threePointArc((R+L+R, 0), (R+L, -R))  # Arc to bottom of right semicircle (X=R+L, Z=-R)
        .lineTo(R, -R)  # Bottom line back to start
        .close()
        .extrude(4.0)  # Extrude along Y (positive w direction)
    )

    # The result should be a stadium extrusion with:
    #   span along X: from 0 to 2*R+L = 48 mm
    #   span along Z: from -R to R = -10 to 10 mm (total 20 mm)
    #   span along Y: from 0 to 4 mm
    # This matches the validation intents.

    # Export to STEP
    import cadquery as cq
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102295_86f842dd_0000\\neg_02/generated.step")

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
