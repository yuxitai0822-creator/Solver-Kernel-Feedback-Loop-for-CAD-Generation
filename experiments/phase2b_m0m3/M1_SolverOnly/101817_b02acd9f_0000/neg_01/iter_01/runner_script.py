import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: extruded rectangular frame
    # Outer rectangle: u from 6.0 to 10.0, v from -7.0 to -3.0 (in UV frame)
    # Inner rectangle: u from 6.12 to 9.88, v from -6.88 to -3.12
    # Extrude in +w direction by 780.0 mm (after unit conversion: original 78.0 cm -> 780.0 mm)
    # The perturbation description says perturbed=117.0 (cm) but the design plan says 780.0 mm.
    # We follow the design plan (780.0 mm) as the authoritative source.

    # Define the outer rectangle dimensions (in UV space)
    outer_u_min = 6.0
    outer_u_max = 10.0
    outer_v_min = -7.0
    outer_v_max = -3.0

    # Define the inner rectangle dimensions (in UV space)
    inner_u_min = 6.12
    inner_u_max = 9.88
    inner_v_min = -6.88
    inner_v_max = -3.12

    # Extrude distance (in mm)
    extrude_distance = 780.0

    # Build the profile on the XZ plane (since u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0])
    # The sketch plane is XZ (u=x, v=z), extrude along Y (w=y)

    # Create the outer rectangle
    result = (cq.Workplane("XZ")
              .moveTo(outer_u_min, outer_v_min)
              .lineTo(outer_u_max, outer_v_min)
              .lineTo(outer_u_max, outer_v_max)
              .lineTo(outer_u_min, outer_v_max)
              .close()
              .extrude(extrude_distance))

    # Create the inner rectangle as a cut
    inner_cut = (cq.Workplane("XZ")
                 .moveTo(inner_u_min, inner_v_min)
                 .lineTo(inner_u_max, inner_v_min)
                 .lineTo(inner_u_max, inner_v_max)
                 .lineTo(inner_u_min, inner_v_max)
                 .close()
                 .extrude(extrude_distance))

    # Subtract the inner cut from the outer body
    result = result.cut(inner_cut)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0000\neg_01\iter_01\generated.step"
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
