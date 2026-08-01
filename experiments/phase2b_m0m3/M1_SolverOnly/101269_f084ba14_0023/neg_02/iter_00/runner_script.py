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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101269_f084ba14_0023\neg_02\iter_00\generated.step"

    # Design Plan: basic slat v1 (5)
    # Rectangle profile in UV frame:
    #   U direction: [1,0,0] (X axis)
    #   V direction: [0,0,-1] (negative Z axis)
    #   W direction: [0,1,0] (Y axis)
    # Profile rectangle corners in UV coordinates:
    #   (0,0), (9.525, 0), (9.525, 57.15), (0, 57.15)
    #   But note: the perturbed value for the U-span is 11.43 (not 9.525)
    #   The perturbation description says: operator=E1_envelope; original=9.525; perturbed=11.43
    #   So we use 11.43 for the U dimension.
    # Extrude distance: 19.05 mm in +W direction (Y axis)

    # Build the rectangle on the XZ plane (since V is -Z, U is X, W is Y)
    # The rectangle spans from 0 to 11.43 in U (X) and 0 to 57.15 in V (Z)
    # But the UV coordinates in the design plan show:
    #   start_uv: (9.525, 57.15) to (9.525, 0)  -> this is the right edge
    #   start_uv: (0, 57.15) to (9.525, 57.15) -> top edge
    #   start_uv: (0, 0) to (0, 57.15) -> left edge
    #   start_uv: (9.525, 0) to (0, 0) -> bottom edge
    # So the rectangle is 9.525 x 57.15, but perturbed to 11.43 x 57.15

    # Create workplane on XZ plane (since V is -Z, we work on XZ)
    # The rectangle will be drawn on XZ plane, then extruded in Y direction
    result = (
        cq.Workplane("XZ")
        .rect(11.43, 57.15, centered=False)
        .extrude(19.05)
    )

    # Export to STEP
    exporters.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
