import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions: straight_length = 28.0 mm, radius = 10.0 mm, extrude distance = 4.0 mm
# The stadium profile consists of two arcs (radius 10) and two lines (length 28).
# The profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so positive V goes downward in Z)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The profile curves (in UV coordinates):
#   Arc1: center (1.0, 0.0), radius 1.0, start_angle 0, end_angle 180
#   Line1: (1.0, -1.0) to (3.8, -1.0)
#   Arc2: center (3.8, 0.0), radius 1.0, start_angle 0, end_angle 180
#   Line2: (3.8, 1.0) to (1.0, 1.0)
#
# The dimensions table says straight_length = 28.0, radius = 10.0.
# The UV coordinates above are scaled by 10 (since radius 1.0 -> 10.0, line length 2.8 -> 28.0).
# So we multiply all UV coordinates by 10.

scale = 10.0

# Build the stadium profile in the XY plane (since we will orient it later)
# We'll create a wire from the scaled points and arcs.

# Points (scaled)
center1 = (1.0 * scale, 0.0)
center2 = (3.8 * scale, 0.0)
p1 = (1.0 * scale, -1.0 * scale)  # start of line1
p2 = (3.8 * scale, -1.0 * scale)  # end of line1
p3 = (3.8 * scale, 1.0 * scale)   # start of line2 (reverse direction)
p4 = (1.0 * scale, 1.0 * scale)   # end of line2

# Build the profile using CadQuery's 2D primitives
# We'll create a Workplane on XY, then use points and arcs.

result = (
    cq.Workplane("XY")
    .moveTo(p1[0], p1[1])
    .threePointArc(
        (center1[0], center1[1] + 1.0 * scale),  # top of arc (center + radius in Y)
        (p4[0], p4[1])
    )
    .lineTo(p3[0], p3[1])
    .threePointArc(
        (center2[0], center2[1] - 1.0 * scale),  # bottom of arc (center - radius in Y)
        (p2[0], p2[1])
    )
    .lineTo(p1[0], p1[1])  # close the profile
    .close()
    .extrude(4.0)  # extrude along Z (which corresponds to +w direction = Y in original frame)
)

# The above extrudes along Z, but the design plan says w_dir = (0,1,0) i.e. Y axis.
# We need to rotate the result so that the extrusion direction aligns with Y.
# The profile was built in XY plane (normal Z). We want the profile normal to be -Z (v_dir) and extrude along Y.
# Actually, the original frame: u_dir = X, v_dir = -Z, w_dir = Y.
# Our current result has profile in XY (normal Z), extruded along Z.
# To match: we need profile normal = -Z, extrude = Y.
# So rotate 90 degrees around X axis: Z -> -Y, Y -> Z. That doesn't match.
# Better: build the profile in XZ plane with normal Y, then extrude along Y.
# Let's redo properly.

# Redo: profile in XZ plane (so normal is Y). Then extrude along Y.
# In XZ plane: u_dir = X, v_dir = Z (but we need v_dir = -Z, so we flip).
# We'll build in XZ with reversed v.

result = (
    cq.Workplane("XZ")
    .moveTo(p1[0], -p1[1])  # flip Y to Z and negate for v_dir = -Z
    .threePointArc(
        (center1[0], -(center1[1] + 1.0 * scale)),
        (p4[0], -p4[1])
    )
    .lineTo(p3[0], -p3[1])
    .threePointArc(
        (center2[0], -(center2[1] - 1.0 * scale)),
        (p2[0], -p2[1])
    )
    .lineTo(p1[0], -p1[1])
    .close()
    .extrude(4.0)  # extrudes along Y (normal of XZ plane)
)

# Now the result has profile in XZ (normal Y), extruded along Y.
# But the profile orientation: u_dir = X, v_dir = -Z (since we negated Y coordinate).
# Extrude direction = +Y = +w. This matches the design plan.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102295_86f842dd_0000\neg_01/generated.step")