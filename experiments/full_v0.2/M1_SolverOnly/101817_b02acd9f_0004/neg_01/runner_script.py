import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 1200 mm, width_v = 600 mm, extrude_distance = 20 mm
    # The profile is defined in a local frame where:
    #   u_dir = (1,0,0) -> x-axis
    #   v_dir = (0,0,-1) -> negative z-axis
    #   w_dir = (0,1,0) -> y-axis (extrude direction)
    # The rectangle corners in UV space:
    #   (127.82976131535646, -66.34402294937294)  -> top-right? Actually these are offsets from origin.
    #   (7.829761315356478, -66.34402294937294)   -> bottom-right
    #   (127.82976131535646, -6.344022949372942)  -> top-left
    #   (7.829761315356478, -6.344022949372942)   -> bottom-left
    # The span in u-direction: 127.82976 - 7.82976 = 120.0 (but expected 1200 mm)
    # The span in v-direction: -6.34402 - (-66.34402) = 60.0 (but expected 600 mm)
    # Note: The design plan states unit conversion cm_to_mm (x10).
    # The UV values appear to be in cm (120 cm = 1200 mm, 60 cm = 600 mm).
    # So we multiply by 10 to get mm.
    # Also the extrude distance is 20 mm (already mm).

    # Build the rectangle in the local frame, then transform to world frame.
    # Local frame: u -> x, v -> -z, w -> y
    # So a point (u, v) in local frame maps to (u, 0, -v) in world frame.
    # The rectangle corners in UV (cm):
    #   A: (127.82976131535646, -66.34402294937294)
    #   B: (7.829761315356478, -66.34402294937294)
    #   C: (127.82976131535646, -6.344022949372942)
    #   D: (7.829761315356478, -6.344022949372942)
    # Convert to mm: multiply by 10.

    scale = 10.0  # cm to mm

    # UV points in mm
    u1 = 127.82976131535646 * scale  # ~1278.2976
    v1 = -66.34402294937294 * scale   # ~-663.4402
    u2 = 7.829761315356478 * scale    # ~78.2976
    v2 = -6.344022949372942 * scale    # ~-63.4402

    # In local frame: (u, v) -> world (x, y, z) = (u, 0, -v)
    # So corners:
    p1 = (u1, 0, -v1)  # (1278.2976, 0, 663.4402)
    p2 = (u2, 0, -v1)  # (78.2976, 0, 663.4402)
    p3 = (u1, 0, -v2)  # (1278.2976, 0, 63.4402)
    p4 = (u2, 0, -v2)  # (78.2976, 0, 63.4402)

    # Create wire from points
    wire = cq.Workplane("XY").moveTo(p1[0], p1[2]).lineTo(p2[0], p2[2]).lineTo(p4[0], p4[2]).lineTo(p3[0], p3[2]).close()

    # Extrude in +w direction (world y-axis) by 20 mm
    result = wire.extrude(20.0)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0004\\neg_01/generated.step")

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
