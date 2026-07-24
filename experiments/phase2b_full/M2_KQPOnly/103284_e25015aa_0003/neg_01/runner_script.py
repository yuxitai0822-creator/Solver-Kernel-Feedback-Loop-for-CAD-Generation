import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Lever Switch - Disk
    # Dimensions:
    #   Radius: 25.4 mm (from dimensions.profiles[0].radius.value)
    #   Extrude distance: 8.89 mm (from extrude.distance_total.value)
    #   Center UV: (16.994661, 17.998557) - used for positioning
    # Note: The design plan indicates a unit conversion from cm to mm (x10).
    #       The radius in the plan is 25.4 mm, extrude is 8.89 mm.
    #       The center_uv is given as (16.994661, 17.998557) which seems to be
    #       in the local coordinate system. We'll place the circle at the origin
    #       and then translate to match the center_uv if needed, but since the
    #       part is a simple disk, we'll center it at (0,0) and extrude.
    #       The validation expects spans of 50.8 x 50.8 x 8.89, which matches
    #       a disk of radius 25.4 (diameter 50.8) extruded by 8.89.

    # Build the disk
    result = (
        cq.Workplane("XY")
        .circle(25.4)  # radius in mm
        .extrude(8.89)  # extrude distance in mm
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\103284_e25015aa_0003\\neg_01/generated.step")

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
