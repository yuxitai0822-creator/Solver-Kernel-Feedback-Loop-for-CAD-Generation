import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a cylinder (extruded circle) with radius 7.5 mm and height 20.0 mm
    # The design plan specifies a disk (cylinder) with radius 7.5 and extrude distance 20.0
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the circle is in the u-v plane (x-z plane) and extrudes along w (y-axis)
    # To match standard orientation, we create the circle on the XY plane and extrude along Z
    # Then rotate to match the specified frame orientation

    # Create the base cylinder: circle radius 7.5 on XY plane, extrude 20.0 along Z
    result = (
        cq.Workplane("XY")
        .circle(7.5)
        .extrude(20.0)
    )

    # The design plan frame has w_dir = (0,1,0) meaning the extrusion direction is along Y
    # Our current extrusion is along Z, so we need to rotate -90 degrees around X axis
    # This maps Z -> Y, matching the design plan
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Export the result
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104524_f829aab2_0001\\neg_01/generated.step")

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
