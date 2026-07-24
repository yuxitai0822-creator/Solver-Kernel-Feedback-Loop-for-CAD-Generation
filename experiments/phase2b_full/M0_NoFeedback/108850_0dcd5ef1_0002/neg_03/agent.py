import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u-direction) = 171.45 mm, Width (v-direction) = 38.1 mm, Extrude distance (w-direction) = 6.35 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle is in the X-Z plane (using u and v), extruded along Y (w direction)

# Build the rectangle profile in the XZ plane
# The rectangle corners in UV space: (0,0), (171.45,0), (171.45,38.1), (0,38.1)
# But note: v_dir = [0,0,-1], so v coordinate maps to -Z
# So point (u,v) maps to (u, 0, -v) in world coordinates
# To keep the plate centered or at origin, we'll place it so that the minimum corner is at (0,0,0)
# That means: u=0 -> x=0, v=0 -> z=0, so the rectangle goes from (0,0,0) to (171.45, 0, -38.1)
# Then extrude along Y (w direction) by 6.35 mm

# Create the rectangle as a wire
rect = cq.Workplane("XZ").rect(171.45, 38.1, centered=False).extrude(6.35)

# The rect is created with the rectangle in XZ plane, extruded in Y direction
# But the default orientation: rect in XZ plane, centered at origin by default
# We used centered=False, so the rectangle starts at (0,0) in the workplane
# In the XZ workplane, (0,0) is at the origin, and the rectangle extends to (171.45, 38.1)
# This matches our mapping: u->X, v->Z (positive), but we need v-> -Z
# To correct: we need to mirror or adjust the orientation

# Let's rebuild with explicit vertex placement to match the design plan exactly
# The design plan specifies:
#   start_uv: (0.0, 3.81) -> end_uv: (0.0, 0.0)  (line along -v direction)
#   start_uv: (0.0, 0.0) -> end_uv: (17.145, 0.0) (line along +u direction)
#   start_uv: (17.145, 0.0) -> end_uv: (17.145, 3.81) (line along +v direction)
#   start_uv: (17.145, 3.81) -> end_uv: (0.0, 3.81) (line along -u direction)
# Note: the UV values are in cm (since unit_conversion_applied: cm_to_mm x10)
# So 17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm
# The rectangle goes from (0,0) to (171.45, 38.1) in UV space
# With u_dir = X, v_dir = -Z, the world coordinates are:
#   (u, 0, -v)
# So the rectangle corners in world:
#   (0, 0, 0), (171.45, 0, 0), (171.45, 0, -38.1), (0, 0, -38.1)
# Extrude along w_dir = Y by 6.35 mm

# Build using a polyline
pts = [
    (0.0, 0.0, 0.0),
    (171.45, 0.0, 0.0),
    (171.45, 0.0, -38.1),
    (0.0, 0.0, -38.1),
    (0.0, 0.0, 0.0)  # close
]

# Create the base rectangle as a wire
wire = cq.Workplane("XY").polyline(pts).close().extrude(6.35)

# But this extrudes along Z, not Y. We need to extrude along Y.
# Let's use a different approach: create the face in the XZ plane and extrude along Y

# Create the rectangle in XZ plane
# Points in XZ plane: (x, 0, z)
pts_xz = [
    (0.0, 0.0, 0.0),
    (171.45, 0.0, 0.0),
    (171.45, 0.0, -38.1),
    (0.0, 0.0, -38.1),
    (0.0, 0.0, 0.0)
]

# Build using a workplane on the XZ plane
result = cq.Workplane("XZ").polyline(pts_xz).close().extrude(6.35)

# The extrude direction for Workplane("XZ") is along the normal of XZ, which is Y
# So this should give us a plate from y=0 to y=6.35

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108850_0dcd5ef1_0002\\neg_03/generated.step")
