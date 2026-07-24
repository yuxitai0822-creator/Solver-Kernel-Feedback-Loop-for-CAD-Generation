import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with an extruded rectangle
# The profile is defined in a local frame where:
#   u_dir = [1,0,0] (X axis)
#   v_dir = [0,0,-1] (negative Z axis)
#   w_dir = [0,1,0] (Y axis)
# The rectangle corners in UV space are:
#   (127.82976, -66.34402) to (7.82976, -6.34402)
# This gives length_u = 120.0 and width_v = 60.0 in the original units (cm)
# After unit conversion (cm_to_mm x10): length = 1200mm, width = 600mm
# Extrude distance = 20.0mm in +w direction (Y axis)

# Build the rectangle profile in the XY plane (since we'll work in world coords)
# The plate will be centered at origin for simplicity

result = (
    cq.Workplane("XY")
    .rect(1200.0, 600.0)
    .extrude(20.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0004\\neg_01/generated.step")
