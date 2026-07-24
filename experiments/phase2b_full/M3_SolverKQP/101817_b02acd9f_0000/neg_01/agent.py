import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 40 x 40 mm (in u-v plane)
# Inner rectangle: 37.6 x 37.6 mm (wall thickness ~1.2 mm)
# Extrude along w direction: 780 mm

# Define points for outer rectangle (u, v coordinates)
# Outer rectangle corners: (10, -7), (6, -7), (6, -3), (10, -3)
# This gives a 4x4 square? Let's check: u from 6 to 10 => width 4, v from -7 to -3 => height 4
# But dimensions say outer_length_u = 40, outer_width_v = 40
# The coordinates are in a local frame, need to scale or interpret correctly.
# The design plan says unit_conversion_applied: cm_to_mm (x10)
# So the coordinates in the plan are in cm, we need to multiply by 10 to get mm.
# Let's scale all coordinates by 10.

scale = 10.0

# Outer rectangle (scaled to mm)
outer_pts = [
    (10.0 * scale, -7.0 * scale),
    (6.0 * scale, -7.0 * scale),
    (6.0 * scale, -3.0 * scale),
    (10.0 * scale, -3.0 * scale),
]

# Inner rectangle (scaled to mm)
inner_pts = [
    (6.12 * scale, -6.88 * scale),
    (6.12 * scale, -3.12 * scale),
    (9.88 * scale, -3.12 * scale),
    (9.88 * scale, -6.88 * scale),
]

# Build the profile in the XY plane (u=x, v=y, w=z)
# Outer profile
outer_wire = cq.Workplane("XY").polyline(outer_pts).close()

# Inner profile
inner_wire = cq.Workplane("XY").polyline(inner_pts).close()

# Combine: create a face with a hole
# We need to create the outer face first, then cut the inner
result = (
    cq.Workplane("XY")
    .polyline(outer_pts).close()
    .extrude(780.0)  # extrude along +z (w direction)
)

# Now cut the inner hole through the entire extrusion
# Create the inner profile as a separate extrusion and subtract
inner_solid = (
    cq.Workplane("XY")
    .polyline(inner_pts).close()
    .extrude(780.0)
)

result = result.cut(inner_solid)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0000\\neg_01/generated.step")
