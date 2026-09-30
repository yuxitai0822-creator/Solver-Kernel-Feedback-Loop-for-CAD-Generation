import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# Extrude in +w direction by 25.0 mm

# Create the outer rectangle profile
outer = (
    cq.Workplane("XY")
    .moveTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .lineTo(-2.5, 57.5)
    .close()
)

# Create the inner rectangle profile (cutout)
inner = (
    cq.Workplane("XY")
    .moveTo(0.0, 0.0)
    .lineTo(193.0, 0.0)
    .lineTo(193.0, 55.0)
    .lineTo(0.0, 55.0)
    .close()
)

# Build the frame by extruding the outer rectangle and cutting the inner
result = (
    cq.Workplane("XY")
    .moveTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .lineTo(-2.5, 57.5)
    .close()
    .extrude(25.0)
    .faces("<Z")
    .workplane()
    .moveTo(0.0, 0.0)
    .lineTo(193.0, 0.0)
    .lineTo(193.0, 55.0)
    .lineTo(0.0, 55.0)
    .close()
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101427_a9bcb09c_0001\\neg_01/generated.step")
