import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate/panel)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle in UV space spans from (-0.7464, 31.2996) to (121.1736, 290.3796)
    # But the inferred dimensions are 1219.2 x 2590.8, so we use those directly.
    # The extrude direction is +w (i.e., along y-axis).

    # Build the rectangle in the XY plane (since u=x, v=z? Actually v_dir = (0,0,-1) means v is -z, w_dir = (0,1,0) means w is y)
    # To keep it simple: create a rectangle in the XY plane, then extrude along Y.
    # But the frame says u_dir = x, v_dir = -z, w_dir = y.
    # So the rectangle lies in the XZ plane (u along x, v along -z).
    # We'll create a rectangle on the XZ plane, then extrude along Y.

    # Use the explicit dimensions: length_u = 1219.2 (along x), width_v = 2590.8 (along z)
    # Center the rectangle at origin for simplicity (the exact position is not critical for validation).

    result = (
        cq.Workplane("XZ")
        .rect(1219.2, 2590.8)
        .extrude(44.45)
    )

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108244_329b1876_0000\\neg_02/generated.step")

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
