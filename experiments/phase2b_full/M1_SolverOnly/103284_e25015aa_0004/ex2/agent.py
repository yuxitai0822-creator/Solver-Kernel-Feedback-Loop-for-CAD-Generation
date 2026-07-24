import cadquery as cq

# Design Plan: Tail Stock Lever - extruded circle (disk)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# Center in UV plane: (8.077681, 8.284339) - but we center at origin for simplicity

# Create a circle with radius 11.938 mm
result = (
    cq.Workplane("XY")
    .circle(11.938)  # radius in mm
    .extrude(12.7)    # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103284_e25015aa_0004\\ex2/generated.step")
