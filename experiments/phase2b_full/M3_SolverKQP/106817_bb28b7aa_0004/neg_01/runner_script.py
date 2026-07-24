import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: washer (extruded annulus)
    # Dimensions (in mm):
    #   Outer radius = 5.5372 mm
    #   Inner radius = 1.9812 mm
    #   Thickness (extrude distance) = 1.3208 mm
    #   Center in UV plane: u=-25.400001, v=12.7
    #   Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    #   Extrude direction: +w (positive y in world)

    # Build the washer centered at origin in local frame, then translate to match center_uv.
    # Since the frame has v_dir = (0,0,-1), the profile lies in the u-v plane (x-z plane in world).
    # We'll create the annulus in the XY plane (default CQ workplane) and then rotate/translate.

    # Step 1: Create the outer circle and inner circle as a single wire (annulus) in XY plane.
    outer_radius = 5.5372
    inner_radius = 1.9812
    thickness = 1.3208

    # Center in local UV: u=-25.400001, v=12.7
    # In world coordinates after applying frame:
    #   u -> x, v -> -z (since v_dir = (0,0,-1)), w -> y
    # So center in world: x = -25.400001, y = 0 (since w=0 for profile), z = -12.7
    center_x = -25.400001
    center_z = -12.7  # because v_dir = (0,0,-1) maps v to -z

    # Build the washer by extruding a circle and subtracting inner cylinder.
    # Use a workplane on the XZ plane? Actually easier: build in XY then rotate.
    # But the frame says profile is in u-v plane where u=x, v=-z, so the profile plane is XZ (y=0).
    # We'll use workplane("XZ") and then extrude in +Y direction.

    result = (
        cq.Workplane("XZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(thickness)
        # Translate to the correct center position
        .translate((center_x, 0, center_z))
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0004\\neg_01/generated.step")

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
