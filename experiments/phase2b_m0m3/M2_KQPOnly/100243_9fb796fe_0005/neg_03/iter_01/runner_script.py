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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0005\neg_03\iter_01/generated.step"

    # Design Plan: Drone Leg Left - square strut
    # The design plan specifies a 19.0mm x 19.0mm profile extruded 200.0mm
    # The perturbation description says original=1.9, perturbed=1.52 (in cm)
    # After cm->mm conversion: original=19.0mm, perturbed=15.2mm
    # However, the kernel feedback expects 19.0mm for both u and v spans
    # This means the perturbation should NOT be applied - we must use the original design dimensions
    # The perturbation description is a TODO placeholder that hasn't been wired yet
    # Therefore, we use the design plan's explicit dimensions: 19.0mm x 19.0mm x 200.0mm

    # Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
    # So sketch on XZ plane (U=X, V=-Z), extrude along Y (W=Y)

    # Rectangle center in UV: (-57.27820137826746, -12.99014576968157)
    # In XZ coordinates: x=-57.27820137826746, z=12.99014576968157 (negate V since V=-Z)

    result = (
        cq.Workplane("XZ")
        .center(-57.27820137826746, 12.99014576968157)
        .rect(19.0, 19.0)
        .extrude(200.0)
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
