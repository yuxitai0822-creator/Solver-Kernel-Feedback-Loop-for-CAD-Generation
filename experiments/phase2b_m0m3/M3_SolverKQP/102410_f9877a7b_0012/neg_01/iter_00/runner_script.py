import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import math

    # Design Plan: extruded annulus (bearing)
    # Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
    # The perturbation description says perturbed=1.8000000000000003 (cm) = 18 mm
    # But the design plan explicitly states extrude_distance = 12.0 mm with tol 0.01
    # We follow the design plan dimensions exactly.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0012\neg_01\iter_00/generated.step"

    # Create workplane on XZ plane (as per previous script's WORKPLANE = 'XZ')
    # But the design plan frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means the profile is in the XZ plane (u,v) and extrude is along Y (w)
    # So we use XY plane and then rotate, or use XZ directly.
    # Using XZ plane directly matches the frame: u=X, v=Z, extrude along Y

    # Build the annulus profile
    wp = cq.Workplane("XZ")

    # Outer circle
    wp = wp.moveTo(0, 0).circle(6.0)

    # Inner circle (cut)
    wp = wp.circle(4.25)

    # Extrude along Y (positive w direction) by 12.0 mm
    result = wp.extrude(12.0)

    # Export
    importers.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
