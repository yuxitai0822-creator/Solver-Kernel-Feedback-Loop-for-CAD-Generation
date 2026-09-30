import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk)
    # Dimensions:
    #   radius = 4.7117 mm (from profile radius, note: the center_uv is given but we place at origin)
    #   extrude distance = 12.192 mm
    # The profile center_uv is (50.800002, 63.500002) but in part-local frame we can place at origin.
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # We'll create a circle on the XY plane (normal = (0,0,1)) and extrude along Z.
    # However the design plan's v_dir is (0,0,-1) and w_dir is (0,1,0).
    # To match the intended orientation, we can create the circle on the XZ plane and extrude along Y.
    # But simpler: create on XY plane, extrude along Z, then rotate if needed.
    # The validation expects span_u = 9.4234 (diameter), span_v = 9.4234, span_w = 12.192.
    # If we place circle on XY plane and extrude along Z, then u = X, v = Y, w = Z.
    # That matches the expected spans: diameter 9.4234 in X and Y, height 12.192 in Z.
    # So we can use standard orientation.

    radius = 4.7117
    height = 12.192

    # Create the disk
    result = cq.Workplane("XY").circle(radius).extrude(height)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0003\\neg_03/generated.step")

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
