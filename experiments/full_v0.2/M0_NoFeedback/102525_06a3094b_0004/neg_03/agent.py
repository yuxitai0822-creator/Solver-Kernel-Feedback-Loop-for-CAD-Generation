import cadquery as cq

# Create a rectangular prism with dimensions: length_u=8.5, width_v=18.0, extrude_distance=2.5
# The profile is centered on the origin in the UV plane, then extruded in the +w direction.
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle in UV (u from -4.25 to 4.25, v from -9.0 to 9.0) maps to:
#   X = u, Z = -v, Y = 0 initially, then extrude in Y direction by 2.5

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0004\\neg_03/generated.step")
