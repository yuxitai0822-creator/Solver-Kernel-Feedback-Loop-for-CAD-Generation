import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle from (-3.9, 0) to (0, 6.8) in UV space, but the dimensions indicate
# length_u=39.0 and width_v=68.0. The UV coordinates given are in cm (since unit_conversion_applied: cm_to_mm x10).
# Converting: -3.9 cm = -39 mm, 6.8 cm = 68 mm, 0 cm = 0 mm.
# So the rectangle spans from (-39, 0) to (0, 68) in mm, giving length 39 mm and width 68 mm.
# Extrude in +w direction by 10.0 mm.

result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0, centered=False)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102175_699d5e7c_0003\\neg_02/generated.step")
