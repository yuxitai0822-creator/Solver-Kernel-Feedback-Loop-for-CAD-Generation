import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 40 x 40 mm (in u-v plane)
# Inner rectangle: 37.6 x 37.6 mm (centered)
# Extrude 780 mm along w direction (which is +y in world)

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(40, 40)
)

# Build the inner rectangle (centered)
inner = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(37.6, 37.6)
)

# Create the frame profile by subtracting inner from outer
frame_profile = outer.cut(inner)

# Extrude the frame profile along the Z axis (which corresponds to +w direction)
# The design plan says w_dir = [0,1,0] but we use XY plane and extrude along Z
# to get a 780 mm long hollow box
result = frame_profile.extrude(780)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0000\\neg_03/generated.step")
