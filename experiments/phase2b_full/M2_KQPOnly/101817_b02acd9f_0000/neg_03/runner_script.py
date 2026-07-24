import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular frame (hollow box) based on the design plan
    # Outer dimensions: 40mm x 40mm, inner dimensions: 37.6mm x 37.6mm
    # Extrude distance: 780mm along the w-direction (which is +y in world coordinates)

    # Define the outer rectangle points (in UV plane, where U=x, V=-z, W=y)
    # Outer rectangle: from (6, -7) to (10, -3) in UV coordinates
    # But the dimensions indicate outer is 40x40, inner is 37.6x37.6
    # The UV coordinates given: outer corners at (6,-7), (10,-7), (10,-3), (6,-3)
    # This gives a 4x4 square in UV space, but actual dimensions are 40x40
    # So scaling factor is 10: UV units are in cm, converted to mm (x10)

    # Let's build the profile in the XY plane (U=X, V=Y) then extrude along Z
    # But the design says: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So U=X, V=-Z, W=Y. We'll work in XY plane and then rotate/extrude appropriately

    # Simpler approach: build the profile in XY plane, extrude along Y
    # Outer square: 40x40 centered at origin
    # Inner square: 37.6x37.6 centered at origin

    # Create the outer rectangle
    outer = cq.Workplane("XY").rect(40, 40)

    # Create the inner rectangle (hole)
    inner = cq.Workplane("XY").rect(37.6, 37.6)

    # Combine to create the frame profile
    # We need to subtract inner from outer
    frame_profile = outer.cut(inner)

    # Extrude along Y (positive Y direction) by 780mm
    result = frame_profile.extrude(780)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0000\\neg_03/generated.step")

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
