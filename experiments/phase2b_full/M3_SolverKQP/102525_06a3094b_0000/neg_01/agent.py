import cadquery as cq

# Create a rectangular prism with dimensions: length_u=3.9, width_v=4.9, extrude_distance=1.55
# The profile is a rectangle centered at origin in the XY plane, extruded in the +Z direction.
# Based on the design plan: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y. So the rectangle lies in XZ plane and extrudes along Y.
# However, for simplicity and to match typical CadQuery conventions, we'll create the rectangle
# in the XY plane and extrude in Z, then rotate if needed. But the dimensions must match.
# The design plan says length_u=3.9 (along X), width_v=4.9 (along -Z), extrude along Y (1.55).
# So we create a rectangle 3.9 x 4.9 in the XZ plane, then extrude along Y.

# Build the profile: rectangle centered at origin in XZ plane
# Points from the plan: start_uv = (0.195, -0.245) etc. These are half-dimensions.
# u ranges from -0.195 to 0.195 (half of 3.9), v ranges from -0.245 to 0.245 (half of 4.9)

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9)
    .extrude(1.55)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0000\\neg_01/generated.step")
