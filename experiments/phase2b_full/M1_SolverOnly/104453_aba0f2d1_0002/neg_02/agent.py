import cadquery as cq

# Design Plan: stadium extrusion (ArmRest v1)
# Dimensions:
#   straight_length = 500.0 mm (inferred from point span)
#   radius = 50.0 mm (from curve field)
#   extrude distance = 100.0 mm
# Note: The plan's profile curves use radius=5.0 and straight_length=50.0 in UV,
# but the dimensions section says straight_length=500.0 and radius=50.0.
# The dimensions section is the authoritative source for the final part size.
# Therefore we scale the UV profile by 10x to match the intended dimensions.

# Build the stadium profile in the XY plane (u=x, v=y, w=z)
# Center of first arc at (0,0), radius=50, from 0 to 180 deg (top half)
# Then line from (0,-50) to (500,-50) (bottom edge)
# Then arc at (500,0), radius=50, from 0 to 180 deg (top half, but actually bottom arc?)
# Wait: arcs are drawn from start_angle=0 to end_angle=180, which in standard math is counterclockwise from +x.
# For a stadium shape, the arcs should be at the ends, connecting the two lines.
# Let's trace carefully:
#   Arc1: center (0,0), radius 50, start_angle=0 -> end_angle=180: this draws a semicircle from (50,0) to (-50,0) going through (0,50)?
#   Actually start_angle=0 is along +x axis, end_angle=180 is along -x axis, so it goes through the upper half (positive y).
#   Then line from (0,-50) to (500,-50): bottom straight edge.
#   Then Arc2: center (500,0), radius 50, start_angle=0 -> end_angle=180: from (550,0) to (450,0) through (500,50)? That would be upper half again.
#   Then line from (500,50) to (0,50): top straight edge.
# This gives a stadium shape with arcs on the left and right ends, but the arcs are on the top? Let's check:
#   The first arc goes from (50,0) to (-50,0) via upper half -> left end cap.
#   The second arc goes from (550,0) to (450,0) via upper half -> right end cap.
#   The bottom line connects (-50,0) to (450,0)? No, the line endpoints are (0,-50) to (500,-50).
#   The top line connects (500,50) to (0,50).
# This is inconsistent: the arcs endpoints are at y=0, but lines are at y=±50.
# The correct stadium: arcs at ends, lines connecting top and bottom.
# Let's reinterpret: The UV coordinates given are in a local frame where the stadium is aligned with u-axis.
#   Arc1: center (0,0), radius 5, start_angle=0 -> 180: this is a semicircle from (5,0) to (-5,0) going through (0,5) (upper half).
#   Line1: from (0,-5) to (50,-5): bottom edge.
#   Arc2: center (50,0), radius 5, start_angle=0 -> 180: from (55,0) to (45,0) through (50,5) (upper half).
#   Line2: from (50,5) to (0,5): top edge.
# This forms a closed loop: start at (5,0) -> arc to (-5,0) -> line to (50,-5) -> arc to (55,0) -> line to (5,0)? No, line2 goes from (50,5) to (0,5).
# Actually the loop order: arc1 (from (5,0) to (-5,0) via upper), line1 (from (-5,0) to (45,-5)? No, line1 is from (0,-5) to (50,-5).
# The endpoints don't match: arc1 ends at (-5,0), line1 starts at (0,-5). There's a gap.
# This suggests the UV coordinates are not meant to be directly connected; they define the shape in a parametric sense.
# Given the dimensions section says straight_length=500, radius=50, we'll build a proper stadium shape.

# Build a proper stadium: two semicircles of radius 50 at ends, connected by straight lines of length 500.
# Total length along u = 2*radius + straight_length = 100 + 500 = 600.
# Total width along v = 2*radius = 100.

# Create the stadium profile using CadQuery's 2D construction
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .hLine(500)  # bottom edge from (0,0) to (500,0)
    .threePointArc((550, 50), (500, 100))  # right semicircle (center at 500,50)
    .hLine(-500)  # top edge from (500,100) to (0,100)
    .threePointArc((-50, 50), (0, 0))  # left semicircle (center at 0,50)
    .close()
    .extrude(100.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\104453_aba0f2d1_0002\neg_02/generated.step")
