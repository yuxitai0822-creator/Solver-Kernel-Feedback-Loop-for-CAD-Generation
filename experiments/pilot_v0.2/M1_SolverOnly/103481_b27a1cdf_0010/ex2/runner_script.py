import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Build a rectangular prism: 101.6 x 101.6 x 38.1 mm
    # The profile is centered at origin in the XY plane, spanning from -5.08 to 5.08 in both X and Y.
    # Wait, the design plan says the rectangle spans from -5.08 to 5.08, which is 10.16 x 10.16.
    # But the dimensions specify length_u = 101.6 and width_v = 101.6.
    # The compiler notes indicate a unit conversion of cm_to_mm (x10) was applied.
    # So the original sketch coordinates (5.08 cm) were converted to 50.8 mm.
    # However, the design plan still lists the UV coordinates as 5.08 (which must be interpreted as 50.8 mm after conversion).
    # To match the validation intents (span_u = 101.6, span_v = 101.6), we use the explicit dimensions.

    length_u = 101.6
    width_v = 101.6
    extrude_distance = 38.1

    result = cq.Workplane("XY").rect(length_u, width_v).extrude(extrude_distance)

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
