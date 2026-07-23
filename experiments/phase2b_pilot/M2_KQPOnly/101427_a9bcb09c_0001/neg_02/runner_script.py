import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\101427_a9bcb09c_0001\neg_02"
    OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

    # Outer rectangle dimensions (from outer ring UV coordinates)
    outer_u_min = -2.5
    outer_u_max = 195.5
    outer_v_min = -2.5
    outer_v_max = 57.5
    outer_length_u = outer_u_max - outer_u_min  # 198.0 mm
    outer_width_v = outer_v_max - outer_v_min    # 60.0 mm

    # Inner rectangle dimensions (from inner ring UV coordinates)
    inner_u_min = 0.0
    inner_u_max = 193.0
    inner_v_min = 0.0
    inner_v_max = 55.0
    inner_length_u = inner_u_max - inner_u_min  # 193.0 mm
    inner_width_v = inner_v_max - inner_v_min    # 55.0 mm

    # Extrude distance
    extrude_distance = 25.0

    # Build the rectangular frame by subtracting the inner box from the outer box
    # The frame coordinate system has w_dir = [0, 1, 0], meaning extrusion is along the Y axis.
    # We construct the outer and inner boxes centered at origin, then translate to match the UV coordinates.

    outer_box = (
        cq.Workplane("XY")
        .rect(outer_length_u, outer_width_v)
        .extrude(extrude_distance)
    )

    inner_box = (
        cq.Workplane("XY")
        .rect(inner_length_u, inner_width_v)
        .extrude(extrude_distance)
    )

    result = outer_box.cut(inner_box)

    # Translate to match the design plan's coordinate system (origin at bbox_min_corner)
    # The outer box was centered at origin, so we shift by half dimensions + the min offsets.
    # Since outer_u_min = -2.5 and outer_v_min = -2.5, the center of the outer box in UV is at (96.5, 27.5).
    # In 3D: u maps to X, v maps to -Z (since v_dir = [0, 0, -1]), w maps to Y.
    # So the center in 3D is at (96.5, 12.5, -27.5) and we need bbox_min at (-2.5, 0, -57.5).
    # Translation vector: (outer_u_min + outer_length_u/2, extrude_distance/2, -(outer_v_min + outer_width_v/2))
    # = (-2.5 + 99.0, 12.5, -(-2.5 + 30.0)) = (96.5, 12.5, -27.5)
    # This correctly places bbox_min at (-2.5, 0, -57.5).

    result = result.translate((96.5, 12.5, -27.5))

    os.makedirs(OUT_DIR, exist_ok=True)
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
