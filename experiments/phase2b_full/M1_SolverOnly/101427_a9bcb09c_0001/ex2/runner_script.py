import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create the outer rectangle profile
    outer = cq.Workplane("XY").rect(1980.0, 600.0).extrude(25.0)

    # Create the inner rectangle profile (the hole)
    inner = cq.Workplane("XY").rect(1930.0, 550.0).extrude(25.0)

    # Position the inner rectangle relative to the outer
    # Outer: centered at origin, spans -990 to 990 in X, -300 to 300 in Y
    # Inner: should be offset so that its bottom-left corner is at (0,0) in UV space
    # From the design plan: inner starts at (0,0) and goes to (1930, 550) in UV
    # Outer starts at (-2.5, -2.5) and goes to (195.5, 57.5) in UV
    # But the dimensions say outer is 1980x600 and inner is 1930x550
    # The UV coordinates seem scaled differently (divided by 10?)
    # Let's interpret: outer spans from (-2.5, -2.5) to (195.5, 57.5) in UV
    # That's 198.0 in U and 60.0 in V, but dimensions say 1980 and 600
    # So UV is in cm? The compiler notes say cm_to_mm (x10)
    # So UV coordinates are in cm, multiply by 10 to get mm
    # Outer: (-25, -25) to (1955, 575) in mm -> width 1980, height 600
    # Inner: (0, 0) to (1930, 550) in mm -> width 1930, height 550
    # So inner is offset by (25, 25) from outer's bottom-left
    # Outer center is at (965, 275) in mm
    # Inner center is at (965, 275) in mm
    # They share the same center!

    # Let's verify: outer bottom-left at (-25, -25), top-right at (1955, 575)
    # Center: ((1955-25)/2, (575-25)/2) = (965, 275)
    # Inner bottom-left at (0, 0), top-right at (1930, 550)
    # Center: ((1930-0)/2, (550-0)/2) = (965, 275)
    # Yes, same center!

    # So we can create the frame by cutting the inner from the outer
    result = cq.Workplane("XY").rect(1980.0, 600.0).extrude(25.0)

    # Cut the inner rectangle
    result = result.faces(">Z").workplane().rect(1930.0, 550.0).cutThruAll()

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101427_a9bcb09c_0001\\ex2/generated.step")

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
