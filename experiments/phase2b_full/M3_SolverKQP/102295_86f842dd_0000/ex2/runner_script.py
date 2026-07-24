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
    #   - straight_length: 28.0 mm (inferred from point span)
    #   - radius: 10.0 mm (explicit)
    #   - extrude distance: 4.0 mm
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
    # The arc radius in UV is 1.0, which maps to 10 mm.
    # The straight segment length in UV is 2.8 (from 1.0 to 3.8), which maps to 28 mm.
    # So scaling factor = 10.

    # Build the stadium profile in the XY plane (since we'll rotate later)
    # We'll construct it centered at origin for convenience.

    radius = 10.0
    straight_length = 28.0

    # The UV coordinates: arc centers at (1.0, 0.0) and (3.8, 0.0) with radius 1.0
    # After scaling by 10: centers at (10, 0) and (38, 0), radius 10.
    # The straight segment goes from (10, -10) to (38, -10) and back.

    # Build the profile using CadQuery's 2D construction
    # We'll create a wire from points and arcs.

    # Start at the bottom-left of the right arc (going clockwise)
    # Actually, let's trace the profile in order: 
    #   Arc1 (top semicircle, left side), Line1 (top straight), Arc2 (top semicircle, right side), Line2 (bottom straight)
    # But the UV arcs go from 0 to 180 degrees, which in standard math is counterclockwise from +X axis.
    # In UV: start_angle=0, end_angle=180 means from +U to -U (semicircle above the U axis? Actually depends on orientation)
    # Let's just build it step by step.

    # We'll use the workplane on XY plane, then extrude in Y direction (w_dir = (0,1,0))
    # But the design plan says v_dir = (0,0,-1), so the profile is in XZ plane? 
    # Actually, let's keep it simple: build in XY, extrude in Z, then rotate if needed.
    # The validation expects span along u=48, v=20, w=4.
    # u_dir = X, v_dir = -Z, w_dir = Y.
    # So the profile lies in the X-Z plane (u-v plane), and extrude along Y.
    # Let's build in the XZ plane.

    # Create the stadium profile in the XZ plane (Y=0)
    # We'll use a workplane on the XZ plane (which is 'XZ' in CadQuery)

    result = (
        cq.Workplane("XZ")
        .moveTo(10, 0)  # start at center of left arc
        .threePointArc((0, 10), (10, 20))  # arc from (10,0) to (10,20) through (0,10) -> radius 10, center (10,10)?
        # Actually, let's do it more carefully.
    )

    # Let's rebuild from scratch with explicit points.
    # The stadium in UV: 
    #   Arc1: center (1,0), radius 1, from angle 0 to 180 -> points from (2,0) to (0,0) through (1,1)? 
    #   Actually start_angle=0 at (center_x + r, center_y) = (2,0), end_angle=180 at (0,0).
    #   So arc goes from (2,0) to (0,0) through (1,1) (counterclockwise).
    #   Line1: from (2, -1) to (0, -1)? No, start_uv of line is (1.0, -1.0) to (3.8, -1.0).
    #   Wait, the line connects the bottom of Arc1 to bottom of Arc2.
    #   Arc1 bottom is at (1, -1) (since center (1,0), radius 1, angle -90 deg).
    #   Arc2 bottom is at (3.8, -1) (center (3.8,0), radius 1, angle -90 deg).
    #   So line goes from (1, -1) to (3.8, -1).
    #   Arc2 goes from (3.8, -1) to (3.8, 1) through (4.8, 0) (counterclockwise from -90 to +90).
    #   Line2 goes from (3.8, 1) to (1, 1).
    #   Arc1 top goes from (1, 1) to (1, -1) through (0, 0) (counterclockwise from +90 to -90).
    #
    # So the profile is: start at (1, -1), line to (3.8, -1), arc to (3.8, 1), line to (1, 1), arc to (1, -1).
    # Scaled by 10: (10, -10), (38, -10), (38, 10), (10, 10), back to (10, -10).

    # Build the wire manually.
    from math import pi

    # Points in 2D (XZ plane, where X=U, Z=V)
    pts = [
        (10.0, -10.0),  # start bottom left
        (38.0, -10.0),  # bottom right
        (38.0, 10.0),   # top right
        (10.0, 10.0),   # top left
    ]

    # Create the stadium shape using CadQuery's polygon with arcs
    # We'll use the workplane to create a closed wire.

    # Approach: create a 2D sketch with lines and arcs
    wp = cq.Workplane("XZ")

    # Build the profile as a closed wire
    # Start at bottom-left corner of the left arc (10, -10)
    # The left arc is a semicircle from (10, -10) to (10, 10) with center (10, 0), radius 10
    # The right arc is a semicircle from (38, -10) to (38, 10) with center (38, 0), radius 10

    # We can use the 'sagitta' method or threePointArc.
    # For left arc: from (10, -10) to (10, 10) through (0, 0) (center at (10,0), radius 10, going left)
    # For right arc: from (38, 10) to (38, -10) through (48, 0) (center at (38,0), radius 10, going right)

    # Let's build the wire step by step:
    wire = (
        cq.Workplane("XZ")
        .moveTo(10.0, -10.0)  # start at bottom of left arc
        .lineTo(38.0, -10.0)  # bottom straight
        .threePointArc((48.0, 0.0), (38.0, 10.0))  # right arc (through (48,0) to (38,10))
        .lineTo(10.0, 10.0)   # top straight
        .threePointArc((0.0, 0.0), (10.0, -10.0))  # left arc (through (0,0) to (10,-10))
        .close()  # close the wire
    )

    # Now extrude along Y axis (w_dir) by 4.0 mm
    # The workplane is XZ, so extrude in Y direction (positive Y)
    result = wire.extrude(4.0)

    # The resulting solid should have:
    #   - span along X (u): from min X to max X = from 0 to 48 = 48 mm
    #   - span along Z (v): from -10 to 10 = 20 mm
    #   - span along Y (w): from 0 to 4 = 4 mm
    # This matches the validation intents.

    # Export to STEP
    import cadquery as cq
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102295_86f842dd_0000\\ex2/generated.step")

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
