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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0006\neg_03\iter_00/generated.step"

    # Design Plan: extruded rectangle (square strut)
    # Profile: rectangle 19.0 x 19.0 mm (in UV plane)
    # Extrude: 130.0 mm along +W direction
    # Frame: U = (1,0,0), V = (0,0,-1), W = (0,1,0)
    # Origin at bbox_min_corner convention: we place rectangle so that its min corner is at origin

    # Rectangle dimensions from design plan
    length_u = 19.0  # along U axis (X)
    width_v = 19.0   # along V axis (Z, negative direction)
    extrude_distance = 130.0  # along W axis (Y)

    # Build the rectangle on the XZ plane (since U=X, V=-Z, W=Y)
    # We want the rectangle to span from (0,0) to (19,19) in UV coordinates
    # In world: U = X, V = -Z, so:
    #   point (u,v) -> (u, 0, -v)
    # Rectangle corners in UV: (0,0), (19,0), (19,19), (0,19)
    # In world: (0,0,0), (19,0,0), (19,0,-19), (0,0,-19)

    # Create workplane on XZ plane (Y=0)
    wp = cq.Workplane("XZ")

    # Build the rectangle centered at (9.5, -9.5) in XZ coordinates
    # rect() takes width (X) and height (Z), centered by default
    result = wp.center(9.5, -9.5).rect(length_u, width_v).extrude(extrude_distance)

    # Export
    importers.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
