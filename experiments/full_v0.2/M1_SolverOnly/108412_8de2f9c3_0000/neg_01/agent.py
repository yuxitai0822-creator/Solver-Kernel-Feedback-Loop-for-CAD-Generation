import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
# This gives length_u = 243.84 mm and width_v = 121.92 mm
# Note: The design plan dimensions show 2438.4 and 1219.2, but the UV coordinates
# are in cm (converted to mm by factor 10). The actual UV coordinates in mm are:
# -121.92 to 121.92 = 243.84 mm (length_u)
# -60.96 to 60.96 = 121.92 mm (width_v)
# The extrude distance is 12.7 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(243.84, 121.92)  # width = 243.84, height = 121.92
    .extrude(12.7)  # extrude by 12.7 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108412_8de2f9c3_0000\\neg_01/generated.step")
