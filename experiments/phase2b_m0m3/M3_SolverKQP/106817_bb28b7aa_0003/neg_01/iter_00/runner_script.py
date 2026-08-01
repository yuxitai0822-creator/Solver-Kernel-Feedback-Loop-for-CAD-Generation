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

    # Design Plan: extruded circle (disk)
    # - Circle center in UV: (5.080000162124634, 6.350000202655792) but note the profile center_uv is (50.800002, 63.500002) after cm->mm conversion
    # - Radius: 4.7117 mm (from profile radius value)
    # - Extrude distance: 12.192 mm (from explicit dimension, not the perturbed 18.288)
    # - Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0) -> sketch on XZ plane, extrude along Y
    # - The circle center in the sketch plane (XZ) should be (5.080000162124634, 6.350000202655792) in original units,
    #   but after cm->mm conversion the profile center_uv is (50.800002, 63.500002). We use the profile center_uv directly.

    # Build the disk
    result = (
        cq.Workplane("XZ")  # v_dir = (0,0,-1) means v is -Z, u is X, so sketch plane is XZ
        .moveTo(50.800002, 63.500002)  # center in sketch coordinates (u, v) = (X, Z)
        .circle(4.7117)  # radius in mm
        .extrude(12.192)  # extrude along w_dir = (0,1,0) = Y axis
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0003\neg_01\iter_00\generated.step"
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
