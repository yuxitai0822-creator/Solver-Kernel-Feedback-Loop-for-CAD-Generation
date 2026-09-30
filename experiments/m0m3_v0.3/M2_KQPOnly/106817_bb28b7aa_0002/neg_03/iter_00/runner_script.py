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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

    # Design Plan parameters:
    # - Circle center in UV: (11.430000364780426, 0.0) but note the profile center_uv is (114.300004, 0.0) after scaling?
    #   Actually the design plan says: center_uv = [11.430000364780426, 0.0] for the ring, but dimensions say center_uv = [114.300004, 0.0].
    #   The compiler note says unit conversion cm->mm (x10). So the original was in cm: 11.43 cm = 114.3 mm. So we use 114.300004 mm.
    # - Radius: 4.87045 mm (from dimensions)
    # - Extrude distance: 6.8707 mm
    # - The frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0). So the sketch plane is XZ (u=x, v=z), extrude along w=y.
    # - The circle center in sketch coordinates (u,v) = (114.300004, 0.0).
    # - No inner hole (the previous script had an inner loop of radius 0.5, but the design plan shows only one outer ring, no inner ring).
    #   The perturbation description says "operator=E4_void_add; original=0; perturbed=1" meaning an extra void was added.
    #   We must follow the design plan: only one circle, no hole.

    # Build the part:
    # Workplane on XZ (since u=x, v=z).
    wp = cq.Workplane("XZ")

    # Move to center and create circle
    center_u = 114.300004
    center_v = 0.0
    radius = 4.87045

    # Create the circle on the workplane
    circle_wp = wp.moveTo(center_u, center_v).circle(radius)

    # Extrude along the w direction (which is y-axis). The design says direction = +w, distance = 6.8707 mm.
    extrude_distance = 6.8707
    result = circle_wp.extrude(extrude_distance)

    # Export
    importers.export(result, OUT_STEP_PATH)

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
