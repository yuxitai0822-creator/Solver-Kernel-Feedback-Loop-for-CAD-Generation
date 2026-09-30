import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: rectangular prism with dimensions 12mm x 60mm x 40mm
    # The profile is a rectangle in the UV plane, extruded along W direction.
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means: U -> X, V -> -Z, W -> Y
    # Profile rectangle: u from -0.6 to 0.6 (width 1.2? but dimensions say length_u=12.0)
    # Wait: The profile curves show start_uv and end_uv values like -0.6, 0.6, -3.0, 3.0
    # But dimensions say length_u=12.0, width_v=60.0
    # The UV coordinates in the profile are scaled: the rectangle spans u in [-0.6, 0.6] and v in [-3.0, 3.0]
    # So the actual size in mm is: u_range = 1.2 -> but length_u=12.0 means scaling factor 10?
    # Actually the compiler note says unit_conversion_applied: cm_to_mm (x10)
    # So the profile coordinates are in cm? The values -0.6 to 0.6 cm = -6 to 6 mm = 12 mm span. Yes.
    # Similarly v: -3.0 to 3.0 cm = -30 to 30 mm = 60 mm span.
    # So we can directly use the UV values multiplied by 10 to get mm.
    # But simpler: just create a rectangle centered at origin with dimensions 12mm x 60mm in the X-Z plane?
    # Actually frame: u_dir = X, v_dir = -Z, so the profile lies in the X-Z plane (with v reversed).
    # Extrude along w_dir = Y for 40mm.

    # Let's build using the explicit dimensions from the plan:
    length_u = 12.0  # mm
    width_v = 60.0   # mm
    extrude_distance = 40.0  # mm

    # Create the rectangle profile on the X-Z plane (since u=X, v=-Z, we can just use X and Z)
    # The rectangle is centered at origin in UV space: u in [-6, 6], v in [-30, 30] in mm
    # But v_dir = -Z, so v coordinate maps to -Z. So v=30 maps to Z=-30, v=-30 maps to Z=30.
    # So the rectangle in X-Z: X from -6 to 6, Z from -30 to 30.
    # We'll create a workplane on the XZ plane (Y=0) and draw the rectangle.

    result = (cq.Workplane("XZ")
              .center(0, 0)
              .rect(length_u, width_v)
              .extrude(extrude_distance))

    # The extrusion direction is along the workplane normal, which for "XZ" is Y (positive).
    # But the plan says extrude in +w direction, w_dir = (0,1,0) = Y. So this matches.

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\105278_909f3813_0000\\neg_03/generated.step")

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
