import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: stadium extrusion
    # Dimensions:
    #   - straight_length: 28.0 mm (inferred from point span)
    #   - radius: 10.0 mm (explicit)
    #   - extrude distance: 4.0 mm
    #
    # The stadium profile consists of two arcs (radius 10) and two straight lines (length 28).
    # The arcs are centered at (1,0) and (3.8,0) in UV space, but these are normalized coordinates.
    # The actual dimensions: radius = 10, straight_length = 28.
    # The total width = 2*radius + straight_length = 20 + 28 = 48 mm.
    # The total height = 2*radius = 20 mm.
    #
    # We build the stadium in the XY plane, then extrude in the Z direction (positive).

    # Create the stadium profile as a wire
    radius = 10.0
    straight = 28.0

    # Center of left arc at (0, 0), right arc at (straight, 0) = (28, 0)
    # The stadium goes from x=0 to x=straight+2*radius = 48, y from -radius to +radius

    # Build the profile using CadQuery's 2D construction
    # We'll create a workplane and draw the stadium
    result = (
        cq.Workplane("XY")
        .center(radius + straight/2, 0)  # center the shape at origin
        .stadium(straight, radius)  # stadium(length, radius) - length is the straight portion
        .extrude(4.0)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102295_86f842dd_0000\neg_03/generated.step")

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
