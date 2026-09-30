import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate based on the design plan
    # Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
    # The profile is a rectangle with corners at (0,0), (171.45,0), (171.45,110.998), (0,110.998)
    # Note: The design plan uses a local frame where u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the rectangle lies in the XZ plane (u along X, v along -Z) and extrudes along Y (w direction)

    # Build the rectangle in the XY plane for simplicity, then rotate to match the frame
    # Actually, we can just build it in the XY plane and extrude along Z, then rotate if needed.
    # But the design plan's frame has v_dir = (0,0,-1) and w_dir = (0,1,0).
    # To match: u along X, v along -Z, w along Y.
    # So the rectangle is in the X-Z plane (with v reversed), extruded along Y.
    # We'll create a workplane on the XZ plane, draw the rectangle, and extrude along Y.

    # Create the rectangle on the XZ plane (front plane in CadQuery)
    # The rectangle spans from (0,0) to (171.45, 110.998) in the local UV coordinates.
    # In the XZ plane: u -> X, v -> -Z, so the rectangle goes from X=0 to X=171.45, Z=0 to Z=-110.998
    # We'll offset so that the min corner is at (0,0,0) in world coordinates.

    result = (
        cq.Workplane("XZ")
        .rect(171.45, 110.998, centered=False)
        .extrude(6.35)
    )

    # The rect is drawn with the first corner at (0,0) in the workplane, which corresponds to (0,0,0) in world.
    # The extrusion direction is along the workplane normal, which for "XZ" is the Y axis (positive).
    # This matches the design plan: w_dir = (0,1,0), extrude in +w direction.

    # Export the result
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108850_0dcd5ef1_0004\\neg_03/generated.step")

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
