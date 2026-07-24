import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile based on the design plan
    # The profile is defined in the UV plane where:
    #   u_dir = (1,0,0)  -> X axis
    #   v_dir = (0,0,-1) -> -Z axis (so positive V goes in -Z direction)
    #   w_dir = (0,1,0)  -> Y axis (extrude direction)
    #
    # The rectangle corners in UV space:
    #   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
    # But note: the curves are given in a specific order that forms a closed loop.
    # We'll construct the rectangle using the span dimensions:
    #   length_u = 95.25 mm  (along u direction = X)
    #   width_v = 571.5 mm   (along v direction = -Z)
    #
    # The extrude distance is 19.05 mm along +w direction = +Y

    # Build the rectangle in the XY plane (since we want to extrude along Y)
    # We'll place the rectangle so that its bottom-left corner is at (0,0,0)
    # and it spans 95.25 in X and 571.5 in Z (since v_dir = -Z, positive v goes to negative Z)
    # To keep things simple, we'll just create a rectangle in the XZ plane and extrude along Y.

    result = (
        cq.Workplane("XY")
        .rect(95.25, 571.5)  # width along X, height along Z (since rect uses X and Y of current plane)
        .extrude(19.05)       # extrude along positive Z of current plane (which is Y in world? Actually Workplane("XY") extrudes along Z)
    )

    # But careful: Workplane("XY") means the workplane is the XY plane, and extrude goes along Z.
    # The design plan says: u_dir = X, v_dir = -Z, w_dir = Y, extrude along +w = +Y.
    # So we need the rectangle in the XZ plane and extrude along Y.
    # Let's use Workplane("XZ") instead.

    result = (
        cq.Workplane("XZ")
        .rect(95.25, 571.5)  # width along X, height along Z
        .extrude(19.05)       # extrude along Y (positive Y)
    )

    # The rectangle is centered by default. We want it positioned so that the min corner is at origin.
    # rect() creates a rectangle centered at (0,0) of the workplane. To shift it so that one corner is at origin,
    # we can use .center() or .moveTo() before rect, or use .polyline() to define exact points.
    # Let's use .polyline() to define the exact corners as per the design plan.
    # The corners in UV: (0,0), (9.525,0), (9.525,57.15), (0,57.15)
    # But these are in UV space where U = X, V = -Z. So in world coordinates:
    #   (0,0) -> (0, 0, 0)
    #   (9.525,0) -> (9.525, 0, 0)
    #   (9.525,57.15) -> (9.525, 0, -57.15)
    #   (0,57.15) -> (0, 0, -57.15)
    # Wait, the design plan says length_u = 95.25, but the UV coordinates only go up to 9.525?
    # That's suspicious. Let me re-read: the curves show start_uv and end_uv values like 9.525 and 57.15.
    # The dimensions say length_u = 95.25, width_v = 571.5.
    # The UV coordinates in the curves seem to be scaled by 0.1? Or maybe the compiler notes say cm_to_mm (x10).
    # So the original was in cm, converted to mm by multiplying by 10.
    # 9.525 cm = 95.25 mm, 57.15 cm = 571.5 mm. So the UV values are in cm, but we need mm.
    # So the rectangle corners in mm are:
    #   (0,0), (95.25,0), (95.25,571.5), (0,571.5)
    # In world: X from 0 to 95.25, Z from -571.5 to 0 (since v_dir = -Z).

    # Let's build it properly with polyline to ensure exact placement.

    result = (
        cq.Workplane("XZ")
        .polyline([
            (0, 0),          # point 1: (X=0, Z=0)
            (95.25, 0),      # point 2: (X=95.25, Z=0)
            (95.25, -571.5), # point 3: (X=95.25, Z=-571.5) because v_dir = -Z, so positive V goes to negative Z
            (0, -571.5)      # point 4: (X=0, Z=-571.5)
        ])
        .close()
        .extrude(19.05)  # extrude along Y (positive Y)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\101269_f084ba14_0023\ex2/generated.step")

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
