import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 209.55 mm and width_v = 57.912 mm
# The extrusion distance is 19.05 mm in the +w direction

# Create the rectangle profile on the XY plane (u=x, v=y, w=z)
result = (
    cq.Workplane("XY")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0009\\neg_03/generated.step")
