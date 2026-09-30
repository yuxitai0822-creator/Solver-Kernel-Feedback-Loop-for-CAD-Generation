import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 171.45 mm, width_v = 38.1 mm, extrude_distance = 6.35 mm
    # The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle profile in UV space: u from 0 to 171.45, v from 0 to 38.1
    # Note: The design plan uses a coordinate system where v_dir = (0,0,-1) and w_dir = (0,1,0)
    # This means the rectangle lies in the XZ plane (u along X, v along Z negative), extruded along Y (w direction)

    # Build the rectangle in the XY plane (CadQuery default) then rotate/translate to match the frame.
    # Simpler: create a box directly with the correct dimensions and position.
    # The rectangle corners in UV: (0,0), (171.45,0), (171.45,38.1), (0,38.1)
    # In world coordinates (using frame):
    #   u_dir = X, v_dir = -Z, w_dir = Y
    # So point (u,v) maps to (u, 0, -v) in world (since v_dir is -Z).
    # The extrude direction is +w = +Y, distance 6.35.
    # So the solid is a box from (0, 0, -38.1) to (171.45, 6.35, 0).

    result = cq.Workplane("XY").box(171.45, 6.35, 38.1, centered=(False, False, False)).translate((0, 0, -38.1))

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108850_0dcd5ef1_0002\\neg_03/generated.step")

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
