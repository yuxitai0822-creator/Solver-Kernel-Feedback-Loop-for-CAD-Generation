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
    #   extrude distance = 8.89 mm (from dimensions.extrude_distance.value)
    #   center_uv = [16.994661, 17.998557] (from dimensions.profiles[0].center_uv)
    #   profile circle center_uv = [1.6994660913961006, 1.7998556732836484] (from profiles[0].rings[0].curves[0].center_uv)
    #   profile circle radius = 2.54 (from profiles[0].rings[0].curves[0].radius)
    #
    # Note: The design plan shows two different center_uv values and two different radii.
    # The "dimensions" section gives radius=25.4 and center_uv=[16.994661, 17.998557].
    # The "profiles" section gives radius=2.54 and center_uv=[1.6994660913961006, 1.7998556732836484].
    # The validation intents expect span_u=50.8, span_v=50.8, span_w=8.89.
    # span_u=50.8 implies diameter=50.8, so radius=25.4. This matches the dimensions section.
    # The profile radius=2.54 seems to be a scaled version (maybe cm to mm conversion factor 10).
    # We use the dimensions section values: radius=25.4, extrude=8.89.
    # The center_uv is just the position in the sketch plane; we place the circle at origin for simplicity.

    result = (
        cq.Workplane("XY")
        .circle(25.4)
        .extrude(8.89)
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\103284_e25015aa_0003\neg_03/generated.step")

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
