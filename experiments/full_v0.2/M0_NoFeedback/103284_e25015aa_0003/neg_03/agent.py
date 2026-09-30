import cadquery as cq

# Design Plan: Lever Switch - Disk
# Dimensions:
#   Radius: 25.4 mm (from dimensions.profiles[0].radius.value)
#   Extrude distance: 8.89 mm (from extrude.distance_total.value)
#   Center UV: (16.994661, 17.998557) - used for positioning in sketch plane
#
# The design describes a single extruded circle (disk) with:
#   - Circle center at (16.994661, 17.998557) in the sketch plane
#   - Radius 25.4 mm
#   - Extruded 8.89 mm in the +w direction (which is +z in world coordinates)
#
# Note: The center_uv coordinates are in the sketch plane (u,v).
# Since we are creating a simple disk, we place the circle at the given center
# and extrude. The resulting part will have bounding box spans:
#   u: 50.8 mm (diameter)
#   v: 50.8 mm (diameter)
#   w: 8.89 mm (extrude height)

# Create the workplane (XY plane, which corresponds to u-v plane)
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius 25.4 mm
    .extrude(8.89)  # extrude 8.89 mm in +z direction
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103284_e25015aa_0003\\neg_03/generated.step")
