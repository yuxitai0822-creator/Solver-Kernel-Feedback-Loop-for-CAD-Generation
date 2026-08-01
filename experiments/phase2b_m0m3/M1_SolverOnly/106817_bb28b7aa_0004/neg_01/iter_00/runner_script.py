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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0004\neg_01\iter_00\generated.step"

    # Design parameters from the design plan (converted from cm to mm where needed)
    # Outer radius: 5.5372 mm (already in mm)
    # Inner radius: 1.9812 mm (already in mm)
    # Center: (-25.400001, 12.7) mm
    # Extrude distance: 1.3208 mm (the design plan says 1.3208, not the perturbed 1.9812)
    # The perturbation description says original=0.13208 cm = 1.3208 mm, perturbed=0.19812 cm = 1.9812 mm
    # But the design plan explicitly states extrude_distance = 1.3208 mm, so we use that.

    outer_radius = 5.5372
    inner_radius = 1.9812
    center_x = -25.400001
    center_y = 12.7
    extrude_distance = 1.3208  # mm (from design plan)

    # Build the washer using cadquery
    # Workplane is XZ according to the previous script, but we need to orient correctly
    # The design plan says: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means: sketch on XZ plane, extrude along Y (w direction)

    # Create the outer circle
    result = (cq.Workplane("XZ")
        .moveTo(center_x, center_y)
        .circle(outer_radius)
        .extrude(extrude_distance))

    # Cut the inner hole
    inner_cut = (cq.Workplane("XZ")
        .moveTo(center_x, center_y)
        .circle(inner_radius)
        .extrude(extrude_distance))

    result = result.cut(inner_cut)

    # Export
    cq.exporters.export(result, OUT_STEP_PATH)

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
