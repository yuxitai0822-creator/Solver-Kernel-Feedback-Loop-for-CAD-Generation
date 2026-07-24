import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, total height = 10.0 mm (symmetric extrusion)

# Create the outer circle
outer = cq.Workplane("XY").circle(17.5)

# Create the inner circle (cutout)
inner = cq.Workplane("XY").circle(12.5)

# Build the annulus by extruding the outer circle and cutting the inner circle
# Use symmetric extrusion: both sides by half the total distance
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer profile
    .extrude(10.0, both=True)  # symmetric extrusion, total height 10 mm
    .faces("<Z")  # select bottom face to cut from
    .workplane()
    .circle(12.5)  # inner profile
    .cutThruAll()  # cut through the entire body
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106323_77f22d29_0004\\ex2/generated.step")
