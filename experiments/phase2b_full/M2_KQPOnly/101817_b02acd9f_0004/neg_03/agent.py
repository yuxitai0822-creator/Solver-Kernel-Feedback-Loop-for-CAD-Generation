import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a rectangle in UV space with:
# - U direction: [1,0,0] (X axis)
# - V direction: [0,0,-1] (negative Z axis)
# - W direction: [0,1,0] (Y axis)
# The rectangle corners in UV are:
#   (127.82976, -66.34402) to (7.82976, -6.34402)
# This gives length_u = 120.0 and width_v = 60.0 in UV space
# But the dimensions say length_u = 1200.0, width_v = 600.0
# The UV coordinates appear to be scaled by 0.1 (cm to mm conversion factor of 10)
# So we use the explicit dimensions: 1200mm x 600mm x 20mm

# Build the plate centered at origin for simplicity
result = (
    cq.Workplane("XY")
    .rect(1200, 600)
    .extrude(20)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0004\\neg_03/generated.step")
