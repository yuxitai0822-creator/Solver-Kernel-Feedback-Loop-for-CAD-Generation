import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular frame by extruding a rectangular profile with a hole
    # Outer rectangle: 40 x 40 mm (from u: 6 to 10, v: -7 to -3, scaled by 10)
    # Inner rectangle: 37.6 x 37.6 mm (from u: 6.12 to 9.88, v: -6.88 to -3.12, scaled by 10)
    # Extrude 780 mm in the w direction (positive y after scaling)

    # Build the outer rectangle
    outer = (
        cq.Workplane("XY")
        .moveTo(60, -70)  # start_uv (10, -7) * 10
        .lineTo(60, -30)  # to (10, -3) * 10
        .lineTo(100, -30) # to (6, -3) * 10
        .lineTo(100, -70) # to (6, -7) * 10
        .close()
    )

    # Build the inner rectangle (hole)
    inner = (
        cq.Workplane("XY")
        .moveTo(61.2, -68.8)  # start_uv (6.12, -6.88) * 10
        .lineTo(61.2, -31.2)  # to (6.12, -3.12) * 10
        .lineTo(98.8, -31.2)  # to (9.88, -3.12) * 10
        .lineTo(98.8, -68.8)  # to (9.88, -6.88) * 10
        .close()
    )

    # Combine: outer rectangle with inner hole subtracted
    result = (
        cq.Workplane("XY")
        .polyline(outer.ctx.points)
        .close()
        .extrude(780.0)
    )

    # Subtract the inner hole
    result = (
        result
        .faces(">Z")
        .workplane()
        .polyline(inner.ctx.points)
        .close()
        .cutThruAll()
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0000\\neg_01/generated.step")

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
