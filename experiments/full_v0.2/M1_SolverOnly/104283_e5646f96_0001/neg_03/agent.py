import cadquery as cq

# Design Plan: Extruded profile with a circular hole
# The profile consists of an outer shape (rectangle with rounded corners approximated by a circle) and an inner circle (hole)
# Based on the design plan, the outer profile is defined by:
#   - A vertical line from (0.9188, 1.7937) to (0.9188, 0.0)
#   - A horizontal line from (0.9188, 0.0) to (3.8000, 0.0)
#   - A vertical line from (3.7174, 1.7937) to (3.7174, 0.0)
#   - A circle centered at (2.3181, 1.7491) with radius 1.4
# The inner hole is a circle centered at (2.3181, 1.7491) with radius 1.25
# Extrude distance: 18.0 mm

# Note: The coordinates in the design plan are in mm (converted from cm).
# The outer profile is a closed loop: start at (0.9188, 1.7937), go down to (0.9188, 0.0), right to (3.8000, 0.0), up to (3.7174, 1.7937), then arc to close.
# However, the circle center is at (2.3181, 1.7491) with radius 1.4, which connects the two vertical lines at the top.
# We'll construct the profile using CadQuery's wire and face building.

# Build the outer profile as a closed wire
# Points (in XY plane):
# P1 = (0.9188335453558412, 1.7936743887554851)
# P2 = (0.9188335453558412, 0.0)
# P3 = (3.8000000566244125, 0.0)
# P4 = (3.7174115708793822, 1.7936743887554851)
# The top edge is a circular arc from P4 to P1 with center at (2.3181225581176115, 1.7490620724718653) radius 1.4

# We'll use cq.Workplane to build the shape

# Start with a workplane
result = cq.Workplane("XY")

# Build the outer profile by creating a polygon with the straight edges and then adding the arc
# Since CadQuery's polygon doesn't support arcs directly, we'll use a different approach:
# Create the outer shape by sweeping a circle along a path? No, better to use 2D construction.

# Alternative: Use cq.Wire.makeCircle for the arc and cq.Wire.makeLine for the straight edges, then combine.
# But simpler: approximate the outer shape as a rectangle with a circular top.
# Actually, the design plan shows the outer profile is a closed loop with 4 curves: 3 lines and 1 circle.
# The circle is the top edge, and the lines form the left, bottom, and right edges.
# So the shape is like a "D" shape: flat bottom and sides, rounded top.

# Let's construct the wire manually:

# Define points
p1 = (0.9188335453558412, 1.7936743887554851)
p2 = (0.9188335453558412, 0.0)
p3 = (3.8000000566244125, 0.0)
p4 = (3.7174115708793822, 1.7936743887554851)
center = (2.3181225581176115, 1.7490620724718653)
radius_outer = 1.4
radius_inner = 1.25

# Create the outer wire
# We'll build edges and then combine into a wire

# Edge 1: line from p1 to p2
edge1 = cq.Edge.makeLine(cq.Vector(p1[0], p1[1], 0), cq.Vector(p2[0], p2[1], 0))
# Edge 2: line from p2 to p3
edge2 = cq.Edge.makeLine(cq.Vector(p2[0], p2[1], 0), cq.Vector(p3[0], p3[1], 0))
# Edge 3: line from p3 to p4
edge3 = cq.Edge.makeLine(cq.Vector(p3[0], p3[1], 0), cq.Vector(p4[0], p4[1], 0))
# Edge 4: circular arc from p4 to p1 (counterclockwise? The design plan shows start_uv and end_uv, but we need to ensure proper orientation)
# The arc should go from p4 to p1 with center at (2.3181, 1.7491) and radius 1.4
# We need to determine the start and end angles
# Vector from center to p4: (3.7174-2.3181, 1.7937-1.7491) = (1.3993, 0.0446)
# Vector from center to p1: (0.9188-2.3181, 1.7937-1.7491) = (-1.3993, 0.0446)
# The arc goes from p4 to p1, likely clockwise or counterclockwise. We'll use the normal direction.
# Since the shape is a closed loop, the arc should be the top part.
# We'll create the arc using makeCircle with angle parameters.

# Compute angles
import math
v4 = cq.Vector(p4[0] - center[0], p4[1] - center[1], 0)
v1 = cq.Vector(p1[0] - center[0], p1[1] - center[1], 0)
angle_start = math.atan2(v4.y, v4.x)  # angle of p4 relative to center
angle_end = math.atan2(v1.y, v1.x)    # angle of p1 relative to center
# The arc should go from p4 to p1 in the positive (counterclockwise) direction
# If angle_end < angle_start, add 2*pi to angle_end
if angle_end < angle_start:
    angle_end += 2 * math.pi

# Create the arc
edge4 = cq.Edge.makeCircle(radius_outer, cq.Vector(center[0], center[1], 0), 
                           angle1=math.degrees(angle_start), angle2=math.degrees(angle_end))

# Combine edges into a wire
outer_wire = cq.Wire.assembleEdges([edge1, edge2, edge3, edge4])

# Create the inner circle wire
inner_circle = cq.Wire.makeCircle(radius_inner, cq.Vector(center[0], center[1], 0))

# Create a face from the outer wire with a hole
# We need to create a planar face with the outer boundary and subtract the inner circle
# Use cq.Face.makeFromWires
outer_face = cq.Face.makeFromWires(outer_wire, [inner_circle])

# Extrude the face
solid = cq.Solid.extrudeFace(outer_face, cq.Vector(0, 0, 18.0))

# Convert to Workplane for export
result = cq.Workplane("XY").newObject([solid])

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0001\\neg_03/generated.step")
