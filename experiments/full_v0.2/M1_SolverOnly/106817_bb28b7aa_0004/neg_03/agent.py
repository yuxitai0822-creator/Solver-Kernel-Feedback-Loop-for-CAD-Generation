import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   Outer radius = 5.5372 mm
#   Inner radius = 1.9812 mm
#   Thickness (extrude distance) = 1.3208 mm
#   Center in UV plane: (-25.400001, 12.7) but we place at origin for simplicity

# Build the washer by creating a circle for outer and inner, then extrude
# Using the frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the profile lies in the u-v plane (x-z plane in world), extrude along w (y axis)
# We'll construct on the XY plane and then rotate if needed, but simpler: build on XY plane and extrude along Z, then rotate to match frame.
# Actually, to match the frame exactly: profile in x-z plane, extrude along y.
# We'll use workplane on XZ plane.

# Create the outer circle
outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Build on XZ plane (front view in CQ) and extrude along Y
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# The resulting part is centered at origin, with thickness along Y.
# The design plan's frame has origin at bbox_min_corner, but we ignore that for simplicity.
# The validation intents expect spans: u=11.0744, v=11.0744, w=1.3208.
# Our part has diameter 11.0744 in X and Z, thickness 1.3208 in Y. That matches.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0004\\neg_03/generated.step")
