import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm (explicit)
#
# The stadium profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so v points downward in Z)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The profile curves (in UV coordinates):
#   Arc1: center (1.0, 0.0), radius 1.0, start 0°, end 180°
#   Line1: (1.0, -1.0) to (3.8, -1.0)
#   Arc2: center (3.8, 0.0), radius 1.0, start 0°, end 180°
#   Line2: (3.8, 1.0) to (1.0, 1.0)
#
# The UV coordinates are scaled by the radius (10 mm) and straight_length (28 mm).
# The arc radius in UV is 1.0, which maps to radius=10 mm.
# The straight segment length in UV is (3.8 - 1.0) = 2.8, which maps to 28 mm.
# So scaling factor = 10.
#
# After scaling:
#   Arc1: center (10, 0), radius 10, start 0°, end 180°
#   Line1: (10, -10) to (38, -10)
#   Arc2: center (38, 0), radius 10, start 0°, end 180°
#   Line2: (38, 10) to (10, 10)
#
# The profile lies in the XY plane (since u->X, v->-Z, but we'll build in XY and then rotate).
# Actually, simpler: build the stadium in the XY plane (X=u, Y=v) and then orient.
# But v_dir = (0,0,-1) means v maps to -Z. So we build in XZ plane with v as -Z.
# Let's build in the XZ plane: X = u, Z = -v.
# Then extrude in Y direction (w_dir = (0,1,0)).

# Build the stadium profile in the XZ plane
# We'll use a workplane on the XZ plane (Y=0)

# Create the stadium shape using a series of edges
# Start with the first arc (top arc in UV, but in XZ it's the arc at positive Z? Let's be careful)
# UV: v positive is "up" in UV, but v_dir = (0,0,-1) so v positive maps to Z negative.
# So the profile in XZ:
#   Arc1: center (10, 0) in XZ, radius 10, from angle 0° to 180° (counterclockwise from +X axis)
#         This arc goes from (20, 0) to (0, 0) through the upper half (positive Z? Actually angle 0° is +X, 180° is -X, so it goes through +Z? No, standard math: 0° = (R,0), 90° = (0,R), 180° = (-R,0). So it goes through positive Z (since Z is the second coordinate).
#   Line1: from (20, 0) to (38, 0)? Wait, start_uv of line1 is (1.0, -1.0) scaled = (10, -10). In XZ that's (10, 10) because Z = -v. So line1 goes from (10, 10) to (38, 10).
#   Arc2: center (38, 0), radius 10, from 0° to 180°: goes from (48, 0) to (28, 0) through positive Z.
#   Line2: from (38, -10) in UV = (38, 10) in XZ to (10, -10) in UV = (10, 10) in XZ.
#
# Actually let's just build it step by step with wires.

# Scale factor
R = 10.0  # radius
L = 28.0  # straight length
# The UV coordinates: arc centers at (1,0) and (1+2.8, 0) = (3.8, 0)
# Scaled: centers at (10, 0) and (38, 0)
# Arc radius = 10
# Line endpoints: (10, -10) to (38, -10) and (38, 10) to (10, 10)

# Build in XZ plane (Y=0)
# We'll create a wire from edges

# Arc1: center (10, 0), radius 10, start 0°, end 180°
# In XZ plane, this arc goes from (20, 0) to (0, 0) through positive Z
arc1 = cq.Edge.makeCircle(
    radius=R,
    center=cq.Vector(10, 0, 0),
    normal=cq.Vector(0, -1, 0),  # normal pointing in -Y to get arc in XZ plane
    angle1=0,
    angle2=180
)

# Line1: from (10, -10) in UV -> in XZ: (10, 10) to (38, 10)
line1 = cq.Edge.makeLine(
    cq.Vector(10, 0, 10),
    cq.Vector(38, 0, 10)
)

# Arc2: center (38, 0), radius 10, start 0°, end 180°
# Goes from (48, 0) to (28, 0) through positive Z
arc2 = cq.Edge.makeCircle(
    radius=R,
    center=cq.Vector(38, 0, 0),
    normal=cq.Vector(0, -1, 0),
    angle1=0,
    angle2=180
)

# Line2: from (38, 10) to (10, 10) in XZ
line2 = cq.Edge.makeLine(
    cq.Vector(38, 0, 10),
    cq.Vector(10, 0, 10)
)

# Combine into a wire
wire = cq.Wire.assembleEdges([arc1, line1, arc2, line2])

# Create a face from the wire
face = cq.Face.makeFromWires(wire)

# Extrude along Y (w_dir) by 4.0 mm
# The extrude direction is +w = (0,1,0)
result = cq.Workplane("XY").newObject([face]).extrude(4.0)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
