import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate/panel)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle profile in UV space has corners:
    #   (121.17356129030935, 31.299551148092803) -> (-0.7464387096940412, 31.299551148092803)
    #   (121.17356129030935, 290.379551148076) -> (-0.7464387096940412, 290.379551148076)
    # The span in U is ~121.92, but the inferred length_u is 1219.2 mm (scale factor 10 from cm->mm).
    # The span in V is ~259.08, inferred width_v is 2590.8 mm.
    # We'll create a rectangle centered at origin with those dimensions, then extrude along w_dir (Y axis).

    # Create the rectangle profile on the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
    # Actually, to match the frame: u along X, v along -Z, w along Y.
    # So the profile lies in the X-Z plane (with v along -Z).
    # We'll create a workplane on the XZ plane, draw rectangle, then extrude along Y.

    length_u = 1219.2  # mm
    width_v = 2590.8   # mm
    extrude_dist = 44.45  # mm

    # Build the rectangle centered at origin, aligned with X and Z axes
    result = (cq.Workplane("XZ")
              .rect(length_u, width_v, centered=True)
              .extrude(extrude_dist))

    # Export to STEP
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
