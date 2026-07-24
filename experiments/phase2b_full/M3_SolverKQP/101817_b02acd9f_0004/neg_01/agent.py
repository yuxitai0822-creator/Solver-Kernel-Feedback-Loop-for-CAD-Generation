import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 1200.0 mm, width_v = 600.0 mm, extrude_distance = 20.0 mm
# The profile is defined in a local frame where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> negative Z axis (so width is along Z)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
# The rectangle corners in UV space:
#   (127.82976131535646, -66.34402294937294)  -> top-right
#   (7.829761315356478,  -66.34402294937294)  -> top-left
#   (127.82976131535646, -6.344022949372942)  -> bottom-right
#   (7.829761315356478,  -6.344022949372942)  -> bottom-left
# The UV extents: U from 7.83 to 127.83 (delta = 120.0), V from -66.34 to -6.34 (delta = 60.0)
# But the design plan says length_u = 1200.0, width_v = 600.0, so the UV coordinates are scaled by 10x?
# Actually the compiler notes say "cm_to_mm (x10)" — the UV values are in cm, so multiply by 10 to get mm.
# Let's compute: U range = 127.82976131535646 - 7.829761315356478 = 120.0 cm = 1200 mm. V range = -6.344022949372942 - (-66.34402294937294) = 60.0 cm = 600 mm.
# So we build the rectangle in the XY plane (since u_dir = X, v_dir = Z? Wait, v_dir = (0,0,-1) means V maps to negative Z.
# The frame: u_dir = X, v_dir = -Z, w_dir = Y. So the rectangle lies in the XZ plane (with V reversed).
# To make it simple, we'll create the rectangle in the XY plane and then rotate/translate as needed.
# Actually, let's just use the UV coordinates directly: we'll create a 2D rectangle in the XY plane with the correct dimensions,
# then extrude along Y (w_dir). The UV origin is at (7.83, -66.34) in cm, but we'll work in mm.
# Better: create a rectangle centered at origin with length_u=1200 along X, width_v=600 along Z (since v_dir = -Z, we'll use Z).
# Then extrude along Y by 20 mm.

# Let's build the plate in the XY plane for simplicity, then rotate if needed.
# The design plan says the plate is flat, so we can just create a box with the right dimensions.
# But to match the exact UV coordinates, we'll create the rectangle in the XZ plane and extrude along Y.

# Create the rectangle profile in the XZ plane (since u_dir = X, v_dir = -Z, so V maps to -Z)
# The UV coordinates: U from 7.83 to 127.83 cm -> X from 78.3 to 1278.3 mm
# V from -66.34 to -6.34 cm -> Z from -663.4 to -63.4 mm (since v_dir = -Z, V positive gives negative Z)
# Actually, let's just use the dimensions directly: length_u=1200, width_v=600, extrude=20.
# We'll place the plate so that its min corner is at (78.3, 0, -663.4) in world coordinates.

# But the design plan's origin convention is bbox_min_corner, so the part's bounding box min corner is at origin.
# The UV coordinates suggest the min corner in UV space is (7.83, -66.34) cm = (78.3, -663.4) mm.
# To have the bbox min corner at (0,0,0), we need to translate.

# Let's compute the translation: the rectangle in UV space has min U=7.83, min V=-66.34.
# In world coordinates (using the frame):
#   world_point = origin + u * u_dir + v * v_dir
#   where u_dir = (1,0,0), v_dir = (0,0,-1)
#   So world_x = u, world_z = -v
#   Min corner: u=7.83, v=-66.34 -> world_x=7.83, world_z=66.34
#   Max corner: u=127.83, v=-6.34 -> world_x=127.83, world_z=6.34
# So the plate extends from x=7.83 to 127.83, z=6.34 to 66.34 (in cm).
# After scaling to mm: x=78.3 to 1278.3, z=63.4 to 663.4.
# The extrude direction is +w = +Y, so the plate extends from y=0 to y=20.
# To have bbox min corner at (0,0,0), we translate by (-78.3, 0, -63.4).

# But wait: the design plan says the dimensions are 1200x600x20 mm. The UV coordinates are just for positioning.
# Let's just create a box centered at origin with those dimensions, then translate so min corner is at origin.
# That's simpler and matches the validation intents.

# Create the plate as a box: length_u=1200 (X), width_v=600 (Z), extrude=20 (Y)
# But the frame says v_dir = (0,0,-1), so width is along Z (but reversed). We'll just use Z.

# Let's create the rectangle in the XY plane (X = u, Y = w) and then rotate? No, the extrude is along w_dir = Y.
# So the profile is in the XZ plane, extruded along Y.

# Approach: create a workplane on the XZ plane, draw a rectangle, extrude along Y.

result = (
    cq.Workplane("XZ")
    .rect(1200.0, 600.0, centered=False)
    .extrude(20.0)
)

# The above creates a plate with min corner at (0,0,0) in the XZ plane? 
# Actually, cq.Workplane("XZ") sets the plane with X and Z axes, and the rectangle is drawn with its
# first corner at the current point (which defaults to (0,0,0) in the plane).
# rect(1200, 600, centered=False) draws a rectangle with lower-left corner at the current point.
# So the plate will have its min corner at (0,0,0) in the XZ plane, which is world (0,0,0).
# The extrude goes in the positive Y direction (normal to XZ plane).
# This gives a plate from (0,0,0) to (1200, 20, 600).
# That matches the expected spans: u=1200, v=600, w=20.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\101817_b02acd9f_0004\neg_01\generated.step")
