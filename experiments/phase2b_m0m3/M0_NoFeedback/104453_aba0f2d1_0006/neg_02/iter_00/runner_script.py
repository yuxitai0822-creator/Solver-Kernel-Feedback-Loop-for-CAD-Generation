import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0006\neg_02\iter_00\generated.step"

    # Build the rectangular frame: outer rectangle 500x300, inner rectangle 400x200 (5mm offset from edges)
    # Extrude 500mm in +Z direction

    # Create outer rectangle
    outer = cq.Workplane("XY").rect(500, 300).extrude(500)

    # Create inner rectangle (hole) and cut it out
    inner = cq.Workplane("XY").rect(400, 200).extrude(500)

    # Position inner rectangle centered (since outer is centered at origin, inner also centered)
    # Outer rect: centered at (0,0), width 500, height 300
    # Inner rect: centered at (0,0), width 400, height 200 -> offset from outer edges: (500-400)/2=50 on each side in X, (300-200)/2=50 in Y
    # But design plan shows inner offset 5mm from edges? Actually curves show inner starts at (5,5) to (45,25) in UV (0-50,0-30) scaled by 10? 
    # Let's re-evaluate: outer UV spans 0-50 in U and 0-30 in V, inner spans 5-45 in U and 5-25 in V. 
    # Scaled by 10 (since outer dimensions 500x300): inner offset = 50mm from each edge, so inner dimensions = 400x200.
    # So inner rectangle centered at (0,0) with width 400, height 200 is correct.

    result = outer.cut(inner)

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
