import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 6.0 mm, inner radius = 4.25 mm, extrude distance = 12.0 mm
# The annulus is centered at (0,0) in the sketch plane, extruded along +w direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: sketch on XZ plane (u=x, v=z), extrude along +y (w).

# Build the outer circle (radius 6.0) and inner circle (radius 4.25) as a single wire
# using CadQuery's workplane on the XZ plane (front view).

result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer circle
    .circle(4.25)  # inner circle (hole)
    .extrude(12.0)  # extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102410_f9877a7b_0012\\neg_01/generated.step")
