import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: SoapCutterLeg1 v1
    # Extruded rectangle: 209.55 x 57.912 mm, extrude 19.05 mm
    # Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
    # Origin at bbox_min_corner, so rectangle starts at (0,0) in UV plane

    # Build the rectangle profile on the XZ plane (since v_dir is (0,0,-1), w_dir is (0,1,0))
    # The profile is defined in UV coordinates where:
    #   U axis = (1,0,0) = X
    #   V axis = (0,0,-1) = -Z
    # So the sketch plane is XZ (with V inverted)

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Rectangle dimensions from design plan:
    # length_u = 209.55 mm (along X)
    # width_v = 57.912 mm (along -Z, but we'll use positive and handle orientation)
    # The profile curves show start_uv=(0, 5.7912) to (0,0) etc., so rectangle spans
    # u: 0 to 20.955 (note: 20.955 = 209.55/10? No, the values are in cm originally?)
    # Actually the design plan says unit_conversion_applied: cm_to_mm (x10)
    # So the profile values are in cm? Let's check: 20.955 cm = 209.55 mm, 5.7912 cm = 57.912 mm
    # The curves show start_uv=(0.0, 5.791200000000001) to (0.0, 0.0) etc.
    # So in UV space: u from 0 to 20.955, v from 0 to 5.7912
    # But these are in cm originally, so in mm: u from 0 to 209.55, v from 0 to 57.912

    # Since the profile is defined with v from 0 to 5.7912 (cm) = 57.912 mm,
    # and u from 0 to 20.955 (cm) = 209.55 mm, we use these dimensions directly.
    # The rectangle is centered at (209.55/2, 57.912/2) for convenience.

    rect = wp.center(209.55/2, 57.912/2).rect(209.55, 57.912, centered=True)

    # Extrude along w direction (0,1,0) = Y axis, distance = 19.05 mm
    result = rect.extrude(19.05)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0009\neg_01\iter_00\generated.step"
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
