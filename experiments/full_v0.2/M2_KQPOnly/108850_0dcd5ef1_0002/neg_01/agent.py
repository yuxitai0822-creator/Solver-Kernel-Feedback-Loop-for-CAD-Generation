import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 171.45 mm, Width (v) = 38.1 mm, Extrude distance (w) = 6.35 mm
# The profile is defined in the uv-plane, then extruded in the +w direction.
# Based on the frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the XZ plane (with v reversed), extruded along Y.

# Build the rectangle profile on the XZ plane (using workplane on Y=0)
result = (
    cq.Workplane("XY")
    .center(171.45/2, 38.1/2)  # center the rectangle at origin for convenience
    .rect(171.45, 38.1)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108850_0dcd5ef1_0002\\neg_01/generated.step")
