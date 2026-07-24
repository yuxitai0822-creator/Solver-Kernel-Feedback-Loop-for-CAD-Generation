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
    # But for simplicity, we create the disk in the XY plane and then rotate/translate
    # to match the frame. However, the simplest approach: create a cylinder along Y axis
    # with radius 0.8 and height 4.0, centered at origin, then translate so min corner is at origin.

    # Create a cylinder with axis along Y (since w_dir = (0,1,0) and extrusion is -w)
    # The profile is a circle of radius 0.8 in the XZ plane (u-v plane: u=(1,0,0), v=(0,0,-1))
    # Extrude distance 4.0 along -w = (0,-1,0)

    # Build the cylinder: center at (0, 2, 0) so that the bottom face (at y=0) is the min corner
    # Actually, we want the bounding box min corner at origin. The cylinder spans from y=0 to y=4.
    # So center at (0, 2, 0) with height 4 gives y from 0 to 4.

    result = (
        cq.Workplane("XZ")
        .circle(0.8)
        .extrude(4.0)  # extrudes along Y positive by default from XZ plane
    )

    # The above creates a cylinder centered at (0,0,0) in the XZ plane, extruded along Y.
    # The bounding box: x: -0.8 to 0.8, y: 0 to 4, z: -0.8 to 0.8
    # We need to translate so that min corner is at origin: shift by (0.8, 0, 0.8)
    result = result.translate((0.8, 0, 0.8))

    # Now the bounding box should be: x: 0 to 1.6, y: 0 to 4, z: 0 to 1.6
    # This matches the expected spans: u_span=1.6, v_span=1.6, w_span=4.0

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102760_26430589_0037\neg_01/generated.step")

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
