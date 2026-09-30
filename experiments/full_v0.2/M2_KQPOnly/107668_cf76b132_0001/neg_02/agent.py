import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait, dimensions say 132.5 and 75.0)
# The design plan dimensions: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0
# All in mm.

# Build the annulus by creating a circle for outer and inner, then extrude
outer_radius = 132.5
inner_radius = 75.0
extrude_height = 100.0

# Create the outer circle wire
outer_circle = cq.Workplane("XY").circle(outer_radius)

# Create the inner circle wire (as a hole)
inner_circle = cq.Workplane("XY").circle(inner_radius)

# Build the annulus: start with outer circle, cut inner circle, extrude
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)  # this creates a second circle on same plane
    .extrude(extrude_height)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107668_cf76b132_0001\\neg_02/generated.step")
