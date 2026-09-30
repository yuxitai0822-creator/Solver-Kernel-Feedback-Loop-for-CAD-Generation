import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0001\neg_01\iter_01\generated.step"

    # Design Plan dimensions (in mm, after cm->mm conversion x10):
    # Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
    # Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    # Extrude distance: 25.0 mm (original was 2.5 cm = 25 mm, perturbed to 3.75 cm = 37.5 mm)
    # Per the perturbation description: operator=E2_extrude_depth; original=2.5; perturbed=3.75
    # So we use 37.5 mm as the extrude depth.

    EXTENT_TOTAL_MM = 37.5  # Perturbed value: 3.75 cm = 37.5 mm

    # Build the outer rectangle
    outer = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(198.0, 60.0, centered=True)

    # Build the inner rectangle for the hole
    inner = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(193.0, 55.0, centered=True)

    # Extrude the outer rectangle
    result = outer.extrude(EXTENT_TOTAL_MM)

    # Cut the inner hole
    cut_prism = inner.extrude(EXTENT_TOTAL_MM * 1.5)
    result = result.cut(cut_prism)

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
