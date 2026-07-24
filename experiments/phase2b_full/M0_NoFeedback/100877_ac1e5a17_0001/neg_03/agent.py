import cadquery as cq

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm->mm conversion (x10), so values are already in mm.

# Create the rectangular profile
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)  # length_u along X, width_v along Y
    .extrude(1.5875)      # extrude in +Z direction
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\100877_ac1e5a17_0001\neg_03/generated.step")
