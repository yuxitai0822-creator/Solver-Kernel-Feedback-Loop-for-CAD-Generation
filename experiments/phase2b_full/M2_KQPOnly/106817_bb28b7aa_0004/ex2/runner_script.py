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

    # Build the washer by creating a 2D annulus in the XY plane, then extruding in Z.
    # The frame indicates the profile lies in the (u,v) plane where u=x, v=-z, w=y.
    # To keep it simple and correct, we create the annulus centered at origin in XY,
    # then translate to the given center, and extrude along Y (world y = +w).

    # Create outer circle
    outer = cq.Workplane("XY").circle(5.5372)
    # Create inner circle (hole)
    inner = cq.Workplane("XY").circle(1.9812)

    # Build the annulus: start with outer circle, cut inner circle
    # We'll use a single Workplane and cut
    result = (
        cq.Workplane("XY")
        .circle(5.5372)  # outer
        .circle(1.9812)  # inner (will be subtracted)
        .extrude(1.3208)  # extrude along Z (positive)
    )

    # Now we need to rotate/translate to match the design frame:
    # The design says: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    # This means: u=x, v=-z, w=y.
    # The profile center in UV is (-25.400001, 12.7).
    # In world: x = u = -25.400001, z = -v = -12.7, y = 0 (since profile is at w=0 before extrude).
    # Extrude direction is +w = +y.
    # So we need to translate the annulus to (x=-25.400001, y=0, z=-12.7) and then extrude along y.
    # But we already extruded along Z. Let's redo properly.

    # Better approach: create the annulus in the correct orientation from the start.
    # The profile plane is (u,v) = (x, -z). So we can work in the XZ plane, then extrude along Y.
    # But cadquery's Workplane("XZ") has normal along Y, which is what we want.
    # However, the v_dir is (0,0,-1), meaning v axis is -z. In XZ plane, the axes are x and z.
    # To match v = -z, we can just use the XZ plane and treat z as negative v.
    # The center in (u,v) is (-25.400001, 12.7). In (x,z) that is (-25.400001, -12.7).

    result = (
        cq.Workplane("XZ")
        .center(-25.400001, -12.7)
        .circle(5.5372)
        .circle(1.9812)
        .extrude(1.3208)  # extrude along Y (positive)
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\106817_bb28b7aa_0004\ex2/generated.step")

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
