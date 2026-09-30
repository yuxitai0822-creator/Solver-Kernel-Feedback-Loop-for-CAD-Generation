import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # Origin at bbox_min_corner, so we place the rectangle in the XY plane (u=x, v=z, w=y)
    # The rectangle is defined in UV space: u from 0 to 171.45, v from 0 to 110.998
    # But v_dir = (0,0,-1) means v axis points in -z direction.
    # To keep positive extents, we define the rectangle in the xz plane with v reversed.
    # Actually simpler: use standard Cadquery workflow: create rectangle in XY plane, extrude in Z.
    # But the frame says w_dir = (0,1,0) so extrusion is along y.
    # We'll create a rectangle in the XZ plane (u=x, v=z) and extrude in +y direction.
    # The rectangle corners: (0,0) to (171.45, 110.998) in UV, but v_dir = (0,0,-1) so v=0 is z=0, v=110.998 is z=-110.998.
    # To keep the part in positive octant, we shift so that min corner is at origin.
    # Actually the origin_convention is bbox_min_corner, so the part's bounding box minimum corner is at (0,0,0).
    # So we place the rectangle with u from 0 to 171.45, v from 0 to 110.998, but v maps to -z.
    # That means z goes from 0 to -110.998, which puts min corner at z=-110.998, not 0.
    # To have min corner at (0,0,0), we need to shift: set v=0 at z=-110.998 and v=110.998 at z=0.
    # So the rectangle in world: x from 0 to 171.45, z from -110.998 to 0, then extrude in +y from 0 to 6.35.
    # That gives bbox min = (0, 0, -110.998) which is not (0,0,0). 
    # To satisfy bbox_min_corner origin, we need to translate so that min corner is at origin.
    # The min corner is (0, 0, -110.998). So we translate by (0, 0, 110.998).
    # But the design plan says origin_convention is bbox_min_corner, meaning the part's local origin is at its min corner.
    # So we should build the part with its min corner at (0,0,0).
    # Let's redefine: rectangle in UV: u from 0 to 171.45, v from 0 to 110.998.
    # Map u->x, v->z (but v_dir = (0,0,-1) so v maps to -z).
    # So x = u, z = -v.  When u=0, x=0; when u=171.45, x=171.45.
    # When v=0, z=0; when v=110.998, z=-110.998.
    # So the rectangle in xz plane goes from (0,0) to (171.45, -110.998).
    # The min corner in xz is (0, -110.998). To shift min corner to (0,0), translate by (0, 0, 110.998).
    # After translation: x from 0 to 171.45, z from 0 to 110.998.
    # Then extrude in +y (w_dir) from 0 to 6.35.
    # So final bbox: x: [0, 171.45], y: [0, 6.35], z: [0, 110.998].
    # That matches the expected spans: u=171.45, v=110.998, w=6.35.

    # Build the rectangle in the xz plane, then translate, then extrude in y.

    result = (
        cq.Workplane("XZ")
        .rect(171.45, 110.998, centered=False)
        .translate((0, 0, 110.998))  # shift so min corner at origin
        .extrude(6.35)
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\108850_0dcd5ef1_0004\ex2/generated.step")

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
