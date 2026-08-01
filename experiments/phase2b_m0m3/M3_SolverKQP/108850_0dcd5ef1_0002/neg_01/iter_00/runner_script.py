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

    # Design Plan: MPPF_FrameBottom1 4x6 v1
    # Extruded rectangle: 171.45 mm x 38.1 mm, extrude 6.35 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in UV plane: u from 0 to 171.45, v from 0 to 38.1
    # Extrude in +w direction (y-axis) by 6.35 mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108850_0dcd5ef1_0002\neg_01\iter_00/generated.step"

    # Build the rectangle in the XZ plane (since v_dir = [0,0,-1] means v is -Z, u is X)
    # The profile curves in UV space:
    # start_uv=(0.0, 3.81) -> end_uv=(0.0, 0.0)  (v from 3.81 to 0)
    # start_uv=(0.0, 0.0) -> end_uv=(17.145, 0.0) (u from 0 to 17.145)
    # start_uv=(17.145, 0.0) -> end_uv=(17.145, 3.81) (v from 0 to 3.81)
    # start_uv=(17.145, 3.81) -> end_uv=(0.0, 3.81) (u from 17.145 to 0)
    # Note: UV coordinates are scaled: u values are 17.145 but length_u is 171.45 (factor of 10)
    # The design plan says length_u=171.45, width_v=38.1
    # The curves use 17.145 and 3.81 which are 1/10 of the actual dimensions
    # This is likely a unit conversion issue (cm to mm). We'll use the explicit dimensions.

    # Create workplane on XZ plane (since v_dir = [0,0,-1] means v is -Z, u is X)
    # The rectangle will be drawn in the XZ plane, then extruded along Y (+w direction)

    # Use the explicit dimensions from the design plan
    length_u = 171.45  # mm
    width_v = 38.1     # mm
    extrude_distance = 6.35  # mm

    # Build the rectangle centered at origin for simplicity
    # The rectangle spans from u=0 to u=171.45, v=0 to v=38.1 in UV space
    # In XYZ: u -> X, v -> -Z (since v_dir = [0,0,-1])
    # So X from 0 to 171.45, Z from -38.1 to 0

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Draw rectangle: center at (171.45/2, -38.1/2) with size 171.45 x 38.1
    # In XZ plane, X is horizontal, Z is vertical
    result = wp.moveTo(length_u/2, -width_v/2).rect(length_u, width_v, centered=True).extrude(extrude_distance)

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
