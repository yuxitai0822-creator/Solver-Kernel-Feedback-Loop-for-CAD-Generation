import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame
    # Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude direction: -w (which maps to -x in world coordinates per frame definition)
    # Extrude distance: 1120.0 mm

    # Create the outer rectangle profile
    outer = (
        cq.Workplane("XY")
        .moveTo(-6.12, 10.88)
        .lineTo(-6.12, 15.12)
        .lineTo(-1.88, 15.12)
        .lineTo(-1.88, 10.88)
        .close()
    )

    # Create the inner rectangle profile (cutout)
    inner = (
        cq.Workplane("XY")
        .moveTo(-6.0, 11.0)
        .lineTo(-6.0, 15.0)
        .lineTo(-2.0, 15.0)
        .lineTo(-2.0, 11.0)
        .close()
    )

    # Build the frame by extruding the outer profile and cutting the inner
    # The frame definition says u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So the profile lies in the V-W plane? Actually the profile is defined in UV coordinates.
    # The extrude direction is -w, which is [-1,0,0] in world coordinates.
    # We'll build on the XY plane and extrude along -X.

    # First create the outer extrusion
    result = outer.extrude(1120.0, combine=False)

    # Create the inner extrusion as a separate solid
    inner_solid = inner.extrude(1120.0, combine=False)

    # Cut the inner from the outer
    result = result.cut(inner_solid)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0002\\neg_01/generated.step")

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
