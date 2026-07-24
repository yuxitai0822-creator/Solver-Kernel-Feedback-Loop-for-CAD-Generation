import cadquery as cq

# Design Plan: stadium extrusion (ArmRest v1)
# Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
# Note: The design plan uses a stadium profile with two arcs (radius 5.0) and two lines (length 50.0).
# However, the dimensions section says straight_length=500.0 and radius=50.0.
# The profile curves use radius=5.0 and line length 50.0, which is inconsistent with the dimensions.
# We follow the explicit curve data: radius=5.0, line length=50.0 (so total length = 50+2*5 = 60? Actually the lines go from 0 to 50, so straight part = 50, radius=5, total width = 10, total length = 50+10=60).
# But the dimensions say straight_length=500, radius=50. We'll use the dimensions as they are the explicit dimensions.
# Let's re-read: The curves have start_uv/end_uv with values like 0.0,-5.0 to 50.0,-5.0 (line length 50) and radius 5.0.
# The dimensions section says straight_length=500, radius=50. This is likely a scaling factor of 10 (since unit conversion was cm_to_mm x10).
# So we scale the profile by 10: radius=50, line length=500.
# The extrude distance is 100.0 (already in mm).

# Build the stadium profile
radius = 50.0
length = 500.0

# Create the base rectangle part first, then add arcs
# Using CadQuery's 2D construction
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(0, radius)
    .threePointArc((radius, 0), (0, -radius))  # left arc
    .lineTo(length, -radius)
    .threePointArc((length + radius, 0), (length, radius))  # right arc
    .lineTo(0, radius)
    .close()
    .extrude(100.0)
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\104453_aba0f2d1_0002\neg_01/generated.step")
