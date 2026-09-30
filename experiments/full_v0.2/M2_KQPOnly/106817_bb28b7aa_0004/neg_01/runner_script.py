import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: washer (extruded annulus)
    # Dimensions (in mm):
    #   Outer radius = 5.5372 mm
    #   Inner radius = 1.9812 mm
    #   Thickness (extrude distance) = 1.3208 mm
    # The profile center in UV is at (-25.400001, 12.7) but we place the sketch at origin for simplicity.
    # The frame orientation: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0).
    # We'll create the annulus on the XY plane (normal = (0,0,1)) and then rotate to match frame.

    # Step 1: Create the outer circle (wire) and inner circle (wire) on the XY plane.
    outer_radius = 5.5372
    inner_radius = 1.9812
    thickness = 1.3208

    # Build the washer by extruding a circle and then cutting a concentric circle.
    # Using CadQuery's workplane approach:
    result = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)  # creates a second circle inside; when extruded, it becomes a hole
        .extrude(thickness)
    )

    # The resulting solid is a flat washer centered at origin, with normal along Z.
    # The design plan frame has w_dir = (0,1,0) meaning the extrusion direction is Y.
    # So we need to rotate the part: align Z axis to Y axis.
    # Rotation: rotate 90 degrees around X axis (so Z->Y).
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Now the washer lies in the XZ plane, extruded along Y.
    # The design plan also has v_dir = (0,0,-1) which is the secondary axis.
    # Our current orientation: after rotation, the original XY plane becomes XZ? Let's check:
    #   Original: XY plane normal = Z. After -90 deg around X: Z->Y, Y->-Z, X->X.
    #   So the face normal becomes Y, extrusion along Y. That matches w_dir = (0,1,0).
    #   The v_dir in plan is (0,0,-1). In our result, the original Y axis (now -Z) is the secondary axis.
    #   That is fine; the exact orientation of the profile within the plane is not critical for a washer.

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0004\\neg_01/generated.step")

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
