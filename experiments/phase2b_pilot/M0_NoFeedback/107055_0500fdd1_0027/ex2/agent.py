import cadquery as cq

# Washer parameters (dimensions in mm, converted from cm)
outer_radius = 3.49
inner_radius = 2.0
thickness = 0.36

# Build the washer as an extruded annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Export to STEP file
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\107055_0500fdd1_0027\ex2/generated.step")