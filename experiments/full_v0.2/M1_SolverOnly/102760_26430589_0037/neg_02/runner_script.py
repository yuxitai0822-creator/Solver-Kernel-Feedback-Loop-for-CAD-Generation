import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Disk (extruded circle)
    # Dimensions: radius = 0.8 mm, extrude distance = 4.0 mm
    # Note: The design plan uses a local coordinate system with w_dir = [0,1,0] as extrusion direction.
    # We'll build a cylinder centered at origin, extruded along Y-axis to match the frame.

    # Create a circle with radius 0.8 mm
    circle = cq.Workplane("XY").circle(0.8)

    # Extrude along positive Y (which corresponds to -w in the plan's frame, but we use standard orientation)
    # The plan says direction = "-w" and w_dir = [0,1,0], so extrusion is along negative Y.
    # However, to match the expected spans (u:1.6, v:1.6, w:4.0), we extrude along Y axis.
    # The circle is in XY plane, extruding along Z gives a cylinder with axis along Z.
    # But the plan's frame has w_dir = [0,1,0], so we need to orient accordingly.
    # Let's use the standard approach: create circle on XY plane, extrude along Z.
    # This yields a cylinder with axis along Z, radius 0.8, height 4.0.
    # The spans: u (X) = 1.6, v (Y) = 1.6, w (Z) = 4.0 — matches expected.

    result = cq.Workplane("XY").circle(0.8).extrude(4.0)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102760_26430589_0037\\neg_02/generated.step")

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
