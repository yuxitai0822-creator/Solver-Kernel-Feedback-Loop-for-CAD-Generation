import cadquery as cq

# Create a rectangular frame (hollow box) by extruding a rectangular profile with a hole
# The frame is defined in a local coordinate system where:
# u_dir = [1,0,0] (X axis)
# v_dir = [0,0,-1] (Z axis, negative)
# w_dir = [0,1,0] (Y axis)
# Extrude along +w (positive Y) by 780 mm

# Outer rectangle: from (6, -7) to (10, -3) in UV space
# But the dimensions indicate outer length 40mm and outer width 40mm.
# The UV coordinates given: start_uv = [10, -7], end_uv = [6, -7] etc.
# Let's interpret: The outer rectangle corners in UV:
# (6, -7), (10, -7), (10, -3), (6, -3)
# This gives width = 10-6 = 4, height = -3 - (-7) = 4 (in UV units)
# But the actual dimensions say outer_length_u = 40mm, outer_width_v = 40mm.
# So UV units are scaled: 1 UV unit = 10 mm.
# Inner rectangle: from (6.12, -6.88) to (9.88, -3.12)
# Inner width = 9.88-6.12 = 3.76 UV units = 37.6 mm
# Inner height = -3.12 - (-6.88) = 3.76 UV units = 37.6 mm
# Wall thickness = (40-37.6)/2 = 1.2 mm

# Build the profile in the XY plane (since we'll extrude along Z)
# But the frame's u_dir = X, v_dir = -Z, w_dir = Y.
# To extrude along w (Y), we need the profile in the XZ plane.
# Let's map: u -> X, v -> -Z, so v coordinate maps to -Z.
# So in 3D: point (u, v) maps to (u*10, 0, -v*10) in the plane at Y=0.
# Then extrude along Y by 780 mm.

# Scale factor: 1 UV unit = 10 mm
scale = 10.0

# Outer rectangle corners in UV (from curves)
outer_uv = [
    (6.0, -7.0),
    (10.0, -7.0),
    (10.0, -3.0),
    (6.0, -3.0)
]

# Inner rectangle corners in UV
inner_uv = [
    (6.12, -6.88),
    (9.88, -6.88),
    (9.88, -3.12),
    (6.12, -3.12)
]

# Convert UV to 3D points in the XZ plane (Y=0)
# u -> X, v -> -Z (since v_dir = [0,0,-1])
def uv_to_3d(u, v):
    return (u * scale, 0.0, -v * scale)

# Build outer wire
outer_pts = [uv_to_3d(u, v) for u, v in outer_uv]
# Close the loop by adding first point at end
outer_pts_closed = outer_pts + [outer_pts[0]]

# Build inner wire
inner_pts = [uv_to_3d(u, v) for u, v in inner_uv]
inner_pts_closed = inner_pts + [inner_pts[0]]

# Create the profile using CadQuery
# We'll make a rectangular face with a hole
# First make the outer rectangle as a wire
outer_wire = cq.Workplane("XY").polyline(outer_pts).close().wire()

# Make the inner rectangle as a wire
inner_wire = cq.Workplane("XY").polyline(inner_pts).close().wire()

# Build the face with a hole
# Approach: create a plane, make outer face, then cut inner
# Use cq.Face.makeFromWires
outer_face = cq.Face.makeFromWires(outer_wire.val())
inner_face = cq.Face.makeFromWires(inner_wire.val())

# Cut inner from outer to create the frame profile
frame_face = outer_face.cut(inner_face)

# Now extrude along Y (w direction) by 780 mm
result = cq.Workplane("XY").newObject([frame_face]).extrude(780.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0000\\neg_01/generated.step")
