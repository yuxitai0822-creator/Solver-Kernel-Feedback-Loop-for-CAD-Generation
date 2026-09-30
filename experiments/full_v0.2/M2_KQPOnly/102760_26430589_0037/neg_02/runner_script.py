import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
    # The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the extrusion direction is -w = (0,-1,0) in world coordinates.
    # However, for simplicity we create the disk in the XY plane and then rotate/translate
    # to match the frame. The frame origin is at bbox_min_corner, so we place the disk
    # such that its bottom face is at z=0 and it extends along the w axis (world y negative).

    # Create a circle with radius 0.8 mm
    result = (
        cq.Workplane("XY")
        .circle(0.8)
        .extrude(4.0)  # extrude along Z (positive)
    )

    # Now we need to transform to match the design plan frame:
    # The design plan frame has:
    #   u_dir = (1,0,0)  -> world X
    #   v_dir = (0,0,-1) -> world -Z
    #   w_dir = (0,1,0)  -> world Y
    # Extrusion direction is -w = (0,-1,0) -> world -Y
    # Our current disk is centered at origin, extruded along +Z.
    # We need to rotate so that the extrusion axis aligns with -Y.
    # Also the profile plane (XY) should map to the plane spanned by u and v.
    # u = X, v = -Z, so the profile plane is X-Z (with v reversed).
    # Our current profile is in XY, so we need to rotate: 
    #   X stays X, Y maps to -Z, Z maps to Y.
    # This is a rotation: (x,y,z) -> (x, z, -y)  (since new Y = old Z, new Z = -old Y)
    # But we also need to ensure the extrusion direction is -w = -Y.
    # After rotation, old Z (extrusion axis) becomes new Y, so we need to extrude along -Y.
    # Let's do it step by step:

    # Rotate 90 degrees about X axis: (x,y,z) -> (x, -z, y)
    # This makes old Z become new Y, old Y become new -Z.
    # Then we need to flip sign of Z to match v_dir = (0,0,-1)? Actually v_dir is (0,0,-1) which is -Z.
    # After rotation, old Y becomes -Z, so that matches v_dir = -Z.
    # And w_dir = (0,1,0) = Y, which after rotation old Z becomes Y, so extrusion along old Z becomes along Y.
    # But we need extrusion along -w = -Y. So we need to extrude in negative direction.

    # Alternative: just create the disk directly in the correct orientation.
    # The profile is a circle in the uv-plane (u=X, v=-Z). So the profile plane is X-Z.
    # Extrude along -w = -Y.

    result = (
        cq.Workplane("XZ")  # workplane is X-Z plane (normal is Y)
        .circle(0.8)
        .extrude(-4.0)  # extrude along -Y (which is -w direction)
    )

    # Now the disk is centered at origin. The design plan uses bbox_min_corner origin convention.
    # Since the disk is symmetric about origin in X and Z, and extends from -4 to 0 in Y,
    # the min corner is at (-0.8, -4.0, -0.8). We need to translate so that min corner is at (0,0,0).
    result = result.translate((0.8, 4.0, 0.8))

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102760_26430589_0037\\neg_02/generated.step")

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
