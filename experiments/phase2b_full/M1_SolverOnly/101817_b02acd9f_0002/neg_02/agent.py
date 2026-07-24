import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
# Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
# Extrude direction: -w (which maps to -x in world coordinates per frame axes)
# Extrude distance: 1120.0 mm

# Create the outer rectangle profile
outer = (
    cq.Workplane("XY")
    .moveTo(-6.12, 10.88)
    .lineTo(-6.12, 15.12)
    .lineTo(-1.88, 15.12)
    .lineTo(-1.88, 10.88)
    .close()
)

# Create the inner rectangle profile (cutout)
inner = (
    cq.Workplane("XY")
    .moveTo(-6.0, 11.0)
    .lineTo(-6.0, 15.0)
    .lineTo(-2.0, 15.0)
    .lineTo(-2.0, 11.0)
    .close()
)

# Combine: outer rectangle with inner hole
# We build the outer as a solid, then cut the inner
result = (
    cq.Workplane("XY")
    .moveTo(-6.12, 10.88)
    .lineTo(-6.12, 15.12)
    .lineTo(-1.88, 15.12)
    .lineTo(-1.88, 10.88)
    .close()
    .extrude(1120.0)  # extrude in +Z (which corresponds to -w after rotation? We'll handle orientation)
)

# The design plan says extrude direction is -w, and w_dir = [1,0,0] (X axis)
# So -w means extrude in -X direction. But we extruded in +Z.
# We need to rotate the result so that the extrusion direction aligns with -X.
# The frame axes: u_dir = [0,0,-1] (Z-), v_dir = [0,1,0] (Y), w_dir = [1,0,0] (X)
# Our sketch is in XY plane (normal = Z+). We want the extrusion to go along -X.
# So we need to rotate: align Z+ to X-? Actually we want the sketch plane normal to be aligned with w_dir? 
# Let's think: The profile is defined in UV plane. u_dir = -Z, v_dir = Y. So UV plane is Y-Z plane (normal = X).
# The extrude direction is -w = -X. So we should sketch on YZ plane and extrude in -X.
# But our coordinates are given in UV space. Let's map: U = -Z, V = Y.
# So point (-6.12, 10.88) in UV means: U=-6.12 -> Z=6.12, V=10.88 -> Y=10.88.
# So the outer rectangle in YZ plane: Y from 10.88 to 15.12, Z from -6.12 to -1.88? Wait careful:
# U = -Z, so Z = -U. So U=-6.12 => Z=6.12, U=-1.88 => Z=1.88. So Z range is 1.88 to 6.12.
# V = Y, so Y range is 10.88 to 15.12.
# So outer rectangle: Y in [10.88, 15.12], Z in [1.88, 6.12].
# Inner rectangle: Y in [11.0, 15.0], Z in [2.0, 6.0].
# Extrude in -X direction (negative X) by 1120.0 mm.

# Let's rebuild correctly:
outer_pts = [
    (10.88, 1.88),  # (Y, Z) for start? Actually we need to traverse correctly.
    # From design: start_uv = (-1.88, 10.88) => U=-1.88 => Z=1.88, V=10.88 => Y=10.88
    # end_uv = (-1.88, 15.12) => Z=1.88, Y=15.12
    # end_uv = (-6.12, 15.12) => Z=6.12, Y=15.12
    # end_uv = (-6.12, 10.88) => Z=6.12, Y=10.88
    # back to start
]
# So in YZ plane, the rectangle goes: (Y=10.88, Z=1.88) -> (Y=15.12, Z=1.88) -> (Y=15.12, Z=6.12) -> (Y=10.88, Z=6.12)

inner_pts = [
    # start_uv = (-6.0, 11.0) => Z=6.0, Y=11.0
    # end_uv = (-2.0, 11.0) => Z=2.0, Y=11.0
    # end_uv = (-2.0, 15.0) => Z=2.0, Y=15.0
    # end_uv = (-6.0, 15.0) => Z=6.0, Y=15.0
]
# So inner: (Y=11.0, Z=6.0) -> (Y=11.0, Z=2.0) -> (Y=15.0, Z=2.0) -> (Y=15.0, Z=6.0)

# Build on YZ plane (normal = X), extrude in -X direction
result = (
    cq.Workplane("YZ")
    .moveTo(10.88, 1.88)
    .lineTo(15.12, 1.88)
    .lineTo(15.12, 6.12)
    .lineTo(10.88, 6.12)
    .close()
    .extrude(-1120.0)  # extrude in -X direction
)

# Now cut the inner rectangle
# We need to create the inner rectangle as a separate solid and cut it
inner_solid = (
    cq.Workplane("YZ")
    .moveTo(11.0, 6.0)
    .lineTo(11.0, 2.0)
    .lineTo(15.0, 2.0)
    .lineTo(15.0, 6.0)
    .close()
    .extrude(-1120.0)
)

result = result.cut(inner_solid)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0002\\neg_02/generated.step")
