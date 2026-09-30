import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\106817_bb28b7aa_0002\ex2"
    OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

    os.makedirs(OUT_DIR, exist_ok=True)

    # Design Plan Parameters
    # Radius: 4.87045 mm (from dimensions section, overriding profiles section)
    # Extrude distance: 6.8707 mm
    # Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
    # Extrude direction: +w (which maps to +Y in world coordinates)
    # Origin convention: bbox_min_corner

    radius = 4.87045
    extrude_distance = 6.8707

    # Build the extruded circle (cylinder)
    # The circle is centered at (0, 0) on the sketch plane.
    # Sketch plane is defined by u and v directions: u=(1,0,0) -> X, v=(0,0,-1) -> -Z
    # This corresponds to cadquery's 'XZ' plane (normal is Y, which aligns with w=(0,1,0))
    # Extrude direction +w = +Y

    result = (cq.Workplane("XZ")
              .circle(radius)
              .extrude(extrude_distance))

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
