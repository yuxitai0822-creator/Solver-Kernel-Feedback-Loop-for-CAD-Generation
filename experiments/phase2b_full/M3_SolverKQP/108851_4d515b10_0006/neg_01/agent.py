import cadquery as cq

# Create a rectangular prism with dimensions:
# length_u = 95.25 mm (along x-axis)
# width_v = 19.05 mm (along z-axis, since v_dir = [0,0,-1])
# extrude_distance = 12.7 mm (along y-axis, since w_dir = [0,1,0])

# The profile is a rectangle in the uv-plane (x-z plane)
# u corresponds to x, v corresponds to z (but v_dir is [0,0,-1], so we use positive z for simplicity)
# The rectangle spans from (0, 0) to (95.25, 19.05) in uv coordinates

# Create the rectangle profile on the xz-plane (y=0)
result = (
    cq.Workplane("XZ")
    .rect(95.25, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0006\\neg_01/generated.step")
