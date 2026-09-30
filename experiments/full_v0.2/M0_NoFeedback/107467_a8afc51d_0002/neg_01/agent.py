import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 25.0 mm
# The design plan specifies a disk-like part (extruded circle) with:
# - radius: 3.0 mm (from dimensions.profiles[0].radius.value)
# - extrude distance: 25.0 mm (from dimensions.extrude_distance.value)
# - center at origin (0,0,0) in the local frame

# Build the result: a cylinder centered at the origin
result = cq.Workplane("XY").circle(3.0).extrude(25.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\107467_a8afc51d_0002\\neg_01/generated.step")
