import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
# This gives length_u = 243.84 mm and width_v = 121.92 mm
# Note: The design plan indicates a unit conversion from cm to mm (x10),
# so the actual dimensions in mm are: length = 2438.4 mm, width = 1219.2 mm
# The extrude distance is 12.7 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108412_8de2f9c3_0000\\neg_02/generated.step")
