import cadquery as cq

# Design Plan: Lever Switch - Disk
# Dimensions:
#   Radius: 25.4 mm (from dimensions.profiles[0].radius.value)
#   Extrude distance: 8.89 mm (from extrude.distance_total.value)
#   Center UV: (16.994661, 17.998557) - used for positioning in sketch plane
#   Note: The profile circle center_uv is (16.994661, 17.998557) but since we are
#         creating a single disk centered at origin for simplicity, we place the
#         circle at (0,0) and then translate if needed. However, the design plan
#         indicates a disk with radius 25.4, so we create a cylinder of radius 25.4
#         and height 8.89.

# Create the disk (cylinder) centered at origin
result = cq.Workplane("XY").circle(25.4).extrude(8.89)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103284_e25015aa_0003\\neg_01/generated.step")
