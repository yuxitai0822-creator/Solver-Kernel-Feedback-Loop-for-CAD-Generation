import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_02\iter_02/generated.step"

    # The design plan specifies:
    # - straight_length = 500.0 mm (after cm->mm conversion: 50cm -> 500mm)
    # - radius = 50.0 mm (after cm->mm conversion: 5cm -> 50mm)
    # - extrude distance = 100.0 mm
    # The validation intents expect:
    # - span_u = 600.0 mm (500 + 2*50)
    # - span_v = 100.0 mm (2*50)
    # - span_w = 100.0 mm
    #
    # The perturbation description says radius changed from 5.0 to 6.25 (cm),
    # which would be 62.5mm. But the validation intents expect 50mm radius.
    # We follow the design plan dimensions: straight_length=500mm, radius=50mm.

    # Build the stadium profile using a workplane
    # The stadium consists of:
    # - Left semicircle: center (0,0), radius 50, from 90° to 270° (or 0° to 180° in the design plan)
    # - Top line: from (0, 50) to (500, 50)
    # - Right semicircle: center (500,0), radius 50, from 270° to 90° (or 0° to 180° in the design plan)
    # - Bottom line: from (500, -50) to (0, -50)

    # Use threePointArc to ensure correct arc direction
    # For the right arc: start at (500, -50), end at (500, 50), midpoint at (550, 0)
    # For the left arc: start at (0, 50), end at (0, -50), midpoint at (-50, 0)

    wire = (
        cq.Workplane("XY")
        .moveTo(0, -50)
        .lineTo(500, -50)
        .threePointArc((550, 0), (500, 50))  # Arc from (500,-50) to (500,50) via (550,0)
        .lineTo(0, 50)
        .threePointArc((-50, 0), (0, -50))  # Arc from (0,50) to (0,-50) via (-50,0)
        .close()
    )

    # Extrude the wire to create the solid
    result = wire.extrude(100.0)

    # Export to STEP
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
