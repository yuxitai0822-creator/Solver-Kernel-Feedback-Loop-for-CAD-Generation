import cadquery as cq

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm (symmetric about XY plane)

# Create the outer circle (radius 17.5)
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (radius 12.5) as a hole
inner_circle = cq.Workplane("XY").circle(12.5)

# Build the annulus by extruding the outer circle and cutting the inner circle
# Since symmetric extrusion is requested, we extrude half on each side
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer circle
    .extrude(5.0)   # extrude up 5 mm (half of total 10 mm)
    .faces(">Z")   # move to top face
    .workplane()
    .circle(12.5)   # inner circle on top face
    .cutThruAll()   # cut through the entire body
)

# Now mirror to get symmetric extrusion (both sides)
# Alternatively, we can build the full symmetric extrusion directly
result = (
    cq.Workplane("XY")
    .circle(17.5)
    .extrude(5.0, both=True)  # symmetric extrusion: 5 mm each side, total 10 mm
    .faces(">Z")
    .workplane()
    .circle(12.5)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106323_77f22d29_0004\\neg_01/generated.step")
