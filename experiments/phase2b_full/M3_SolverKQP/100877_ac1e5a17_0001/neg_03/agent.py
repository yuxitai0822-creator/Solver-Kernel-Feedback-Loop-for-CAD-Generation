import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm->mm conversion (x10), so values are already in mm.
# The profile is defined in UV coordinates with origin at (0,0) and rectangle corners:
#   (0,0), (27.94,0), (27.94,21.59), (0,21.59)
# These are in cm? Actually the plan says unit_conversion_applied: cm_to_mm (x10).
# The raw values in the curves are 27.94 and 21.59, which after x10 become 279.4 and 215.9.
# So we use the explicit dimensions from the dimensions block: 279.4 x 215.9 x 1.5875 mm.

# Build the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\100877_ac1e5a17_0001\\neg_03/generated.step")
