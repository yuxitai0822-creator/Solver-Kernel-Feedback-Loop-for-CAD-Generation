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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101269_f084ba14_0023\neg_02\iter_00\generated.step"

    # Design Plan: extruded rectangle
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in UV plane: u from 0 to 95.25, v from 0 to 571.5
    # But the curves in the design plan show start_uv and end_uv with values:
    #   curve0: (9.525, 57.15) -> (9.525, 0.0)
    #   curve1: (0.0, 57.15) -> (9.525, 57.15)
    #   curve2: (0.0, 0.0) -> (0.0, 57.15)
    #   curve3: (9.525, 0.0) -> (0.0, 0.0)
    # This describes a rectangle from u=0 to u=9.525, v=0 to v=57.15
    # But the dimensions say length_u=95.25, width_v=571.5
    # The perturbation says original=9.525, perturbed=11.43
    # So the perturbed rectangle should be u from 0 to 11.43, v from 0 to 57.15
    # Wait, the dimensions say length_u=95.25, width_v=571.5
    # But the curves show u from 0 to 9.525, v from 0 to 57.15
    # The perturbation changes 9.525 to 11.43
    # So the rectangle should be u from 0 to 11.43, v from 0 to 57.15
    # But the dimensions say length_u=95.25, width_v=571.5
    # This is inconsistent. Let me re-read the design plan.
    # The curves are in UV space. The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # The rectangle in UV space: u from 0 to 9.525, v from 0 to 57.15
    # But the dimensions say length_u=95.25, width_v=571.5
    # 95.25 / 9.525 = 10, 571.5 / 57.15 = 10
    # So the curves are scaled by 10? Or the dimensions are scaled?
    # Actually, looking at the previous script, it uses coordinates like (104.775, 571.5) and (-9.525, 0.0)
    # The width is 104.775 - (-9.525) = 114.3, height is 571.5 - 0 = 571.5
    # But the design plan says length_u=95.25, width_v=571.5
    # The previous script has a different coordinate system.
    # Let me just follow the design plan exactly.
    # The design plan says:
    #   rectangle in UV plane: u from 0 to 9.525, v from 0 to 57.15
    #   But the perturbation changes 9.525 to 11.43
    #   So u from 0 to 11.43, v from 0 to 57.15
    #   Extrude in +w direction by 19.05 mm
    # The frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So in world coordinates:
    #   u axis = x axis
    #   v axis = -z axis
    #   w axis = y axis
    # So the rectangle in world: x from 0 to 11.43, z from -57.15 to 0 (since v_dir=[0,0,-1])
    # Extrude in +y direction by 19.05 mm

    # Build the rectangle in the XZ plane (since v_dir is -z, the sketch plane is XZ)
    # Actually, let's use the Workplane on XZ plane
    result = (
        cq.Workplane("XZ")
        .rect(11.43, 57.15, centered=False)
        .extrude(19.05)
    )

    # But wait, the rectangle should be positioned at u=0, v=0 in UV space
    # In world, that's x=0, z=0 (since v_dir=[0,0,-1], v=0 means z=0)
    # The rect() with centered=False places the rectangle with its lower-left corner at the current point
    # So we need to move to (0, 0) first
    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .rect(11.43, 57.15, centered=False)
        .extrude(19.05)
    )

    # But the design plan says the rectangle goes from u=0 to u=11.43, v=0 to v=57.15
    # In world: x from 0 to 11.43, z from 0 to -57.15 (since v_dir=[0,0,-1])
    # The rect() with centered=False places the rectangle with its lower-left corner at the current point
    # So if we moveTo(0, 0), the rectangle will be from (0, 0) to (11.43, 57.15) in the sketch plane
    # But the sketch plane is XZ, so x from 0 to 11.43, z from 0 to 57.15
    # But we want z from 0 to -57.15
    # So we need to negate the v dimension or use a different approach
    # Let's use a polyline to be precise

    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(11.43, 0)
        .lineTo(11.43, -57.15)
        .lineTo(0, -57.15)
        .close()
        .extrude(19.05)
    )

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
