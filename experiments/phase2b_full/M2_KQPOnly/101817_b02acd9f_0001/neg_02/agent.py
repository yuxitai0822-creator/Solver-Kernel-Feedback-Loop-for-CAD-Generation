import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u x v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Create the outer rectangle (centered at origin on XY plane)
outer = cq.Workplane("XY").rect(40, 40).extrude(520)

# Create the inner rectangle (hollow) with wall thickness 1.2 mm
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(520)

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0001\\neg_02/generated.step")
