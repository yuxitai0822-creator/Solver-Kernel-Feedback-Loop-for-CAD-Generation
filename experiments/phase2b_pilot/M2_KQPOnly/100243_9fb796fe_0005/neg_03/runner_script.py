import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Build the extruded rectangle (square strut) based on the design plan.
    # The profile is a 19x19 rectangle, extruded 200mm along the +w direction.
    # In the part's local frame, u=(1,0,0), v=(0,0,-1), w=(0,1,0).
    # This means the extrusion happens along the +Y axis.
    # The profile lies in the XZ plane, with Z inverted (v_dir = -Z).
    # The rectangle corners in uv are (-58.278, -13.940) to (-56.378, -12.040).
    # Mapping uv to XYZ: X = u, Z = -v.
    # So the rectangle in XYZ spans from X=-58.278 to X=-56.378, and Z=12.040 to Z=13.940.

    result = (
        cq.Workplane("XZ")
        .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
        .rect(19.0, 19.0)
        .translate((-57.32820137826746, 0, 12.99014576968157))
        .extrude(200.0)
    )

    # Export the result to STEP format
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\100243_9fb796fe_0005\neg_03/generated.step"
    cq.exporters.export(result, OUT_STEP_PATH)

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
