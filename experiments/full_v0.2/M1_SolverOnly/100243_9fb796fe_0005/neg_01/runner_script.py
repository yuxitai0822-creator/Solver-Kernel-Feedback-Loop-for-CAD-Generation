import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile in the UV plane
    # From the design plan:
    #   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    #   rectangle corners in UV: (-58.2782, -12.0401) to (-56.3782, -13.9401)
    #   This gives a rectangle of size 1.9 x 1.9 in UV (but dimensions say 19.0 x 19.0 mm)
    #   The UV coordinates appear to be in cm (since compiler note says cm_to_mm x10)
    #   So we scale by 10: rectangle from (-582.782, -120.401) to (-563.782, -139.401)
    #   But simpler: just use the explicit dimensions: length_u=19.0, width_v=19.0
    #   The profile is centered? No, the UV coordinates define exact placement.
    #   We'll create the rectangle at the given UV coordinates, scaled by 10.

    # Actually, let's use the explicit dimensions: 19.0 x 19.0 mm rectangle
    # The UV coordinates in the plan are in cm (before scaling), so after *10 they become mm.
    # Let's compute:
    #   start_uv: (-58.27820137826746, -12.04014576968157) -> (-582.7820137826746, -120.4014576968157)
    #   end_uv:   (-56.37820137826746, -13.940145769681571) -> (-563.7820137826746, -139.40145769681571)
    #   width in U: -56.3782 - (-58.2782) = 1.9 cm = 19 mm
    #   width in V: -13.9401 - (-12.0401) = -1.9 cm = -19 mm (absolute 19 mm)

    # So we create a rectangle with lower-left at (-582.782, -139.401) and size (19, 19)
    # But the order of V is reversed (v_dir = [0,0,-1]), so we need to be careful.
    # Simpler: just create a 19x19 rectangle centered at the midpoint of the UV coordinates.

    # Midpoint in UV (cm): ((-58.2782 + -56.3782)/2, (-12.0401 + -13.9401)/2) = (-57.3282, -12.9901)
    # In mm: (-573.282, -129.901)

    # But the extrude direction is +w = [0,1,0], distance = 200 mm

    # Let's build the profile in the XY plane (since u_dir = X, v_dir = -Z, w_dir = Y)
    # Actually, we need to map UVW to XYZ:
    #   u -> X
    #   v -> -Z (so V axis is negative Z)
    #   w -> Y

    # So the rectangle in UV maps to:
    #   X = U coordinate
    #   Z = -V coordinate
    #   Y = 0 (starting plane)

    # Let's compute the rectangle in XYZ:
    #   U range: [-582.782, -563.782] mm
    #   V range: [-139.401, -120.401] mm (note: V goes from -12.04 to -13.94 in cm, so -120.4 to -139.4 in mm)
    #   So Z = -V: Z range = [120.401, 139.401] mm

    # Rectangle in XZ plane: X from -582.782 to -563.782, Z from 120.401 to 139.401
    # Width in X = 19 mm, Width in Z = 19 mm

    # Create the rectangle
    result = (cq.Workplane("XY")
              .center(-573.282, 129.901)  # center of rectangle in XZ plane
              .rect(19.0, 19.0)
              .extrude(200.0))

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100243_9fb796fe_0005\\neg_01/generated.step")

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
