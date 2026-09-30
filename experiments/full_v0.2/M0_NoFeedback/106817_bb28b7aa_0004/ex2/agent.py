import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   outer radius = 5.5372
#   inner radius = 1.9812
#   thickness (extrude distance) = 1.3208
#   center_uv = (-25.400001, 12.7)  # in sketch plane
#
# The frame defines: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the sketch lies in the X-Z plane (u along X, v along -Z),
# and extrusion is along +w = +Y.
#
# We build the annulus centered at (cx, cy, 0) in the sketch plane,
# then extrude in the Y direction.

# Center in sketch coordinates (u, v) = (-25.400001, 12.7)
# Map to 3D: u -> X, v -> -Z (since v_dir = (0,0,-1))
# So center in 3D: (cx, 0, -cy) = (-25.400001, 0, -12.7)
cx = -25.400001
cy = 12.7

# Radii
outer_r = 5.5372
inner_r = 1.9812

# Extrude distance (thickness)
thickness = 1.3208

# Build the washer
# Start with a cylinder for the outer shape, then cut the inner hole.
# We'll create a workplane on the XZ plane (Y=0) and draw circles.

result = (
    cq.Workplane("XZ")
    .center(cx, -cy)  # note: v_dir = (0,0,-1) so v maps to -Z
    .circle(outer_r)
    .circle(inner_r)
    .extrude(thickness)  # extrudes along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\106817_bb28b7aa_0004\ex2/generated.step")
