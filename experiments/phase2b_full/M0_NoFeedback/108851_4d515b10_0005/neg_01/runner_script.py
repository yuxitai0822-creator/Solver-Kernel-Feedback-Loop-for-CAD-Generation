import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 307.848 mm, width_v = 19.05 mm, extrude_distance = 12.7 mm
    # The profile is a rectangle in the UV plane, then extruded along +W direction.
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means: U = X, V = -Z, W = Y
    # So the rectangle lies in the X-Z plane (with V reversed), and extrudes along Y.

    # Build the rectangle in the XY plane (since CadQuery's default is XY), then rotate/translate as needed.
    # Actually, we can directly use the frame: sketch on plane with normal = w_dir = (0,1,0) (Y-axis).
    # The plane normal is Y, so the sketch plane is XZ.
    # In that plane, u_dir = X, v_dir = -Z.
    # So we draw a rectangle of size length_u along X, width_v along -Z (i.e., Z direction reversed).
    # But CadQuery's rectangle is defined by width (X) and height (Y) in the sketch plane.
    # We'll use a Workplane on the Y-axis plane (normal Y), then draw rectangle centered at origin.
    # However, the design plan origin is at bbox_min_corner, so we need to position the rectangle so that its min corner is at (0,0,0) in the frame.
    # In the frame: u_min = 0, v_min = 0. So the rectangle spans from (0,0) to (length_u, width_v) in UV.
    # In world coordinates: U = X, V = -Z, so point (u,v) maps to (u, 0, -v).
    # So the rectangle corners:
    #   (0,0) -> (0, 0, 0)
    #   (length_u, 0) -> (length_u, 0, 0)
    #   (length_u, width_v) -> (length_u, 0, -width_v)
    #   (0, width_v) -> (0, 0, -width_v)
    # So the rectangle lies in the plane Y=0, with Z negative.
    # Then extrude along +W = +Y direction by 12.7 mm.

    # We'll build a box directly to be simpler and more robust.
    # The box spans: X: 0 to 307.848, Y: 0 to 12.7, Z: -19.05 to 0.
    # But careful: the extrude direction is +W = +Y, so the base is at Y=0 and it goes to Y=12.7.
    # The profile is at Y=0, extruded upward.

    result = (
        cq.Workplane("XY")
        .box(307.848, 12.7, 19.05, centered=(False, False, False))
        .translate((0, 0, -19.05))  # move so that Z goes from -19.05 to 0
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\108851_4d515b10_0005\neg_01/generated.step")

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
