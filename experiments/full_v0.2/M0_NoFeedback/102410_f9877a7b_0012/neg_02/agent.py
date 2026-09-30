import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 6.0 mm, inner radius = 4.25 mm, extrude distance = 12.0 mm
# The annulus is centered at (0,0) in the sketch plane, extruded along +w direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the sketch plane is u-v (x-z plane) and extrusion is along w (y-axis).

# Build the outer circle (radius 6.0) and inner circle (radius 4.25)
outer_circle = cq.Workplane("XZ").circle(6.0)
inner_circle = cq.Workplane("XZ").circle(4.25)

# Create the annulus by cutting the inner circle from the outer circle
# We work on the XZ plane (u-v plane) and extrude along Y (w direction)
result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer circle
    .circle(4.25)  # inner circle (will be subtracted)
    .extrude(12.0)  # extrude along Y (positive w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102410_f9877a7b_0012\\neg_02/generated.step")
