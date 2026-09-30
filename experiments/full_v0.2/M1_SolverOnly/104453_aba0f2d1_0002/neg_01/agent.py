import cadquery as cq

# Design Plan: extruded stadium (ArmRest v1)
# Stadium profile: straight length 500 mm, radius 50 mm (scaled from 50.0 and 500.0 in plan)
# Extrude distance: 100 mm

# Build stadium profile using CadQuery's 2D primitives
# The stadium consists of two arcs (radius 50) and two lines (length 500)
# We'll create a wire from points and arcs

# Define points for the stadium profile (centered at origin for convenience)
# Straight section along X from -250 to +250, arcs at ends with radius 50
# Total width = 500 + 2*50 = 600, total height = 2*50 = 100

# Build the profile as a closed wire
pts = [
    (-250.0, -50.0),  # start bottom-left of straight
    (250.0, -50.0),   # bottom-right of straight
    (250.0, 50.0),    # top-right of straight
    (-250.0, 50.0)    # top-left of straight
]

# Create the stadium shape using a workplane and appropriate operations
# Approach: make a rectangle with rounded ends (stadium) using two arcs and two lines
# Use CadQuery's 2D construction

result = (
    cq.Workplane("XY")
    .moveTo(-250.0, -50.0)
    .lineTo(250.0, -50.0)
    .threePointArc((300.0, 0.0), (250.0, 50.0))
    .lineTo(-250.0, 50.0)
    .threePointArc((-300.0, 0.0), (-250.0, -50.0))
    .close()
    .extrude(100.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104453_aba0f2d1_0002\\neg_01/generated.step")
