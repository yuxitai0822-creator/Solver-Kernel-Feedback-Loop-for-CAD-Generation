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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_03\iter_00/generated.step"

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: corners at (6.0, -7.0), (10.0, -7.0), (10.0, -3.0), (6.0, -3.0) in UV plane
    # Inner rectangle (hole): corners at (6.12, -6.88), (6.12, -3.12), (9.88, -3.12), (9.88, -6.88)
    # Extrude direction: +w (which maps to +Y in world), distance 780.0 mm
    # The UV plane corresponds to XZ in world (u->X, v->Z, w->Y)

    # Build outer rectangle on XZ plane
    result = (
        cq.Workplane("XZ")
        .moveTo(6.0, -7.0)
        .lineTo(10.0, -7.0)
        .lineTo(10.0, -3.0)
        .lineTo(6.0, -3.0)
        .close()
        .extrude(780.0)  # extrude in +Y direction
    )

    # Cut inner hole (the void)
    inner = (
        cq.Workplane("XZ")
        .moveTo(6.12, -6.88)
        .lineTo(6.12, -3.12)
        .lineTo(9.88, -3.12)
        .lineTo(9.88, -6.88)
        .close()
        .extrude(780.0)  # same extrusion to cut through
    )

    result = result.cut(inner)

    # Export
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
