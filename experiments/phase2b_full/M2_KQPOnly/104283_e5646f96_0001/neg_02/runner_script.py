import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Extruded profile with a circular hole
    # The profile consists of an outer shape (rectangle with rounded corners approximated by a circle) and an inner circle (hole).
    # Based on the curves, the outer shape is defined by two vertical lines at x≈0.9188 and x≈3.7174, and a circle at center (2.3181, 1.7491) radius 1.4.
    # The inner hole is a circle at same center with radius 1.25.
    # The extrusion distance is 18.0 mm.

    # Build the outer profile as a rectangle with a circular arc at the top.
    # Actually, the curves describe: left vertical line from (0.9188, 1.7937) to (0.9188, 0.0), bottom horizontal line to (3.8, 0.0), right vertical line from (3.7174, 1.7937) to (3.7174, 0.0), and a circle at (2.3181, 1.7491) radius 1.4.
    # The circle likely connects the tops of the two vertical lines, forming a rounded top.
    # So the outer shape is a rectangle [0.9188, 3.8] x [0.0, 1.7937] with a circular top of radius 1.4.
    # But the circle center y=1.7491, radius 1.4 gives top y≈3.1491, which is higher than 1.7937. This suggests the circle is the top arc, and the vertical lines go up to meet it.
    # Actually, the start_uv of the first line is (0.9188, 1.7937) and end_uv (0.9188, 0.0). The circle center is (2.3181, 1.7491) radius 1.4. The distance from center to left line x=0.9188 is 1.3993 ≈ radius, so the left line touches the circle at (0.9188, 1.7491) approximately. But start_uv y=1.7937 is slightly above center y, so the line goes from a point on the circle down to y=0.
    # Similarly right line at x=3.7174, distance to center = 1.3993 ≈ radius, so it also touches the circle.
    # The bottom is a horizontal line from (0.9188, 0.0) to (3.8, 0.0). Note the right end is at x=3.8, but the right vertical line is at x=3.7174. This suggests the bottom line extends slightly beyond the right vertical line, but the profile is closed by the circle.
    # To simplify, we can construct the outer shape as a rectangle with a circular top, but the exact geometry is tricky.
    # Better: Use the given curves directly: create a wire from the lines and arc, then make a face.

    # However, CadQuery does not easily support arbitrary wire from mixed lines and arcs with precise coordinates.
    # We can approximate by building a 2D sketch with points and arcs.

    # Let's interpret the profile:
    # Outer ring: 4 curves:
    # 1. line from (0.9188335, 1.7936744) to (0.9188335, 0.0)
    # 2. line from (0.9188335, 0.0) to (3.8000001, 0.0)
    # 3. line from (3.7174116, 1.7936744) to (3.7174116, 0.0)  (note: this line goes downward, but the start is at y=1.7937, end at y=0)
    # 4. circle at (2.3181226, 1.7490621) radius 1.4
    # The circle connects the tops of the two vertical lines.
    # So the outer shape is like a 'U' shape with a circular cap.

    # Inner ring: a circle at same center radius 1.25 (hole).

    # We can build this in CadQuery by:
    # - Create a workplane on XY plane.
    # - Draw the outer profile as a closed wire: left line, bottom line, right line, and an arc (the circle segment).
    # - But the circle is a full circle, not an arc. The outer ring uses the circle as the top arc, but the circle is also used in the inner ring? Actually the outer ring's 4th curve is a circle, but it's listed as a circle (full circle). That would close the shape with a circle, but then the vertical lines would be inside? This is ambiguous.

    # Let's re-examine: The outer ring has 4 curves: line, line, line, circle. The circle is the 4th curve, and it starts at (3.7174, 1.7937) and ends at (0.9188, 1.7937) implicitly? Actually a circle defined by center and radius doesn't have start/end in the JSON, but the start_uv/end_uv for the circle are missing? The JSON shows "start_uv" and "end_uv" for the circle? No, for the circle it only has "center_uv" and "radius". So it's a full circle. That would mean the outer ring is a circle plus three lines? That doesn't make a simple closed loop.

    # Given the complexity, I'll approximate the design as a rectangular plate with a circular top and a circular hole.
    # The dimensions: width = 3.8 - 0.9188 = 2.8812 mm, height = 1.7937 mm (straight part), plus the circular top of radius 1.4 mm.
    # But the circle center is at y=1.7491, so the top of the circle is at y=3.1491. The vertical lines go up to y=1.7937, which is slightly above the center. So the circle extends above the lines.

    # A simpler interpretation: The outer shape is a rectangle with a circular hole? No, the inner ring is a hole.

    # Let's look at the dimensions in the plan: line_lengths: 17.936744, 28.811665, 17.936744 (these are in mm? Actually the unit is mm, but the values are large: 17.9 mm, 28.8 mm, 17.9 mm. The coordinates are around 0.9 to 3.8, so these lengths are scaled? Wait, the plan says unit_conversion_applied: cm_to_mm (x10). So the original coordinates were in cm, multiplied by 10 to get mm. So the coordinates in the plan are already in mm. So 0.9188 mm is very small. But the line lengths are 17.9 mm, which is much larger. This suggests the profile is actually much larger than the coordinates indicate. Possibly the coordinates are in a local UV space, not in mm? The plan says unit is mm, but the line lengths are inferred from point span, so they might be the actual lengths in mm.

    # Given the confusion, I'll create a simple rectangular block with a circular hole, matching the approximate dimensions.
    # The extrude distance is 18.0 mm.
    # The outer profile: width ~ 2.88 mm (from 0.9188 to 3.8), height ~ 1.79 mm (from 0 to 1.7937), plus a circular top of radius 1.4 mm.
    # But the line lengths suggest the vertical lines are 17.9 mm long, which is much larger than 1.79. So maybe the coordinates are not in mm? The unit is mm, but the line lengths are 17.9, so the vertical lines are 17.9 mm long. That means the y-coordinate range is about 17.9 mm, not 1.79. The start_uv y=1.7937 and end_uv y=0.0 gives length 1.7937, not 17.9. So there's inconsistency.

    # I'll trust the line_lengths: 17.936744 mm for the vertical lines. So the vertical lines are about 17.94 mm long. The bottom line is 28.81 mm long. The circle radius is 14.0 mm (from circle_radii value 14.0). So the profile is much larger: width ~28.8 mm, height ~17.9 mm, with a circular top of radius 14 mm.

    # So the outer shape: left vertical line from (x=0.9188, y=17.9367) down to (x=0.9188, y=0), bottom horizontal from (0.9188, 0) to (29.7304, 0) (since 0.9188+28.8117=29.7305), right vertical from (x=29.7305? Actually the right line x=3.7174? That's too small. The coordinates in the curves are likely in a local UV space, not the actual mm. The line_lengths give the actual mm lengths.

    # Given the difficulty of reconstructing the exact shape from the UV coordinates, I'll create a simplified version that matches the key features: a rectangular plate with a circular top (like a semicircular top) and a circular hole.

    # Let's define the outer profile as a rectangle of width 28.8 mm and height 17.9 mm, with a circular arc of radius 14 mm on top.
    # The center of the arc is at (width/2, height) = (14.4, 17.9), but the arc radius is 14, so the arc extends from x=0.4 to x=28.4 at y=17.9+? Actually the arc center at (14.4, 17.9) with radius 14 gives top at y=31.9.

    # Alternatively, the circle radius 14 mm and the vertical lines are 17.9 mm long, so the circle center is at y=17.9? The line_lengths say vertical lines are 17.9367, so the lines go from y=0 to y=17.9367. The circle center is at y=1.7491 in UV, but in mm it should be around y=17.9? Not clear.

    # I'll make a pragmatic decision: create a rectangular block of size 28.8 mm x 17.9 mm x 18.0 mm, then add a cylindrical boss on top? No, the profile is extruded.

    # Actually, the design plan shows two profiles: one outer ring (with a circle) and one inner ring (hole). The outer ring has a circle of radius 14 mm, and the inner hole has radius 12.5 mm (1.25 * 10? Actually radius 1.25 in UV, but circle_radii value is 14.0 for outer, and inner radius is 1.25, but the dimensions list only one circle_radii of 14.0. The inner hole radius is 1.25, which is 12.5 mm after cm_to_mm? The conversion is x10, so 1.25 cm = 12.5 mm. So inner hole radius is 12.5 mm.

    # So the part is: a plate with a large circular top (radius 14 mm) and a concentric circular hole (radius 12.5 mm). The plate has straight sides and a flat bottom.

    # Let's build it:
    # - Create a workplane.
    # - Draw the outer profile: start at (0, 0), go right 28.8 mm, go up 17.9 mm, then a circular arc of radius 14 mm to the left side, then back down to (0,0).
    # - But the arc center should be at (14.4, 17.9) and radius 14, so the arc goes from (28.8, 17.9) to (0, 17.9) with center at (14.4, 17.9). That's a semicircle of radius 14.4? Actually the distance from center to (28.8, 17.9) is 14.4, not 14. So radius 14 would not reach the corners. Let's adjust: the width is 28.8, so half-width is 14.4. If the arc radius is 14, then the arc will not reach the sides. So the vertical lines must extend above the center? The circle center is at y=1.7491 in UV, which is near the top of the vertical lines (y=1.7937). So the circle center is slightly below the top of the vertical lines. In mm, the vertical lines are 17.9 mm tall, so the circle center is at y=17.9 - (1.7937-1.7491)*? Not sure.

    # Given the time, I'll create a simpler shape: a rectangular block with a circular hole, ignoring the rounded top. The validation intents expect 2 cylindrical faces (outer and inner), 5 plane faces, and 1 through void. A rectangular block with a through hole will have 6 plane faces (if no rounded top) and 2 cylindrical faces, which matches the expected surface type distribution (5 planes + 2 cylinders). But the expected plane count is 5, not 6. So one plane is missing, likely because the top is curved (cylinder). So the top face is a cylindrical surface, not a plane. So the outer shape has a cylindrical top.

    # So the outer profile is a rectangle with a circular arc top, and the inner is a circle.

    # Let's construct it step by step:
    # 1. Create a rectangle of width 28.8 mm and height 17.9 mm.
    # 2. Create a circle of radius 14 mm centered at (14.4, 17.9).
    # 3. Combine them to form the outer shape: the union of the rectangle and the circle? Actually the circle sits on top of the rectangle, so the outer shape is the union of the rectangle and the circle, but the circle's bottom half is inside the rectangle. The resulting shape is a rectangle with a semicircular top.
    # 4. Subtract the inner circle (radius 12.5 mm) centered at (14.4, 17.9).

    # But the inner circle is concentric with the outer circle, so the hole is centered at the same point.

    # Let's implement this.

    import cadquery as cq

    # Parameters
    width = 28.811665  # from line_lengths bottom
    height = 17.936744  # from line_lengths vertical
    outer_radius = 14.0
    inner_radius = 12.5  # 1.25 cm * 10 = 12.5 mm
    extrude_dist = 18.0

    # Build the outer profile
    # Start with a rectangle
    rect = cq.Workplane("XY").rect(width, height)
    # Add a circle at the top center
    circle_outer = cq.Workplane("XY").circle(outer_radius).translate((width/2, height, 0))
    # Combine: union of rectangle and circle
    # But we need to create a single closed wire. We can use the union of the two shapes and then take the outer wire.
    # However, CadQuery's workplane operations are easier with 2D boolean.
    # Let's create a 2D sketch by combining the rectangle and the circle.

    # Alternative: Use the CadQuery sketch() method with a list of edges.
    # Or, we can create the profile by drawing the outline manually.

    # Since the rectangle and circle overlap, the union will have a smooth top.
    # We can do:
    # - Create a workplane
    # - Draw the rectangle
    # - Add the circle
    # - Fuse them
    # - Then cut the inner circle

    # But the rectangle and circle union will have a flat top where the circle extends above? Actually the circle center is at y=height, so the top of the circle is at y=height+radius = 31.9 mm. The rectangle top is at y=height=17.9 mm. So the union will be a rectangle with a semicircular bump on top.

    # Let's do it:

    result = (
        cq.Workplane("XY")
        .rect(width, height)
        .union(cq.Workplane("XY").circle(outer_radius).translate((width/2, height, 0)))
        .extrude(extrude_dist)
    )

    # Now cut the inner hole
    result = (
        result
        .faces(">Z")  # top face
        .workplane()
        .circle(inner_radius)
        .cutThruAll()
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\104283_e5646f96_0001\neg_02/generated.step")

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
