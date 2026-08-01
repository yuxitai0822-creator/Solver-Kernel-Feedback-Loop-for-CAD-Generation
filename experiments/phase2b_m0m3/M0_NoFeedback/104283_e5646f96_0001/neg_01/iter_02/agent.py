import cadquery as cq
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0001\neg_01\iter_02\generated.step"

# Design Plan interpretation:
# - Single body with an extruded profile that has a circular top and a through hole
# - The outer profile is a rectangle with a circular arc at the top
# - The inner profile is a circle (hole)
# - Extrude 18.0 mm in +Z direction

# Build the outer profile using a proper closed wire
# Points from the design plan:
p1 = (0.9188335453558412, 0.0)  # bottom-left
p2 = (3.8000000566244125, 0.0)  # bottom-right
p3 = (3.7174115708793822, 1.7936743887554851)  # right-top (arc start)
p4 = (0.9188335453558412, 1.7936743887554851)  # left-top (arc end)

# Center and radius for the top arc
center = (2.3181225581176115, 1.7490620724718653)
radius = 1.4

# Create the outer wire using a more robust approach: build edges and then make a wire
# Start with the bottom edge
L1 = cq.Edge.makeLine(cq.Vector(p1[0], p1[1], 0), cq.Vector(p2[0], p2[1], 0))
# Right vertical edge
L2 = cq.Edge.makeLine(cq.Vector(p2[0], p2[1], 0), cq.Vector(p3[0], p3[1], 0))
# Top arc from p3 to p4 (counterclockwise)
# Calculate angles for the arc
start_angle = math.atan2(p3[1] - center[1], p3[0] - center[0])
end_angle = math.atan2(p4[1] - center[1], p4[0] - center[0])
# Ensure the arc goes the correct way (counterclockwise from p3 to p4)
# p3 is to the right, p4 is to the left, so we go through the top
# The arc should sweep from start_angle to end_angle going through the top
# Since start_angle is negative (below center) and end_angle is also negative but larger,
# we need to go counterclockwise from start_angle to end_angle + 2*pi
if end_angle < start_angle:
    end_angle += 2 * math.pi
A1 = cq.Edge.makeCircle(radius, cq.Vector(center[0], center[1], 0), 
                         angle1=math.degrees(start_angle), 
                         angle2=math.degrees(end_angle))
# Left vertical edge
L3 = cq.Edge.makeLine(cq.Vector(p4[0], p4[1], 0), cq.Vector(p1[0], p1[1], 0))

# Combine edges into a wire
wire = cq.Wire.combine([L1, L2, A1, L3])

# Create a face from the wire
face = cq.Face.makeFromWires(wire)

# Extrude the face to create the solid
result = cq.Workplane("XY").newObject([face]).extrude(18.0)

# Now create the inner hole (circle at center with radius 1.25)
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.2500000000000002

# Cut the inner hole using a cylinder
hole = cq.Workplane("XY").moveTo(inner_center[0], inner_center[1]).circle(inner_radius).extrude(18.0)
result = result.cut(hole)

cq.exporters.export(result, OUT_STEP_PATH)