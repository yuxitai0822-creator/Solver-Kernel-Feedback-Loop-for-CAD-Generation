import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: rectangular prism with dimensions 8.5mm x 18.0mm x 2.5mm
    # The profile is a rectangle centered at origin in the XY plane (u,v directions)
    # Extrude in +w direction (which is +Y in world coordinates)

    # Create the rectangle profile centered at origin
    # Width along u (X) = 8.5mm, length along v (Z) = 18.0mm
    # The rectangle vertices from the plan: u from -0.425 to 0.425, v from -0.9 to 0.9
    # But these are half-dimensions: 0.425*2 = 0.85? Wait, let's check.
    # Actually the plan says length_u = 8.5, width_v = 18.0
    # The uv coordinates in the curves: start_uv = [0.425, -0.9] etc.
    # That means u range: -0.425 to 0.425 => width = 0.85? That doesn't match 8.5
    # The unit conversion note says cm_to_mm (x10). So the uv values are in cm?
    # Actually the plan says unit is mm, but compiler notes say cm_to_mm (x10)
    # So the original source was in cm, converted to mm by multiplying by 10.
    # The uv coordinates given are 0.425 and 0.9 which in mm would be 4.25 and 9.0
    # But the dimensions say 8.5 and 18.0. So the uv coordinates are half-dimensions.
    # Let's use the explicit dimensions: length_u=8.5, width_v=18.0
    # The rectangle should be centered at origin, so half-widths are 4.25 and 9.0

    # Create the workplane and draw rectangle centered at origin
    result = (cq.Workplane("XY")
              .rect(8.5, 18.0, centered=True)
              .extrude(2.5))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0004\\ex2/generated.step")

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
