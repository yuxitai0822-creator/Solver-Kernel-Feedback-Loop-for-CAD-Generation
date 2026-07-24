import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle: 27.94 mm in u-direction, 5.08 mm in v-direction
# But note: the dimensions table says length_u = 279.4 mm, width_v = 50.8 mm
# The profile curves show 27.94 and 5.08, which appear to be in cm (converted to mm by factor 10)
# So the actual dimensions are 279.4 mm x 50.8 mm, extruded 19.05 mm

# Build the rectangle in the XY plane (u=x, v=y, w=z)
result = (
    cq.Workplane("XY")
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0007\\neg_01/generated.step")
