import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
    # The design plan specifies a flat plate/panel with extruded rectangle profile
    # Profile rectangle corners in UV space:
    #   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
    #   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
    #   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
    #   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
    # The rectangle spans from u=7.83 to u=127.83 (delta = 120.0) and v=-66.34 to v=-6.34 (delta = 60.0)
    # But the dimensions say length_u=1200.0, width_v=600.0, extrude_distance=20.0
    # The UV coordinates appear to be scaled by 0.1 (cm to mm conversion factor of 10 applied)
    # So we use the explicit dimensions: 1200 x 600 x 20 mm

    # Build the plate centered at origin for simplicity
    result = (
        cq.Workplane("XY")
        .rect(1200, 600)
        .extrude(20)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0004\\ex2/generated.step")

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
