import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm
#
# The stadium profile consists of two arcs (radius 10.0) connected by two lines.
# The arcs are centered at (1.0, 0.0) and (3.8, 0.0) in UV space, but these are
# normalized coordinates. The actual dimensions are: straight_length = 28.0 mm,
# radius = 10.0 mm. So the total width = 2*radius + straight_length = 20 + 28 = 48 mm.
# The height = 2*radius = 20 mm.
#
# We build the stadium profile in the XY plane, then extrude in the Z direction.

# Parameters
radius = 10.0
straight_length = 28.0
extrude_distance = 4.0

# Total width of stadium
width = 2 * radius + straight_length  # 48.0 mm
height = 2 * radius  # 20.0 mm

# Build the stadium profile using CadQuery's 2D construction
# We'll create a workplane and draw the profile
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(-width/2 + radius, 0)  # start at left arc top? Actually start at rightmost point of left arc
    # Better approach: use two arcs and two lines
    # Left arc: center at (-straight_length/2, 0), radius=radius, from 90° to -90° (or 0 to 180)
    # Actually let's use the standard stadium: two semicircles on left and right, connected by lines
    # Left semicircle: center at (-straight_length/2, 0), radius=radius, from 90° to -90° (going clockwise)
    # Right semicircle: center at (straight_length/2, 0), radius=radius, from -90° to 90°
    # Lines: top and bottom
    
    # Start at top of left arc
    .moveTo(-straight_length/2, radius)
    # Left arc (clockwise from top to bottom)
    .threePointArc(
        (-straight_length/2 - radius, 0),
        (-straight_length/2, -radius)
    )
    # Bottom line
    .lineTo(straight_length/2, -radius)
    # Right arc (clockwise from bottom to top)
    .threePointArc(
        (straight_length/2 + radius, 0),
        (straight_length/2, radius)
    )
    # Top line back to start
    .lineTo(-straight_length/2, radius)
    .close()
    # Extrude
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102295_86f842dd_0000\\ex2/generated.step")
