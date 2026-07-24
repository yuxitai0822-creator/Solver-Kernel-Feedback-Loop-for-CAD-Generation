import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile in the UV plane
    # From the design plan:
    #   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    #   rectangle corners in UV: (-58.2782, -12.0401) to (-56.3782, -13.9401)
    #   This gives a 1.9 x 1.9 mm square (19 mm after cm->mm conversion? Actually values are in mm already)
    #   The extrude distance is 200.0 mm along +w (which is +Y)

    # Build the rectangle in the XY plane, then rotate to match the frame.
    # The frame has u=X, v=-Z, w=Y.
    # So we can create the rectangle in the XZ plane (u=X, v=-Z) and then extrude along Y.

    # Rectangle dimensions: width along u = 19.0 mm, height along v = 19.0 mm
    # The UV coordinates given: u from -58.2782 to -56.3782 (delta = 1.9) ??? Wait, that's 1.9 mm, but dimensions say 19.0 mm.
    # The design plan dimensions say length_u=19.0, width_v=19.0. The UV coordinates in the profile are in the local frame.
    # The compiler note says cm_to_mm (x10). So the UV values are in cm? Actually they are -58.2782 etc, which are large.
    # But the explicit dimensions say 19.0 mm. The profile coordinates might be in a different scale or offset.
    # Let's trust the explicit dimensions: 19.0 x 19.0 mm rectangle, extruded 200.0 mm.
    # The UV coordinates given are just for the shape; we can create a 19x19 rectangle centered at origin.

    # However, the design plan specifies the rectangle corners precisely. Let's use those UV values directly.
    # The UV values: (-58.2782, -12.0401) to (-56.3782, -13.9401). 
    # Delta u = 1.9, delta v = -1.9 (so 1.9 mm). But dimensions say 19.0 mm. 
    # This is a discrepancy. The compiler note says cm_to_mm (x10). So the UV values are in cm? 
    # -58.2782 cm = -582.782 mm, that's huge. But the dimensions say 19.0 mm.
    # I think the UV coordinates are in the original cm units before conversion.
    # The explicit dimensions are the correct ones: 19.0 mm x 19.0 mm.
    # So I'll create a 19.0 x 19.0 mm rectangle centered at the origin in the UV plane.

    # Let's use the frame: u=X, v=-Z, w=Y.
    # So the rectangle lies in the XZ plane (since u=X, v=-Z).
    # We'll create a rectangle centered at (0,0) in the XZ plane, then extrude along Y.

    # Create the rectangle in the XZ plane
    rect = cq.Workplane("XZ").rect(19.0, 19.0, centered=True)

    # Extrude along Y (positive Y = +w direction) by 200.0 mm
    result = rect.extrude(200.0)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100243_9fb796fe_0005\\neg_03/generated.step")

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
