import cadquery as cq

# Design Plan: SoapCutterBedBack1 v1
# Dimensions: length_u = 307.848 mm, width_v = 19.05 mm, extrude_distance = 12.7 mm
# The profile is a rectangle in the UV plane, extruded along W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the XZ plane (u along X, v along -Z), extruded along Y.

# Create the rectangle profile in the XZ plane
# The rectangle spans from (0, 0) to (307.848, 19.05) in UV coordinates.
# In 3D: u along X, v along -Z, so point (u, v) maps to (u, 0, -v)
# Start at (0, 0) -> (0, 0, 0)
# End at (307.848, 19.05) -> (307.848, 0, -19.05)

result = (
    cq.Workplane("XZ")
    .center(307.848/2, -19.05/2)  # center the rectangle at origin for symmetric extrusion
    .rect(307.848, 19.05)
    .extrude(12.7)  # extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0005\\neg_02/generated.step")
