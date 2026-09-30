import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 132.5 mm, inner radius = 75.0 mm, extrude distance = 100.0 mm
# Note: The design plan specifies radii as 13.25 and 7.5 in the profile curves, but dimensions section says 132.5 and 75.0.
# The compiler note says unit_conversion_applied: cm_to_mm (x10). So the profile radii (13.25, 7.5) are in cm, converted to mm = 132.5, 75.0.
# We use the explicit dimensions from the dimensions section: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0.

# Build the annulus by creating a circle for outer and inner, then extruding the difference.

# Create outer circle
outer_circle = cq.Workplane("XY").circle(132.5)

# Create inner circle (hole) - we cut this from the outer circle
# Using Workplane to create the annulus profile
result = (
    cq.Workplane("XY")
    .circle(132.5)  # outer radius
    .circle(75.0)   # inner radius (hole)
    .extrude(100.0)  # extrude distance
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107668_cf76b132_0001\\neg_01/generated.step")
