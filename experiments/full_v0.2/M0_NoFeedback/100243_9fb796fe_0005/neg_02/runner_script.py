import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile in the UV plane
    # The profile is a 19mm x 19mm square centered at the origin
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The profile coordinates are given in UV space:
    #   u range: [-58.2782, -56.3782]  -> width = 1.9? Wait, let's check.
    #   v range: [-13.9401, -12.0401]  -> height = 1.9? Wait, let's check.
    # Actually the dimensions say length_u = 19.0, width_v = 19.0
    # The UV coordinates span: u from -58.2782 to -56.3782 = 1.9? That's 1.9, not 19.
    # But the design plan says explicit_dimension: 19.0 mm. 
    # The compiler note says cm_to_mm (x10). So the UV coordinates are in cm? 
    # The profile coordinates: u diff = 1.9, v diff = 1.9. After cm->mm conversion: 19 mm.
    # So we need to scale the profile by 10 to get mm.
    # Alternatively, we can just create a 19x19 rectangle centered appropriately.
    # The profile center in UV: u_center = (-58.2782 + -56.3782)/2 = -57.3282, v_center = (-13.9401 + -12.0401)/2 = -12.9901
    # After scaling by 10: u_center = -573.282, v_center = -129.901
    # But we can also just create the rectangle at the origin and translate.
    # Let's create the rectangle in the XY plane (which maps to UV plane via the frame)
    # The frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # So UV plane is the XZ plane (with v inverted).
    # We'll create a rectangle in the XZ plane, then extrude along Y (w direction).

    # Create the rectangle profile
    # Width along u (x) = 19.0, height along v (z) = 19.0
    # Center at (u_center_scaled, v_center_scaled) = (-573.282, -129.901) in UV space
    # But in world coordinates: x = u, z = -v (since v_dir = (0,0,-1))
    # So center in world: x = -573.282, z = 129.901

    # Actually, let's just use the explicit dimensions: 19x19 rectangle, extruded 200mm
    # The position in the design plan is given by the profile coordinates.
    # We'll create the rectangle at the correct position.

    # Create a workplane on the XZ plane (since u_dir = x, v_dir = -z)
    # We'll use the XY plane and rotate? No, let's use the XZ plane directly.

    # The profile center in UV: u=-57.3282, v=-12.9901 (in cm, before scaling)
    # After cm->mm: u=-573.282, v=-129.901
    # In world: x = u = -573.282, z = -v = 129.901 (because v_dir = (0,0,-1))

    # Let's create the rectangle centered at that point
    center_x = -573.282
    center_z = 129.901

    # Create the rectangle on the XZ plane
    result = (cq.Workplane("XZ")
              .center(center_x, center_z)
              .rect(19.0, 19.0)
              .extrude(200.0))  # extrude along Y (w direction = (0,1,0))

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\100243_9fb796fe_0005\neg_02/generated.step")

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
