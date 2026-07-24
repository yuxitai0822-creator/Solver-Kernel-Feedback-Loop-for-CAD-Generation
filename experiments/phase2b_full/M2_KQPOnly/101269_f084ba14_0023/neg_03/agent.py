import cadquery as cq

# Create a rectangular profile in the XY plane
# The design plan specifies a rectangle with dimensions:
#   length_u = 95.25 mm (along x-axis)
#   width_v = 571.5 mm (along y-axis, but note v_dir is [0,0,-1] so we use negative y)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> x, v -> -z, w -> y
# The profile is defined in uv space, with points:
#   (9.525, 57.15), (9.525, 0), (0, 57.15), (0, 0)
# These are offsets from the origin in the uv coordinate system.
# Since the rectangle spans from u=0 to u=9.525 and v=0 to v=57.15,
# but the actual dimensions are length_u=95.25 and width_v=571.5,
# the uv coordinates are scaled by a factor of 10.
# So we create a rectangle from (0,0) to (95.25, 571.5) in the uv plane.
# In the frame: u -> x, v -> -z, so the rectangle lies in the xz plane.
# We'll create the rectangle in the XY plane and then rotate if needed.
# Simpler: create a rectangle in the XY plane with dimensions 95.25 x 571.5
# and extrude along Z by 19.05 mm.

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\neg_03/generated.step")
