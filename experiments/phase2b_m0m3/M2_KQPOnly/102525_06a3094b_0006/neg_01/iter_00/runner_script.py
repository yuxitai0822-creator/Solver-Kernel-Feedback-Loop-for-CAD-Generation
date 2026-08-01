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

    # Design Plan: rectangular prism (SOP-28 body)
    # Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle centered at origin in UV plane
    # Extrude along +w (Y axis) by 3.0 mm

    # Build the rectangle profile on the XZ plane (since v_dir is -Z, u_dir is X, w_dir is Y)
    # The rectangle spans u: [-5.65, 5.65] and v: [-10.5, 10.5] (since v_dir is -Z, v coordinate maps to -Z)
    # We'll work on XY plane and then rotate, or directly on XZ plane

    # Using XZ workplane: u -> X, v -> Z (but v_dir is -Z, so we negate Z coordinates)
    # Actually simpler: create on XY plane with correct dimensions, then rotate to align with frame

    # Create the base rectangle on XY plane (centered)
    result = (cq.Workplane("XY")
              .center(0, 0)
              .rect(11.3, 21.0)  # length_u=11.3 along X, width_v=21.0 along Y
              .extrude(3.0))      # extrude along Z (w_dir should be Y, but we'll rotate)

    # Rotate to match frame: w_dir=[0,1,0] means extrusion should be along Y
    # Current extrusion is along Z, so rotate -90 deg around X axis
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Now the part is oriented correctly:
    # - X axis corresponds to u_dir (length 11.3)
    # - Z axis corresponds to v_dir (width 21.0, but v_dir is -Z, so we need to check)
    # - Y axis corresponds to w_dir (extrude 3.0)

    # The v_dir is [0,0,-1], meaning the width direction is negative Z.
    # Our rectangle had width 21.0 along Y before rotation, after rotation it's along Z.
    # But we need to ensure the sign matches. The profile coordinates show v from -10.5 to 10.5,
    # which is symmetric, so sign doesn't matter for the shape.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0006\neg_01\iter_00/generated.step"
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
