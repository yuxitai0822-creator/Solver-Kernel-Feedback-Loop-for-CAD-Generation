import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a rectangle in UV space with:
#   u: 7.82976 to 127.82976 (width = 120.0? but dimensions say 1200.0)
#   v: -66.344 to -6.344 (height = 60.0? but dimensions say 600.0)
# The dimensions in the plan explicitly state length_u=1200.0, width_v=600.0, extrude=20.0
# The UV coordinates appear to be scaled by 0.1 (possibly due to cm->mm conversion factor of 10)
# We use the explicit dimensions from the plan.

# Build the plate centered at origin for simplicity, then translate to match UV origin
# The UV origin is at (7.82976, -66.344) in the plan's coordinate frame
# But since we're using explicit dimensions, we'll create the plate with correct size

result = (
    cq.Workplane("XY")
    .rect(1200.0, 600.0)
    .extrude(20.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0004\\neg_02/generated.step")
