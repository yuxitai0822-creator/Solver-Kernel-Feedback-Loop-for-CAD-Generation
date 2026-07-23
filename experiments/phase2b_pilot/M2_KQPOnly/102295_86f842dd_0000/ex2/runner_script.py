import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import os

    # Ensure output directory exists
    OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102295_86f842dd_0000\ex2'
    OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')
    os.makedirs(OUT_DIR, exist_ok=True)

    # Parameters from design plan (unit conversion cm_to_mm applied)
    straight_length = 28.0  # mm
    radius = 10.0            # mm
    extrude_distance = 4.0  # mm

    # Build the stadium extrusion
    # A stadium is a rectangle with two semicircular caps on opposite ends.
    # We construct it by extruding a rectangle and then unioning two half-cylinders.

    # 1. Central rectangular section
    rect = (cq.Workplane("XY")
            .rect(straight_length, 2 * radius)
            .extrude(extrude_distance))

    # 2. Left semicircular cap (half cylinder)
    left_cap = (cq.Workplane("XY")
                .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
                .circle(radius)
                .extrude(extrude_distance))

    # Cut the left cap to keep only the left half (y >= 0 in local coords maps to x <= 0 in stadium center coords)
    # The center of the left arc is at x = -straight_length/2. We want the half facing left.
    left_half = (cq.Workplane("XY")
                 .transformed(offset=(-straight_length/2, 0, 0))
                 .rect(radius, 2 * radius)
                 .extrude(extrude_distance))

    left_cap_half = left_cap.cut(left_half)

    # 3. Right semicircular cap (half cylinder)
    right_cap = (cq.Workplane("XY")
                 .transformed(offset=(straight_length/2, 0, 0))
                 .circle(radius)
                 .extrude(extrude_distance))

    # Cut the right cap to keep only the right half (y <= 0 in local coords maps to x >= 0)
    right_half = (cq.Workplane("XY")
                  .transformed(offset=(straight_length/2, 0, 0))
                  .rect(radius, 2 * radius)
                  .extrude(extrude_distance))

    right_cap_half = right_cap.cut(right_half)

    # 4. Union all three parts to form the complete stadium
    result = rect.union(left_cap_half).union(right_cap_half)

    # Export the result to STEP file
    cq.exporters.export(result, OUT_STEP_PATH)

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
