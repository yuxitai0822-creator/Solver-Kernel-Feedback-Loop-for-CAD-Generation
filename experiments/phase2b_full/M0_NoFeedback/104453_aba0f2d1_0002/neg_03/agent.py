import cadquery as cq

# Design Plan: stadium extrusion (ArmRest v1)
# Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
# Note: The design plan uses a coordinate system with origin at bbox_min_corner.
# We build the stadium profile in the XY plane (u=x, v=y) and extrude along Z (+w).

# Create the stadium profile:
# The stadium consists of two arcs (radius 50) at ends and two straight lines (length 500).
# Total length along u (x) = 500 + 2*50 = 600, width along v (y) = 2*50 = 100.
# We place the shape so that the origin (0,0) is at the bottom-left corner of the bounding box.
# The profile is centered at y=50 (since radius=50, total height=100).
# We'll build it using CadQuery's 2D primitives.

# Build the stadium as a wire, then make a face, then extrude.

# Parameters
straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile using lines and arcs.
# We'll start at the bottom-left corner of the straight section: (0, 0)
# Then go right along bottom line: (straight_length, 0)
# Then arc to top: (straight_length, 2*radius)
# Then left along top line: (0, 2*radius)
# Then arc back to start: (0, 0)

# However, the design plan's curves are defined with center_uv and start/end angles.
# Let's follow the exact geometry from the plan:
# Arc1: center (0,0), radius 5? Wait, the plan says radius=5.0 in curves but dimensions say radius=50.0.
# The curves section has radius=5.0, but dimensions section says radius=50.0.
# The compiler note says unit_conversion_applied: cm_to_mm (x10).
# So the curves radius=5.0 in the plan is actually 50 mm after conversion.
# Similarly, the straight_length in curves is 50.0 (from 0 to 50) but dimensions say 500.0.
# So we use the dimensions values: straight_length=500.0, radius=50.0.

# Build the profile using CadQuery's 2D construction.
# We'll create a workplane and use the standard stadium approach.

result = (
    cq.Workplane("XY")
    .center(0, 0)  # origin at bottom-left corner of bounding box
    .moveTo(0, 0)
    .lineTo(straight_length, 0)  # bottom line
    .threePointArc(
        (straight_length + radius, radius),
        (straight_length, 2*radius)
    )  # right arc (center at (straight_length, radius))
    .lineTo(0, 2*radius)  # top line
    .threePointArc(
        (-radius, radius),
        (0, 0)
    )  # left arc (center at (0, radius))
    .close()
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104453_aba0f2d1_0002\\neg_03/generated.step")
