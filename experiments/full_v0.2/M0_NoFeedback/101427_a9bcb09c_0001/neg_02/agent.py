import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle dimensions: 1980 mm x 600 mm (from outer_length_u, outer_width_v)
# Inner rectangle dimensions: 1930 mm x 550 mm (from inner_length_u, inner_width_v)
# Extrude distance: 25 mm (from extrude_distance)

# Build the outer rectangle
outer = cq.Workplane("XY").rect(1980, 600).extrude(25)

# Build the inner rectangle (to be subtracted)
inner = cq.Workplane("XY").rect(1930, 550).extrude(25)

# Subtract inner from outer to create the frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101427_a9bcb09c_0001\\neg_02/generated.step")
