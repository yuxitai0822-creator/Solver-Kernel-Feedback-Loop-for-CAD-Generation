import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
    # The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the extrusion direction is -w = (0,-1,0) (negative Y in world)
    # But for simplicity, we create the circle in the XZ plane and extrude along Y.

    # Create a workplane on the XZ plane (normal = Y axis)
    # The circle center is at (0,0) in UV, which maps to (0,0) in the plane.
    # Radius = 0.8 mm (from profile radius, note the profile curve radius is 0.08 but that's a scaling? 
    # Actually the profile curve radius is 0.08, but the explicit dimension says radius = 0.8. 
    # The profile curve radius 0.08 seems to be a mistake or scaling factor; we use the explicit dimension 0.8.

    radius = 0.8  # mm
    height = 4.0  # mm

    # Build the disk: circle extruded along Y axis (since w_dir = (0,1,0) and extrude direction is -w)
    # We'll extrude in the negative Y direction, but the result is symmetric.
    result = (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(height)  # extrude along Y positive by default; we want 4 mm total
    )

    # The extrusion direction in the design plan is -w, which is (0,-1,0).
    # To match exactly, we can extrude in the negative Y direction by using a negative distance.
    # But the absolute distance is 4.0, so we extrude -4.0 in Y.
    # However, the Workplane circle is centered at origin, so extruding in either direction gives same shape.
    # Let's do it explicitly:
    result = (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(-height)  # extrude 4 mm in negative Y direction
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\102760_26430589_0037\neg_01/generated.step")

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
