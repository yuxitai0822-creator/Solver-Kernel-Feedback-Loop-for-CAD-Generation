import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u,v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Build the outer rectangle (centered at origin for convenience)
outer = cq.Workplane("XY").rect(40, 40).extrude(520)

# Build the inner rectangle (hole) with same center
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(520)

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0001\\neg_03/generated.step")
