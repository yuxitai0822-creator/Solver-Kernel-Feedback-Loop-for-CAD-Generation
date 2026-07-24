import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait: dimensions say outer_radius=132.5, inner_radius=75.0)
# The design plan states unit is mm, and dimensions are given as 132.5 and 75.0.
# However the profile radii are 13.249999999999998 and 7.499999999999998, which are 1/10 of the dimensions.
# The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the profile radii are in cm? 
# Actually the dimensions block says outer_radius=132.5, inner_radius=75.0 (mm). The profile radii are 13.25 and 7.5 (cm) which after x10 become 132.5 and 75.0 mm.
# So we use the dimension values: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0.

outer_radius = 132.5
inner_radius = 75.0
height = 100.0

# Build the annulus by creating a circle, then a circle hole, then extrude
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\107668_cf76b132_0001\neg_03/generated.step")
