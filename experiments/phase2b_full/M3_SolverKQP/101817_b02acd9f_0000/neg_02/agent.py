import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer dimensions: 40mm x 40mm (from outer_length_u and outer_width_v)
# Inner dimensions: 37.6mm x 37.6mm (from inner_length_u and inner_width_v)
# Extrude distance: 780mm along the w direction (which is +y in world coordinates)

# Build the outer rectangle (40x40)
outer = cq.Workplane("XY").rect(40, 40).extrude(780)

# Build the inner rectangle (37.6x37.6) to cut out
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(780)

# Subtract inner from outer to create the frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0000\\neg_02/generated.step")
