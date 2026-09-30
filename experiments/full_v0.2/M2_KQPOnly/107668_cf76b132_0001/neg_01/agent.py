import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion: 132.5/10 = 13.25)
# The design plan specifies outer_radius = 132.5 mm, inner_radius = 75.0 mm
# But note: the profile curves show radius 13.249999999999998 and 7.499999999999998
# This is because the original was in cm and converted to mm by dividing by 10?
# Actually the dimensions section says outer_radius=132.5, inner_radius=75.0
# The curves section shows 13.25 and 7.5 which are 1/10 of those values.
# The compiler note says "unit_conversion_applied: cm_to_mm (x10)"
# So the original was in cm, converted to mm by multiplying by 10.
# The curves radii are in the original cm units? Or the dimensions are in mm?
# Let's use the dimensions section values: outer_radius=132.5 mm, inner_radius=75.0 mm

outer_r = 132.5
inner_r = 75.0
extrude_dist = 100.0

# Build the annulus by extruding a circle and subtracting the inner circle
# Using workplane on the XY plane (default)
result = (
    cq.Workplane("XY")
    .circle(outer_r)
    .circle(inner_r)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\107668_cf76b132_0001\neg_01/generated.step")
