import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u x v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Create the outer rectangle (40 x 40)
outer = cq.Workplane("XY").rect(40, 40)

# Create the inner rectangle (37.6 x 37.6) for the hollow cutout
inner = cq.Workplane("XY").rect(37.6, 37.6)

# Build the frame profile by subtracting inner from outer
frame_profile = outer.cut(inner)

# Extrude the profile along Z (w direction) by 520 mm
result = frame_profile.extrude(520)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0001\\neg_02/generated.step")
