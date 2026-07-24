import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded stadium (ArmRest v1)
    # Dimensions: straight_length=500.0 mm, radius=50.0 mm, extrude_distance=100.0 mm
    # Note: The plan's profiles use radius=5.0 and straight_length=50.0 in UV space,
    # but the dimensions section says straight_length=500.0, radius=50.0.
    # The UV curves use radius=5.0 and line length 50.0, which would give a small part.
    # To match the expected spans (u=600, v=100, w=100), we scale by 10x.
    # This is consistent with the compiler note "cm_to_mm (x10)".
    # So we build a stadium with straight_length=500, radius=50, extrude=100.

    # Build the stadium profile in the XY plane (u=x, v=y), then extrude along Z (w).
    # Center the shape so that the bounding box spans are as expected.
    # The stadium consists of two semicircles (radius=50) connected by two lines (length=500).
    # Total width (v direction) = 2*radius = 100, total length (u direction) = 500 + 2*radius = 600.

    # We'll create the profile using a workplane and then extrude.

    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(-250, -50)  # start at bottom-left of the straight section
        .threePointArc((0, -100), (250, -50))  # left semicircle (center at (-250,0)? Actually easier: use two arcs)
        # Simpler: use a slot2D or build with lines and arcs.
        # Let's do a proper stadium: start at (-250, -50), line to (250, -50), arc to (250, 50), line to (-250, 50), arc to (-250, -50).
    )

    # Actually, let's rebuild cleanly:
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(-250, -50)
        .lineTo(250, -50)
        .threePointArc((250 + 50, 0), (250, 50))  # right semicircle (center at (250,0))
        .lineTo(-250, 50)
        .threePointArc((-250 - 50, 0), (-250, -50))  # left semicircle (center at (-250,0))
        .close()
        .extrude(100.0)
    )

    # Export
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104453_aba0f2d1_0002\\neg_01/generated.step")

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
