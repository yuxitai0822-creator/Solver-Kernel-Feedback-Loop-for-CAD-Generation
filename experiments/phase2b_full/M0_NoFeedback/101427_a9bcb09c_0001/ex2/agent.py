import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: width (u) = 198.0 mm, height (v) = 60.0 mm (scaled from 1980/600 by 0.1? Actually plan says 1980 and 600 but unit is mm, so we use as is)
# Wait: The plan says unit is mm, but the coordinates in profiles are small (e.g., -2.5 to 195.5). 
# The dimensions say outer_length_u = 1980.0, outer_width_v = 600.0, inner_length_u = 1930.0, inner_width_v = 550.0.
# The profile coordinates span from -2.5 to 195.5 in u and -2.5 to 57.5 in v, which is 198 x 60. 
# This suggests the plan was originally in cm and converted to mm (x10), but the profile coordinates are in cm? 
# Actually the compiler note says "cm_to_mm (x10)". So the profile coordinates are in cm, and dimensions are in mm.
# We need to scale the profile coordinates by 10 to get mm.
# Outer: u from -2.5 to 195.5 => width = 198.0 cm = 1980 mm. v from -2.5 to 57.5 => height = 60.0 cm = 600 mm.
# Inner: u from 0.0 to 193.0 => width = 193.0 cm = 1930 mm. v from 0.0 to 55.0 => height = 55.0 cm = 550 mm.
# Extrude distance = 25.0 mm (already mm).
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0). So u is X, v is -Z, w is Y.
# We'll build the profile in the XY plane (since extrude is along w = Y), but the profile is defined in uv plane.
# Let's map: u -> X, v -> Z (but v_dir is (0,0,-1), so v coordinate maps to -Z).
# Simpler: build the rectangle in XY plane, then rotate/translate as needed.
# Actually, let's just build the profile in the XY plane with u=X, v=Y, then extrude along Z (w).
# But the plan says w_dir = (0,1,0), so extrude along Y. We'll adapt.

# Scale factor: 10 (cm to mm)
scale = 10.0

# Outer rectangle corners (in cm, from profile)
outer_pts_cm = [
    (-2.5, -2.5),
    (195.5, -2.5),
    (195.5, 57.5),
    (-2.5, 57.5),
]
# Inner rectangle corners (in cm)
inner_pts_cm = [
    (0.0, 0.0),
    (193.0, 0.0),
    (193.0, 55.0),
    (0.0, 55.0),
]

# Scale to mm
outer_pts = [(x*scale, y*scale) for x,y in outer_pts_cm]
inner_pts = [(x*scale, y*scale) for x,y in inner_pts_cm]

# Build the profile as a wire in XY plane (u=X, v=Y)
# We'll create the outer rectangle and inner rectangle as separate wires, then make a compound wire for the face.
outer_wire = cq.Workplane("XY").polyline(outer_pts).close().wire()
inner_wire = cq.Workplane("XY").polyline(inner_pts).close().wire()

# Create the face with a hole: make a plane from outer wire, then cut inner
# Using cq.Workplane to build the face
result = (
    cq.Workplane("XY")
    .polyline(outer_pts).close()
    .extrude(25.0)  # extrude along Z (positive)
)

# Now we need to cut the inner rectangle. But we extruded the outer rectangle as a solid.
# Better: create the profile as a face with a hole, then extrude.
# Let's do it properly:

# Create outer rectangle as a closed wire
outer = cq.Wire.makePolygon([cq.Vector(x,y,0) for x,y in outer_pts], close=True)
# Create inner rectangle as a closed wire
inner = cq.Wire.makePolygon([cq.Vector(x,y,0) for x,y in inner_pts], close=True)

# Create a compound wire for the face (outer with inner hole)
# We need to build a face from the outer wire and then cut the inner wire
# Using cq.Face.makeFromWires
face = cq.Face.makeFromWires(outer, [inner])

# Extrude the face along Z by 25 mm
solid = cq.Solid.extrudeLinear(face, cq.Vector(0,0,25.0))

# The result should be a single solid
result = cq.Workplane("XY").newObject([solid])

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\101427_a9bcb09c_0001\ex2/generated.step")
