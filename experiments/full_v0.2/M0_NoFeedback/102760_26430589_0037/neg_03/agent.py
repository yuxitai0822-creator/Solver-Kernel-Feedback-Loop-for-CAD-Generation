import cadquery as cq

# Design Plan: Disk (extruded circle)
# Dimensions: radius = 0.8 mm, extrude distance = 4.0 mm
# Note: The design plan uses a local coordinate system with w_dir = [0,1,0] as extrusion direction.
# The profile is a circle of radius 0.08 (in the plan's UV plane), but the actual radius is 0.8 mm.
# The extrude distance is 4.0 mm.

# Create the circle profile (radius 0.8 mm)
result = (
    cq.Workplane("XY")
    .circle(0.8)
    .extrude(4.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102760_26430589_0037\\neg_03/generated.step")
