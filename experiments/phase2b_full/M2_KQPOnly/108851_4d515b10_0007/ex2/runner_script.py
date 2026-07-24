import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: SoapCutterBackBar1 v1
    # Dimensions from plan:
    #   Rectangle profile: length_u = 279.4 mm (along u-axis = x), width_v = 50.8 mm (along v-axis = z negative?)
    #   Extrude distance: 19.05 mm along w-axis (y-axis)
    #
    # Coordinate system from plan:
    #   u_dir = [1,0,0] (x-axis)
    #   v_dir = [0,0,-1] (negative z-axis)
    #   w_dir = [0,1,0] (y-axis)
    #
    # The profile is defined in uv-space:
    #   u ranges 0..27.94 (but note: length_u = 279.4, width_v = 50.8)
    #   The curves show: start_uv (0,5.08) -> (0,0) -> (27.94,0) -> (27.94,5.08) -> (0,5.08)
    #   This is a rectangle of size 27.94 x 5.08 in uv-space.
    #   But the dimensions say length_u=279.4, width_v=50.8.  The uv values are scaled?
    #   Actually, the plan says "unit_conversion_applied: cm_to_mm (x10)".
    #   The uv values 27.94 and 5.08 are in cm? 27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm.
    #   So the uv coordinates are in cm, but we work in mm.  So we must scale by 10.
    #   Alternatively, the plan's explicit dimensions already give mm values.
    #   Let's use the explicit dimensions: length_u=279.4 mm, width_v=50.8 mm.
    #   The uv coordinates in the curves are 27.94 and 5.08, which are cm values.
    #   So we multiply by 10 to get mm: 279.4 and 50.8.
    #
    # The frame: u=x, v=-z, w=y.
    # So the rectangle lies in the xz-plane (u along x, v along -z).
    # Extrude along w = y direction, distance 19.05 mm.
    #
    # We'll create a rectangle on the xz-plane, centered or corner?  The uv origin is (0,0) which maps to (0,0,0) in world?
    # The plan says origin_convention: bbox_min_corner.  So the rectangle's min corner is at (0,0,0).
    # u=0..279.4, v=0..50.8.  But v is along -z, so v=0 maps to z=0, v=50.8 maps to z=-50.8.
    # So the rectangle corners: (0,0,0), (279.4,0,0), (279.4,0,-50.8), (0,0,-50.8).
    # Extrude along +y (w direction) by 19.05 mm.

    # Build the profile in the xz-plane.
    # Use a 2D rectangle on the workplane XY?  Actually, we need to orient correctly.
    # Simpler: create a box directly with dimensions 279.4 x 19.05 x 50.8, but that would be axis-aligned.
    # The box would have y as height, but we need the rectangle in xz and extrude along y.
    # That is exactly a box: length x=279.4, height y=19.05, depth z=50.8.
    # But the v direction is negative z, so the rectangle's v coordinate goes from 0 to 50.8 along -z.
    # That means the box's z extent is from -50.8 to 0.
    # So we can create a box centered or from corner.  Let's use a box from corner (0,0,-50.8) to (279.4,19.05,0).
    # That matches the uv mapping: u=0..279.4 (x), v=0..50.8 (z from -50.8 to 0), w=0..19.05 (y).

    result = cq.Workplane("XY").box(279.4, 19.05, 50.8, centered=(False, False, False))
    # But box centered=False places the box with min corner at (0,0,0) in the workplane's local coordinates.
    # Workplane XY: the box extends in x, y, z.  With centered=False, the box is in the first octant.
    # That would give x from 0 to 279.4, y from 0 to 19.05, z from 0 to 50.8.
    # But we need z from -50.8 to 0.  So we need to translate.
    # Alternatively, we can build the profile on the XZ plane and extrude along Y.

    # Let's do it properly with a sketch on the XZ plane.
    # Workplane("XZ") gives a plane with x and z axes.  Then we can draw a rectangle and extrude along Y.
    # But the v direction is -z, so the rectangle's v coordinate goes from 0 to 50.8 along -z.
    # That means the rectangle's z coordinate goes from 0 to -50.8.
    # So we draw a rectangle from (0,0) to (279.4, -50.8) in the XZ plane.
    # Then extrude along the normal (which is Y) by 19.05 mm.

    result = (
        cq.Workplane("XZ")
        .rect(279.4, 50.8, centered=False)
        .extrude(19.05)
    )
    # But rect centered=False places the rectangle with min corner at (0,0) in the workplane's local coordinates.
    # In XZ workplane, local coordinates are (x, z).  So rect(279.4, 50.8) gives x from 0 to 279.4, z from 0 to 50.8.
    # We need z from -50.8 to 0.  So we can translate the rectangle in z by -50.8.
    # Or we can use a polyline to define the exact corners.

    # Let's use a polyline to be precise.
    # Corners in (x,z): (0,0), (279.4,0), (279.4,-50.8), (0,-50.8)
    result = (
        cq.Workplane("XZ")
        .polyline([(0,0), (279.4,0), (279.4,-50.8), (0,-50.8)])
        .close()
        .extrude(19.05)
    )

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0007\\ex2/generated.step")

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
