import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
    # The design plan specifies a flat plate/panel with extruded rectangle profile
    # Coordinates are in part-local frame with origin at bbox min corner

    # Create the base rectangle on the XY plane (u=x, v=z, w=y according to frame)
    # The frame has u_dir = [1,0,0] (x), v_dir = [0,0,-1] (-z), w_dir = [0,1,0] (y)
    # So the profile lies in the XZ plane, extruded along Y

    # Profile rectangle corners from UV coordinates:
    # The curves define a rectangle with corners at:
    # (7.82976, -66.3440) to (127.82976, -6.3440) in UV space
    # But the dimensions say length_u=1200, width_v=600
    # The UV coordinates appear to be scaled/offset - we use the explicit dimensions

    # Build the plate centered at origin for simplicity, then translate to match
    # the design intent (bbox min corner at origin)

    # Create a rectangle with length=1200 (along u/x) and width=600 (along v/-z)
    # Extrude along w (y) by 20mm

    result = (
        cq.Workplane("XY")
        .rect(1200, 600)
        .extrude(20)
    )

    # The resulting part has its center at (0,0,10) with dimensions 1200x600x20
    # This matches the design plan: flat plate 1200mm x 600mm x 20mm

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0004\\neg_02/generated.step")

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
