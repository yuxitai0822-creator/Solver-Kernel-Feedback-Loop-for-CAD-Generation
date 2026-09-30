import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular prism with dimensions:
    # Length (u): 95.25 mm, Width (v): 19.05 mm, Height (extrude distance w): 12.7 mm
    # The profile is a rectangle in the uv-plane, extruded along the w-direction.
    # Based on the design plan, the frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # This means: u = X, v = -Z, w = Y.
    # So the rectangle lies in the XZ plane (with v along -Z), and extrudes along Y.

    # Build the rectangle profile on the XZ plane (workplane XY in CadQuery, but we need to orient correctly)
    # Using workplane with normal in Y direction (w_dir), then draw rectangle in u (X) and v (Z) directions.
    # Since v_dir = (0,0,-1), the width is along -Z, but we can just draw a rectangle with positive dimensions
    # and the orientation will be handled by the workplane.

    result = (
        cq.Workplane("XY")  # normal is +Z, but we need normal along Y; use workplane with normal (0,1,0)
        .workplane(offset=0, centerOption="CenterOfMass")
        .center(0, 0)
        .rect(95.25, 19.05)  # width along X, height along Z (since workplane XY)
        .extrude(12.7)  # extrude along normal (Z), but we need along Y; we'll rotate
    )

    # The above extrudes along Z, but we need the final part oriented with:
    # u (length 95.25) along X, v (width 19.05) along -Z, w (height 12.7) along Y.
    # So we need to rotate the result: from (X, Z, Y) to (X, -Z, Y).
    # Actually, the rect on XY plane gives width along X, height along Y (in workplane coordinates).
    # Let's redo properly:

    # Use workplane with normal (0,1,0) so that the plane is XZ.
    result = (
        cq.Workplane("XZ")  # normal is Y, so plane is XZ
        .rect(95.25, 19.05)  # width along X, height along Z
        .extrude(12.7)  # extrudes along Y (normal direction)
    )

    # Now the part has:
    # - length 95.25 along X (u_dir)
    # - width 19.05 along Z (but v_dir is (0,0,-1), so we need to flip Z)
    # - height 12.7 along Y (w_dir)
    # To match v_dir = (0,0,-1), we need to mirror or rotate about X axis by 180 degrees.
    # Rotating 180 degrees around X axis will map Z -> -Z, Y -> -Y. But we want Y unchanged.
    # Better: mirror across the XY plane (i.e., scale Z by -1).
    # Use mirror: mirror about plane YZ? No, we want to flip Z only.
    # We can rotate 180 degrees around X axis, then rotate back 180 around Y? That's messy.
    # Simpler: just use a transform to scale Z by -1.

    # Actually, the design plan's frame has v_dir = (0,0,-1). This means the width direction is negative Z.
    # Our current part has width along positive Z. So we need to flip the sign of Z.
    # We can do this by mirroring across the XY plane (which flips Z).
    result = result.mirror("XY")

    # Now the part has:
    # - length 95.25 along X
    # - width 19.05 along -Z (matches v_dir)
    # - height 12.7 along Y (matches w_dir)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0006\\ex2/generated.step")

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
