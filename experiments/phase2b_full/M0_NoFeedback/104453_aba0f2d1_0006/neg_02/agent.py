import cadquery as cq

# Create the outer rectangle profile
outer = cq.Workplane("XY").rect(50.0, 30.0)

# Create the inner rectangle profile (the hole)
inner = cq.Workplane("XY").rect(40.0, 20.0)

# Build the frame by extruding the outer rectangle and cutting the inner rectangle
result = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)  # outer profile
    .extrude(500.0)     # extrude along Z
    .faces("<Z")       # select bottom face
    .workplane()
    .rect(40.0, 20.0)  # inner profile
    .cutThruAll()       # cut through the entire body
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104453_aba0f2d1_0006\\neg_02/generated.step")
