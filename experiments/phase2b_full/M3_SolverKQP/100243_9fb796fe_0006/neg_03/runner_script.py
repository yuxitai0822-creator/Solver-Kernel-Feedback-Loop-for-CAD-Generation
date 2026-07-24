import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Drone Leg - square strut
    # Profile: rectangle 19mm x 19mm, extruded 130mm
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The profile is defined in UV space with corners at:
    #   (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
    # This is a 1.9mm x 1.9mm rectangle (but dimensions say 19mm x 19mm, so scaling factor 10 from cm->mm conversion)
    # The UV coordinates are in cm originally, converted to mm by multiplying by 10.
    # Actually the compiler notes say cm_to_mm (x10), so the UV values are in cm, we need to scale to mm.
    # Let's compute: width in U = 2.0 cm = 20 mm, width in V = 1.9 cm = 19 mm. But dimensions say 19mm x 19mm.
    # The UV coordinates: U range = -58.2782 to -56.3782 = 1.9 cm = 19 mm. V range = -13.9401 to -12.0401 = 1.9 cm = 19 mm.
    # So the rectangle is 19mm x 19mm in UV space (after cm->mm conversion).
    # We'll build the profile in the UV plane, then extrude along W direction (0,1,0) by 130mm.

    # Define the rectangle in UV coordinates (in mm, after scaling from cm)
    # The center of the rectangle in UV:
    center_u = (-58.27820137826746 + -56.37820137826746) / 2.0  # = -57.32820137826746
    center_v = (-12.04014576968157 + -13.940145769681571) / 2.0  # = -12.99014576968157
    # Width in U: 1.9 cm = 19 mm, Width in V: 1.9 cm = 19 mm

    # Build the profile as a rectangle centered at (center_u, center_v) with size 19x19
    # But we need to respect the exact UV coordinates from the plan.
    # Let's just use the exact corners scaled to mm (they are already in mm after cm->mm conversion? 
    # The plan says unit_conversion_applied: cm_to_mm (x10), so the values are in cm originally, now in mm after x10.
    # Actually the values in the plan are already the converted mm values? Let's check: 
    # The values are like -58.2782, which is -5.82782 cm, plausible for a part. 
    # The width is 1.9 cm = 19 mm, so the values are in mm already (since 19mm width).
    # So we can use them directly.

    # Create the rectangle profile in the UV plane (which is the XZ plane in CadQuery? 
    # Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    # So U maps to X, V maps to -Z, W maps to Y.
    # We'll create the profile on the XZ plane (Y=0) and extrude along Y.

    # The rectangle corners in (U,V) = (X, -Z):
    # We'll build a wire from the points.

    pts = [
        (-58.27820137826746, -12.04014576968157),   # (U, V) = (X, -Z)
        (-58.27820137826746, -13.940145769681571),
        (-56.37820137826746, -13.940145769681571),
        (-56.37820137826746, -12.04014576968157),
        (-58.27820137826746, -12.04014576968157),   # close
    ]

    # Convert to 3D points: (U, 0, -V) because V maps to -Z
    pts_3d = [(p[0], 0.0, -p[1]) for p in pts]

    # Build the profile
    wire = cq.Workplane("XZ").polyline(pts_3d).close().wire()

    # Make a face from the wire
    face = cq.Face.makeFromWires(wire)

    # Extrude along W direction = (0,1,0) by 130mm
    result = cq.Solid.extrudeLinear(face, (0, 1, 0), 130.0)

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\100243_9fb796fe_0006\neg_03/generated.step")

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
