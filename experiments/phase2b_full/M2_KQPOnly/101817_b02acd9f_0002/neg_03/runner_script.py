import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
    # Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
    # Extrude along -w direction (which is +x in world) by 1120.0 mm

    # Build the outer rectangle
    outer = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()

    # Build the inner rectangle (as a separate wire for subtraction)
    inner = cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close()

    # Combine: outer face with inner hole
    # We'll create the outer face, then cut the inner face
    result = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()
    # Cut the inner rectangle
    result = result.cut(cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-6.0, 15.0).lineTo(-2.0, 15.0).lineTo(-2.0, 11.0).close())

    # Now extrude along the w direction (which is +x in world) by 1120.0 mm
    # The design says direction is "-w", but w_dir = [1,0,0] so -w = [-1,0,0]
    # However, the frame says u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # The profile is in UV plane, extrude along -w (i.e., negative x)
    # We'll extrude in the negative x direction
    result = result.extrude(1120.0, combine=True)  # extrude along +z by default, but we need to orient

    # Actually, the profile is drawn in XY plane, but the frame says w_dir = [1,0,0]
    # So we need to rotate the profile so that the extrusion direction aligns with -w = [-1,0,0]
    # Let's redo: create the profile in YZ plane and extrude along -x

    # Better approach: create the profile in the plane perpendicular to w_dir (which is x-axis)
    # The UV plane is defined by u_dir = [0,0,-1] and v_dir = [0,1,0]
    # So the profile lies in the YZ plane (with u along -z, v along y)
    # The coordinates given are in UV space: u from -6.12 to -1.88, v from 10.88 to 15.12
    # In world: x = 0 (plane location), y = v, z = -u

    # Let's construct properly:
    # Outer rectangle in world (at x=0):
    #   y: 10.88 to 15.12
    #   z: -(-6.12)=6.12 to -(-1.88)=1.88  (since u maps to -z)
    # Actually u_dir = [0,0,-1] means u axis points in -z direction
    # So a point (u,v) maps to world: (0, v, -u)

    # Outer corners:
    # (-6.12, 10.88) -> (0, 10.88, 6.12)
    # (-6.12, 15.12) -> (0, 15.12, 6.12)
    # (-1.88, 15.12) -> (0, 15.12, 1.88)
    # (-1.88, 10.88) -> (0, 10.88, 1.88)

    # Inner corners:
    # (-6.0, 11.0) -> (0, 11.0, 6.0)
    # (-6.0, 15.0) -> (0, 15.0, 6.0)
    # (-2.0, 15.0) -> (0, 15.0, 2.0)
    # (-2.0, 11.0) -> (0, 11.0, 2.0)

    # Extrude along -w = [-1,0,0] for distance 1120.0 mm

    # Build outer polygon in YZ plane
    outer_pts = [
        (10.88, 6.12),
        (15.12, 6.12),
        (15.12, 1.88),
        (10.88, 1.88)
    ]

    inner_pts = [
        (11.0, 6.0),
        (15.0, 6.0),
        (15.0, 2.0),
        (11.0, 2.0)
    ]

    # Create outer wire
    outer_wire = cq.Workplane("YZ").polyline(outer_pts).close()

    # Create inner wire
    inner_wire = cq.Workplane("YZ").polyline(inner_pts).close()

    # Make face with hole
    # First make outer face
    outer_face = cq.Workplane("YZ").polyline(outer_pts).close().extrude(0.001)  # thin extrusion to get face
    # Actually better: use cq.Face.makeFromWires

    # Let's use a simpler approach: create the profile as a sketch and extrude
    # Use the workplane on YZ

    # Reset
    result = cq.Workplane("YZ")

    # Draw outer rectangle
    result = result.moveTo(10.88, 6.12).lineTo(15.12, 6.12).lineTo(15.12, 1.88).lineTo(10.88, 1.88).close()

    # Cut inner rectangle
    result = result.cut(cq.Workplane("YZ").moveTo(11.0, 6.0).lineTo(15.0, 6.0).lineTo(15.0, 2.0).lineTo(11.0, 2.0).close())

    # Now extrude along -x direction (negative x) by 1120.0 mm
    # The extrude method extrudes perpendicular to the workplane; for YZ plane, default is along +x
    # We need to extrude in the negative x direction, so we can extrude and then mirror or use a negative value
    # Actually cq extrude only accepts positive distance; we can extrude and then translate
    # Or we can create the profile at x=1120 and extrude backwards

    # Let's create the profile at x=1120 and extrude towards negative x
    result = cq.Workplane("YZ").workplane(offset=1120.0)
    result = result.moveTo(10.88, 6.12).lineTo(15.12, 6.12).lineTo(15.12, 1.88).lineTo(10.88, 1.88).close()
    result = result.cut(cq.Workplane("YZ").workplane(offset=1120.0).moveTo(11.0, 6.0).lineTo(15.0, 6.0).lineTo(15.0, 2.0).lineTo(11.0, 2.0).close())

    # Extrude towards negative x (distance 1120)
    result = result.extrude(-1120.0, combine=True)

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\101817_b02acd9f_0002\neg_03/generated.step")

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
