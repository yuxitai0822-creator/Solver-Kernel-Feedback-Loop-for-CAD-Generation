import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: extruded rectangular frame
    # Outer rectangle: corners at (-1.88,10.88), (-1.88,15.12), (-6.12,15.12), (-6.12,10.88)
    # Inner rectangle: corners at (-6.0,11.0), (-2.0,11.0), (-6.0,15.0), (-2.0,15.0)
    # Extrude direction: -w (which is -x in the design plan frame)
    # Extrude distance: 1120.0 mm
    # The design plan frame has u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So the profile is in the u-v plane (y-z plane in world), extrude along -w = -x

    # Build the outer rectangle using the exact corner coordinates from the design plan
    # The outer rectangle corners in uv coordinates:
    # (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88)
    # Center of outer rectangle: ((-1.88 + -6.12)/2, (10.88 + 15.12)/2) = (-4.0, 13.0)
    # Width in u: |-1.88 - (-6.12)| = 4.24, Height in v: |15.12 - 10.88| = 4.24

    # Build the inner rectangle using the exact corner coordinates from the design plan
    # The inner rectangle corners in uv coordinates:
    # (-6.0, 11.0), (-2.0, 11.0), (-6.0, 15.0), (-2.0, 15.0)
    # Center of inner rectangle: ((-6.0 + -2.0)/2, (11.0 + 15.0)/2) = (-4.0, 13.0)
    # Width in u: |-6.0 - (-2.0)| = 4.0, Height in v: |15.0 - 11.0| = 4.0

    # Create the profile on the YZ plane (which corresponds to the u-v plane in the design plan)
    # The design plan frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So u maps to -z, v maps to y, w maps to x
    # We'll work on the YZ plane and extrude along -x

    # Create the profile using a simpler approach
    # Start with a rectangle on YZ plane
    result = (
        cq.Workplane("YZ")
        .center(-4.0, 13.0)
        .rect(4.24, 4.24)
        .extrude(1120.0)
    )

    # Now cut out the inner rectangle
    result = (
        result
        .faces(">X")
        .workplane()
        .center(-4.0, 13.0)
        .rect(4.0, 4.0)
        .cutThruAll()
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0002\neg_01\iter_02\generated.step"
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
