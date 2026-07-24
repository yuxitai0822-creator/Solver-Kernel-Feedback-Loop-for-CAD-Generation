import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: from (-6.12, 10.88) to (-1.88, 15.12) in UV plane
# Inner rectangle: from (-6.0, 11.0) to (-2.0, 15.0) in UV plane
# Extrude direction: -w (which maps to -x in world coordinates per frame definition)
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

# Build the frame by extruding the outer profile and cutting the inner
# The frame definition says u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So the profile lies in the V-W plane? Actually the profile is defined in UV coordinates.
# The extrude direction is -w, which is -x in world.
# We'll build the profile on the YZ plane (since w is x) and extrude along -x.

# Rebuild on YZ plane to match frame orientation
# In UV: u is along [0,0,-1] (negative Z), v is along [0,1,0] (Y)
# So profile coordinates: u (Z), v (Y)
# Outer: u from -6.12 to -1.88, v from 10.88 to 15.12
# Inner: u from -6.0 to -2.0, v from 11.0 to 15.0

# Build on YZ plane (Y vertical, Z horizontal)
outer_rect = (
    cq.Workplane("YZ")
    .moveTo(10.88, -6.12)  # (v, u) -> (Y, Z)
    .lineTo(15.12, -6.12)
    .lineTo(15.12, -1.88)
    .lineTo(10.88, -1.88)
    .close()
)

inner_rect = (
    cq.Workplane("YZ")
    .moveTo(11.0, -6.0)
    .lineTo(15.0, -6.0)
    .lineTo(15.0, -2.0)
    .lineTo(11.0, -2.0)
    .close()
)

# Extrude outer along -x (negative w direction) by 1120 mm
frame = outer_rect.extrude(1120.0)

# Cut inner from frame
cutout = inner_rect.extrude(1120.0)
result = frame.cut(cutout)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0002\\neg_03/generated.step")
