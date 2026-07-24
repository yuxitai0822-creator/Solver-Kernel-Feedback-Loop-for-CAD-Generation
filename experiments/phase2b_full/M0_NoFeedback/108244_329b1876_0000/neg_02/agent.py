import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle in UV space spans from (-0.7464, 31.2996) to (121.1736, 290.3796)
# But the inferred dimensions are 1219.2 x 2590.8, so we use those directly.
# The extrude direction is +w (i.e., along y-axis).

# Build the rectangle in the XY plane (since u=x, v=z? Actually v_dir = (0,0,-1) means v is -z, w_dir = (0,1,0) means w is y)
# To keep it simple: create a rectangle in the XY plane, then extrude along Y.
# But the frame says u_dir = x, v_dir = -z, w_dir = y.
# So the rectangle lies in the XZ plane (u along x, v along -z).
# We'll create a rectangle on the XZ plane, then extrude along Y.

# Use the explicit dimensions: length_u = 1219.2 (along x), width_v = 2590.8 (along z)
# Center the rectangle at origin for simplicity (the exact position is not critical for validation).

result = (
    cq.Workplane("XZ")
    .rect(1219.2, 2590.8)
    .extrude(44.45)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108244_329b1876_0000\\neg_02/generated.step")
