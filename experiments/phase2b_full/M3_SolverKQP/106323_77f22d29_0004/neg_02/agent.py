import cadquery as cq

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm (symmetric about XY plane)

# Create the outer circle (radius 17.5)
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (radius 12.5) as a hole
inner_circle = cq.Workplane("XY").circle(12.5)

# Build the annulus by extruding the outer circle and cutting the inner circle
# Since the extrude is symmetric (both sides), we extrude half the total distance in each direction
# Total distance = 10.0 mm, so extrude 5.0 mm both ways
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer profile
    .extrude(5.0, both=True)  # symmetric extrusion: total height = 10.0 mm
    .faces(">Z")  # select top face to cut the hole
    .workplane()
    .circle(12.5)  # inner profile
    .cutThruAll()  # cut through the entire body
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106323_77f22d29_0004\\neg_02/generated.step")
