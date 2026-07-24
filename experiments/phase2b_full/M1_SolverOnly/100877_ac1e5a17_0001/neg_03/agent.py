import cadquery as cq

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm_to_mm conversion (x10), so the values are already in mm.
# The profile coordinates in the plan are in UV space (0 to 27.94 in U, 0 to 21.59 in V).
# These correspond to 279.4 mm and 215.9 mm respectively (multiply by 10).

# Create the rectangular profile
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)  # width (U) = 279.4 mm, height (V) = 215.9 mm
    .extrude(1.5875)      # extrude in +W direction by 1.5875 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100877_ac1e5a17_0001\\neg_03/generated.step")
