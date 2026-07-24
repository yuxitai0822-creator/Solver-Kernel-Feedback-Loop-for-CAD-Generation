import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame
    # Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude direction: -w (which maps to -x in world coordinates per frame definition)
    # Extrude distance: 1120.0 mm

    # Build the profile on the YZ plane (since u_dir = -z, v_dir = +y, w_dir = +x)
    # We'll create the outer and inner rectangles as wires, then make a face with a hole.

    # Outer rectangle points (in UV coordinates: u along -z, v along +y)
    # Convert to 3D: point = origin + u*u_dir + v*v_dir
    # Since origin is at bbox_min_corner, we can place the sketch at x=0 (w=0) and extrude in -x direction.

    # Outer rectangle corners in UV:
    # P1: (-1.88, 10.88)
    # P2: (-1.88, 15.12)
    # P3: (-6.12, 15.12)
    # P4: (-6.12, 10.88)

    # Inner rectangle corners in UV:
    # P1: (-6.0, 11.0)
    # P2: (-2.0, 11.0)
    # P3: (-2.0, 15.0)
    # P4: (-6.0, 15.0)

    # Map UV to 3D: (x, y, z) = (0, v, -u) because u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
    # So u -> -z, v -> y, w -> x.  We'll place the sketch at x=0.

    # Outer rectangle in 3D (x=0 plane):
    outer_pts = [
        (0, 10.88, 1.88),   # u=-1.88 -> z=1.88
        (0, 15.12, 1.88),   # u=-1.88 -> z=1.88
        (0, 15.12, 6.12),   # u=-6.12 -> z=6.12
        (0, 10.88, 6.12),   # u=-6.12 -> z=6.12
    ]

    # Inner rectangle in 3D (x=0 plane):
    inner_pts = [
        (0, 11.0, 6.0),     # u=-6.0 -> z=6.0
        (0, 11.0, 2.0),     # u=-2.0 -> z=2.0
        (0, 15.0, 2.0),     # u=-2.0 -> z=2.0
        (0, 15.0, 6.0),     # u=-6.0 -> z=6.0
    ]

    # Build wires
    outer_wire = cq.Workplane("XZ").polyline(outer_pts).close().wire()
    inner_wire = cq.Workplane("XZ").polyline(inner_pts).close().wire()

    # Build face with hole
    # We need to combine them into a single face.  Use cq.Face.makeFromWires
    outer_face = cq.Face.makeFromWires(outer_wire, [inner_wire])

    # Extrude in -w direction (which is -x) by 1120 mm
    result = cq.Workplane("XY").newObject([outer_face]).extrude(1120.0, both=False, taper=0.0)

    # The extrusion direction is along the normal of the face.  Our face is on the YZ plane (x=0), normal is +x.
    # Extrude by 1120 in +x gives a solid from x=0 to x=1120.  But we need -w direction (i.e., -x).
    # So we extrude in the opposite direction by using a negative distance or by mirroring.
    # Let's extrude by -1120 to go in -x direction.
    # Actually, we can just extrude and then translate if needed, but the design says direction is -w.
    # Since w_dir = +x, -w = -x.  So we want the solid to extend from x=0 to x=-1120.
    # We'll extrude in the negative direction by using a negative distance.

    # Rebuild with negative extrude:
    result = cq.Workplane("XY").newObject([outer_face]).extrude(-1120.0, both=False, taper=0.0)

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\101817_b02acd9f_0002\neg_01/generated.step")

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
