import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: thumb screw (disk)
    # Profile: circle with radius 4.87045 mm, center at (114.300004, 0.0) in UV
    # Extrude: distance 6.8707 mm along +w direction
    # Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    # The circle center in UV is (114.300004, 0.0). However, the radius given in the profile curves is 0.487045 (likely a typo in curves),
    # but the explicit dimension says radius = 4.87045 mm. We use the explicit dimension.
    # The center_uv in profiles is [114.300004, 0.0] but the radius dimension is 4.87045, so the circle is centered at (114.300004, 0.0) in the sketch plane.
    # The frame: u_dir = X, v_dir = -Z, w_dir = Y. So sketch plane is X-Z (since u=X, v=-Z), extrude along Y (w).
    # We'll create a workplane on the XZ plane, offset to center the circle appropriately.
    # Since the center_uv is (114.300004, 0.0) and the radius is 4.87045, the circle spans from 109.429554 to 119.170454 in u (X).
    # We'll just place the circle at that center.

    result = (
        cq.Workplane("XZ")
        .circle(4.87045)
        .extrude(6.8707)
    )

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0002\\ex2/generated.step")

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
