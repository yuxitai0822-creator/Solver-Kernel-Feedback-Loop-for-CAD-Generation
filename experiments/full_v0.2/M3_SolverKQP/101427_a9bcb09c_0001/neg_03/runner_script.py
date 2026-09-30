import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangular frame
    # Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
    # Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    # Extrude in +w direction by 25.0 mm

    # Create the outer rectangle
    outer = cq.Workplane("XY").rect(198.0, 60.0).extrude(25.0)

    # Create the inner rectangle (to be subtracted)
    inner = cq.Workplane("XY").rect(193.0, 55.0).extrude(25.0)

    # Position inner rectangle centered within outer
    # Outer center: (96.5, 27.5)  (since rect centers at origin by default, we need to shift)
    # Actually, using rect() centers at origin, so we need to position properly.
    # Better approach: build the frame as a single sketch with two rectangles.

    # Let's rebuild using a single workplane with two rectangles (outer and inner)
    result = (
        cq.Workplane("XY")
        .rect(198.0, 60.0)  # outer: u from -99 to 99, v from -30 to 30
        .extrude(25.0)
    )

    # Now cut the inner rectangle
    result = (
        result
        .faces(">Z")
        .workplane()
        .rect(193.0, 55.0)
        .cutThruAll()
    )

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
