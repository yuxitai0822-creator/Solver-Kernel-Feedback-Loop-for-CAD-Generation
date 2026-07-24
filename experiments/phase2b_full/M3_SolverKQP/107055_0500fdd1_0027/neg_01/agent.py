import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer_radius=3.49, inner_radius=2.0, thickness=0.36

# Create the washer by extruding an annulus (circle with hole)
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer circle
    .circle(2.0)   # inner circle (hole)
    .extrude(0.36) # extrude along +Z
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107055_0500fdd1_0027\\neg_01/generated.step")
