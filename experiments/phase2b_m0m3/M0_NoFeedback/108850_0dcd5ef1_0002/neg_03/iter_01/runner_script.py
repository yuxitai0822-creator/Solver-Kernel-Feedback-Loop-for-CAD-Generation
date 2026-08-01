import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import os

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108850_0dcd5ef1_0002\neg_03\iter_01/generated.step"

    # Design plan: extruded rectangle, 171.45 x 38.1 mm, extrude 6.35 mm
    # Perturbation: original v-span 38.1 -> perturbed to 30.48 (3.81 -> 3.048 in uv)
    # The design plan's frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So u is X, v is -Z, w is Y. Profile lies in X-Z plane, extrude along Y.
    # The rectangle in uv: u from 0 to 17.145, v from 0 to 3.81 (cm).
    # After cm_to_mm scaling (x10): 171.45 x 38.1 mm.
    # Perturbation changes v-coordinate from 3.81 to 3.048 cm, giving width_v = 30.48 mm.

    length_u = 171.45  # mm
    width_v = 30.48    # mm (perturbed: 3.048 cm * 10 = 30.48 mm)
    extrude_dist = 6.35  # mm

    # Create workplane on XZ (u-v plane)
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at origin
    result = wp.rect(length_u, width_v).extrude(extrude_dist)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

    # Export to STEP
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
