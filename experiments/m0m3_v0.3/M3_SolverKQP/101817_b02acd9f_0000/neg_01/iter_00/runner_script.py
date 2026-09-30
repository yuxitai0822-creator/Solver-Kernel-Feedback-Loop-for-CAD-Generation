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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0000\neg_01\iter_00\generated.step"

    # Design parameters from the design plan (all in mm)
    # Outer rectangle: from curves, span in u (x) direction: 10.0 - 6.0 = 4.0? Wait, let's recalc.
    # The design plan gives outer_length_u = 40.0, outer_width_v = 40.0.
    # The curves in uv space: start_uv (10.0, -7.0) to (6.0, -7.0) etc.
    # But the design plan says outer dimensions are 40x40, inner 37.6x37.6.
    # The uv coordinates seem scaled by 10? Actually the compiler notes say cm_to_mm (x10).
    # So the original cm values: outer 4cm x 4cm = 40mm x 40mm, inner 3.76cm x 3.76cm = 37.6mm x 37.6mm.
    # The uv coordinates in the design plan are in mm already (since unit=mm).
    # Let's use the explicit dimensions from the design plan.

    outer_u = 40.0  # mm
    outer_v = 40.0  # mm
    inner_u = 37.6  # mm
    inner_v = 37.6  # mm

    # Extrude distance: from design plan, distance_total = 780.0 mm (not 1170!)
    # The perturbation description says original=78.0, perturbed=117.0 (in cm?)
    # But the design plan says 780.0 mm (which is 78 cm). The previous script used 1170 mm (117 cm).
    # We must follow the design plan: 780.0 mm.
    extrude_distance = 780.0  # mm

    # Build the frame on the XZ plane (as per previous script's WORKPLANE = 'XZ')
    # The frame's u_dir = [1,0,0] (X), v_dir = [0,0,-1] (negative Z), w_dir = [0,1,0] (Y)
    # So the profile lies in the XZ plane, extrude along Y.

    # Create the outer rectangle centered at origin
    wp = cq.Workplane("XZ").center(0, 0).rect(outer_u, outer_v, centered=True)

    # Create the inner rectangle (hole) centered at origin
    wp_inner = cq.Workplane("XZ").center(0, 0).rect(inner_u, inner_v, centered=True)

    # Extrude the outer rectangle along Y (positive direction) by extrude_distance
    result = wp.extrude(extrude_distance)

    # Cut out the inner hole: extrude the inner rectangle by the same distance and subtract
    cut_prism = wp_inner.extrude(extrude_distance)
    result = result.cut(cut_prism)

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
