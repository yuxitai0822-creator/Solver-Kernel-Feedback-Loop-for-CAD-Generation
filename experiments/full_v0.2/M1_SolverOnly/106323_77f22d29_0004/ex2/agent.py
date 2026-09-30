import cadquery as cq

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# Symmetric extrusion about the sketch plane

# Create the outer circle (radius 17.5)
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (radius 12.5) as a hole
inner_circle = cq.Workplane("XY").circle(12.5)

# Build the annulus by extruding the outer circle and cutting the inner circle
# Using symmetric extrusion (both sides) with total distance 10.0 mm
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer boundary
    .extrude(5.0, both=True)  # symmetric extrusion: 5 mm each side = 10 mm total
    .faces("<Z")  # select top face for cutting
    .workplane()
    .circle(12.5)  # inner hole
    .cutThruAll()  # cut through the entire body
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106323_77f22d29_0004\\ex2/generated.step")
