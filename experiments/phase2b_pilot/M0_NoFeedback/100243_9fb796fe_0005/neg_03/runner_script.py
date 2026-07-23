import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    # Ensure output directory exists
    OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\100243_9fb796fe_0005\neg_03'
    OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

    os.makedirs(OUT_DIR, exist_ok=True)

    # Design Plan Parameters:
    # - Primitive: extruded_rectangle
    # - Profile dimensions: length_u = 19.0 mm, width_v = 19.0 mm
    # - Extrude distance: 200.0 mm
    # - Extrude direction: +w (which maps to +Y in CadQuery's default coordinate system)
    # - Profile origin in local frame: u = -58.27820137826746, v = -13.940145769681571

    # In CadQuery, the default workplane (XY plane) extrudes along the Z axis.
    # To map the design plan's +w direction to CadQuery's extrusion axis, we construct the geometry on the XZ plane.
    # This aligns: u -> X, v -> Z, w(+Y) -> Y.

    # Calculate the center of the rectangle in the XZ plane
    u_min = -58.27820137826746
    u_max = -56.37820137826746
    v_min = -13.940145769681571
    v_max = -12.04014576968157

    center_x = (u_min + u_max) / 2.0  # -57.32820137826746
    center_z = (v_min + v_max) / 2.0  # -12.99014576968157

    # Build the rectangular profile on the XZ plane centered at the computed coordinates
    result = (
        cq.Workplane("XZ")
        .center(center_x, center_z)
        .rect(19.0, 19.0)
        .extrude(200.0)
    )

    # Export the result to STEP format
    cq.exporters.export(result, OUT_STEP_PATH)

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
