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

    # Design Plan: Drone Leg Left - square strut
    # Profile: rectangle 19.0mm x 19.0mm (in UV frame)
    # Extrude: 200.0mm along W direction
    # Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
    # Profile center in UV: (-57.27820137826746, -12.99014576968157)
    # Profile half-widths: 9.5mm in U, 9.5mm in V

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0005\neg_03\iter_00\generated.step"

    # Build the part using the frame axes from the design plan
    # Workplane on XZ (since V is [0,0,-1] and W is [0,1,0], the sketch plane is XZ)
    # The rectangle is defined in UV coordinates, where U=X, V=-Z
    # Center of rectangle in UV: (-57.27820137826746, -12.99014576968157)
    # Convert to XZ: x = u, z = -v
    cx = -57.27820137826746
    cz = 12.99014576968157  # -v since v = -z
    w = 19.0
    h = 19.0

    # Create workplane on XZ
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at (cx, cz) with dimensions w x h
    result = wp.moveTo(cx, cz).rect(w, h, centered=True).extrude(200.0)

    # Export
    cq.exporters.export(result, OUT_STEP_PATH)

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
