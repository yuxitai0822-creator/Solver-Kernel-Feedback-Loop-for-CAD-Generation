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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0002\neg_02\iter_01/generated.step"

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: corners at (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88) in UV plane
    # Inner rectangle: corners at (-6.0, 11.0), (-2.0, 11.0), (-6.0, 15.0), (-2.0, 15.0) in UV plane
    # Frame axes: u=[0,0,-1], v=[0,1,0], w=[1,0,0]
    # Extrude distance: 1120.0 mm along -w direction (i.e., negative x)
    # Outer dimensions: 42.4 x 42.4 (span along u and v)
    # Inner dimensions: 40.0 x 40.0
    # The perturbation is E4_void_remove: original had 1 void (inner hole), perturbed has 0 voids
    # So we must produce a solid rectangular prism WITHOUT the inner hole

    # Build the outer rectangle on the YZ plane (since w=[1,0,0], the profile is in YZ)
    # The UV coordinates map to YZ: u -> -z, v -> y
    # Convert UV points to YZ:
    # Outer: u=-1.88 -> z=1.88, u=-6.12 -> z=6.12; v=10.88 -> y=10.88, v=15.12 -> y=15.12
    # So outer rectangle in YZ: y from 10.88 to 15.12, z from 1.88 to 6.12
    # Width in y = 15.12 - 10.88 = 4.24, height in z = 6.12 - 1.88 = 4.24
    # Center in y = (10.88 + 15.12)/2 = 13.0, center in z = (1.88 + 6.12)/2 = 4.0

    # Extrude along -w = -x direction, distance 1120.0 mm
    # So the solid extends from x=0 to x=-1120 (or we can center it)

    # Since the design plan says "one_side" extrusion in -w direction, we'll extrude from x=0 to x=-1120

    # NOTE: The design plan dimensions are in mm, but the UV coordinates are in cm (as noted in compiler_notes: unit_conversion_applied = cm_to_mm x10)
    # So the actual dimensions in mm are: outer rectangle 42.4 x 42.4 mm, inner rectangle 40.0 x 40.0 mm
    # The UV coordinates given are in cm, so we need to multiply by 10 to get mm
    # Outer: u=-1.88 -> -18.8 mm, u=-6.12 -> -61.2 mm; v=10.88 -> 108.8 mm, v=15.12 -> 151.2 mm
    # So outer rectangle in YZ: y from 108.8 to 151.2, z from 18.8 to 61.2
    # Width in y = 151.2 - 108.8 = 42.4, height in z = 61.2 - 18.8 = 42.4
    # Center in y = (108.8 + 151.2)/2 = 130.0, center in z = (18.8 + 61.2)/2 = 40.0

    result = (
        cq.Workplane("YZ")
        .center(130.0, 40.0)  # center of outer rectangle in YZ (in mm)
        .rect(42.4, 42.4)     # width=42.4 (y), height=42.4 (z) in mm
        .extrude(-1120.0)     # extrude along -x direction, 1120.0 mm
    )

    # No inner hole (perturbation: void removed)

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
