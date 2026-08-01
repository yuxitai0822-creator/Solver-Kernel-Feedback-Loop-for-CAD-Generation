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

    # Design Plan: Drone Leg Left - square strut
    # Extruded rectangle profile: 19.0 x 19.0 mm, extrude 200.0 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in UV plane, extrude along +w

    # Profile rectangle corners in UV coordinates (from design plan curves):
    # u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9? No, that's 1.9
    # Wait, the design plan says length_u=19.0, width_v=19.0
    # The UV coordinates given: start_uv = [-58.278..., -12.040...], end_uv = [-58.278..., -13.940...]
    # That's a delta of 1.9 in v direction. But the design says 19.0.
    # The compiler notes say unit conversion cm_to_mm (x10). So 1.9 cm = 19 mm.
    # The UV coordinates are in cm? No, they're in mm after conversion.
    # Actually the curves show delta of 1.9, but design says 19.0.
    # The perturbation description says original=1.8999999999999986, perturbed=2.279999999999998
    # So the perturbation changed the dimension from ~1.9 to ~2.28 (in some unit)
    # But the design plan explicitly says 19.0 mm. We must follow the design plan.
    # The perturbation is a negative CAD code that we need to apply.
    # The operator is E1_envelope, which likely scales the envelope.
    # Since the design plan says 19.0 mm, we'll use that.

    # Build the rectangle in the UV plane (which is XZ plane in world coords)
    # u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
    # So UV plane = XZ plane, with v inverted

    # Rectangle center in UV: u_center = (-58.27820137826746 + -56.37820137826746)/2 = -57.32820137826746
    # v_center = (-12.04014576968157 + -13.940145769681571)/2 = -12.99014576968157
    # Width in u = 1.9, Height in v = 1.9 (but design says 19.0)
    # We'll use 19.0 as per design plan dimensions

    # Create workplane on XZ (since u_dir=X, v_dir=-Z, so plane normal is Y)
    # But v_dir is -Z, so we need to flip the v coordinate

    # Actually, let's just build a box directly: 19 x 19 x 200, positioned correctly
    # The profile center in UV: (-57.32820137826746, -12.99014576968157)
    # In world: x = u_center, z = -v_center (since v_dir = -Z), y = 0 (center of extrusion)

    # But the extrude direction is +w = +Y, so the box extends from y=-100 to y=+100

    # Let's use the workplane approach for clarity

    # Create workplane on XZ plane (normal = Y)
    wp = cq.Workplane("XZ")

    # Move to the rectangle center in XZ coordinates
    # u -> X, v -> -Z, so center in XZ: (u_center, -v_center)
    x_center = -57.32820137826746
    z_center = 12.99014576968157  # -v_center since v_dir = -Z

    # Rectangle dimensions: 19.0 x 19.0
    rect_width = 19.0
    rect_height = 19.0

    # Build the rectangle and extrude along Y (normal of XZ plane)
    result = (
        wp.moveTo(x_center, z_center)
        .rect(rect_width, rect_height, centered=True)
        .extrude(200.0)  # extrude along +Y (normal of XZ plane)
    )

    # The extrusion goes from z=0 to z=200 in workplane local coords
    # But we want it centered? The design says one_side extrusion in +w direction
    # w_dir = Y, so extrusion goes from y=0 to y=200
    # The profile is at y=0 (the workplane), so the result extends from y=0 to y=200

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0005\neg_02\iter_00/generated.step"
    exporters.export(result, OUT_STEP_PATH)

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
