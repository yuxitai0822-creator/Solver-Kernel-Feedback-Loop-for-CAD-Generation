import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: rectangular prism 12mm x 60mm x 40mm (extruded rectangle)
    # Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
    # Profile rectangle in uv-plane: u from -0.6 to 0.6 (width 1.2? No, dimensions say length_u=12, width_v=60)
    # The curves show start_uv and end_uv values that are half-dimensions: u: -0.6 to 0.6 (span 1.2) but length_u=12 means scaling factor 10?
    # Actually the compiler notes say unit conversion cm_to_mm (x10). So the uv values are in cm, need to multiply by 10.
    # So rectangle in mm: u from -6 to 6 (span 12), v from -30 to 30 (span 60).
    # Extrude along w direction (0,1,0) by 40mm.

    # Build on XZ plane (since w=[0,1,0] is Y axis, sketch plane is XZ)
    result = (cq.Workplane("XZ")
              .center(0, 0)
              .rect(12.0, 60.0, centered=True)
              .extrude(40.0))

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\105278_909f3813_0000\neg_01\iter_00/generated.step"
    exporters.export(result, OUT_STEP_PATH)

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
