import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    # Dimensions from design plan (unit conversion cm_to_mm applied)
    length_u = 12.0  # span along u
    width_v = 60.0   # span along v
    extrude_w = 40.0 # span along w

    # Build the rectangular prism
    # The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means the rectangle is drawn on the XZ plane (u=X, v=-Z)
    # and extruded along the Y axis (w=Y) by 40mm.
    # Using centered=True ensures the extrusion spans from Y=0 to Y=40.
    result = (
        cq.Workplane("XZ")
        .rect(length_u, width_v)
        .extrude(extrude_w)
    )

    # Ensure output directory exists
    out_dir = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\105278_909f3813_0000\ex2"
    os.makedirs(out_dir, exist_ok=True)

    # Export to STEP
    out_step_path = os.path.join(out_dir, "generated.step")
    cq.exporters.export(result, out_step_path)

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
