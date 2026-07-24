import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle: 27.94 mm x 5.08 mm (in UV space)
# But the dimensions table says length_u = 279.4 mm, width_v = 50.8 mm
# The profile curves show 27.94 and 5.08, which appear to be scaled by 10x
# The compiler notes indicate cm_to_mm conversion (x10), so the actual dimensions are:
# length_u = 279.4 mm, width_v = 50.8 mm
# Extrude distance = 19.05 mm

# Build the base rectangle in the XY plane (u=x, v=z, w=y per frame definition)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So u -> X, v -> -Z, w -> Y
# The profile is defined in UV space, so we draw in XZ plane with v reversed

result = (
    cq.Workplane("XZ")
    .center(279.4/2, 50.8/2)  # center the rectangle at origin
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0007\\neg_02/generated.step")
