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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0002\neg_03\iter_01/generated.step"

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: corners at (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: corners at (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude along W direction (X axis) by 1120.0 mm
    # The frame axes: U = -Z, V = +Y, W = +X
    # So the profile is in the YZ plane (U=-Z, V=+Y)

    # Build the outer rectangle using exact corner coordinates
    # Outer rectangle: center at ((-6.12 + -1.88)/2, (10.88 + 15.12)/2) = (-4.0, 13.0)
    # Width = 4.24, Height = 4.24
    outer = cq.Workplane("YZ").center(-4.0, 13.0).rect(4.24, 4.24, centered=True)

    # Build the inner rectangle (hole)
    # Inner rectangle: center at ((-6.0 + -2.0)/2, (11.0 + 15.0)/2) = (-4.0, 13.0)
    # Width = 4.0, Height = 4.0
    inner = cq.Workplane("YZ").center(-4.0, 13.0).rect(4.0, 4.0, centered=True)

    # Create the profile by subtracting inner from outer
    profile = outer.cut(inner)

    # Extrude along X (W direction) by 1120.0 mm
    result = profile.extrude(1120.0)

    # Export
    importers = cq.exporters
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
