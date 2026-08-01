import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Constants from design plan
    OUTER_LENGTH = 500.0  # mm (u direction)
    OUTER_WIDTH = 300.0   # mm (v direction)
    INNER_LENGTH = 400.0  # mm (u direction)
    INNER_WIDTH = 200.0   # mm (v direction)
    EXTRUDE_DISTANCE = 500.0  # mm (w direction)

    # Build the rectangular frame profile
    # Outer rectangle: 500 x 300 mm
    # Inner rectangle: 400 x 200 mm, offset 50 mm from edges
    # (outer - inner)/2 = (500-400)/2 = 50 in u, (300-200)/2 = 50 in v

    # Create workplane on XY plane
    wp = cq.Workplane("XY")

    # Draw outer rectangle centered at origin
    # Outer: width=500 (x), height=300 (y)
    outer = wp.moveTo(0, 0).rect(OUTER_LENGTH, OUTER_WIDTH, centered=True)

    # Draw inner rectangle (cutout) centered at origin
    # Inner: width=400 (x), height=200 (y)
    inner = wp.moveTo(0, 0).rect(INNER_LENGTH, INNER_WIDTH, centered=True)

    # Create the frame by extruding outer and subtracting inner
    # First extrude the outer rectangle
    frame = outer.extrude(EXTRUDE_DISTANCE)

    # Create the inner cutting prism
    cut_prism = inner.extrude(EXTRUDE_DISTANCE)

    # Subtract inner from outer to create hollow frame
    result = frame.cut(cut_prism)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0006\neg_02\iter_02/generated.step"
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
