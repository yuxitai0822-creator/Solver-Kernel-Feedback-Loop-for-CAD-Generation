import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk) with radius 25.4 mm and height 8.89 mm
    # The profile circle center is at (16.994661, 17.998557) in UV plane, but since we work in
    # part-local coordinates, we can place the circle at the origin and then translate if needed.
    # However, the design plan indicates the circle center in UV coordinates, which correspond to
    # the local frame's u and v axes. We'll create the circle centered at (0,0) and then translate
    # to match the specified center. But the validation intents only check spans (50.8 x 50.8 x 8.89),
    # so the absolute position doesn't matter for those checks. We'll place it at the specified center.

    # Create a workplane on the XY plane (which corresponds to the UV plane in the design plan)
    result = (cq.Workplane("XY")
              .circle(25.4)  # radius from design plan (value 25.4, note the profile radius is 25.4, not 2.54)
              .extrude(8.89)  # extrude distance from design plan
             )

    # The design plan shows center_uv = [16.994661, 17.998557], but since we are creating the
    # circle at the origin, we need to translate the result to match the specified center.
    # However, the validation intents only check spans, so translation doesn't affect them.
    # We'll translate to match the design plan center.
    result = result.translate((16.994661, 17.998557, 0))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103284_e25015aa_0003\\ex2/generated.step")

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
