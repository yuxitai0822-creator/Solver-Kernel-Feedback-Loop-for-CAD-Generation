import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Outer rectangle: u spans from -2.5 to 195.5 (198.0mm), v spans from -2.5 to 57.5 (60.0mm)
    outer_u_min = -2.5
    outer_u_max = 195.5
    outer_v_min = -2.5
    outer_v_max = 57.5

    outer_length = outer_u_max - outer_u_min
    outer_width = outer_v_max - outer_v_min

    # Inner rectangle: u spans from 0.0 to 193.0 (193.0mm), v spans from 0.0 to 55.0 (55.0mm)
    inner_u_min = 0.0
    inner_u_max = 193.0
    inner_v_min = 0.0
    inner_v_max = 55.0

    inner_length = inner_u_max - inner_u_min
    inner_width = inner_v_max - inner_v_min

    # Extrusion distance along +w (which is +Y in world coordinates)
    extrude_distance = 25.0

    # Build the rectangular frame profile on the XZ plane (u=X, v=-Z -> Z inverted for CadQuery Y-up)
    # Outer rectangle centered at origin for easy rect() construction
    outer_rect = cq.Workplane("XZ").rect(outer_length, outer_width)

    # Inner rectangle offset relative to the outer rectangle's center
    # Center offset in X: (inner_u_min + inner_u_max)/2 - (outer_u_min + outer_u_max)/2
    offset_x = (inner_u_min + inner_u_max) / 2.0 - (outer_u_min + outer_u_max) / 2.0
    # Center offset in Z: (inner_v_min + inner_v_max)/2 - (outer_v_min + outer_v_max)/2.0
    offset_z = (inner_v_min + inner_v_max) / 2.0 - (outer_v_min + outer_v_max) / 2.0

    inner_rect = outer_rect.rect(inner_length, inner_width).center(offset_x, offset_z)

    # Extrude the frame profile along +Y (which corresponds to +w)
    result = inner_rect.extrude(extrude_distance)

    # Translate the result so the bounding box minimum corner aligns with the part_local origin (0,0,0)
    # Current bbox min is at (outer_u_min, 0, -outer_v_max) due to XZ plane and extrusion
    result = result.translate((0 - outer_u_min, 0, 0 - (-outer_v_max)))

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot_m0\M0\101427_a9bcb09c_0001\neg_02/generated.step"
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
