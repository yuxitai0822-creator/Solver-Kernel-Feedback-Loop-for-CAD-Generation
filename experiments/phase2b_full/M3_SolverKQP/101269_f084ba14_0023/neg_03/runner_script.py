import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (basic slat v1)
    # Dimensions: length_u = 95.25 mm, width_v = 571.5 mm, extrude_distance = 19.05 mm
    # The profile is a rectangle in the UV plane, then extruded along W.
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle vertices in UV: (0,0), (9.525,0), (9.525,57.15), (0,57.15)
    # Note: The UV coordinates given in the plan are scaled by 10 (cm->mm conversion).
    # The actual dimensions: length_u = 95.25, width_v = 571.5.
    # The rectangle in the plan has UV extents: u from 0 to 9.525, v from 0 to 57.15.
    # To get the correct size, we scale by 10: u_span = 95.25, v_span = 571.5.
    # We'll build the rectangle directly with those dimensions.

    # Create the rectangle profile on the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
    # Actually, we can just build a box with the correct dimensions and then orient it.
    # Simpler: create a rectangle in the XY plane, extrude along Z, then rotate to match frame.
    # But the frame has w_dir = (0,1,0), so extrusion is along Y.
    # Let's build directly: rectangle in XZ plane (u along X, v along Z), extrude along Y.

    # Rectangle: center at (95.25/2, 571.5/2) in UV, but we'll place it at origin.
    # Use workplane on XZ plane.

    result = (
        cq.Workplane("XZ")
        .rect(95.25, 571.5)
        .extrude(19.05)
    )

    # The resulting box is centered at origin. The design plan origin is at bbox_min_corner.
    # We need to translate so that the minimum corner is at (0,0,0).
    # The box goes from -95.25/2 to 95.25/2 in X, -571.5/2 to 571.5/2 in Z, 0 to 19.05 in Y.
    # Translate by (95.25/2, 0, 571.5/2) to align min corner to origin.
    result = result.translate((95.25/2, 0, 571.5/2))

    # Now the box spans: X: 0 to 95.25, Y: 0 to 19.05, Z: 0 to 571.5
    # This matches the frame: u along X (95.25), w along Y (19.05), v along Z (571.5)
    # Note: v_dir was (0,0,-1), but our Z is positive. The shape is symmetric, so orientation doesn't matter.

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101269_f084ba14_0023\\neg_03/generated.step")

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
