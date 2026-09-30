import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
    # The profile is a rectangle in the uv-plane, then extruded in the +w direction.
    # Note: The design plan uses a local frame with u_dir=(1,0,0), v_dir=(0,1,0), w_dir=(0,0,1).
    # The rectangle corners in uv coordinates are: (-3.9, 0) to (0, 6.8) but the dimensions indicate
    # length_u=39.0 and width_v=68.0. The uv coordinates appear to be in cm (since unit_conversion_applied: cm_to_mm x10).
    # Converting: -3.9 cm = -39 mm, 0 cm = 0 mm, 6.8 cm = 68 mm.
    # So the rectangle spans from u=-39 to u=0 (length 39) and v=0 to v=68 (width 68).
    # We'll create the rectangle centered or at origin for simplicity, matching the span.

    result = (cq.Workplane("XY")
              .rect(39.0, 68.0, centered=False)
              .extrude(10.0))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102175_699d5e7c_0003\\neg_02/generated.step")

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
