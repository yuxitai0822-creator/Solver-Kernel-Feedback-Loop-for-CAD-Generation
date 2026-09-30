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
    #   v_dir = (0,0,-1) -> -Z axis (so positive v goes downward in Z)
    #   w_dir = (0,1,0)  -> Y axis (extrude direction)
    #
    # The profile curves (in UV coordinates):
    #   Arc1: center (1.0, 0.0), radius 1.0, start_angle=0, end_angle=180
    #   Line1: from (1.0, -1.0) to (3.8, -1.0)
    #   Arc2: center (3.8, 0.0), radius 1.0, start_angle=0, end_angle=180
    #   Line2: from (3.8, 1.0) to (1.0, 1.0)
    #
    # The UV coordinates are scaled by the radius (10 mm) and straight_length (28 mm).
    # The arc centers are at u = 1.0 and u = 3.8 in UV space.
    # The straight length in UV space is (3.8 - 1.0) = 2.8.
    # Scaling: radius_scale = 10.0 / 1.0 = 10.0
    #          straight_scale = 28.0 / 2.8 = 10.0
    # So scaling factor = 10.0

    scale = 10.0

    # Build the stadium profile in the XY plane (since we'll rotate later)
    # We'll construct it centered at origin for convenience.
    # In UV space: arc1 center at (1,0), arc2 center at (3.8,0), radius=1.
    # After scaling: arc1 center at (10,0), arc2 center at (38,0), radius=10.
    # The straight length = 28 mm, which matches (38-10) = 28.

    # We'll build the profile using CadQuery's 2D primitives.
    # Approach: create a rectangle for the straight section and two circles for the ends,
    # then fuse them. But to get exact stadium shape, we can use a workplane and sketch.

    # Create a workplane in XY plane (we'll later orient to match the design frame)
    # The design frame: u_dir = X, v_dir = -Z, w_dir = Y.
    # So the profile lies in the X-Z plane (u along X, v along -Z).
    # We'll build on the XZ plane and then extrude along Y.

    # Build the stadium profile on the XZ plane (Y=0)
    # We'll use a workplane on the XZ plane (front plane in CadQuery)
    # Actually, CadQuery's default workplane is XY. We'll use workplane("XZ") to get XZ.

    # Create the profile by combining a rectangle and two circles
    # Rectangle: from x=10 to x=38, z from -10 to 10 (width 20 = 2*radius)
    # Circles: at (10,0) and (38,0) with radius 10

    # Using CadQuery's 2D operations:
    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .moveTo(10, -10)
        .lineTo(38, -10)
        .threePointArc((48, 0), (38, 10))
        .lineTo(10, 10)
        .threePointArc((0, 0), (10, -10))
        .close()
        .extrude(4.0)  # extrude along Y (positive direction)
    )

    # The above builds the stadium with the correct dimensions:
    # - Straight section from x=10 to x=38, z from -10 to 10
    # - Arc at right end: center at (38,0), radius 10, from z=-10 to z=10 (180 degrees)
    # - Arc at left end: center at (10,0), radius 10, from z=10 to z=-10 (180 degrees)
    # - Extrude 4 mm along Y

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102295_86f842dd_0000\neg_01/generated.step")

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
