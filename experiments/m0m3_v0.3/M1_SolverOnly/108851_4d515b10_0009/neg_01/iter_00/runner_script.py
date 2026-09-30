import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: SoapCutterLeg1 v1
    # Extruded rectangle: 209.55 x 57.912 mm, extrude 19.05 mm
    # Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
    # Origin at bbox min corner

    # Build the rectangle profile on the XZ plane (since v is along -Z, w is along Y)
    # The profile is in UV coordinates where U -> X, V -> -Z
    # Rectangle corners in UV: (0,0), (20.955,0), (20.955,5.7912), (0,5.7912)
    # But dimensions are 209.55 x 57.912, so scale factor is 10x from UV to mm
    # Actually the UV values are in cm? No, the design plan says unit is mm.
    # The profile curves show start_uv/end_uv values that are 1/10 of the actual dimensions.
    # This is because the source was in cm and converted to mm (x10).
    # So we use the actual dimensions: 209.55 mm x 57.912 mm

    # Create workplane on XZ (since v is along -Z, the sketch plane is XZ)
    # The frame: u_dir=(1,0,0) -> X axis, v_dir=(0,0,-1) -> -Z axis, w_dir=(0,1,0) -> Y axis
    # So the sketch plane normal is w_dir = (0,1,0) which is Y axis
    # Workplane('XZ') has normal (0,1,0) - correct!

    wp = cq.Workplane('XZ')

    # Draw rectangle centered at (209.55/2, 57.912/2) in the XZ plane
    # Note: in XZ workplane, X is first coordinate, Z is second
    result = wp.center(209.55/2, 57.912/2).rect(209.55, 57.912).extrude(19.05)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0009\neg_01\iter_00\generated.step"
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
