import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude distance = 6.35 mm
# The profile is a rectangle with corners at (0,0), (171.45,0), (171.45,110.998), (0,110.998)
# Note: The design plan uses a local frame where u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the rectangle lies in the XZ plane (u along X, v along -Z), extruded along Y (w direction)

# Build the rectangle in the XZ plane
result = (
    cq.Workplane("XZ")
    .rect(171.45, 110.998)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108850_0dcd5ef1_0004\\neg_02/generated.step")
