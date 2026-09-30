import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Constants from design plan
    EXTENT_TOTAL_MM = 1120.0
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0002\neg_03\iter_01/generated.step"

    # The design plan describes a rectangular frame (hollow box) extruded along -w direction.
    # Frame axes: u=[0,0,-1], v=[0,1,0], w=[1,0,0]
    # So the profile is in the YZ plane (u-v plane), extruded along X (w direction).
    # Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
    #   => width in u = 4.24, height in v = 4.24
    #   => center at u=-4.0, v=13.0
    # Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0
    #   => width in u = 4.0, height in v = 4.0
    #   => center at u=-4.0, v=13.0
    # Extrude distance = 1120.0 mm along -w (negative X direction)

    # Build the profile on YZ plane (X=0)
    # We'll create the outer rectangle, then subtract the inner rectangle

    # Create workplane on YZ (front view)
    wp = cq.Workplane("YZ")

    # Outer rectangle centered at (-4.0, 13.0) in YZ coordinates
    # Note: In YZ plane, u maps to Y? Actually u=[0,0,-1] means u is along -Z
    # v=[0,1,0] means v is along Y
    # So in YZ plane: Y corresponds to v, Z corresponds to -u
    # Outer rectangle in YZ: Y from 10.88 to 15.12 (v range), Z from 1.88 to 6.12 (since u=-1.88 to -6.12, negate for Z)
    # Center: Y=13.0, Z=4.0
    # Width in Y = 4.24, Height in Z = 4.24

    # Actually let's just use the raw coordinates from the design plan
    # The profile is defined in uv space. We'll place it on YZ plane.
    # u maps to -Z, v maps to Y
    # So outer: u in [-6.12, -1.88] => Z in [1.88, 6.12], v in [10.88, 15.12] => Y in [10.88, 15.12]
    # Inner: u in [-6.0, -2.0] => Z in [2.0, 6.0], v in [11.0, 15.0] => Y in [11.0, 15.0]

    # Build outer rectangle
    outer = wp.moveTo(13.0, 4.0).rect(4.24, 4.24, centered=True)  # Y=13, Z=4

    # Build inner rectangle for subtraction
    inner = wp.moveTo(13.0, 4.0).rect(4.0, 4.0, centered=True)

    # Create the profile with hole
    profile = outer.cut(inner)

    # Extrude along -X direction (negative w direction)
    # The profile is on YZ plane at X=0, extrude 1120mm in negative X
    result = profile.extrude(-EXTENT_TOTAL_MM)

    # Export
    importers = None
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
