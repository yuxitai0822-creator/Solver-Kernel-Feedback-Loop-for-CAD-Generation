import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: MPPF_FrameBottom1 4x6 v1
    # Extruded rectangle: 171.45mm x 38.1mm x 6.35mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Rectangle in UV plane: u from 0 to 171.45, v from 0 to 38.1
    # Extrude in +w direction by 6.35mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108850_0dcd5ef1_0002\neg_01\iter_00\generated.step"

    # Create workplane on XY plane (default)
    # The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So we work on XY plane, then extrude in Y direction

    # Rectangle dimensions from design plan:
    # length_u = 171.45 mm, width_v = 38.1 mm
    # extrude_distance = 6.35 mm

    # Build the rectangle on XY plane, centered at origin for simplicity
    # Then we'll position it so that the rectangle spans from (0,0) to (171.45, 38.1) in UV
    # In XY plane: u -> X, v -> Y (but v_dir is [0,0,-1], so v maps to -Z? No, we need to be careful)
    # Actually, the frame says u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means: u axis = X, v axis = -Z, w axis = Y
    # So the rectangle is in the XZ plane (u along X, v along -Z)
    # Extrude in +w direction = +Y direction

    # Let's build on XZ plane
    result = (
        cq.Workplane("XZ")
        .center(171.45/2, -38.1/2)  # center the rectangle; v goes from 0 to 38.1, but v_dir is -Z, so v=0 is at z=0, v=38.1 is at z=-38.1
        .rect(171.45, 38.1)
        .extrude(6.35)  # extrude in +Y direction (perpendicular to XZ plane)
    )

    # The rectangle should span from (0,0,0) to (171.45, 6.35, -38.1) in XYZ
    # But we centered it, so let's adjust: center at (171.45/2, 6.35/2, -38.1/2)
    # Actually, let's just build it from the corner to be precise

    # Better approach: build directly from corner
    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)  # start at u=0, v=0 -> x=0, z=0
        .rect(171.45, 38.1, centered=False)  # rectangle from (0,0) to (171.45, -38.1) in XZ
        .extrude(6.35)  # extrude in +Y
    )

    # Now the solid spans from (0,0,0) to (171.45, 6.35, -38.1)
    # This matches the design plan: u from 0 to 171.45, v from 0 to 38.1 (but v_dir=-Z, so v=38.1 maps to z=-38.1)
    # Extrude in +w (Y) by 6.35

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
