import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
# which corresponds to length_u = 243.84 mm and width_v = 121.92 mm
# Note: The design plan values are in mm, but the UV coordinates appear to be in cm
# (2438.4 mm = 243.84 cm, 1219.2 mm = 121.92 cm)
# The UV coordinates given are: 121.92, -60.96 etc. which match the cm values
# So we use the UV coordinates directly as they are already in the correct unit

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(243.84, 121.92)  # width = 243.84 mm, height = 121.92 mm
    .extrude(12.7)  # extrude by 12.7 mm in +Z direction
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108412_8de2f9c3_0000\\neg_02/generated.step")
