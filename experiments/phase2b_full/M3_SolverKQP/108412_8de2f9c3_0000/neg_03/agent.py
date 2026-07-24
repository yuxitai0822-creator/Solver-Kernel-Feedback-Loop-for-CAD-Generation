import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The rectangle is centered at origin with corners at (±121.92, ±60.96) in UV space
# Note: The design plan uses cm->mm conversion (x10), so the actual dimensions are:
#   length_u = 2438.4 mm (along X)
#   width_v = 1219.2 mm (along Y)
#   thickness = 12.7 mm (along Z)

# Create the rectangle profile centered at origin
# The UV coordinates from the plan: corners at (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
# These are in cm originally, converted to mm by multiplying by 10
# So actual corners: (1219.2, -609.6), (1219.2, 609.6), (-1219.2, 609.6), (-1219.2, -609.6)

# Build the plate
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(2438.4, 1219.2)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108412_8de2f9c3_0000\neg_03/generated.step")
