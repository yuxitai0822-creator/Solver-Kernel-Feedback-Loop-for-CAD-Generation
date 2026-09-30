import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import math

    # Design Plan: Drone Leg - square strut
    # Extruded rectangle: 19.0 x 19.0 mm profile, extruded 130.0 mm
    # The profile is defined in UV space with frame:
    #   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # The rectangle corners in UV are:
    #   (-58.2782, -12.0401) to (-56.3782, -13.9401)
    # This gives width_u = 1.9, width_v = 1.9 (in cm -> 19 mm after conversion)
    # Extrude distance = 130.0 mm

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
    # The UV coordinates are in cm, convert to mm by multiplying by 10
    # But the design plan says unit is mm, and the coordinates are already in mm
    # Let's verify: width_u = 19.0 mm, width_v = 19.0 mm
    # The UV coordinates span: u from -58.2782 to -56.3782 = 1.9 (in original units)
    # v from -13.9401 to -12.0401 = 1.9 (in original units)
    # These are in cm originally, converted to mm by multiplying by 10 -> 19 mm
    # So the coordinates in the plan are already in mm (after conversion)

    # Create workplane on XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # Actually, with u_dir=[1,0,0], v_dir=[0,0,-1], the sketch plane normal is u x v = [0,1,0] = w_dir
    # So the sketch is on the XZ plane

    result = (
        cq.Workplane("XZ")
        .center(-57.32820137826746, -12.99014576968157)  # center of rectangle
        .rect(19.0, 19.0)  # width=19mm, height=19mm
        .extrude(130.0)  # extrude along Y (w_dir = [0,1,0])
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0006\neg_01\iter_00\generated.step"
    exporters.export(result, OUT_STEP_PATH)

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
