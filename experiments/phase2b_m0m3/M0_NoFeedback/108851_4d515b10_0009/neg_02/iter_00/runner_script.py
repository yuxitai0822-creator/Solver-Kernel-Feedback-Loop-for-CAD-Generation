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

    # Design Plan: SoapCutterLeg1 v1
    # Extruded rectangle with dimensions:
    #   length_u (X): 209.55 mm (original 20.955 cm * 10)
    #   width_v (Z): 57.912 mm (original 5.7912 cm * 10)
    #   extrude_distance (Y): 19.05 mm (original 1.905 cm * 10)
    #
    # Frame: u_dir=[1,0,0] (X), v_dir=[0,0,-1] (Z negative), w_dir=[0,1,0] (Y)
    # So the rectangle lies in XZ plane, extruded in Y direction.

    # Dimensions in mm (converted from cm)
    LENGTH_U = 209.55   # X direction
    WIDTH_V = 57.912    # Z direction (note: v_dir is [0,0,-1], but magnitude is same)
    EXT_DIST = 19.05    # Y direction

    # Build the rectangle on the XZ plane (workplane 'XZ')
    # The rectangle is centered at origin for simplicity.
    # The design plan's profile curves start at (0, 5.7912) and go to (20.955, 0) in UV space.
    # UV: u along X, v along Z (but v_dir is [0,0,-1], so v coordinate maps to -Z).
    # To match the exact vertex positions, we'll place the rectangle such that
    # the min corner is at (0, -5.7912) in (X, Z) and max corner at (20.955, 0) in (X, Z).
    # But the design plan says length_u=209.55, width_v=57.912, so the rectangle spans
    # 209.55 in X and 57.912 in Z. The start_uv (0, 5.7912) and end_uv (20.955, 0) in the
    # curves seem to be in cm (original before conversion). After cm->mm conversion:
    #   start_uv: (0, 57.912)  end_uv: (209.55, 0)
    # So the rectangle goes from (0, 0) to (209.55, 57.912) in UV space.
    # In world coordinates (X, Z): u->X, v-> -Z (since v_dir = [0,0,-1])
    # So min corner: (0, -57.912) in (X, Z), max corner: (209.55, 0) in (X, Z).
    # We'll build it centered at (104.775, -28.956) for convenience.

    # Create workplane on XZ
    wp = cq.Workplane("XZ")

    # Build the rectangle centered at the midpoint of the bounding box
    cx = LENGTH_U / 2.0
    cz = -WIDTH_V / 2.0  # because v maps to -Z, and v goes from 0 to WIDTH_V

    # Create the rectangle
    rect = wp.moveTo(cx, cz).rect(LENGTH_U, WIDTH_V, centered=True)

    # Extrude in the +Y direction (w_dir = [0,1,0])
    result = rect.extrude(EXT_DIST)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0009\neg_02\iter_00\generated.step"
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
