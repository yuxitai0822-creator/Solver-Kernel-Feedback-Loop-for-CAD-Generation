import cadquery as cq

# Create a rectangular profile in the XY plane (u = X, v = Z, w = Y)
# Dimensions from design plan:
#   length_u = 279.4 mm (X direction)
#   width_v = 50.8 mm (Z direction)
#   extrude distance = 19.05 mm (Y direction, +w)

# The profile is a rectangle with corners at (0,0), (279.4,0), (279.4,50.8), (0,50.8)
# in the UV plane. We map U->X, V->Z, extrude along Y (+w).

result = (
    cq.Workplane("XY")
    .rect(279.4, 50.8, centered=False)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0007\\ex2/generated.step")
