import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Origin convention: bbox_min_corner -> we place the rectangle in the XY plane (u,v) and extrude along w (Y axis)

# Create rectangle in the XY plane (u = X, v = Z, but v_dir is (0,0,-1) so we invert Z)
# To match the frame: u along X, v along -Z, w along Y
# So the rectangle lies in the XZ plane, with v reversed.
# We'll create a rectangle from (0,0) to (171.45, 110.998) in the XZ plane, then extrude along Y.

result = (
    cq.Workplane("XZ")
    .rect(171.45, 110.998)
    .extrude(6.35)
)

# The resulting box is centered on the origin. To match bbox_min_corner convention,
# we need to translate so that the minimum corner is at (0,0,0).
# The rect is centered, so min corner is at (-171.45/2, -6.35/2, -110.998/2)
# We translate by (171.45/2, 6.35/2, 110.998/2) to bring min corner to origin.
result = result.translate((171.45/2, 6.35/2, 110.998/2))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108850_0dcd5ef1_0004\\ex2/generated.step")
