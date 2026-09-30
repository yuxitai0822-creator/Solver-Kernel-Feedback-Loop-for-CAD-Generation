import cadquery as cq

# Create the outer circle (radius 17.5 mm) and inner circle (radius 12.5 mm)
# The design plan specifies an extruded annulus with symmetric extrusion of total 10 mm
# Note: The radii in the profiles section are 1.75 and 1.25, but the dimensions section
# gives outer_radius=17.5 and inner_radius=12.5. The compiler notes mention cm_to_mm (x10),
# so the profile radii are in cm and need to be multiplied by 10 to get mm.
# We use the explicit dimensions from the dimensions section.

outer_radius = 17.5  # mm
inner_radius = 12.5  # mm
total_height = 10.0  # mm (symmetric extrusion, so half on each side)

# Build the annulus by extruding a washer shape
# Start with a circle, then subtract the inner circle
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(total_height / 2, both=True)  # symmetric extrusion
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106323_77f22d29_0004\\ex2/generated.step")
