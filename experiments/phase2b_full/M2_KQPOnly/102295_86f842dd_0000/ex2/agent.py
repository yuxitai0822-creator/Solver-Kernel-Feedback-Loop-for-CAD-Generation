import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions: straight_length = 28.0 mm, radius = 10.0 mm, extrude distance = 4.0 mm
# The stadium profile consists of two arcs (radius 10.0) connected by two lines (length 28.0)
# The profile is defined in the UV plane where U is along the straight length and V is perpendicular.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the profile lies in the XZ plane (U=X, V=-Z) and extrudes along Y (W direction).

# Build the stadium profile in the XY plane for simplicity, then rotate/translate as needed.
# Using the frame: u_dir = X, v_dir = -Z, w_dir = Y
# So the profile is in the X-Z plane, with V = -Z.
# We'll construct the profile in the XY plane (X = U, Y = V) and then rotate to match the frame.

# Create the stadium profile as a wire
# Center of first arc at (1.0, 0.0) in UV, radius 1.0 (but actual radius is 10.0 mm, so scale?)
# Wait: The design plan uses normalized coordinates? Let's check dimensions.
# The dimensions say straight_length = 28.0, radius = 10.0.
# The curves use center_uv with radius 1.0, but that's likely normalized.
# The span along U is 48.0 (from validation), along V is 20.0.
# So the actual stadium has: two arcs of radius 10.0, centers separated by 28.0 (straight length).
# Total length = 28.0 + 2*10.0 = 48.0, width = 2*10.0 = 20.0. Matches validation.
# The curves in the plan have radius 1.0 and centers at (1.0, 0.0) and (3.8, 0.0) -> separation 2.8.
# This is a normalized version (scale factor 10). So we multiply all UV coordinates by 10.

# Build the profile using actual dimensions
radius = 10.0
straight_length = 28.0

# Center of first arc at (0, 0) in UV, second arc at (straight_length, 0) = (28, 0)
# But the plan shows centers at (1.0, 0.0) and (3.8, 0.0) scaled by 10 -> (10, 0) and (38, 0)?
# Actually 1.0*10 = 10, 3.8*10 = 38. So separation = 28.0. Correct.
# The arcs go from 0 to 180 degrees (top half) and 0 to 180 degrees (bottom half?)
# Actually: first arc start_angle=0, end_angle=180 -> goes from right to left along top.
# Second arc start_angle=0, end_angle=180 -> also from right to left along top.
# But the lines connect bottom points: (1.0, -1.0) to (3.8, -1.0) and (3.8, 1.0) to (1.0, 1.0).
# So the stadium is oriented with straight sides on top and bottom? Let's trace:
# Arc1: center (10, 0), radius 10, from angle 0 (point at (20, 0)) to 180 (point at (0, 0)) -> top semicircle
# Line1: from (10, -10) to (38, -10) -> bottom straight
# Arc2: center (38, 0), radius 10, from angle 0 (point at (48, 0)) to 180 (point at (28, 0)) -> top semicircle
# Line2: from (38, 10) to (10, 10) -> top straight
# Wait, this gives a shape with straight sides on top and bottom, arcs on left and right.
# But the start/end points: arc1 goes from (20,0) to (0,0) along top, arc2 from (48,0) to (28,0) along top.
# Lines connect bottom: (10,-10) to (38,-10) and top: (38,10) to (10,10).
# This forms a stadium with arcs on left and right, straight on top and bottom.
# The span U = 48, span V = 20. Correct.

# Let's build this profile in the XY plane (U=X, V=Y) then transform to match frame.
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# So U -> X, V -> -Z, W -> Y
# We'll build in XY plane (X=U, Y=V), then rotate: Y -> -Z, keep X, then Z becomes Y.
# Actually simpler: build directly in the correct orientation.
# The profile lies in the X-Z plane (U=X, V=-Z). So we build in XZ plane.
# Points: arc centers at (10, 0) and (38, 0) in XZ (Z=0).
# Arc1: center (10, 0, 0), radius 10, in XZ plane, from angle 0 to 180.
# But in XZ plane, angle 0 is along +X, angle 90 is along +Z.
# Arc1 from angle 0 (point at (20, 0, 0)) to 180 (point at (0, 0, 0)) goes through +Z side.
# Line1: from (10, 0, -10) to (38, 0, -10) -> along -Z side
# Arc2: center (38, 0, 0), radius 10, from angle 0 (point at (48, 0, 0)) to 180 (point at (28, 0, 0)) -> through +Z
# Line2: from (38, 0, 10) to (10, 0, 10) -> along +Z side
# This gives a stadium in XZ plane, then extrude along Y (W direction).

# Build using CadQuery's workplane
result = (
    cq.Workplane("XZ")
    .moveTo(10, -10)  # start at bottom-left of straight section
    .lineTo(38, -10)  # bottom straight
    .threePointArc((48, 0), (38, 10))  # right arc (center at 38,0)
    .lineTo(10, 10)  # top straight
    .threePointArc((0, 0), (10, -10))  # left arc (center at 10,0)
    .close()
    .extrude(4.0)  # extrude along Y (positive direction)
)

# The extrusion direction is +W = +Y, which matches the frame.
# The profile is centered? Let's check: the profile spans X from 0 to 48, Z from -10 to 10.
# The validation expects span_u=48, span_v=20, span_w=4. This matches.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102295_86f842dd_0000\\ex2/generated.step")
