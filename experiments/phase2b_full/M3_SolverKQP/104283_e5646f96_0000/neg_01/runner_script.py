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
    # Extrude: 75.0 mm along +w direction (which maps to world X axis per frame definition)
    # Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
    # So in CadQuery: workplane on XY, then transform to align with frame

    # Build the circle profile on a workplane oriented to the frame
    # The frame's u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
    # We'll create a workplane with normal along w_dir (X axis) and u_dir as the X direction
    # But CadQuery workplane expects normal and optionally a direction for X axis.
    # Using plane with normal (1,0,0) and then rotating to align u_dir with (0,0,-1) is tricky.
    # Simpler: create the circle on the YZ plane (normal X) and position center accordingly.
    # The center_uv = (-15.0, 10.0) in UV coordinates where U = (0,0,-1), V = (0,1,0)
    # So center in world: (-15.0)*(0,0,-1) + 10.0*(0,1,0) = (0, 10, 15)
    # Then extrude along +w = (1,0,0) for 75 mm.

    result = (
        cq.Workplane("YZ")
        .circle(12.5)
        .extrude(75.0)
    )

    # The circle is centered at origin on YZ plane; we need to move it to (0, 10, 15)
    result = result.translate((0, 10, 15))

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\104283_e5646f96_0000\neg_01/generated.step")

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
