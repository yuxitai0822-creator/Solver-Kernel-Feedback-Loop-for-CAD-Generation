import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame
    # Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude along -w direction (which is x-axis in world) by 1120.0 mm

    # Create the outer rectangle
    outer = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()

    # Create the inner rectangle (as a separate wire for subtraction)
    inner = cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close()

    # Combine: outer face with inner hole
    # We'll build the outer face, then cut the inner face
    result = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()

    # Now cut the inner rectangle
    result = result.cut(cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close())

    # Extrude along the w direction (which is x-axis in world, but we use the frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0])
    # The extrude direction is -w, so along negative x-axis
    # But since we are working in XY plane, we need to orient correctly.
    # The frame says: u_dir = [0,0,-1] (z negative), v_dir = [0,1,0] (y), w_dir = [1,0,0] (x)
    # So the profile is in the UV plane, which corresponds to ZY plane in world.
    # To get the correct orientation, we should create the profile in the YZ plane and extrude along X.

    # Let's redo properly: create profile in YZ plane (since u=z, v=y)
    # Outer rectangle in UV: u from -6.12 to -1.88, v from 10.88 to 15.12
    # So in YZ: z from -6.12 to -1.88, y from 10.88 to 15.12
    # Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0
    # So in YZ: z from -6.0 to -2.0, y from 11.0 to 15.0

    # Build outer profile in YZ plane
    outer_face = cq.Workplane("YZ").moveTo(10.88, -6.12).lineTo(15.12, -6.12).lineTo(15.12, -1.88).lineTo(10.88, -1.88).close()

    # Build inner profile in YZ plane
    inner_face = cq.Workplane("YZ").moveTo(11.0, -6.0).lineTo(15.0, -6.0).lineTo(15.0, -2.0).lineTo(11.0, -2.0).close()

    # Cut inner from outer
    frame_profile = outer_face.cut(inner_face)

    # Extrude along -w direction = negative x-axis, distance 1120.0 mm
    result = frame_profile.extrude(-1120.0)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0002\\neg_03/generated.step")

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
