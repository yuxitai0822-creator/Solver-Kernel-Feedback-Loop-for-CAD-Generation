import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_03\iter_01\generated.step"

    # Design Plan: extruded rectangle (square strut)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile: rectangle in uv-plane
    # Rectangle dimensions: length_u=19.0, width_v=19.0 (original)
    # Perturbation: 20% reduction -> 15.2 mm
    # Extrude distance: 130.0 mm along +w (y-axis)

    # The frame defines:
    #   u = x-axis
    #   v = -z-axis (negative z)
    #   w = y-axis
    # So we sketch on the XZ plane (u,v) and extrude along Y (w)

    # The rectangle corners from the design plan curves:
    # u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9
    # v range: [-12.04014576968157, -13.940145769681571] -> height = 1.9
    # These are in cm (original 1.9 cm = 19 mm, perturbed 1.52 cm = 15.2 mm)
    # The rectangle is not centered at origin; it's offset in uv space

    # To match the exact position from the design plan, we need to place the rectangle
    # at the correct uv coordinates. The center of the rectangle in uv space:
    # u_center = (-58.27820137826746 + -56.37820137826746) / 2 = -57.32820137826746
    # v_center = (-12.04014576968157 + -13.940145769681571) / 2 = -12.99014576968157

    # Convert to mm (multiply by 10 since original was in cm)
    # But wait - the perturbation says original=1.9, perturbed=1.52
    # So the rectangle size is 15.2 mm (perturbed from 19 mm)
    # The center coordinates should also be scaled? No, the center position is absolute.
    # The curves show the rectangle at specific uv coordinates.
    # Since the original was 1.9 cm = 19 mm, and the coordinates are in mm,
    # the center is at (-57.3282, -12.9901) in mm.

    # However, the design plan dimensions say length_u=19.0, width_v=19.0
    # and the perturbation changed this to 15.2 mm.
    # The center coordinates remain the same as they define position, not size.

    size = 15.2  # mm (perturbed from 19.0)
    extrude_dist = 130.0  # mm

    # Center of rectangle in uv coordinates (from design plan curves)
    u_center = -57.32820137826746  # mm
    v_center = -12.99014576968157  # mm

    # Build on XZ plane (cq.Workplane("XZ"))
    # Move to the center position, then create rectangle
    result = (cq.Workplane("XZ")
              .center(u_center, v_center)
              .rect(size, size)
              .extrude(extrude_dist))

    # The extrusion direction is along Y (normal to XZ plane), which matches w_dir=[0,1,0]

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
