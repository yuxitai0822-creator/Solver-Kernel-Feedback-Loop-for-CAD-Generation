import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait: dimensions say outer_radius=132.5, inner_radius=75.0)
# The design plan states unit is mm, and dimensions are given as 132.5 and 75.0.
# However the profile radii are 13.25 and 7.5? Let's check: In profiles, radius is 13.249999999999998 and 7.499999999999998.
# But dimensions section says outer_radius=132.5, inner_radius=75.0. This is a factor of 10 discrepancy.
# The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the profile radii are in cm? Actually the plan says unit=mm.
# The profile radii (13.25, 7.5) are likely in cm before conversion? But the dimensions say 132.5 and 75.0 mm.
# We'll use the explicit dimensions from the dimensions section: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0.

outer_r = 132.5
inner_r = 75.0
height = 100.0

# Build the annulus by extruding a circle and then cutting a concentric circle
result = (
    cq.Workplane("XY")
    .circle(outer_r)
    .extrude(height)
    .faces(">Z")  # top face
    .workplane()
    .circle(inner_r)
    .cutThruAll()
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\107668_cf76b132_0001\neg_03/generated.step")
