import cadquery as cq

# Design Plan: Lever Switch - Disk
# Dimensions:
#   - Circle radius: 25.4 mm (from dimensions.profiles[0].radius.value)
#   - Extrude distance: 8.89 mm (from extrude.distance_total.value)
# Note: The profile center_uv is [16.994661, 17.998557] but since we use
#       bbox_min_corner origin convention, we place the circle at (0,0)
#       and the resulting part will be centered accordingly.

# Create a 2D circle with radius 25.4 mm
result = cq.Workplane("XY").circle(25.4)

# Extrude the circle by 8.89 mm along +Z (positive w direction)
result = result.extrude(8.89)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103284_e25015aa_0003\\neg_01/generated.step")
