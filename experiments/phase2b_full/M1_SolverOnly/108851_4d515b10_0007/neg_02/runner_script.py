import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # The profile is a rectangle: 27.94 mm x 5.08 mm (in UV space)
    # But the dimensions table says length_u = 279.4 mm, width_v = 50.8 mm
    # The profile curves show 27.94 and 5.08, which appear to be scaled by 10x
    # The compiler notes indicate cm_to_mm conversion (x10), so the actual dimensions are:
    # length_u = 279.4 mm, width_v = 50.8 mm
    # Extrude distance = 19.05 mm

    # Build the base rectangle in the XY plane (u=x, v=z, w=y per frame definition)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So u -> X, v -> -Z, w -> Y
    # The profile is defined in UV space, so we draw in XZ plane with v reversed

    result = (
        cq.Workplane("XZ")
        .center(279.4/2, 50.8/2)  # center the rectangle at origin
        .rect(279.4, 50.8)
        .extrude(19.05)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0007\\neg_02/generated.step")

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
