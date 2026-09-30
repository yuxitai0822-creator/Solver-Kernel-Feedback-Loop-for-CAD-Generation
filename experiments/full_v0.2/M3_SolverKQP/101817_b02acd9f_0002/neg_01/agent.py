import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
#   => width (u) = 4.24, height (v) = 4.24  (but dimensions say 42.4?)
#   Note: compiler notes say cm_to_mm (x10) applied. The uv values are in cm?
#   Actually the dimensions say outer_length_u = 42.4 mm, outer_width_v = 42.4 mm
#   The uv coordinates: -6.12 to -1.88 => span = 4.24 (in some unit)
#   After cm->mm conversion: 4.24 cm = 42.4 mm. So uv coordinates are in cm.
#   We'll work in mm: multiply all uv coordinates by 10.
# Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0 => span = 4.0 cm = 40 mm
# Extrude distance: 1120.0 mm (already in mm)
# Frame axes: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
#   So u is along -Z, v is along Y, w is along X
#   The profile is in the uv-plane (YZ-plane), extruded along w (X direction)
#   Extrude direction: -w => along -X

# Convert cm to mm factor
cm_to_mm = 10.0

# Outer rectangle corners (in cm, then convert to mm)
outer_pts_cm = [
    (-1.88, 10.88),
    (-1.88, 15.12),
    (-6.12, 15.12),
    (-6.12, 10.88),
]
outer_pts_mm = [(u*cm_to_mm, v*cm_to_mm) for u, v in outer_pts_cm]

# Inner rectangle corners (in cm, then convert to mm)
inner_pts_cm = [
    (-6.0, 11.0),
    (-2.0, 11.0),
    (-2.0, 15.0),
    (-6.0, 15.0),
]
inner_pts_mm = [(u*cm_to_mm, v*cm_to_mm) for u, v in inner_pts_cm]

# Build the profile in the uv-plane (YZ plane)
# u -> Z, v -> Y (since u_dir = [0,0,-1], v_dir = [0,1,0])
# We'll create the profile on the YZ plane (X=0) then extrude along X

# Create outer wire
outer_wire = cq.Workplane("YZ").moveTo(outer_pts_mm[0][0], outer_pts_mm[0][1])
for pt in outer_pts_mm[1:]:
    outer_wire = outer_wire.lineTo(pt[0], pt[1])
outer_wire = outer_wire.close()

# Create inner wire
inner_wire = cq.Workplane("YZ").moveTo(inner_pts_mm[0][0], inner_pts_mm[0][1])
for pt in inner_pts_mm[1:]:
    inner_wire = inner_wire.lineTo(pt[0], pt[1])
inner_wire = inner_wire.close()

# Combine into a single wire (outer with inner hole)
# We need to create a face with a hole. Use CQ's approach: 
# Create the outer face, then cut the inner face.

# Build the outer face
outer_face = cq.Workplane("YZ").polyline(outer_pts_mm).close().extrude(0.001)  # thin plate

# Build the inner face as a solid to cut
inner_cut = cq.Workplane("YZ").polyline(inner_pts_mm).close().extrude(0.001)

# Actually simpler: create the profile as a sketch with a hole
# Use the workplane approach
result = (
    cq.Workplane("YZ")
    .polyline(outer_pts_mm).close()
    .extrude(1120.0)  # extrude along X (positive direction)
)

# Now cut the inner hole
# We need to extrude the inner profile through the whole part
inner_hole = (
    cq.Workplane("YZ")
    .polyline(inner_pts_mm).close()
    .extrude(1120.0)
)

result = result.cut(inner_hole)

# The extrusion direction should be -w (along -X), but since we extruded along +X,
# the part is symmetric. The design says direction = -w, but the result is the same
# if we just mirror or accept the orientation. For correctness, we can mirror if needed.
# Actually the profile is at X=0, extruding along +X gives a part from X=0 to X=1120.
# The design expects extrusion along -w (negative X), so the part would be from X=-1120 to X=0.
# We'll mirror to match the expected orientation.
result = result.mirror("YZ")

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0002\\neg_01/generated.step")
