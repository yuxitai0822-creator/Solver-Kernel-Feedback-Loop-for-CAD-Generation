import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame
    # Outer rectangle: 40mm x 40mm (u: 10 to 6, v: -7 to -3 => span 4? Wait, need to interpret correctly)
    # Actually from curves: outer ring points: (10,-7), (6,-7), (6,-3), (10,-3) => width = 4, height = 4? That's 4x4, but dimensions say 40x40.
    # The plan says unit conversion cm_to_mm (x10), so original cm values become mm: 4cm -> 40mm. So the uv coordinates are in cm? No, the plan says unit is mm, but compiler notes say cm_to_mm (x10).
    # The uv coordinates given: 10,6,7,3 etc. If these are in cm, then 10cm = 100mm, but outer length is 40mm. That doesn't match.
    # Let's re-examine: outer ring start_uv (10,-7) to (6,-7) is a line. The span in u direction: from 6 to 10 = 4 units. In v direction: from -7 to -3 = 4 units. So outer square is 4x4 units.
    # Dimensions say outer_length_u = 40mm, outer_width_v = 40mm. So 4 units = 40mm => 1 unit = 10mm. So the uv coordinates are in cm (10mm per unit).
    # Inner ring: (6.12,-6.88) to (6.12,-3.12) etc. Span: u from 6.12 to 9.88 = 3.76 units = 37.6mm. v from -6.88 to -3.12 = 3.76 units = 37.6mm. Matches inner dimensions.
    # So we need to scale uv coordinates by 10 to get mm.

    # Frame axes: u_dir = (1,0,0) = x, v_dir = (0,0,-1) = -z, w_dir = (0,1,0) = y.
    # So the profile lies in the x-z plane (u=x, v=-z), and extrude direction is +w = +y.
    # Extrude distance = 780mm.

    scale = 10.0  # cm to mm

    # Outer rectangle in mm (scaled from cm)
    outer_pts = [
        (10.0 * scale, -7.0 * scale),
        (6.0 * scale, -7.0 * scale),
        (6.0 * scale, -3.0 * scale),
        (10.0 * scale, -3.0 * scale),
    ]

    # Inner rectangle in mm (scaled from cm)
    inner_pts = [
        (6.12 * scale, -6.88 * scale),
        (6.12 * scale, -3.12 * scale),
        (9.88 * scale, -3.12 * scale),
        (9.88 * scale, -6.88 * scale),
    ]

    # Build the profile in the x-z plane (u=x, v=-z, so v coordinate maps to -z)
    # We'll create a 2D sketch on the xz plane (Y=0), then extrude in +Y direction.

    # Create outer wire
    outer_wire = cq.Workplane("XZ").moveTo(outer_pts[0][0], outer_pts[0][1])
    for pt in outer_pts[1:]:
        outer_wire = outer_wire.lineTo(pt[0], pt[1])
    outer_wire = outer_wire.close()

    # Create inner wire (as a separate wire, then cut)
    inner_wire = cq.Workplane("XZ").moveTo(inner_pts[0][0], inner_pts[0][1])
    for pt in inner_pts[1:]:
        inner_wire = inner_wire.lineTo(pt[0], pt[1])
    inner_wire = inner_wire.close()

    # Combine: create face from outer wire, then cut inner hole
    # Use cq.Workplane to build the profile
    result = (
        cq.Workplane("XZ")
        .moveTo(outer_pts[0][0], outer_pts[0][1])
        .lineTo(outer_pts[1][0], outer_pts[1][1])
        .lineTo(outer_pts[2][0], outer_pts[2][1])
        .lineTo(outer_pts[3][0], outer_pts[3][1])
        .close()
        .extrude(780.0)  # extrude in +Y (since workplane is XZ, normal is Y)
    )

    # Now cut the inner hole: create a solid from inner profile and subtract
    inner_solid = (
        cq.Workplane("XZ")
        .moveTo(inner_pts[0][0], inner_pts[0][1])
        .lineTo(inner_pts[1][0], inner_pts[1][1])
        .lineTo(inner_pts[2][0], inner_pts[2][1])
        .lineTo(inner_pts[3][0], inner_pts[3][1])
        .close()
        .extrude(780.0)
    )

    result = result.cut(inner_solid)

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0000\\neg_02/generated.step")

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
