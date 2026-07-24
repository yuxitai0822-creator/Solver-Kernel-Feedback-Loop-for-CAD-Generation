import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle corners in UV: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 290.379551148076)
# We'll compute width and height from these points.

# Compute rectangle dimensions in UV space
x1, y1 = 121.17356129030935, 31.299551148092803
x2, y2 = -0.7464387096940412, 290.379551148076

# Width along U (x direction in UV)
width_u = abs(x2 - x1)  # 121.92
# Height along V (y direction in UV)
height_v = abs(y2 - y1)  # 259.08

# But the design plan says length_u = 1219.2, width_v = 2590.8
# The UV coordinates seem to be in cm (since compiler notes say cm_to_mm x10).
# Indeed: 121.92 * 10 = 1219.2, 259.08 * 10 = 2590.8
# So we need to scale by 10 to get mm.
scale = 10.0

# Build the rectangle in the UV plane (which is XY in CadQuery, but we need to orient correctly)
# Frame: u_dir = (1,0,0) -> X axis, v_dir = (0,0,-1) -> -Z axis, w_dir = (0,1,0) -> Y axis
# So UV plane is XZ (with V along -Z). We'll create a rectangle on the XZ plane, then extrude along Y.

# Center of rectangle in UV (scaled to mm)
center_u = (x1 + x2) / 2.0 * scale
center_v = (y1 + y2) / 2.0 * scale

# Dimensions in mm
length_u = width_u * scale  # 1219.2
width_v = height_v * scale  # 2590.8

# Create the rectangle on the XZ plane (U->X, V->Z, but V is negative Z, so we flip)
# Actually v_dir = (0,0,-1) means V axis points in -Z direction.
# So a point (u, v) in UV maps to (u, 0, -v) in 3D.
# The rectangle corners in UV: (x1,y1) to (x2,y2)
# In 3D: (x1*scale, 0, -y1*scale) to (x2*scale, 0, -y2*scale)
# We'll build a rectangle centered at (center_u, 0, -center_v) with size length_u x width_v

# But simpler: just create a rectangle on the XZ plane, then extrude along Y (w_dir)
# The rectangle should be centered at the midpoint of the UV bounding box.

# Create the workplane on the XZ plane (front view in CadQuery is YZ, but we can use Plane.XZ())
# Actually cq.Workplane("XZ") gives a plane with X as U, Z as V.
# Our V maps to -Z, so we need to negate the V coordinate.

# Let's build the rectangle directly using vertices.
# Corners in UV (scaled):
p1_uv = (x1 * scale, y1 * scale)
p2_uv = (x2 * scale, y1 * scale)
p3_uv = (x2 * scale, y2 * scale)
p4_uv = (x1 * scale, y2 * scale)

# Map to 3D: (u, 0, -v)
p1 = (p1_uv[0], 0, -p1_uv[1])
p2 = (p2_uv[0], 0, -p2_uv[1])
p3 = (p3_uv[0], 0, -p3_uv[1])
p4 = (p4_uv[0], 0, -p4_uv[1])

# Create a wire from these points
wire = cq.Workplane("XZ").moveTo(p1[0], p1[2]).lineTo(p2[0], p2[2]).lineTo(p3[0], p3[2]).lineTo(p4[0], p4[2]).close().wire()

# Make a face from the wire
face = cq.Face.makeFromWires(wire)

# Extrude along Y (w_dir = (0,1,0)) by 44.45 mm
result = cq.Workplane("XZ").placeSketch(cq.Sketch().face(face)).extrude(44.45)

# Alternative simpler approach: use box with correct dimensions and position
# But the above should work. Let's use a more robust method:

# Actually, let's just use a box centered at the midpoint of the rectangle, oriented correctly.
# The rectangle in 3D is on the plane Y=0, with X from min_u to max_u, Z from -max_v to -min_v.
# Center: (center_u, 0, -center_v)
# Size: length_u (X), 44.45 (Y), width_v (Z)

# This is simpler and guaranteed to produce the correct shape.
result = cq.Workplane("XZ").box(length_u, 44.45, width_v, centered=(True, True, True)).translate((center_u, 0, -center_v))

# But wait: the box is centered, so we need to position it correctly.
# The rectangle spans from min_u to max_u in X, and from -max_v to -min_v in Z.
# Center: ((min_u+max_u)/2, 0, (-max_v + -min_v)/2) = (center_u, 0, -center_v)
# This matches.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108244_329b1876_0000\\neg_02/generated.step")
