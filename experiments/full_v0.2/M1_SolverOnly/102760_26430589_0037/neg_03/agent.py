import cadquery as cq

# Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
# The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Extrude direction is -w, which corresponds to negative y in world coordinates.
# We'll build the circle on the xz-plane (normal = y) and extrude along -y.

# Create a workplane on the xz-plane (normal = (0,1,0))
result = (
    cq.Workplane("XZ")
    .circle(0.8)          # radius 0.8 mm
    .extrude(4.0)         # extrude 4.0 mm along normal (positive y)
)

# The design plan specifies extrude direction = -w = -y, so we need to flip.
# We can achieve this by mirroring or by extruding in the opposite direction.
# Simpler: extrude in the negative y direction by using a negative distance.
# But Workplane.extrude only takes positive distance along the plane normal.
# Alternative: build on a plane with normal pointing in -y, or use a transform.
# Let's rebuild with the correct orientation:

# The frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# The profile is on the uv-plane (u,v axes), extrude along -w = -y.
# So we create a circle on the plane defined by u and v axes, with normal w.
# Plane: origin (0,0,0), xDir=(1,0,0), normal=(0,1,0) -> this is the XZ plane.
# But v_dir is (0,0,-1), so the plane's y-axis is reversed. That's fine.
# Extrude along -normal (negative y) for 4.0 mm.

# Use a custom plane:
plane = cq.Plane(cq.Vector(0,0,0), cq.Vector(1,0,0), cq.Vector(0,0,-1))
result = (
    cq.Workplane(plane)
    .circle(0.8)
    .extrude(4.0)  # extrudes along normal = (0,1,0) by default
)

# To extrude in -w direction (-y), we need to extrude negative distance.
# But cadquery's extrude only accepts positive distance along the normal.
# So we can mirror the result about the xz-plane, or use a transform.
# Simpler: use a plane with normal pointing in -y.
plane2 = cq.Plane(cq.Vector(0,0,0), cq.Vector(1,0,0), cq.Vector(0,0,1))
result = (
    cq.Workplane(plane2)
    .circle(0.8)
    .extrude(4.0)  # extrudes along normal = (0,-1,0) -> -y
)

# Check: plane2 has xDir=(1,0,0), normal = cross(xDir, yDir) = cross((1,0,0), (0,0,1)) = (0,-1,0).
# So extrude(4.0) goes along (0,-1,0) which is -y. That matches -w direction.
# The v_dir in the design is (0,0,-1), but here we used (0,0,1) for yDir.
# That flips the v-axis, but since the circle is symmetric, it doesn't matter.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102760_26430589_0037\neg_03/generated.step")
