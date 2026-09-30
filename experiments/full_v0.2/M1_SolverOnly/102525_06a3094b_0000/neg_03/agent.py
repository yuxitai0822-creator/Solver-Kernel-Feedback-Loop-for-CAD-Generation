import cadquery as cq

# Create a rectangular prism based on the design plan
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# The profile is centered at origin in the uv-plane, extruded in +w direction

# Create the rectangle profile centered at origin
# The rectangle spans from -1.95 to 1.95 in u (length 3.9)
# and from -2.45 to 2.45 in v (width 4.9)
result = (
    cq.Workplane("XY")
    .rect(3.9, 4.9)
    .extrude(1.55)
)

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102525_06a3094b_0000\\neg_03/generated.step")
