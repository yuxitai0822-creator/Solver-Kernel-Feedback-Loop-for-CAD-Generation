import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm
# Width (v): 19.05 mm
# Height (w): 12.7 mm

# The profile is a rectangle in the uv-plane, extruded along w.
# From the design plan:
#   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the XZ plane (with v reversed), extruded along Y.

# Build the rectangle profile on the XZ plane (workplane XY, but we'll use XZ)
# Using workplane("XZ") gives us u=X, v=Z, but v_dir is [0,0,-1] so we need to negate Z.
# Simpler: just create a box with the correct dimensions and position it so that
# the origin is at the min corner (bbox_min_corner convention).

# The rectangle in uv coordinates:
#   u: 0 to 95.25  (X)
#   v: 0 to 19.05  (but v_dir = -Z, so v=0 -> Z=0, v=19.05 -> Z=-19.05)
# Extrude along w: w_dir = Y, distance = 12.7

# So the box spans:
#   X: 0 to 95.25
#   Y: 0 to 12.7
#   Z: -19.05 to 0

result = cq.Workplane("XY").box(95.25, 12.7, 19.05).translate((95.25/2, 12.7/2, -19.05/2))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0006\\neg_01/generated.step")
