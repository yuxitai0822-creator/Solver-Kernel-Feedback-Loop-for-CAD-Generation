import cadquery as cq

# Create a rectangular plate based on the design plan
# The profile is a rectangle with dimensions:
#   length_u = 209.55 mm (along x-axis)
#   width_v = 57.912 mm (along z-axis, since v_dir = [0,0,-1])
# Extrude distance = 19.05 mm along w_dir = [0,1,0] (y-axis)

# Create the rectangle profile on the xz-plane (since u=x, v=z)
result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0009\\neg_02/generated.step")
