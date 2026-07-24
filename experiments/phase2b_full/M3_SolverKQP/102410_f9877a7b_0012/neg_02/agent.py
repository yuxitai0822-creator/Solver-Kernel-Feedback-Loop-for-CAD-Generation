import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# The annulus is centered at (0,0) in the sketch plane, extruded along +w direction.
# According to the frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the sketch plane is the X-Z plane (u=x, v=-z), extrusion along +w = +y.
# So we create a circle for outer and inner, extrude in the Y direction.

# Build the outer circle
outer = cq.Workplane("XZ").circle(6.0)

# Build the inner circle (hole)
inner = cq.Workplane("XZ").circle(4.25)

# Create the annulus by cutting inner from outer, then extrude
result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer
    .circle(4.25)  # inner (cut)
    .extrude(12.0)  # extrude along Y (positive w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102410_f9877a7b_0012\\neg_02/generated.step")
