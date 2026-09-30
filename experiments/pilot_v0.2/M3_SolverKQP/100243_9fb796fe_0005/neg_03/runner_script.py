import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    # Ensure output directory exists
    OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\100243_9fb796fe_0005\neg_03"
    OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
    os.makedirs(OUT_DIR, exist_ok=True)

    # Design Plan: extruded_rectangle (square_strut)
    # Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
    # Profile rectangle in uv-plane: u_span=19.0, v_span=19.0
    # Extrude along +w direction (Y axis) by 200.0 mm

    # Rectangle corners in uv-plane:
    # (-58.2782, -12.0401) to (-56.3782, -13.9401)
    # u_span = 1.9, v_span = 1.9 (in cm, converted to mm -> 19.0, 19.0)

    # Map uv to XYZ: X=u, Z=-v, Y=0 (sketch plane)
    # Corner mapping:
    # (-58.2782, -12.0401) -> X=-58.2782, Z=12.0401
    # (-58.2782, -13.9401) -> X=-58.2782, Z=13.9401
    # (-56.3782, -13.9401) -> X=-56.3782, Z=13.9401
    # (-56.3782, -12.0401) -> X=-56.3782, Z=12.0401

    # Build the rectangle on the XZ plane (Y=0) and extrude along +Y
    result = (
        cq.Workplane("XZ")
        .rect(19.0, 19.0)
        .center(-57.3282, 12.9901)  # center of rectangle in XZ
        .rect(19.0, 19.0)
        .extrude(200.0)
    )

    # Export to STEP
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
