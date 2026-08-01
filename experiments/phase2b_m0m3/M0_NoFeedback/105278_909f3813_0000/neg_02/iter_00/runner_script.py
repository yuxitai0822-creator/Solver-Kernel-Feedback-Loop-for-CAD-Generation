import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: rectangular prism 12mm x 60mm x 40mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in uv-plane: u from -0.6 to 0.6, v from -3.0 to 3.0
    # Extrude 40mm in +w direction

    # Build on XY plane, then rotate to match frame orientation
    # Frame: u=x, v=-z, w=y
    # So sketch on XZ plane (u=x, v=z) but v_dir is [0,0,-1], so we need to flip
    # Actually: u=x, v=-z means v points opposite to z
    # w=y means extrude in y direction

    # Simpler: create box directly with correct dimensions
    # The rectangle in uv coordinates: u from -0.6 to 0.6 (width 1.2), v from -3.0 to 3.0 (height 6.0)
    # But dimensions say length_u=12.0, width_v=60.0 - these are the full spans
    # So u span = 12.0, v span = 60.0, w span = 40.0

    # Create the box centered at origin
    result = cq.Workplane("XY").box(12.0, 40.0, 60.0, centered=(True, True, True))

    # The box is oriented with: x=length_u=12, y=extrude=40, z=width_v=60
    # But we need: u=x, v=-z, w=y
    # So the box dimensions are correct: 12 (x=u), 40 (y=w), 60 (z=-v)
    # The v direction is [0,0,-1], so v span = 60 along -z, which is correct

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\105278_909f3813_0000\neg_02\iter_00/generated.step"
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
