import cadquery as cq

# Create a rectangular prism with dimensions: length_u=8.5, width_v=18.0, extrude_distance=2.5
# The profile is centered at the origin in the uv-plane, then extruded in the +w direction.
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the X-Z plane (with v inverted), and extrudes along Y.

# Build the rectangle profile centered at origin in uv-space
# uv coordinates: u from -0.425 to 0.425, v from -0.9 to 0.9
# In world: u -> X, v -> -Z, so:
#   X from -0.425 to 0.425
#   Z from -(-0.9)=0.9 to -(0.9)=-0.9  (i.e., Z from -0.9 to 0.9 after inversion)
# Actually simpler: just use the rectangle center at origin, dimensions 8.5 x 18.0

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(8.5, 18.0)
    .extrude(2.5)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0004\\neg_01/generated.step")
