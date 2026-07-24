import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: SoapCutterBedBack1 v1
    # Part: flat_plate_or_panel, extruded rectangle
    # Dimensions: length_u = 307.848 mm, width_v = 19.05 mm, extrude_distance = 12.7 mm
    # The profile is a rectangle in the UV plane, then extruded along W direction.
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means: U = X, V = -Z, W = Y
    # The rectangle in UV: u from 0 to 30.7848? Wait, the curves show u from 0 to 30.7848, v from 0 to 1.905.
    # But the dimensions say length_u = 307.848, width_v = 19.05.
    # The curves show start_uv and end_uv values: 
    #   (0, 1.905) -> (0, 0) -> (30.7848, 0) -> (30.7848, 1.905) -> (0, 1.905)
    # So the rectangle in UV space is 30.7848 x 1.905.
    # But the dimensions say 307.848 x 19.05. There's a factor of 10 discrepancy.
    # The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # So the original was in cm, converted to mm. The curves are in the original cm units?
    # Actually, the curves show 30.7848 and 1.905, which are 307.848/10 and 19.05/10.
    # So the curves are in cm, but the dimensions are in mm after conversion.
    # We should use the mm dimensions: 307.848 x 19.05, extrude 12.7 mm.
    # The frame: u_dir = X, v_dir = -Z, w_dir = Y.
    # So the rectangle lies in the X-Z plane (since u=X, v=-Z), and extrudes along Y.
    # We'll create a rectangle on the XZ plane, then extrude along Y.

    # Build the base rectangle in the XZ plane (u=X, v=-Z means v goes negative Z, but we can just use positive Z and adjust)
    # Actually, v_dir = (0,0,-1) means the v axis points in the -Z direction.
    # So a point at (u, v) in the profile maps to (u, 0, -v) in world coordinates.
    # The rectangle corners in UV: (0,0), (307.848,0), (307.848,19.05), (0,19.05)
    # In world: (0,0,0), (307.848,0,0), (307.848,0,-19.05), (0,0,-19.05)
    # So the rectangle is on the XZ plane at y=0, spanning x from 0 to 307.848, z from -19.05 to 0.
    # Extrude along +w = +Y direction by 12.7 mm.

    result = (
        cq.Workplane("XZ")
        .center(307.848/2, -19.05/2)  # center the rectangle at (153.924, -9.525)
        .rect(307.848, 19.05)
        .extrude(12.7)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108851_4d515b10_0005\neg_01/generated.step")

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
