import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk)
    # Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
    # Extrude: 75.0 mm along +w direction (which is world X axis)
    # Frame: u = (0,0,-1), v = (0,1,0), w = (1,0,0)
    # So the circle lies in the YZ plane (u-v plane) and extrudes along X.

    # Create the circle profile on the YZ plane (workplane origin at (0,0,0))
    # Center in UV: u=-1.5, v=1.0  (but dimensions say radius=12.5, center_uv=[-15.0, 10.0])
    # The dimensions block overrides the profile curves center_uv? 
    # The profile curves center_uv = [-1.5, 1.0] but dimensions say center_uv = [-15.0, 10.0].
    # The dimensions block is the authoritative source for explicit dimensions.
    # So we use radius=12.5, center at (-15.0, 10.0) in UV coordinates.
    # UV plane: u = (0,0,-1), v = (0,1,0). So u maps to -Z, v maps to +Y.
    # Center in world: u*center_u + v*center_v = (0,0,-1)*(-15) + (0,1,0)*10 = (0, 10, 15)
    # Wait: (0,0,-1)*(-15) = (0,0,15). So center = (0, 10, 15).

    # Workplane: we can use a workplane on the YZ plane (X=0) and then offset.
    # But easier: build a circle at the correct location and extrude along X.

    # Use a workplane on the YZ plane (front plane in cq)
    result = (
        cq.Workplane("YZ")
        .center(10.0, 15.0)  # center in YZ: Y=10, Z=15
        .circle(12.5)
        .extrude(75.0)  # extrude along X (positive direction)
    )

    # The extrusion direction is +w = (1,0,0) which is +X.
    # The circle is at Y=10, Z=15, radius 12.5, extruded 75 mm along X.
    # This matches the design plan.

    import cadquery as cq
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104283_e5646f96_0000\\neg_02/generated.step")

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
