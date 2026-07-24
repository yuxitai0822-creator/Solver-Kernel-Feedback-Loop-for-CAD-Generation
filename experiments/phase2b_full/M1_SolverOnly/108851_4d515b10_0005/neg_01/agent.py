import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 307.848 mm and width_v = 19.05 mm
# The extrude distance is 12.7 mm in the +w direction

# Create the rectangle profile on the XY plane (u=x, v=y, w=z)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> x, v -> -z, w -> y
# So the rectangle lies in the x-z plane, extruded along y

# Build the result
result = (
    cq.Workplane("XZ")
    .rect(307.848, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0005\\neg_01/generated.step")
