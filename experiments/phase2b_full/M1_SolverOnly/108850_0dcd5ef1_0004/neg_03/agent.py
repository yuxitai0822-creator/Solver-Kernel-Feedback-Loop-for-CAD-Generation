import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
# The profile is a rectangle with corners at (0,0), (171.45,0), (171.45,110.998), (0,110.998)
# Note: The design plan uses a frame where u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the rectangle lies in the XZ plane (u along X, v along -Z), extruded along Y (w direction)
# To keep the part simple and centered, we'll create it in the XY plane and then rotate if needed.
# However, the design plan's origin convention is bbox_min_corner, so we place the rectangle starting at origin.

# Create the rectangular profile in the XY plane (u along X, v along Y)
# But the design plan says v_dir = (0,0,-1), so v is along -Z. We'll follow the frame exactly.
# Using workplane on XZ plane (front view) to match u_dir=X, v_dir=-Z

result = (
    cq.Workplane("XZ")
    .rect(171.45, 110.998, centered=False)
    .extrude(6.35)
)

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108850_0dcd5ef1_0004\\neg_03/generated.step")
