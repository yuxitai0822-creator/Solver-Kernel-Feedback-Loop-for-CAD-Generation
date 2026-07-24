import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer dimensions: 40 x 40 mm (u x v), inner dimensions: 37.6 x 37.6 mm
# Extrude distance: 520 mm along w direction

# Create the outer rectangle (centered at origin)
outer = cq.Workplane("XY").rect(40.0, 40.0).extrude(520.0)

# Create the inner rectangle (centered at origin) to cut out the hollow
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(520.0)

# Subtract inner from outer to create the hollow frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0001\\neg_01/generated.step")
