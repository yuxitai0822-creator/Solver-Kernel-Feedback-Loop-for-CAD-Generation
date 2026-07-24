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
    #   outer radius = 5.5372
    #   inner radius = 1.9812
    #   thickness (extrude distance) = 1.3208
    # The profile center in UV is at (-25.400001, 12.7) but we place the sketch at origin for simplicity.
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # We'll create the annulus on the XY plane (normal = (0,0,1)) and extrude along Z.
    # To match the frame orientation, we can rotate the result.

    # Build the washer
    result = (
        cq.Workplane("XY")
        .circle(5.5372)
        .circle(1.9812)
        .extrude(1.3208)
    )

    # The frame in the design plan has v_dir = (0,0,-1) and w_dir = (0,1,0).
    # This means the extrusion direction (w) is Y, and the profile plane normal is -Z.
    # Our current result has extrusion along Z, profile on XY.
    # To match: rotate 90° around X axis so that Z becomes Y.
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0004\\neg_01/generated.step")

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
