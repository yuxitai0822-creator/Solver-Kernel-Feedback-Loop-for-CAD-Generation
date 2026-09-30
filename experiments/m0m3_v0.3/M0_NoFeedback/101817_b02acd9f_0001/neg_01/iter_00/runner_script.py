import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: horizontal leg 1
    # Extruded rectangular frame with outer 40x40 mm and inner 37.6x37.6 mm
    # Extrude distance: 520.0 mm (from design plan, not the perturbed 780.0)
    # The previous script used 780.0 mm (perturbed value) - correcting to 520.0 mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0001\neg_01\iter_00\generated.step"

    # Create workplane
    wp = cq.Workplane("XY")

    # Outer rectangle: 40x40 mm, centered at origin
    # From design plan: outer_length_u=40.0, outer_width_v=40.0
    # The profile curves show outer corners at (-4.0, 4.0), (0.0, 4.0), (-4.0, 0.0), (0.0, 0.0)
    # This is a 4x4 square in UV space, but dimensions say 40x40 mm
    # The UV coordinates are scaled by 10 (cm to mm conversion factor)
    # So outer rectangle is 40x40 mm centered at (-20, 20) in mm

    # Actually, let's re-examine: the curves show start_uv and end_uv values
    # Outer ring curves:
    # (-4.0, 4.0) -> (0.0, 4.0)
    # (-4.0, 0.0) -> (-4.0, 4.0)
    # (0.0, 0.0) -> (-4.0, 0.0)
    # (0.0, 4.0) -> (0.0, 0.0)
    # This forms a 4x4 square from (-4,0) to (0,4) in UV space
    # With cm->mm conversion (x10), this is 40x40 mm from (-40,0) to (0,40)

    # Inner ring curves:
    # (-0.12, 3.88) -> (-0.12, 0.12)
    # (-0.12, 0.12) -> (-3.88, 0.12)
    # (-3.88, 0.12) -> (-3.88, 3.88)
    # (-3.88, 3.88) -> (-0.12, 3.88)
    # This forms a 3.76x3.76 square from (-3.88,0.12) to (-0.12,3.88) in UV space
    # With cm->mm conversion (x10), this is 37.6x37.6 mm from (-38.8,1.2) to (-1.2,38.8)

    # Build the outer rectangle
    # Center at (-20, 20) with size 40x40
    outer = wp.moveTo(-20, 20).rect(40, 40, centered=True)

    # Build the inner rectangle (hole)
    # Center at (-20, 20) with size 37.6x37.6
    inner = cq.Workplane("XY").moveTo(-20, 20).rect(37.6, 37.6, centered=True)

    # Create the profile by subtracting inner from outer
    # We need to combine them into a single wire
    profile = outer.union(inner)

    # Actually, for a proper cut, we should create the outer as a face, then cut the inner
    # Let's use a different approach: create the outer rectangle, extrude, then cut inner

    # Create outer rectangle face
    outer_face = cq.Workplane("XY").moveTo(-20, 20).rect(40, 40, centered=True).extrude(520.0)

    # Create inner rectangle as a cutting tool
    inner_cut = cq.Workplane("XY").moveTo(-20, 20).rect(37.6, 37.6, centered=True).extrude(520.0)

    # Cut the inner hole
    result = outer_face.cut(inner_cut)

    # Export
    importers.export(result, OUT_STEP_PATH)

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
