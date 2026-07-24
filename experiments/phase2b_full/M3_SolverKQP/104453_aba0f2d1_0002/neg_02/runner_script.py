import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded stadium (ArmRest v1)
    # Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
    # Note: The design plan uses a stadium profile with two arcs (radius 5.0) and two lines (length 50.0).
    # However, the dimensions section says straight_length=500.0 and radius=50.0.
    # The profile curves in the plan show radius=5.0 and line length 50.0 (spanning from 0 to 50 in u).
    # This is inconsistent: the curves describe a small stadium (total length 60, width 10),
    # but the dimensions say straight_length=500.0 and radius=50.0 (total length 600, width 100).
    # We follow the explicit dimensions (straight_length=500, radius=50) as they are marked "explicit_dimension"
    # and the curves appear to be scaled incorrectly (possibly a compiler error).
    # The validation intents expect span_u=600, span_v=100, span_w=100, which matches the larger dimensions.

    # Build the stadium profile
    straight_length = 500.0
    radius = 50.0
    extrude_distance = 100.0

    # Create the stadium profile using CadQuery's built-in stadium shape
    # We'll construct it manually: two arcs and two lines
    # Center of left arc at (0,0), right arc at (straight_length, 0)
    # The arcs go from 90 to -90 (top to bottom) for left arc, and -90 to 90 for right arc
    # But the design plan uses 0 to 180 for left arc and 0 to 180 for right arc (different orientation)
    # We'll follow the plan's coordinate system: u along x, v along y

    # Build the wire using edges
    left_arc = cq.Edge.makeCircle(radius, cq.Vector(0, 0), cq.Vector(0, 0, 1), 90.0, -90.0)  # top to bottom
    right_arc = cq.Edge.makeCircle(radius, cq.Vector(straight_length, 0), cq.Vector(0, 0, 1), -90.0, 90.0)  # bottom to top
    bottom_line = cq.Edge.makeLine(cq.Vector(0, -radius), cq.Vector(straight_length, -radius))
    top_line = cq.Edge.makeLine(cq.Vector(straight_length, radius), cq.Vector(0, radius))

    # Combine into a wire
    wire = cq.Wire.assembleEdges([left_arc, bottom_line, right_arc, top_line])

    # Make a face from the wire
    face = cq.Face.makeFromWires(wire)

    # Extrude along z (w direction)
    result = cq.Workplane("XY").placeSketch(cq.Sketch(face)).extrude(extrude_distance)

    # Export
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
