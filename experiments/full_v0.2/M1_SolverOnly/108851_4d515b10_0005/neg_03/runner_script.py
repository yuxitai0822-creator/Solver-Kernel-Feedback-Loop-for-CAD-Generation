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

    # Build the rectangle in the XY plane (since CadQuery defaults to XY for 2D), then rotate/transform.
    # Simpler: create a box directly with the correct dimensions and position.
    # The rectangle in UV: u from 0 to 307.848, v from 0 to 19.05 (but v_dir is -Z, so v=0..19.05 maps to Z=0..-19.05)
    # Extrude along +W = +Y by 12.7 mm.
    # So the solid spans: X: 0 to 307.848, Y: 0 to 12.7, Z: -19.05 to 0.

    result = cq.Workplane("XY").box(307.848, 12.7, 19.05, centered=(False, False, False))
    # The box is centered by default; we need it positioned at origin min corner.
    # box(width, height, depth) with centered=False places the box with one corner at origin.
    # But careful: box(width, height, depth) where width=X, height=Y, depth=Z.
    # We want X: 0..307.848, Y: 0..12.7, Z: -19.05..0.
    # So we can create a box of size (307.848, 12.7, 19.05) and then translate it in Z by -19.05.

    result = cq.Workplane("XY").box(307.848, 12.7, 19.05, centered=(False, False, False)).translate((0, 0, -19.05))

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0005\\neg_03/generated.step")

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
