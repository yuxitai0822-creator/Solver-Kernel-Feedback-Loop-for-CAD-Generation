import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a cylinder (extruded circle) based on the design plan
    # The profile is a circle with radius 4.87045 mm, extruded 6.8707 mm in the +w direction
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means the circle lies in the u-v plane (x-z plane) and extrudes along w (y-axis)

    # Create the circle profile on the workplane (xz-plane, since v_dir is (0,0,-1) which is -z, but we use the plane normal)
    # The frame: u_dir = x-axis, v_dir = -z, w_dir = y-axis
    # So the circle is in the xz-plane, extruded along y

    # Center in uv coordinates: [11.430000364780426, 0.0] but this seems to be in the local frame
    # The radius from dimensions is 4.87045, but the profile curves show radius 0.48704499999999984
    # There's a discrepancy: the profile curve radius is 0.487, but the dimensions say radius 4.87045
    # The compiler notes mention cm_to_mm conversion (x10), so the profile radius 0.487 cm = 4.87 mm
    # So the actual radius is 4.87045 mm

    # The center_uv [11.43, 0.0] in cm = [114.3, 0.0] mm, but that seems large
    # Actually looking at the dimensions: center_uv = [114.300004, 0.0] and radius = 4.87045
    # This places the circle far from origin, but the part is a single disk
    # Likely the center should be at origin for a simple disk
    # The profile curves show center_uv = [11.430000364780426, 0.0] which is 114.3 mm in x
    # But the span estimates are ~9.74 mm in u and v, so the disk radius is ~4.87 mm
    # This suggests the center should be at (0,0) in the local frame, not 114.3 mm away
    # The 114.3 might be a coordinate system offset, but for a single part we center at origin

    # Based on the validation intents: span_u = 9.7409, span_v = 9.7409, span_w = 6.8707
    # This is a disk of diameter ~9.74 mm (radius ~4.87 mm) and height 6.87 mm

    # Create the cylinder centered at origin, extruded along y-axis
    radius = 4.87045
    height = 6.8707

    # Create workplane on the xz-plane (normal to y), then create circle and extrude
    result = (cq.Workplane("XZ")
              .circle(radius)
              .extrude(height))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0002\\neg_01/generated.step")

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
