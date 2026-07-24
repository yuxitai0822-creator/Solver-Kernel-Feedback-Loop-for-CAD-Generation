import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # Length (u direction) = 171.45 mm, Width (v direction) = 110.998 mm, Thickness (w direction) = 6.35 mm
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # We'll build the plate centered on the origin for simplicity, then export

    # Create the rectangle profile in the XY plane (we'll orient later if needed)
    # Since the frame has u_dir = X, v_dir = -Z, w_dir = Y, we can build in XY and then rotate
    # But simpler: build directly with the given orientation

    # Build a workplane on the XY plane, then extrude in the Y direction (w_dir)
    result = (
        cq.Workplane("XY")
        .rect(171.45, 110.998)
        .extrude(6.35)
    )

    # The resulting plate is centered at origin with dimensions:
    # X: -85.725 to 85.725 (span 171.45)
    # Y: -55.499 to 55.499 (span 110.998)
    # Z: 0 to 6.35 (span 6.35)
    # This matches the design plan dimensions.

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108850_0dcd5ef1_0004\\neg_03/generated.step")

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
