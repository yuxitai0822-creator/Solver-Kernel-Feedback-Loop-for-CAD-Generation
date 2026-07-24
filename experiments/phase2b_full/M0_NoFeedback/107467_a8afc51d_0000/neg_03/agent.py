import cadquery as cq

# Design Plan: extruded circle (disk)
# Radius = 3.0 mm, Extrude distance = 14.0 mm

# Create a circle profile and extrude it
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius 3.0 mm
    .extrude(14.0)        # extrude 14.0 mm in +Z direction
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\107467_a8afc51d_0000\\neg_03/generated.step")
