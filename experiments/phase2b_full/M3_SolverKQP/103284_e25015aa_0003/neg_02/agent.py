import cadquery as cq

# Design Plan: Lever Switch - Disk
# Dimensions:
#   - Circle radius: 25.4 mm (from dimensions.profiles[0].radius.value)
#   - Extrude distance: 8.89 mm (from dimensions.extrude_distance.value)
#   - Center UV: (16.994661, 17.998557) - used for positioning in sketch plane
# Note: The design plan indicates a unit conversion from cm to mm (x10).
# The radius in the plan is 25.4 mm, extrude is 8.89 mm.

# Create the disk by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius in mm
    .extrude(8.89)  # height in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0003\\neg_02/generated.step")
