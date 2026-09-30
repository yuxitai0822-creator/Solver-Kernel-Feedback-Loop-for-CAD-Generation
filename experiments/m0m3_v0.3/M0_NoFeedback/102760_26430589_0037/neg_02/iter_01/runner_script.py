import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_02\iter_01\generated.step"

    # Design Plan parameters:
    # - Disk with radius 0.8 mm (from dimensions.profiles[0].radius.value)
    # - Extrude distance 4.0 mm (from dimensions.extrude_distance.value)
    # - Circle profile radius 0.08 mm (from profiles[0].rings[0].curves[0].radius) - this is the sketch radius
    # - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # - Extrude direction: -w (i.e., along negative Y axis)
    # - Perturbation: sketch radius changed from 0.08 to 0.1

    # The design plan has two radius values:
    # 1. profiles[0].rings[0].curves[0].radius = 0.08 (perturbed to 0.1) - this is the sketch circle radius
    # 2. dimensions.profiles[0].radius.value = 0.8 - this is the actual part radius
    #
    # The validation intents expect span_u=1.6 and span_v=1.6, which corresponds to diameter 1.6mm, radius 0.8mm.
    # The sketch radius of 0.08 (or 0.1) would produce a disk with diameter 0.16 (or 0.2), which doesn't match.
    #
    # The correct interpretation: the sketch circle radius is 0.8mm (from dimensions), and the curves section
    # radius of 0.08 is a unit conversion artifact (cm to mm: 0.08 cm = 0.8 mm). The perturbation changed
    # the cm value from 0.08 to 0.1, which corresponds to 1.0 mm in mm units.
    #
    # So we use radius = 0.8 mm (original) or 1.0 mm (perturbed). The perturbation description says
    # original=0.08, perturbed=0.1 (in cm), so in mm: original=0.8, perturbed=1.0.
    # We use the perturbed value: 1.0 mm.

    # Build the part:
    # 1. Create a circle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # 2. Extrude along Y direction (w_dir is [0,1,0], extrude in -w = negative Y)

    result = (
        cq.Workplane("XZ")
        .circle(1.0)  # perturbed radius: 0.1 cm = 1.0 mm
        .extrude(-4.0)  # extrude in negative Y direction (distance 4.0 mm)
    )

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
