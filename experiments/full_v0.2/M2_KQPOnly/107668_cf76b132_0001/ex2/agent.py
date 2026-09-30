import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait, dimensions are in mm already)
# The design plan says outer_radius = 132.5 mm, inner_radius = 75.0 mm, extrude distance = 100.0 mm
# But the profile circles have radius 13.249999999999998 and 7.499999999999998 — these are in cm? 
# The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the profile radii are in cm, 
# and the dimensions are in mm after conversion. Let's use the explicit dimensions: outer_radius=132.5, inner_radius=75.0

# Build the annulus profile
outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Create a workplane and draw two concentric circles, then extrude
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107668_cf76b132_0001\\ex2/generated.step")
