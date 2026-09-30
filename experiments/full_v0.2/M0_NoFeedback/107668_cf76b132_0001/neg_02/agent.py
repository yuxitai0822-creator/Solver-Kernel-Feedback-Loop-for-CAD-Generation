import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion: 132.5/10 = 13.25)
outer_radius = 13.25
inner_radius = 7.5
extrude_distance = 10.0  # 100.0 mm / 10 = 10.0 mm

# Build the annulus by extruding a washer shape
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\107668_cf76b132_0001\\neg_02/generated.step")
