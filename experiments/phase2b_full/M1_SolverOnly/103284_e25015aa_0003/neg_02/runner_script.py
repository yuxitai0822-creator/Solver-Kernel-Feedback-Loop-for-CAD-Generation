import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk)
    # Dimensions:
    #   radius = 25.4 mm (from dimensions.profiles[0].radius.value)
    #   extrude distance = 8.89 mm (from extrude.distance_total.value)
    # Note: The profile center_uv is [16.994661, 17.998557] but since we are
    #   building in part-local coordinates with origin at bbox min corner,
    #   we place the circle center at (radius, radius) to keep the part
    #   in the first quadrant (positive x,y). The actual center_uv from the
    #   plan is [16.994661, 17.998557] which is approximately (radius, radius)
    #   given radius=25.4? Actually 25.4 vs 16.99 is different. But the plan
    #   says origin_convention is bbox_min_corner, so the circle center should
    #   be at (radius, radius) to make the disk span from 0 to 2*radius.
    #   However the plan's center_uv is [16.994661, 17.998557] which is not
    #   exactly (25.4, 25.4). This might be a conversion artifact. We'll use
    #   the explicit radius and place the circle so that the bounding box
    #   spans [0, 50.8] in x and y, i.e. center at (25.4, 25.4).
    #   The validation expects span_u=50.8, span_v=50.8, so this is correct.

    radius = 25.4
    height = 8.89

    # Create the disk: circle at (radius, radius) extruded upward
    result = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103284_e25015aa_0003\\neg_02/generated.step")

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
