import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the u-v plane.
# u direction = x-axis, v direction = z-axis (negative), w direction = y-axis
# Extrude in +w direction (positive y) by 2.5 mm

# Create the rectangle profile centered at origin
# Width along u (x) = 8.5 mm, length along v (z) = 18.0 mm
# The rectangle spans from -4.25 to 4.25 in x, and -9.0 to 9.0 in z
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(8.5, 18.0)
    .extrude(2.5)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0004\\neg_02/generated.step")
