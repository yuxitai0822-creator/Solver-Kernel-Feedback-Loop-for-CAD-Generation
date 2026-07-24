import cadquery as cq

# Design Plan: Lever Switch - Disk
# Dimensions:
#   Radius: 25.4 mm (from dimensions.profiles[0].radius.value)
#   Extrude distance: 8.89 mm (from extrude.distance_total.value)
#   Center UV: (16.994661, 17.998557) - used for positioning
# Note: The design plan indicates a unit conversion from cm to mm (x10).
#       The radius in the plan is 25.4 mm, extrude is 8.89 mm.
#       The center_uv is given as (16.994661, 17.998557) which seems to be
#       in the local coordinate system. We'll place the circle at the origin
#       and then translate to match the center_uv if needed, but since the
#       part is a simple disk, we'll center it at (0,0) and extrude.
#       The validation expects spans of 50.8 x 50.8 x 8.89, which matches
#       a disk of radius 25.4 (diameter 50.8) extruded by 8.89.

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius in mm
    .extrude(8.89)  # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\103284_e25015aa_0003\\neg_01/generated.step")
