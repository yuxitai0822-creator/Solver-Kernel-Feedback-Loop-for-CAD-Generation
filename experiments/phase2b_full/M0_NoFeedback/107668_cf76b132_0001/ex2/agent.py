import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait, dimensions say 132.5 and 75.0, but the profile radii are 13.25 and 7.5. The design plan says unit conversion applied: cm_to_mm (x10). So the profile radii are in cm? Actually the dimensions section says outer_radius: 132.5 mm, inner_radius: 75.0 mm. The profile radii are 13.249999999999998 and 7.499999999999998, which are exactly 1/10 of those. So the profile radii are in cm, and we need to multiply by 10 to get mm. Let's use the explicit dimensions: outer_radius = 132.5 mm, inner_radius = 75.0 mm, extrude_distance = 100.0 mm.

# Build the annulus profile
outer_radius = 132.5
inner_radius = 75.0
height = 100.0

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(outer_radius)

# Create the inner circle (hole)
result = outer_circle.circle(inner_radius).extrude(height)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\107668_cf76b132_0001\\ex2/generated.step")
