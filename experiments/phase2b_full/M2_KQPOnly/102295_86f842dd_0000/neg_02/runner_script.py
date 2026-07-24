import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: stadium extrusion
    # Dimensions: straight_length = 28.0 mm, radius = 10.0 mm, extrude distance = 4.0 mm
    # The stadium profile consists of two arcs (radius 10.0) connected by two lines (length 28.0)
    # The profile is defined in the UV plane where:
    #   u_dir = (1,0,0) -> X axis
    #   v_dir = (0,0,-1) -> -Z axis (so positive v goes in -Z direction)
    #   w_dir = (0,1,0) -> Y axis (extrude direction)
    #
    # To build in CadQuery, we create the stadium profile on the XY plane (or XZ) and extrude along Y.
    # We'll place the stadium centered at origin for simplicity.

    # The stadium: two arcs of radius 10.0, centers at x = -14.0 and x = 14.0 (since straight_length = 28.0)
    # Actually, from the curves:
    #   arc1: center_uv = (1.0, 0.0), radius = 1.0 (in UV coords, but scaled by 10?)
    #   line1: from (1.0, -1.0) to (3.8, -1.0)
    #   arc2: center_uv = (3.8, 0.0), radius = 1.0
    #   line2: from (3.8, 1.0) to (1.0, 1.0)
    # The dimensions say straight_length = 28.0, radius = 10.0.
    # The UV coordinates are scaled: the distance between centers is 2.8 (from 1.0 to 3.8), which corresponds to 28.0 mm.
    # So scale factor = 10.0. The radius in UV is 1.0, which corresponds to 10.0 mm.
    # So we can build directly with the given dimensions.

    # Build the stadium profile using CadQuery's 2D primitives.
    # We'll create a workplane on the XZ plane (since v_dir is -Z, u_dir is X, w_dir is Y).
    # Actually, let's use XY plane and then rotate if needed, but simpler: use XZ plane.
    # The profile lies in the UV plane: u = X, v = -Z. So we can work on plane XZ.

    # Create the stadium as a wire:
    # Center of first arc at (1.0*10, 0) = (10, 0) in mm? Wait, the UV coords are already in mm after scaling.
    # Let's just use the explicit dimensions: straight_length = 28.0, radius = 10.0.
    # The centers are at x = -14.0 and x = 14.0 (half of straight length).
    # The arcs go from 0 to 180 degrees (top half for first arc, bottom half for second? Actually from curves:
    #   arc1: start_angle=0, end_angle=180 -> top semicircle (positive v direction? v is -Z, so careful)
    #   line1: from (1.0, -1.0) to (3.8, -1.0) -> bottom line
    #   arc2: start_angle=0, end_angle=180 -> top semicircle
    #   line2: from (3.8, 1.0) to (1.0, 1.0) -> top line
    # So the stadium is oriented with flat sides on top and bottom, arcs on left and right.
    # In UV: u is horizontal, v is vertical (but v_dir = -Z, so positive v is -Z).
    # We'll build on XY plane and then rotate if needed, but let's just build on XZ plane.

    # Let's build using CadQuery's 2D construction:
    # We'll create a workplane on the XZ plane, then draw the stadium.

    result = (
        cq.Workplane("XZ")
        .moveTo(-14.0, 0.0)  # start at left arc center? Actually start at bottom-left of left arc
        # Better: use the center of left arc at (-14, 0) and draw arc from 180 to 0 (top to bottom?)
        # Let's use the three-point arc method or radius arc.
        # Simpler: use the built-in `stadium` method if available? No, CadQuery doesn't have stadium.
        # We'll construct using lines and arcs.
        # Start at bottom-left corner of left arc: (-14.0, -10.0)
        .moveTo(-14.0, -10.0)
        # Arc from bottom to top around left center (-14, 0), radius 10, from -90 to 90 degrees? 
        # Actually we want the arc that goes from bottom (-14, -10) to top (-14, 10) with center (-14, 0).
        # That's a 180-degree arc. In CadQuery, we can use threePointArc or radiusArc.
        # Using radiusArc: start point is current, end point is (-14, 10), and we need to specify the arc direction.
        # The arc should go to the left (negative X direction) to form a semicircle.
        # But radiusArc expects the arc to be on the workplane, and we need to give the end point and the radius.
        # Actually, radiusArc(endPoint, radius) draws an arc from current point to endPoint with given radius.
        # The arc is drawn in the direction that makes the center lie to the left of the line from start to end.
        # For a semicircle from bottom to top, the center is to the left (negative X), so radiusArc should work.
        .radiusArc(( -14.0, 10.0 ), 10.0 )
        # Now at top-left corner (-14, 10). Draw top line to top-right corner (14, 10).
        .lineTo(14.0, 10.0)
        # Now at top-right corner. Draw arc from top to bottom around right center (14, 0), radius 10.
        # From (14, 10) to (14, -10), center at (14, 0), arc goes to the right (positive X).
        .radiusArc((14.0, -10.0), 10.0)
        # Now at bottom-right corner. Draw bottom line back to start.
        .lineTo(-14.0, -10.0)
        .close()
        # Now we have a closed wire. Extrude along Y (which is w_dir) by 4.0 mm.
        .extrude(4.0)
    )

    # The above builds the stadium on the XZ plane and extrudes along Y.
    # But the design plan says v_dir = (0,0,-1), so positive v is -Z. Our profile uses Z as vertical.
    # That's fine: the profile is in XZ plane, with Z as the v direction (but inverted sign).
    # The extrude direction is w_dir = (0,1,0) = Y. So extrusion along Y is correct.
    # The resulting part should have dimensions: span along X = 48.0 (from -24 to 24? Actually from -14-10=-24 to 14+10=24), 
    # span along Z = 20.0 (from -10 to 10), span along Y = 4.0.
    # That matches the validation intents: q_span_u = 48.0, q_span_v = 20.0, q_span_w = 4.0.

    # Export
    import cadquery as cq
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102295_86f842dd_0000\\neg_02/generated.step")

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
