import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u,v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Create the outer rectangle profile (centered at origin)
outer = cq.Workplane("XY").rect(40, 40)

# Create the inner rectangle profile (centered at origin)
inner = cq.Workplane("XY").rect(37.6, 37.6)

# Build the hollow profile by subtracting inner from outer
# Use the same workplane for both
result = (
    cq.Workplane("XY")
    .rect(40, 40)
    .extrude(520)
)

# Now cut the inner hole
result = (
    result
    .faces(">Z")
    .workplane()
    .rect(37.6, 37.6)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0001\\neg_01/generated.step")
