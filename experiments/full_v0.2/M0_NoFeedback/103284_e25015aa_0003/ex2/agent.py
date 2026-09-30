import cadquery as cq

# Design Plan: Lever Switch - disk with extruded circle
# Dimensions: radius 25.4 mm, extrude distance 8.89 mm
# Center at (16.994661, 17.998557) in UV plane

# Create a circle profile and extrude it
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius from design plan
    .extrude(8.89)  # extrude distance from design plan
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103284_e25015aa_0003\\ex2/generated.step")
