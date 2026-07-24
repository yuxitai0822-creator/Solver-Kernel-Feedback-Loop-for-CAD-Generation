import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
    #   => width (u span) = 4.24 mm, height (v span) = 4.24 mm
    # Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0
    #   => width = 4.0 mm, height = 4.0 mm
    # Extrude distance: 1120.0 mm along -w direction (which is -x in world)
    # The frame axes: u = (0,0,-1), v = (0,1,0), w = (1,0,0)
    # So in world coordinates:
    #   u -> -z, v -> y, w -> x
    # The profile is in the uv-plane (y-z plane), extruded along w (x direction)
    # Outer rectangle corners in uv: (-1.88,10.88), (-1.88,15.12), (-6.12,15.12), (-6.12,10.88)
    # Inner rectangle corners in uv: (-6.0,11.0), (-2.0,11.0), (-2.0,15.0), (-6.0,15.0)
    # Note: inner loop must be opposite direction for proper subtraction

    # Build the outer rectangle (counterclockwise)
    outer_pts = [
        (-1.88, 10.88),
        (-1.88, 15.12),
        (-6.12, 15.12),
        (-6.12, 10.88),
    ]

    # Build the inner rectangle (clockwise for subtraction)
    inner_pts = [
        (-6.0, 11.0),
        (-6.0, 15.0),
        (-2.0, 15.0),
        (-2.0, 11.0),
    ]

    # Create the profile in the uv-plane (which maps to yz-plane in world)
    # We'll work in the YZ plane (x=0) then extrude along X
    profile = (
        cq.Workplane("YZ")
        .polyline(outer_pts)
        .close()
        .polyline(inner_pts)
        .close()
    )

    # Extrude along the w direction (which is +x in world) by 1120 mm
    # The design says direction "-w" but w = (1,0,0), so -w = (-1,0,0)
    # However, the profile is at x=0, extruding in -x will go negative.
    # To match the expected span of 1120 along w, we extrude both ways or just one side.
    # The plan says "one_side" direction "-w", so we extrude 1120 mm in -x direction.
    result = profile.extrude(1120.0, combine=True)

    # The result is a solid with a through hole (hollow box)
    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0002\\neg_02/generated.step")

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
