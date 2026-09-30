import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
# But the actual dimensions are length_u = 2438.4 mm and width_v = 1219.2 mm
# The UV coordinates given are half-extents: 121.92 * 20 = 2438.4, 60.96 * 20 = 1219.2
# So the UV coordinates are in cm (converted to mm by factor 10? Actually 121.92*20 = 2438.4)
# Let's use the explicit dimensions from the plan: 2438.4 x 1219.2 mm

# Create the rectangle centered at origin
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108412_8de2f9c3_0000\\neg_02/generated.step")
