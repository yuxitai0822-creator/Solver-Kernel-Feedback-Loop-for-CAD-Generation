import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Constants from design plan (unit: mm)
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0001\neg_02\iter_02/generated.step"

    # The design plan specifies dimensions in cm (after cm->mm conversion x10):
    # Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
    #   -> width = 195.5 - (-2.5) = 198.0 cm = 1980.0 mm
    #   -> height = 57.5 - (-2.5) = 60.0 cm = 600.0 mm
    # Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    #   -> width = 193.0 - 0.0 = 193.0 cm = 1930.0 mm
    #   -> height = 55.0 - 0.0 = 55.0 cm = 550.0 mm
    # Extrude distance: 25.0 mm in +w direction (which is +Y in our coordinate system)

    # Scale factor: 10 (cm to mm)
    scale = 10.0

    # Outer rectangle in mm (scaled from cm)
    outer_width = 198.0 * scale  # 1980.0 mm
    outer_height = 60.0 * scale  # 600.0 mm

    # Inner rectangle in mm (scaled from cm)
    inner_width = 193.0 * scale  # 1930.0 mm
    inner_height = 55.0 * scale  # 550.0 mm

    # Extrude distance in mm (already in mm)
    extrude_dist = 25.0

    # The profile is in the XZ plane (Y=0), extruded in +Y direction
    # Using centered=False to match the origin convention (bbox_min_corner)
    # The outer rectangle starts at (-2.5*scale, -2.5*scale) in UV space
    # which maps to XZ plane: u->X, v->Z (but v_dir is [0,0,-1], so v maps to -Z)
    # Actually, let's just use the UV coordinates directly and place the rectangle
    # at the correct position.

    # The outer rectangle in UV space: u from -2.5 to 195.5, v from -2.5 to 57.5
    # After scaling: u from -25.0 to 1955.0, v from -25.0 to 575.0
    # The inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    # After scaling: u from 0.0 to 1930.0, v from 0.0 to 550.0

    # Build the outer box first
    result = (
        cq.Workplane("XZ")
        .rect(outer_width, outer_height, centered=False)
        .extrude(extrude_dist)
    )

    # Cut the inner hole to create the frame
    inner = (
        cq.Workplane("XZ")
        .rect(inner_width, inner_height, centered=False)
        .extrude(extrude_dist)
    )

    result = result.cut(inner)

    # Export
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
