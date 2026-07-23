import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # SOIC-8 package body: rectangular prism
    # Dimensions from design plan (after cm->mm conversion):
    #   length_u (along X) = 3.9 mm
    #   width_v (along Z) = 4.9 mm
    #   extrude_distance (along Y) = 1.55 mm

    # The design plan specifies the local frame as:
    #   u_dir = [1, 0, 0]  (X)
    #   v_dir = [0, 0, -1] (Z)
    #   w_dir = [0, 1, 0]  (Y)
    # The profile is drawn in the u-v plane (XZ), and extruded along +w (+Y).
    # Origin convention: bbox_min_corner.

    # Profile rectangle in XZ plane:
    #   u ranges from -0.195 to 0.195 -> span = 0.39 cm = 3.9 mm
    #   v ranges from -0.245 to 0.245 -> span = 0.49 cm = 4.9 mm
    # Since v_dir is -Z, the v coordinate maps to -Z.
    #   v = -0.245 -> Z = 0.245 (max Z)
    #   v = 0.245  -> Z = -0.245 (min Z)
    # To place bbox_min_corner at origin (X=0, Y=0, Z=0):
    #   shift X by +0.195 (from -0.195 to 0)
    #   shift Z by +0.245 (from -0.245 to 0)

    result = (
        cq.Workplane("XZ")
        .transformed(offset=(0.195, 0, 0.245))
        .rect(3.9, 4.9)
        .extrude(1.55)
    )

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
