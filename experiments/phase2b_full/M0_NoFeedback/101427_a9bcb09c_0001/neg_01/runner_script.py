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

    # Position the inner rectangle relative to outer: 
    # Outer spans from x=-990 to x=990, y=-300 to y=300 (centered at origin)
    # Inner should be offset so that its bottom-left corner is at (0,0) in UV space
    # UV space: u from -2.5 to 195.5, v from -2.5 to 57.5
    # Outer rect in UV: u from -2.5 to 195.5, v from -2.5 to 57.5
    # Inner rect in UV: u from 0 to 193, v from 0 to 55
    # Convert to XY: center at (0,0) with width 1980, height 600
    # So UV (u,v) maps to XY (u - 96.5, v - 27.5) approximately
    # Actually: outer rect width=1980, height=600, centered at origin
    # So u_min=-2.5 maps to x=-990, u_max=195.5 maps to x=990 => scale factor = 1980/198 = 10
    # v_min=-2.5 maps to y=-300, v_max=57.5 maps to y=300 => scale factor = 600/60 = 10
    # So inner rect: u from 0 to 193, v from 0 to 55
    # x = (u - 96.5) * 10 = (0 - 96.5)*10 = -965 to (193 - 96.5)*10 = 965
    # y = (v - 27.5) * 10 = (0 - 27.5)*10 = -275 to (55 - 27.5)*10 = 275
    # So inner rect width = 1930, height = 550, centered at origin

    # Subtract inner from outer to create the frame
    result = outer.cut(inner)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101427_a9bcb09c_0001\\neg_01/generated.step")

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
