import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
# This gives length_u = 243.84 mm and width_v = 121.92 mm
# Note: The design plan dimensions show 2438.4 and 1219.2, but the UV coordinates
# are in cm (as noted in compiler_notes: cm_to_mm x10). So we use the UV values directly.

# Create the rectangle profile
result = (cq.Workplane("XY")
    .center(0, 0)
    .rect(243.84, 121.92)  # width = 243.84 (2*121.92), height = 121.92 (2*60.96)
    .extrude(12.7)  # extrude distance from design plan
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108412_8de2f9c3_0000\\neg_03/generated.step")
