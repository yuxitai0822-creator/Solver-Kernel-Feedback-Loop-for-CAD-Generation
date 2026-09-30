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

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: 40x40 mm (in UV plane)
    # Inner rectangle: 37.6x37.6 mm (wall thickness 1.2 mm)
    # Extrude distance: 780 mm along W direction (Y axis)
    # Coordinate system: U=X, V=-Z, W=Y

    # Build the outer rectangle on XZ plane (since V=-Z, W=Y)
    # Outer rectangle corners in UV: (6, -7) to (10, -3) -> span 4 in U, 4 in V
    # But dimensions say outer_length_u=40, outer_width_v=40
    # The UV coordinates are scaled: 10-6=4 units = 40 mm => scale factor 10
    # So we work in mm directly: outer rect from (60, -70) to (100, -30)
    # Inner rect from (61.2, -68.8) to (98.8, -31.2)

    # Workplane: XZ (U=X, V=-Z means V axis is negative Z)
    # We'll build on XY plane then rotate, or build directly on XZ
    # Simpler: build on XY, then rotate to match frame axes

    # Build profile on XY plane (U=X, V=Y initially, then we'll transform)
    # Outer rectangle centered at origin, 40x40
    outer = cq.Workplane("XY").rect(40, 40).extrude(780)

    # Inner rectangle for the hole
    inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(780)

    # Subtract inner from outer to create hollow box
    result = outer.cut(inner)

    # Now rotate to match frame: U=X, V=-Z, W=Y
    # Current: U=X, V=Y, W=Z
    # Need: U=X, V=-Z, W=Y
    # Rotation: rotate 90 degrees around X axis to map Y->Z, Z->-Y
    # Actually: keep X as U, map Y to W, Z to -V
    # So rotate -90 around X: Y->-Z, Z->Y
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Now the box extends along Y (W direction) from 0 to 780
    # But we need to center it or position appropriately
    # The design plan doesn't specify absolute position, just shape

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0000\neg_03\iter_00\generated.step"
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
