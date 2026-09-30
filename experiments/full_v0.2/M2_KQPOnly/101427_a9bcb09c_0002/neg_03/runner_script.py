import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
    # Note: The design plan dimensions are given in mm (converted from cm by factor 10).
    # The profile rectangle is defined in UV space with u along x, v along z (negative direction).
    # The extrude direction is +w which corresponds to +y.

    # Create the rectangle profile on the XY plane (since w_dir = (0,1,0) is the extrude direction)
    # The profile lies in the plane where w=0, i.e., the XY plane.
    # The rectangle corners in UV: (0,55), (0,0), (193,0), (193,55)
    # Map: u -> x, v -> -z (because v_dir = (0,0,-1))
    # So points: (0, 0, -55), (0, 0, 0), (193, 0, 0), (193, 0, -55)

    result = (
        cq.Workplane("XY")
        .moveTo(0, -55)  # start at (0, -55) in XY plane (z=0)
        .lineTo(0, 0)    # to (0, 0)
        .lineTo(193, 0)  # to (193, 0)
        .lineTo(193, -55) # to (193, -55)
        .close()
        .extrude(50.0)   # extrude along +Z (which is +w direction)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0002\\neg_03/generated.step")

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
