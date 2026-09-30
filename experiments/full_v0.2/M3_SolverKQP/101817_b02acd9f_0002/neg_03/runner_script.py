import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: 42.4 x 42.4 mm (from u/v spans)
    # Inner rectangle: 40.0 x 40.0 mm (from inner_length_u/inner_width_v)
    # Extrude distance: 1120.0 mm along -w direction (which is -x in world)
    # The frame's u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So in world: u = -z, v = y, w = x
    # The profile is in the uv-plane (y-z plane), extruded along w (x)
    # Outer ring: u from -6.12 to -1.88, v from 10.88 to 15.12
    # Inner ring: u from -6.0 to -2.0, v from 11.0 to 15.0
    # Note: u is along -z, v is along y. So in world: z = -u, y = v
    # Outer: z from 1.88 to 6.12, y from 10.88 to 15.12
    # Inner: z from 2.0 to 6.0, y from 11.0 to 15.0
    # Extrude along x from 0 to -1120 (since direction is -w = -x)

    # Build the outer rectangle
    outer = (
        cq.Workplane("YZ")
        .center(0, 0)
        .rect(42.4, 42.4)
        .extrude(1120.0)
    )

    # Build the inner rectangle (to be subtracted)
    inner = (
        cq.Workplane("YZ")
        .center(0, 0)
        .rect(40.0, 40.0)
        .extrude(1120.0)
    )

    # Subtract inner from outer to create hollow frame
    result = outer.cut(inner)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0002\\neg_03/generated.step")

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
