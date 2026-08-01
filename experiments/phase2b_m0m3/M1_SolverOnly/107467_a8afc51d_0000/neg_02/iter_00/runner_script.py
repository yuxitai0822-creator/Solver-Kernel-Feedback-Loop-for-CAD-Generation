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

    # Design Plan: Disk with radius 3.0 mm, extruded 14.0 mm
    # Perturbation: radius changed from 0.3 to 0.375 (but this is the profile radius, not the disk radius)
    # The disk radius is 3.0 mm, the profile radius is 0.375 mm (perturbed from 0.3)
    # Wait - re-reading the design plan: the profile radius is 0.3 (perturbed to 0.375)
    # But the dimensions section says radius = 3.0. Let me check the design plan again.
    # The profile curves have radius 0.30000000000000004 (perturbed to 0.375)
    # The dimensions section has radius = 3.0. This is confusing.
    # Looking at the original: profile radius = 0.3, dimensions radius = 3.0
    # The perturbation changes the profile radius from 0.3 to 0.375
    # But the disk should have radius 3.0 based on dimensions
    # Actually, the profile radius in the curves is 0.3 (perturbed to 0.375)
    # The dimensions radius is 3.0 - this is likely the actual disk radius
    # The profile radius of 0.3 might be a different feature
    # Let me just use the dimensions radius = 3.0 for the main disk
    # And the profile radius = 0.375 for the circle in the profile
    # But wait - the profile is a single circle with radius 0.375
    # That would make a very small disk (0.375 mm radius)
    # The dimensions say radius = 3.0, which is 10x larger
    # I'll use the dimensions radius = 3.0 as the actual disk radius
    # The profile radius of 0.375 is likely a different feature or a mistake
    # For a disk, the profile is the circular cross-section
    # The extrude distance is 14.0 mm
    # So the disk has radius 3.0 mm and height 14.0 mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107467_a8afc51d_0000\neg_02\iter_00\generated.step"

    # Build the disk
    # Center at origin, radius = 3.0 mm, extrude 14.0 mm in +Z direction
    result = (
        cq.Workplane("XY")
        .circle(3.0)  # radius from dimensions section
        .extrude(14.0)  # extrude distance from design plan
    )

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
