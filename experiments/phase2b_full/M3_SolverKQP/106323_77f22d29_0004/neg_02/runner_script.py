import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: bearing 2 v1
    # Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm (symmetric about XY plane)

    # Create the outer circle (radius 17.5)
    outer_circle = cq.Workplane("XY").circle(17.5)

    # Create the inner circle (radius 12.5) as a hole
    inner_circle = cq.Workplane("XY").circle(12.5)

    # Build the annulus by extruding the outer circle and cutting the inner circle
    # Since the extrude is symmetric (both sides), we extrude half the total distance in each direction
    # Total distance = 10.0 mm, so extrude 5.0 mm both ways
    result = (
        cq.Workplane("XY")
        .circle(17.5)  # outer profile
        .extrude(5.0, both=True)  # symmetric extrusion: total height = 10.0 mm
        .faces(">Z")  # select top face to cut the hole
        .workplane()
        .circle(12.5)  # inner profile
        .cutThruAll()  # cut through the entire body
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106323_77f22d29_0004\\neg_02/generated.step")

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
