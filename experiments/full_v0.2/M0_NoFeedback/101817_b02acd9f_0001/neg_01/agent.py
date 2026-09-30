import cadquery as cq

# Design Plan: extruded rectangular frame (horizontal leg 1)
# Outer profile: 40x40 mm square, inner profile: 37.6x37.6 mm square (wall thickness 1.2 mm)
# Extrude 520 mm along +w (z-axis)

# Build the outer rectangle (centered at origin, but plan uses bbox_min_corner convention)
# The plan's uv coordinates: outer from (-4,4) to (0,4) etc. in cm? Actually unit is mm, but values are small.
# The plan says unit_conversion_applied: cm_to_mm (x10). So original cm values were multiplied by 10.
# Outer: u from -40 to 0, v from 0 to 40? Wait: start_uv [-4,4] to [0,4] in cm -> mm: [-40,40] to [0,40]
# But the dimensions say outer_length_u=40, outer_width_v=40. So the square is 40x40.
# The uv coordinates: outer ring goes from (-40,40) to (0,40) to (0,0) to (-40,0) back to (-40,40).
# That's a 40x40 square with lower-left at (-40,0) in uv space.
# Inner ring: from (-1.2, 38.8) to (-1.2, 1.2) to (-38.8, 1.2) to (-38.8, 38.8) back.
# That's a 37.6x37.6 square (wall thickness 1.2 mm).

# We'll build the profile on the XY plane (u=x, v=y) and extrude along Z.

# Outer rectangle
outer = cq.Workplane("XY").moveTo(-40, 0).lineTo(0, 0).lineTo(0, 40).lineTo(-40, 40).close()

# Inner rectangle (cutout)
inner = cq.Workplane("XY").moveTo(-38.8, 1.2).lineTo(-1.2, 1.2).lineTo(-1.2, 38.8).lineTo(-38.8, 38.8).close()

# Combine: outer polygon with inner hole
# Use polyline approach: create a single wire with outer and inner
# CadQuery approach: create outer rect, then cut inner rect

# Build base plate with outer profile, extrude, then cut inner
result = (
    cq.Workplane("XY")
    .moveTo(-40, 0)
    .lineTo(0, 0)
    .lineTo(0, 40)
    .lineTo(-40, 40)
    .close()
    .extrude(520.0)  # extrude along +Z
    .faces(">Z")  # select top face
    .workplane()
    .moveTo(-38.8, 1.2)
    .lineTo(-1.2, 1.2)
    .lineTo(-1.2, 38.8)
    .lineTo(-38.8, 38.8)
    .close()
    .cutThruAll()  # cut through the entire body
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0001\\neg_01/generated.step")
