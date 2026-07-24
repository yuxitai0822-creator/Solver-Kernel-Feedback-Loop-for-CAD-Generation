import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions: radius = 25.4 mm, extrude distance = 8.89 mm
# Center in UV plane: (16.994661, 17.998557) - but we place circle at origin for simplicity
# The design plan indicates a single disk with radius 25.4 mm and height 8.89 mm

# Create the disk by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius in mm
    .extrude(8.89)  # height in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0003\\neg_03/generated.step")
