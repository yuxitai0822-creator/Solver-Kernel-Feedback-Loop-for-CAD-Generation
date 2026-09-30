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
    # Extrude along -w direction (which is x-axis in world) by 1120.0 mm

    # Build the profile in the UV plane (z=0 initially, then we'll orient)
    # Outer rectangle
    outer = cq.Workplane("XY").moveTo(-6.12, 10.88).lineTo(-6.12, 15.12).lineTo(-1.88, 15.12).lineTo(-1.88, 10.88).close()
    # Inner rectangle (cutout)
    inner = cq.Workplane("XY").moveTo(-6.0, 11.0).lineTo(-2.0, 11.0).lineTo(-2.0, 15.0).lineTo(-6.0, 15.0).close()

    # Combine: outer minus inner to create the frame profile
    frame_profile = outer.cut(inner)

    # Now extrude along the w direction (which is x-axis in world, but we need to orient correctly)
    # The design plan says: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So UV plane is YZ plane, and extrusion is along X axis.
    # We built the profile in XY plane, so we need to rotate to YZ plane.
    # Actually, let's build directly in YZ plane for clarity.

    # Rebuild: profile in YZ plane (X=0), then extrude along X
    # Outer rectangle in YZ: y from 10.88 to 15.12, z from -6.12 to -1.88 (since u is z, v is y)
    # But careful: u_dir = [0,0,-1] means u axis is negative Z, v_dir = [0,1,0] means v axis is Y.
    # So in world: u corresponds to -z, v corresponds to y.
    # Points in UV: (-6.12, 10.88) -> world: z = -(-6.12) = 6.12? No, u = -z, so z = -u.
    # Let's just use the UV coordinates directly and map:
    #   world_x = w coordinate (extrusion direction)
    #   world_y = v coordinate
    #   world_z = -u coordinate

    # Build profile in YZ plane (world_y = v, world_z = -u)
    # Outer: u from -6.12 to -1.88, v from 10.88 to 15.12
    # So world_z = -u: from 6.12 to 1.88 (note order: -(-6.12)=6.12, -(-1.88)=1.88)
    # world_y = v: from 10.88 to 15.12

    # Let's create the profile using points directly
    pts_outer = [
        (10.88, 6.12),   # v=10.88, u=-6.12 -> y=10.88, z=6.12
        (15.12, 6.12),   # v=15.12, u=-6.12 -> y=15.12, z=6.12
        (15.12, 1.88),   # v=15.12, u=-1.88 -> y=15.12, z=1.88
        (10.88, 1.88),   # v=10.88, u=-1.88 -> y=10.88, z=1.88
    ]

    pts_inner = [
        (11.0, 6.0),     # v=11.0, u=-6.0 -> y=11.0, z=6.0
        (15.0, 6.0),     # v=15.0, u=-6.0 -> y=15.0, z=6.0
        (15.0, 2.0),     # v=15.0, u=-2.0 -> y=15.0, z=2.0
        (11.0, 2.0),     # v=11.0, u=-2.0 -> y=11.0, z=2.0
    ]

    # Build outer polygon
    outer_wire = cq.Workplane("YZ").polyline(pts_outer).close()
    inner_wire = cq.Workplane("YZ").polyline(pts_inner).close()

    # Create face from outer, then cut inner
    result = outer_wire.cut(inner_wire).extrude(1120.0)

    # The extrusion direction is along X (positive by default for YZ plane)
    # But design says direction is "-w" which is negative X. So we extrude in both directions or negative?
    # Actually, we want the part to span from x=0 to x=1120? Or from x=-1120 to x=0?
    # The design says extent_type: one_side, direction: -w. So extrude 1120 mm in negative X direction.
    # Let's rebuild with proper orientation.

    # Better approach: build in XY plane, then rotate the whole thing.
    # Let's use the original approach but ensure correct extrusion direction.

    # Rebuild from scratch with clear coordinate mapping:
    # We'll create the profile in the XY plane (as originally), then transform.

    # Profile in XY plane (x = u, y = v)
    # Outer: u from -6.12 to -1.88, v from 10.88 to 15.12
    outer_pts = [(-6.12, 10.88), (-6.12, 15.12), (-1.88, 15.12), (-1.88, 10.88)]
    inner_pts = [(-6.0, 11.0), (-6.0, 15.0), (-2.0, 15.0), (-2.0, 11.0)]

    # Build outer
    outer_poly = cq.Workplane("XY").polyline(outer_pts).close()
    inner_poly = cq.Workplane("XY").polyline(inner_pts).close()

    # Cut inner from outer to get frame profile
    frame_face = outer_poly.cut(inner_poly)

    # Now we need to orient: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # This means: u (x in our sketch) maps to world -z, v (y in sketch) maps to world y, w maps to world x
    # So we need to rotate: x->-z, y->y, z->x
    # This is a rotation of -90 deg around y axis, then maybe flip?
    # Actually: new_x = old_z, new_y = old_y, new_z = -old_x
    # So we can use a rotation: rotate 90 deg around Y, then mirror?
    # Simpler: build directly in YZ plane as before.

    # Let's use the YZ plane approach but extrude in negative X direction.
    # Build profile in YZ plane (y, z)
    # Map: u -> -z, v -> y
    # Outer: u from -6.12 to -1.88 -> z from 6.12 to 1.88
    #        v from 10.88 to 15.12 -> y from 10.88 to 15.12
    outer_yz = [(10.88, 6.12), (15.12, 6.12), (15.12, 1.88), (10.88, 1.88)]
    inner_yz = [(11.0, 6.0), (15.0, 6.0), (15.0, 2.0), (11.0, 2.0)]

    # Build in YZ plane
    outer_face = cq.Workplane("YZ").polyline(outer_yz).close()
    inner_face = cq.Workplane("YZ").polyline(inner_yz).close()
    frame = outer_face.cut(inner_face)

    # Extrude in negative X direction (since direction is -w, and w is x)
    result = frame.extrude(-1120.0)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0002\\neg_02/generated.step")

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
