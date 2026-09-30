import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u-direction) = 171.45 mm, Width (v-direction) = 110.998 mm, Thickness (w-direction) = 6.35 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle lies in the X-Z plane and extrudes in Y direction

# Create the rectangle profile in the XZ plane
result = (
    cq.Workplane("XZ")
    .rect(171.45, 110.998)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108850_0dcd5ef1_0004\\neg_02/generated.step")
