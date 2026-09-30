import cadquery as cq

# Design Plan: Tail Stock Lever - extruded circle (disk)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm

# Create a circle with radius 11.938 mm and extrude it by 12.7 mm
result = (
    cq.Workplane("XY")
    .circle(11.938)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0004\\ex2/generated.step")
