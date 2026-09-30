import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude direction: -w (which maps to -x in world coordinates per frame definition)
    # Extrude distance: 1120.0 mm

    # Build the outer rectangle
    outer = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()

    # Build the inner rectangle (as a separate wire for subtraction)
    inner = cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close()

    # Combine: outer face with inner hole
    # We'll create the outer face, then subtract the inner face
    result = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()

    # Convert to face, then extrude
    result = result.wire().toPending().extrude(1120.0)

    # Now subtract the inner extrusion
    inner_wire = cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close().wire()
    inner_face = cq.Workplane("XY").polyline([(-6.0, 11.0), (-6.0, 15.0), (-2.0, 15.0), (-2.0, 11.0)]).close().extrude(1120.0)

    # Alternative approach: use cut
    # Build the outer box
    outer_box = cq.Workplane("XY").rect(4.24, 4.24).extrude(1120.0)
    # Build the inner box
    inner_box = cq.Workplane("XY").rect(4.0, 4.0).extrude(1120.0)
    # Center them at the correct position
    # The outer rectangle center: x = (-6.12 + -1.88)/2 = -4.0, y = (10.88 + 15.12)/2 = 13.0
    # The inner rectangle center: x = (-6.0 + -2.0)/2 = -4.0, y = (11.0 + 15.0)/2 = 13.0
    # So both are centered at (-4.0, 13.0)

    outer_box = cq.Workplane("XY").center(-4.0, 13.0).rect(4.24, 4.24).extrude(1120.0)
    inner_box = cq.Workplane("XY").center(-4.0, 13.0).rect(4.0, 4.0).extrude(1120.0)

    result = outer_box.cut(inner_box)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0002\\neg_01/generated.step")

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
