import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of size 171.45 mm x 38.1 mm (length_u x width_v)
# Extrude by 6.35 mm in the +w direction

# Create the rectangle profile on the XY plane (u=x, v=z, w=y)
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So u corresponds to x, v corresponds to -z, w corresponds to y
# We'll work in the XY plane and extrude in Y direction

result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)  # width along x, height along z (but v_dir is -z, so we use positive)
    .extrude(6.35)  # extrude along +y (w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108850_0dcd5ef1_0002\\ex2/generated.step")
