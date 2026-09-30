import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk/shaft)
    # Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
    # Extrude: 75.0 mm along +w direction (which maps to world X axis)
    # Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
    # So in CadQuery: sketch on YZ plane (normal = X), then extrude along +X

    # Create workplane on YZ plane (normal = (1,0,0))
    result = cq.Workplane("YZ").circle(12.5).extrude(75.0)

    # The design specifies center at (-15.0, 10.0) in UV coordinates.
    # In our workplane YZ, U maps to -Z, V maps to Y.
    # So center_uv = (-1.5, 1.0) in design plan (scaled by 10 from cm to mm?)
    # Actually dimensions: radius=12.5, center_uv=[-15.0, 10.0] in mm.
    # In YZ plane: Y = V = 10.0, Z = -U = 15.0 (since u_dir = (0,0,-1))
    # So we need to position the circle at (Y=10, Z=15)

    result = cq.Workplane("YZ").center(10.0, 15.0).circle(12.5).extrude(75.0)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0000\\neg_02/generated.step")

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
