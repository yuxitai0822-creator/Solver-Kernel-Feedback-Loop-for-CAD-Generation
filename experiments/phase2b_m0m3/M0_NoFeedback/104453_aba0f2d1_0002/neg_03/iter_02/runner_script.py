import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0002\neg_03\iter_02/generated.step"

    # Design parameters from the design plan
    # The profile curves show:
    #   arc at (0,0) radius 5.0, start 0, end 180
    #   line from (0,-5) to (50,-5)
    #   arc at (50,0) radius 5.0, start 0, end 180
    #   line from (50,5) to (0,5)
    # This gives straight_length=50, radius=5 (after cm->mm conversion x10 from original 500/50)
    # Extrude distance = 100.0 mm

    straight_length = 50.0  # mm
    radius = 5.0  # mm
    extrude_distance = 100.0  # mm

    # Build the stadium profile correctly:
    # The stadium consists of:
    # - Left arc centered at (0,0) from 0 to 180 degrees (going counterclockwise)
    # - Top line from (0,5) to (50,5)
    # - Right arc centered at (50,0) from 0 to 180 degrees (going counterclockwise)
    # - Bottom line from (50,-5) to (0,-5)
    #
    # In CadQuery, we need to trace the perimeter in order.
    # Starting at (0, -5) (bottom of left arc):
    # 1. Arc from (0,-5) through (5,0) to (0,5)  -- this is the left end cap (180 deg arc)
    # 2. Line from (0,5) to (50,5) -- top straight
    # 3. Arc from (50,5) through (55,0) to (50,-5) -- right end cap (180 deg arc)
    # 4. Line from (50,-5) to (0,-5) -- bottom straight

    result = (
        cq.Workplane("XY")
        .moveTo(0, -radius)  # start at bottom of left arc
        .threePointArc(
            (radius, 0),  # midpoint of arc (top of left cap)
            (0, radius)   # end of arc
        )
        .lineTo(straight_length, radius)  # top straight
        .threePointArc(
            (straight_length + radius, 0),  # midpoint of right arc
            (straight_length, -radius)       # end of right arc
        )
        .lineTo(0, -radius)  # bottom straight back to start
        .close()
        .extrude(extrude_distance)
    )

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
